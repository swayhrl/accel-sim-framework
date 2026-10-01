# 验证摘要

- Git 主源码 checkout 精确为 `b2f71003113defb4e387caf18843b241f6280ba9`，作者四个相关子模块分别精确 checkout 其 gitlink SHA；源码文件 blob 登记在 `SOURCE_REGISTER.tsv`。
- 独立只读 register 校验：20/20 固定 Git blob 与 1/1 作者 PDF SHA-256 匹配，`R19_SOURCE_REGISTER_PASS`。
- 阅读 C++/CUDA/PyTorch API、device helper、FlexGen/InfiniGen、DGL、Legion、ColossalAI 中的生产者和消费者调用点；所报告的融合缺失只覆盖这些固定路径。
- 阅读 IBP 作者 EuroSys 扩展论文，并目视核对 Figure 9：真实 Reddit 的 IBP(C/M) 尚有可见 sampler wait。作者 PDF SHA-256 登记在 source register；不提交 PDF 或页面图片。
- 回读 DFloat11、ZipServ、tile-rANS/GEMM 原文以及 NVIDIA nvCOMP Device API 文档；未用二手综述替代最近邻事实。
- 回读 Round18 R53 erratum 和 literature README；更正已存在。
- 未下载数据集/模型，未编译、未执行 CUDA、GPU、Accel-Sim、Native profiling 或新机制。
