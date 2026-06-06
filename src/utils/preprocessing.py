"""
数据预处理与训练工具模块
支持批量张量标准化、专家输出加权聚合、梯度裁剪及混合精度训练。
"""
import torch
import torch.nn as nn
from torch.cuda.amp import autocast, GradScaler
from typing import List, Optional, Union

__all__ = [
    "normalize_batch_tensor",
    "aggregate_expert_outputs",
    "clip_gradients",
    "MixedPrecisionTrainer",
]


def normalize_batch_tensor(
    tensor: torch.Tensor,
    dim: int = -1,
    eps: float = 1e-8,
    unbiased: bool = False
) -> torch.Tensor:
    """
    对批量输入张量进行标准化（零均值，单位方差）。

    Args:
        tensor: 输入张量，形状通常为 (batch, features, ...)
        dim: 计算均值和标准差的维度
        eps: 防止除零的极小值
        unbiased: 是否使用无偏标准差估计 (Bessel's correction)

    Returns:
        标准化后的张量
    """
    mean = tensor.mean(dim=dim, keepdim=True)
    std = tensor.std(dim=dim, keepdim=True, unbiased=unbiased)
    return (tensor - mean) / (std + eps)


def aggregate_expert_outputs(
    expert_outputs: List[torch.Tensor],
    weights: Union[torch.Tensor, List[float]],
    dim: int = 1,
    normalize_weights: bool = True
) -> torch.Tensor:
    """
    对多个专家模型的输出进行加权聚合。

    Args:
        expert_outputs: 专家输出张量列表，每个形状应为 (batch, ...)
        weights: 权重张量，形状为 (num_experts,) 或 (batch, num_experts)
        dim: 堆叠与聚合的维度
        normalize_weights: 是否对权重进行 Softmax 归一化

    Returns:
        聚合后的张量，形状为 (batch, ...)
    """
    if not expert_outputs:
        raise ValueError("expert_outputs 列表不能为空")

    # 沿指定维度堆叠专家输出: (batch, num_experts, ...)
    stacked = torch.stack(expert_outputs, dim=dim)

    # 统一权重为张量
    if isinstance(weights, list):
        weights = torch.tensor(weights, device=stacked.device, dtype=stacked.dtype)

    # 权重归一化（可选）
    if normalize_weights:
        weights = torch.softmax(weights, dim=-1)

    # 调整权重形状以匹配 stacked 张量进行广播
    if weights.dim() == 1:
        # (num_experts,) -> (1, num_experts, 1, 1, ...)
        shape = [1] * stacked.dim()
        shape[dim] = weights.size(0)
        weights = weights.view(shape)
    elif weights.dim() == 2:
        # (batch, num_experts) -> (batch, num_experts, 1, 1, ...)
        shape = [weights.size(0)] + [1] * (stacked.dim() - 1)
        shape[dim] = weights.size(1)
        weights = weights.view(shape)
    else:
        raise ValueError("weights 必须为 1D 或 2D 张量")

    # 加权求和
    return (stacked * weights).sum(dim=dim)


def clip_gradients(
    model: nn.Module,
    max_norm: float = 1.0,
    norm_type: float = 2.0
) -> float:
    """
    裁剪模型梯度以防止梯度爆炸。

    Args:
        model: PyTorch 模型
        max_norm: 允许的最大梯度范数
        norm_type: 范数类型 (2.0 表示 L2 范数)

    Returns:
        裁剪前的总梯度范数
    """
    return torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm, norm_type)


class MixedPrecisionTrainer:
    """
    混合精度训练封装器，集成自动混合精度(AMP)与梯度裁剪。
    """
    def __init__(
        self,
        enabled: bool = True,
        dtype: torch.dtype = torch.float16,
        init_scale: float = 65536.0,
        growth_factor: float = 2.0,
        backoff_factor: float = 0.5,
        growth_interval: int = 2000
    ):
        self.enabled = enabled and torch.cuda.is_available()
        self.dtype = dtype
        self.scaler = GradScaler(
            enabled=self.enabled,
            init_scale=init_scale,
            growth_factor=growth_factor,
            backoff_factor=backoff_factor,
            growth_interval=growth_interval
        )

    def forward(self, model: nn.Module, inputs: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        """
        在 autocast 上下文中执行模型前向传播。
        """
        with autocast(enabled=self.enabled, dtype=self.dtype):
            outputs = model(inputs, *args, **kwargs)
        return outputs

    def backward_and_step(
        self,
        loss: torch.Tensor,
        optimizer: torch.optim.Optimizer,
        model: nn.Module,
        max_grad_norm: Optional[float] = None
    ) -> float:
        """
        执行反向传播、梯度裁剪、优化器步进与缩放器更新。

        Args:
            loss: 计算得到的损失张量
            optimizer: PyTorch 优化器
            model: PyTorch 模型
            max_grad_norm: 梯度裁剪阈值，若为 None 则不裁剪

        Returns:
            裁剪前的梯度范数（若未裁剪则返回 0.0）
        """
        # 缩放损失并反向传播
        self.scaler.scale(loss).backward()

        grad_norm = 0.0
        if max_grad_norm is not None:
            # 在裁剪前必须反缩放梯度
            self.scaler.unscale_(optimizer)
            grad_norm = clip_gradients(model, max_grad_norm)

        # 优化器步进与缩放器状态更新
        self.scaler.step(optimizer)
        self.scaler.update()
        optimizer.zero_grad()

        return grad_norm