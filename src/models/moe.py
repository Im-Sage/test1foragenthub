"""
Mixture of Experts (MoE) Core Architecture
==========================================
Implements:
- Expert network definition (FFN-based)
- Gating mechanism with dynamic top-k routing
- Sparse activation logic
- Load balancing auxiliary loss
- Training loop integration

Designed for PyTorch 2.x+ with backend service integration in mind.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional


class Expert(nn.Module):
    """Single expert network (typically a Feed-Forward Network)."""
    def __init__(self, dim: int, hidden_dim: int, dropout: float = 0.0):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, dim),
            nn.Dropout(dropout)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class MoEGate(nn.Module):
    """
    Gating network that computes routing probabilities and selects top-k experts.
    Adds small Gaussian noise during training to encourage exploration and prevent expert collapse.
    """
    def __init__(self, dim: int, num_experts: int, top_k: int, noise_std: float = 0.01):
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k
        self.noise_std = noise_std
        self.gate_proj = nn.Linear(dim, num_experts, bias=False)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Args:
            x: (batch, seq_len, dim)
        Returns:
            topk_probs: (batch*seq_len, top_k) routing weights
            topk_indices: (batch*seq_len, top_k) selected expert indices
            gate_probs: (batch*seq_len, num_experts) full softmax probabilities
        """
        B, S, D = x.shape
        x_flat = x.view(-1, D)  # (B*S, D)

        logits = self.gate_proj(x_flat)  # (B*S, num_experts)

        # Add noise during training for exploration
        if self.training and self.noise_std > 0:
            noise = torch.randn_like(logits) * self.noise_std
            logits = logits + noise

        gate_probs = F.softmax(logits, dim=-1)
        topk_probs, topk_indices = torch.topk(gate_probs, self.top_k, dim=-1)

        return topk_probs, topk_indices, gate_probs


class MoELayer(nn.Module):
    """
    Single MoE layer combining gating, sparse expert routing, and load balancing.
    """
    def __init__(
        self,
        dim: int,
        hidden_dim: int,
        num_experts: int,
        top_k: int,
        aux_loss_weight: float = 0.01,
        dropout: float = 0.0
    ):
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k
        self.aux_loss_weight = aux_loss_weight

        self.experts = nn.ModuleList([
            Expert(dim, hidden_dim, dropout) for _ in range(num_experts)
        ])
        self.gate = MoEGate(dim, num_experts, top_k)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x: (batch, seq_len, dim)
        Returns:
            output: (batch, seq_len, dim)
            aux_loss: scalar load balancing loss
        """
        B, S, D = x.shape
        x_flat = x.view(-1, D)  # (B*S, D)

        topk_probs, topk_indices, gate_probs = self.gate(x)

        # Initialize output buffer
        out = torch.zeros_like(x_flat)

        # Track routing statistics for auxiliary loss
        expert_counts = torch.zeros(self.num_experts, device=x.device)
        expert_probs_sum = torch.zeros(self.num_experts, device=x.device)

        # Sparse activation: route tokens to selected experts
        for i in range(self.num_experts):
            # Boolean mask: which tokens selected expert i
            mask = (topk_indices == i)  # (B*S, top_k)
            # Extract corresponding routing weights
            weights = torch.sum(topk_probs * mask.float(), dim=1)  # (B*S,)
            token_mask = weights > 0

            if not token_mask.any():
                continue

            # Forward pass through expert i
            expert_input = x_flat[token_mask]
            expert_output = self.experts[i](expert_input)

            # Weighted scatter back to output
            out[token_mask] += expert_output * weights[token_mask].unsqueeze(-1)

            # Accumulate stats
            expert_counts[i] = token_mask.sum()
            expert_probs_sum[i] = weights.sum()

        out = out.view(B, S, D)

        # Load balancing auxiliary loss (GShard / Switch Transformer formulation)
        # L_aux = α * N * Σ_i (f_i * P_i)
        # f_i: fraction of tokens routed to expert i
        # P_i: average gate probability for expert i
        total_tokens = B * S
        f = expert_counts / total_tokens
        P = expert_probs_sum / total_tokens
        aux_loss = self.aux_loss_weight * torch.sum(f * P) * self.num_experts

        return out, aux_loss


class MoEModel(nn.Module):
    """
    Full MoE model wrapper supporting multiple stacked MoE layers.
    """
    def __init__(
        self,
        dim: int,
        hidden_dim: int,
        num_experts: int,
        top_k: int,
        num_layers: int = 1,
        aux_loss_weight: float = 0.01,
        dropout: float = 0.0
    ):
        super().__init__()
        self.layers = nn.ModuleList([
            MoELayer(dim, hidden_dim, num_experts, top_k, aux_loss_weight, dropout)
            for _ in range(num_layers)
        ])
        self.norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x: (batch, seq_len, dim)
        Returns:
            output: (batch, seq_len, dim)
            total_aux_loss: scalar
        """
        total_aux_loss = torch.tensor(0.0, device=x.device)
        for layer in self.layers:
            x, aux = layer(x)
            total_aux_loss = total_aux_loss + aux
        return self.norm(x), total_aux_loss


# =============================================================================
# Training Loop Example
# =============================================================================
def train_moe_step(
    model: MoEModel,
    optimizer: torch.optim.Optimizer,
    data: torch.Tensor,
    target: torch.Tensor,
    criterion: nn.Module,
    max_grad_norm: float = 1.0
) -> dict:
    """
    Single training step for MoE model.
    Combines task loss with load balancing auxiliary loss.
    """
    model.train()
    optimizer.zero_grad()

    # Forward pass
    output, aux_loss = model(data)
    task_loss = criterion(output, target)
    loss = task_loss + aux_loss

    # Backward & optimize
    loss.backward()
    if max_grad_norm > 0:
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
    optimizer.step()

    return {
        "total_loss": loss.item(),
        "task_loss": task_loss.item(),
        "aux_loss": aux_loss.item()
    }


# =============================================================================
# Usage Example
# =============================================================================
if __name__ == "__main__":
    # Hyperparameters
    BATCH_SIZE = 4
    SEQ_LEN = 16
    DIM = 64
    HIDDEN_DIM = 128
    NUM_EXPERTS = 8
    TOP_K = 2
    NUM_LAYERS = 2
    LR = 1e-3
    EPOCHS = 3

    # Initialize model
    model = MoEModel(
        dim=DIM,
        hidden_dim=HIDDEN_DIM,
        num_experts=NUM_EXPERTS,
        top_k=TOP_K,
        num_layers=NUM_LAYERS,
        aux_loss_weight=0.01
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)
    criterion = nn.MSELoss()

    # Dummy data
    x = torch.randn(BATCH_SIZE, SEQ_LEN, DIM)
    y = torch.randn(BATCH_SIZE, SEQ_LEN, DIM)

    print("Starting MoE training loop...")
    for epoch in range(EPOCHS):
        metrics = train_moe_step(model, optimizer, x, y, criterion)
        print(f"Epoch {epoch+1}/{EPOCHS} | "
              f"Total Loss: {metrics['total_loss']:.4f} | "
              f"Task Loss: {metrics['task_loss']:.4f} | "
              f"Aux Loss: {metrics['aux_loss']:.4f}")

    print("Training complete. Model ready for backend integration.")