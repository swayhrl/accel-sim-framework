# DQ2：小批量 B1→B4 与执行模式

本轮从 164 formal raw 独立得到一个合法的**同点 B1 响应**：MP02 MODE_A 与 MODE_B 各 5 个仪器关闭、请求级 CUDA Event 样本，32 个生成 token 与原数值门槛逐步相同。A 中位数 354.59820556640625 ms，MAD 0.28192138671875 ms；B 中位数 361.45654296875 ms，MAD 0.051788330078125 ms。B/A=1.0193411508989134；以 B 为分母，A 的时间减少 1.8974168640064404%。每生成 token 的请求时间分别为 11.081193923950195 和 11.295516967773438 ms。23 个与 producer 的数值字段交叉核对全部一致。五个 formal 请求不构成统计显著性或跨 shape 推断。

MP03_A 虽有五个 formal 数值（中位数 464.637939453125 ms），但缺少合法的同点 B arm，所以仅能作诊断。原版 MP03_B 在旧 cache gate 前 0 warmup/0 formal；surgical continuation 的两次四行 warmup 正确、编译模型仍有效，但最终 cache 身份门槛失败，formal 仍为 0。因此不能构造 B4 的 A/B pair，不能算 B1→B4 throughput scale，也不能算 Graph×batch/shape interaction。不能把 MP02 的约 1.9% 扩展到 B4 或解释成利用率机制。

终态：`DQ2 = QUESTION_INCOMPLETE`，有效子结果为 `DQ2_NATIVE_RECOVERY_PARTIAL`；`MP02_B1_NATIVE_POINT = SCIENCE_VALID`，`MP03_B4_NATIVE_POINT = INCOMPLETE_EXECUTION_IDENTITY_STOP`。
