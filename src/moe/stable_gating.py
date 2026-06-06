import torch
import torch.nn as nn
import torch.nn.functional as F

class StableMoEGating(nn.Module):
    """
    数值稳定、梯度正确、带负载均衡的 MoE 门控网络实现。
    适用于 Switch Transformer / Mixtral 架构。
    """
    def __init__(
        self,
        hidden_dim: int,
        num_experts: int,
        top_k: int = 2,
        aux_loss_weight: float = 0.01,
        z_loss_weight: float = 1e-4,
        capacity_factor: float = 1.0,
        eps: float = 1e-8
    ):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_experts = num_experts
        self.top_k = top_k
        self.aux_loss_weight = aux_loss_weight
        self.z_loss_weight = z_loss_weight
        self.capacity_factor = capacity_factor
        self.eps = eps
        
        # 门控权重初始化：Xavier 均匀分布，避免初始 logits 过大
        self.gate = nn.Linear(hidden_dim, num_experts, bias=False)
        nn.init.xavier_uniform_(self.gate.weight)

    def forward(self, x: torch.Tensor):
        """
        Args:
            x: (batch, seq_len, hidden_dim)
        Returns:
            topk_indices: (batch, seq_len, top_k) 路由目标专家索引
            topk_probs:   (batch, seq_len, top_k) 归一化路由权重
            aux_loss:     负载均衡辅助损失
            z_loss:       正则化损失
        """
        # 1. 强制 FP32 计算，保障数值稳定性
        logits = self.gate(x.float())
        
        # 2. Log-Sum-Exp 技巧防止 softmax 溢出
        logits_max = logits.max(dim=-1, keepdim=True).values
        logits_stable = logits - logits_max
        probs = F.softmax(logits_stable, dim=-1)
        
        # 3. Top-K 路由
        topk_probs, topk_indices = torch.topk(probs, self.top_k, dim=-1)
        # 归一化 top-k 概率，确保权重和为 1
        topk_probs = topk_probs / (topk_probs.sum(dim=-1, keepdim=True) + self.eps)
        
        # 4. 计算辅助损失
        aux_loss = self._compute_load_balancing_loss(probs, topk_indices)
        z_loss = self._compute_z_loss(logits)
        
        return topk_indices, topk_probs, aux_loss, z_loss

    def _compute_load_balancing_loss(self, probs: torch.Tensor, topk_indices: torch.Tensor) -> torch.Tensor:
        """
        计算负载均衡辅助损失: L_aux = α * Σ(f_i * P_i)
        f_i: 路由到专家 i 的 token 比例
        P_i: 专家 i 的平均门控概率
        """
        # Importance: 每个专家的平均门控概率
        importance = probs.mean(dim=(0, 1))  # (num_experts,)
        
        # Load: 每个专家接收的 token 比例
        mask = F.one_hot(topk_indices, num_classes=self.num_experts).float()
        load = mask.sum(dim=(0, 1))  # (num_experts,)
        load = load / (load.sum() + self.eps)
        importance = importance / (importance.sum() + self.eps)
        
        return self.aux_loss_weight * (importance * load).sum()

    def _compute_z_loss(self, logits: torch.Tensor) -> torch.Tensor:
        """
        Z-Loss: 惩罚过大的 logits，防止 softmax 饱和与梯度消失
        """
        return self.z_loss_weight * (logits ** 2).mean()

    def apply_capacity_mask(self, topk_indices: torch.Tensor, topk_probs: torch.Tensor, seq_len: int):
        """
        容量限制处理：超出容量的 token 路由至 dummy expert (index = num_experts)
        并返回 mask 用于阻断无效梯度。
        """
        capacity = int(torch.ceil(torch.tensor(seq_len * self.top_k / self.num_experts * self.capacity_factor)))
        expert_counts = torch.zeros(self.num_experts, device=topk_indices.device, dtype=torch.long)
        
        # 统计每个专家当前分配的 token 数
        for i in range(self.num_experts):
            expert_counts[i] = (topk_indices == i).sum()
            
        # 生成 overflow mask
        overflow_mask = torch.zeros_like(topk_probs, dtype=torch.bool)
        for i in range(self.num_experts):
            if expert_counts[i] > capacity:
                # 标记超出容量的位置
                indices = (topk_indices == i).nonzero(as_tuple=True)
                overflow_mask[indices[0], indices[1], indices[2]] = True
                
        # 将 overflow 路由至 dummy expert
        topk_indices[overflow_mask] = self.num_experts
        topk_probs[overflow_mask] = 0.0
        
        return topk_indices, topk_probs, ~overflow_mask