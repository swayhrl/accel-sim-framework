# DTC-MAIN CORE32 Oracle 本轮总签署

签署范围：固定 32 程序 × OFF/M/L2/L1 的 128 个受控 trace 性能格、96 个同版本配对，以及 D 独立终审、M 完整机会分析和 Main 交叉核对。固定交接基线为 `3f0036f2868e20a8d9a4b6244c7c74d940954188`；已发布运行结果为 `7ffcca7f908a21f45ba1a6ebb3b335ff962f97df`。

本轮判定：在报告声明的 SM70/V100-derived 64SM trace 范围内，D 的 128 格严格审阅、true164 归档和 native 恢复均为 PASS；M 的 32 程序机会分析和 Main 的逐格、逐配对、GM、分布、kernel 周期及证据连接复核闭合。L2 的 11 个精确零、`myocyte` 和 `srad_v1` 两个有效回退，及计数器缺失和单位限制均保留。正式结论与可审查来源见 `REPORT.zh.md`、`analysis/MAIN_CROSSCHECK.json` 和 `MANIFEST.json`。

发布前回读：独立临时 Git 对象库从 GitHub 取回 `fe1b7e6295997e3ee68f9c17ffdb43d3140c8363`，按当时清单逐文件校验 21 个成员、树内 22 个文件，结果 PASS；机器回执见 `GITHUB_READBACK_PRE_SIGNOFF.json`。本签署和该回执纳入后续发布提交，最终提交须再次从 GitHub 回读并另存本机回执。

限制：Oracle 仅为受控反事实，不许诺可实现结构收益；原生完整应用数值、capture ELF/数据内容绑定、等面积收益、结构机制因果和新输入覆盖仍未证明。英文 LaTeX v0.23、原始 Source、负例和 HOLD 均未改动。旧 `RUNNING`、应用层 `blocked` 与 M 快照 `NOT_YET_FINAL` 是历史静态字段，不表示本轮模型尚未结束。

本 Goal 新增科学模拟、request 和预算消费均为 **0**。后续结构建议仅为待授权草案；DTC-L1-11 审查和下一科学执行授权前 **STOP**。
