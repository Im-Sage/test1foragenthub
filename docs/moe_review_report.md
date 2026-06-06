# MoE 实现代码审查报告

## 1. 数值稳定性审查 (Numerical Stability)
- **Softmax 溢出/下溢风险**：原始实现若直接对 logits 使用 `torch.softmax`，在 FP16/BF16 下极易因指数运算产生 `inf` 或 `0`。已采用 `log-sum-exp` 技巧（减去最大值）确保数值稳定。
- **除法保护**：Top-K 概率归一化时，若 `top_k` 概率和为 0（理论上不可能，但极端初始化可能触发），需添加 `eps=1e-8` 防止 `NaN`。
- **精度隔离**：门控网络计算强制使用 `FP32`，仅在路由完成后将权重转回输入精度。避免低精度下梯度消失或权重爆炸。
- **Z-Loss 引入**：对 logits 平方项施加惩罚，防止门控权重过度自信导致 softmax 饱和，显著提升训练后期稳定性。

## 2. 门控网络梯度传播验证 (Gradient Propagation)
- **Top-K 不可微问题**：`torch.topk` 返回的 `indices` 是离散操作，梯度无法回传。正确做法是：**梯度仅通过 `topk_probs` 传播**，`indices` 仅用于路由分发。
- **梯度流路径**：`loss → expert_output → topk_probs → probs → gate.weight`。实现中已确保 `topk_probs` 保留计算图，且未对概率值执行 `.detach()`。
- **辅助损失梯度**：负载均衡损失 `L_aux` 仅依赖 `probs` 和 `indices` 的统计量，不参与前向路由，但会反向更新 `gate.weight`，符合 Switch Transformer 设计。
- **验证建议**：使用 `torch.autograd.gradcheck` 对门控模块进行数值梯度验证，确保 `gate.weight.grad` 非零且量级合理。

## 3. 专家负载均衡策略评估 (Load Balancing Strategy)
- **当前策略**：采用 `L_aux = α * Σ(f_i * P_i)`，其中 `f_i` 为路由到专家 i 的 token 比例，`P_i` 为专家 i 的平均门控概率。该策略能有效惩罚“热门专家”，促进均匀分配。
- **容量因子 (Capacity Factor)**：若未实现容量限制，长序列下易出现专家 OOM。建议引入 `capacity = ceil(seq_len * top_k / num_experts * capacity_factor)`，超出部分路由至 dummy expert 或丢弃，并配合 mask 阻断梯度。
- **动态调整**：静态 `aux_loss_weight` 在训练初期可能干扰表征学习。建议采用 warmup 策略或根据实际负载方差动态缩放权重。
- **有效性验证**：监控 `load.std() / load.mean()`，理想值应 `< 0.1`。若持续偏高，需增大 `aux_loss_weight` 或检查数据分布偏斜。

## 4. 性能优化建议 (Performance Optimization)
| 优化方向 | 具体方案 | 预期收益 |
|----------|----------|----------|
| **计算融合** | 将 `gate → softmax → topk → normalize` 融合为单个 Triton 内核 | 减少 30%~50% 内存带宽占用 |
| **专家并行** | 使用 `torch.distributed` 的 `AllToAll` 或 `GroupedGEMM` 分发 token | 降低跨设备通信延迟，提升吞吐 |
| **内存布局** | 将专家权重按 `num_experts × hidden_dim × output_dim` 连续存储，配合 `torch.bmm` 或 `einsum` | 提升缓存命中率，减少碎片 |
| **编译加速** | 使用 `torch.compile(mode="reduce-overhead")` 包装门控前向 | 自动内核融合，减少 Python 开销 |
| **梯度裁剪** | 对 `gate.weight.grad` 施加 `max_norm=1.0` | 防止辅助损失引发梯度爆炸 |

## 5. 行动清单
- [ ] 替换原始门控实现为 `src/moe/stable_gating.py`
- [ ] 添加容量因子与 overflow mask 处理逻辑
- [ ] 在训练循环中监控 `aux_loss` 与 `load_balance_ratio`
- [ ] 使用 `torch.autograd.gradcheck` 验证梯度正确性
- [ ] 压测 FP16/BF16 混合精度下的吞吐与显存峰值