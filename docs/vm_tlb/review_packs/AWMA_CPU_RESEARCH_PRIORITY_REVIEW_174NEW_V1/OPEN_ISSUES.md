# 尚未闭合与本轮处置
- **数值**：没有分量/根因/训练质量证据；本轮只 CPU 重算 published 25 坐标。没有读取 6.31 GB 控制 tensor，R26–R27R3 STOP/接受范围保持。
- **模型兼容**：Sobek homogeneous uvu/unique irrep 与 NequIP block 结构存在明确冲突。读取 accepted node164 zip 内 `model/config.yaml`（仅文本 metadata，SHA 与旧 `78b58be5…601a`一致）后，发现 model 指向 `ModelFromCheckpoint`，没有完整展开的每层 TPProblem。因此不能把官方网页超参数或源码模板升级为 loaded instance 构造成功。没有读取 storage/pickle/checkpoint或执行模型。
- **输入**：sitraj chronology 未资格化；MD22 data module 的来源/分割说明不构成时间顺序保证。frame101/107只是未在本轮看过的条件性保留，旧使用状态仍须在未来新合同核对。
- **ALCHEMI**：fixed docs/API 能力已核，没有同一 OAM/Sobek 完整力路径的本机或作者计时。exact/padded COO 与 buffered/immutable 图接口需适配；不能推零成本。
- **论文**：5 组 PAPER_AUTHOR 实际组可定位（3个独立论文）；ALCHEMI官方案例不计性能组。Kitsune 具体训练输入 tensor 维度/benchmark data 实例未在所读主文披露，独立质量验证细节也未核；其模型结果不是 Native 4080。
- **近邻/创新**：排序、CSR、prepare cache、虚拟 tensor、queue/dataflow 均已有。当前没有证明任何有限 hardware residual。
- **工程**：174 raw.githubusercontent DNS失败，用 GitHub contents API 读取同一 pinned 文件并核轻量 SHA；VTC官方PDF经Poppler渲染核表。远端 apply_patch 是 GNU patch wrapper，采用标准 unified patch/ASCII base64传输，未改变科学文件。未新增科研轮次。
