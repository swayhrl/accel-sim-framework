# 下一阶段研究判断（仅 CPU/source decision，不授权实验）

| 选项 | 可能收获 | 当前代价与准入问题 | 判断 |
|---|---|---|---|
| A. 继续修 MP02/03 语义/原生可观测性 | 也许恢复 decode family 时间线或 B4 pair | Python hooks 在 compiled path 为 0/4608；现有 compiler artifact 仅 LEVEL_0；MP03_B 已两次受 cache 身份门槛阻断。继续换 hook/cache policy 会改变强基线或需新增等价性合同，工具修复成本已大于已证明的科学收益。 | 当前 STOP，不启动第四轮恢复。 |
| B. 直接进入 Tier1 或 holdout | 或能看到更细计数/跨输入现象 | 四个问题均未过完整 Tier0 门槛；B4 pair、decode attribution 和 whole-run headroom 仍缺。用 profiler 或 holdout 补准入是倒置治理。 | NOT READY；不运行。 |
| C. 结束当前 Stage A，从天然可测的问题重设下一轮 discovery | 可先选择 strong compiled path 上不依赖 Python module hooks 的原生请求/阶段 observable，再问是否有足够 wall weight 与合法软件对照 | 需要一个新的、事前定义的问题、原生可测端点、最强软件基线、零成本 whole-run 上限与独立验证；不能拿现有不完整结果直接改名为新问题。 | **推荐：STOP 当前 Stage A；未来仅在新问题与可测 observable 同时闭合后重新开启 C16。** |

MP01 的 BF16 prefill 局部组成/时序、MP05 的 AWQ representation control 和 MP02 的 B1 A/B 响应都值得归档，但它们当前不足以单独构成有整请求 headroom、强对照与 holdout 的可推广机制问题。下一轮若存在，应优先选在成熟 compiled runtime 上**天然可测且可独立复算**的现象，不再以强行恢复 module-level chronology 为起点。没有达到这些准入标准的新问题时，研究动作就是 STOP，而非让 GPU 保持忙碌。本文件不生成 Stage A V2、Tier1、holdout 或 GPU 合同。
