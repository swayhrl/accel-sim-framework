# Goal: DTC_HOTSPOT_FORMAT_PROVENANCE_174_V1

环境：此前DTC运行的原174账户/容器，新Codex窗口；不是174-new。完整阅读本目录README。目标是在主实验不停的同时，解决Hotspot的历史shared地址编码解释缺口；本任务不建立另一个仿真调度器。

## 独立工作区

从当前已推送主执行源码及其固定构建Framework建立独立worktree，建议结果分支`hrl/iscas2027-dtc-hotspot-format-174-v1`。不得改主worktree、raw trace、runner、使用中的parser或binary，不得移除ROW_ADMISSION_HOLDS。只读访问主线既有payload。检查已有同名任务与磁盘/进程后再开始。

先读：
- Framework e3dbe3dbf2abb49b923244538d2a3d1828024d4f，`docs/dtc_l1/iscas2027/service_closure_174_v1/HOTSPOT_SHARED_FORMAT_REVIEW_V1.md`。
- 同处`review_pack/trace_body_v1/`的ORACLE_RECEIPT、body audit、已列source/hash与ROW_ADMISSION_HOLDS。
- 构建Framework18a68dcccd795f1b6cda75504e9450d00c9cee02的`gpu-simulator/trace-parser/trace_parser.cc`，以及审计找到的实际compressor路径与history。

已知：90792条Hotspot shared mode1 records的mask不连续。例PC0290/STS/mask fffcfffc/base0x80/stride4，冻结decoder对活动lane2/15/18/31得到128/180/0/0。当前可见compressor却拒绝有空洞的mask；不能据当前compressor推断历史producer。其他11个输入没有该类record；全部629正文审计无需重跑。

## 按证据逐步推进

A. 先复用现有计数/索引定位Hotspot的原始header、压缩/重排阶段与获取来源；查本地历史producer、trace下载索引/发布包、Git历史与与该header相关的上游格式修订。公开仓库可按确切来源检索；不把当前dev默认语义当作历史事实。包装索引若能由已有来源确定性恢复，直接恢复，不把它判为scientific payload丢失。

B. 优先找到能够**唯一确定每个活动lane地址**的原始未压缩地址、原producer版本、相应格式定义，或与本次二进制/采集严格绑定的其他独立来源。不是必须拿到一个特定hash才算证据，但必须排除lane-index与active-lane-ordinal等不同解释。当前地址合法、结果好看或bank冲突更少都不能替代来源。

C. CPU-only复现原oracle及候选encoder/decoder关系；覆盖非零起始lane、内部空洞、多个活动区间、stride正/负/零、base0与非零、LDS/STS实际宽度。对于round-trip，避免用同一错误假设同时写编码和解码后自证。用来源明确的未压缩地址作独立参考，保留全部反例。

D. 来源能唯一消除分歧时，制作隔离候选补丁或显式离线规范化器，默认不改变旧路径；只读枚举受影响Hotspot记录，给出原地址与候选地址差异、是否影响bank服务/动态指令范围。其余格式语义不得改动。没有资料就给具体缺口和可行选项，不自行选一个公式。

## 停止与交付

本任务允许代码原型和CPU单元测试，不允许把地址语义更正合入主Framework、解除Hotspot HOLD或启动正式Hotspot重跑。查明唯一语义也需报告这是更正了哪些既有结果的解释；由主线审查后登记最小配对重验/重跑。若改变parser但可对11个未受影响输入作确定性等价，给出证明范围与hash，不让主线全部重跑。

90分钟左右先推第一份可用状态；约4小时完成来源闭合/候选补丁/证据仍不足三者之一的明确交付。没有新信息时不要循环扫描9GB或搜整台164。若需要重新抓原输入、改用新输入或排除Hotspot，列出代价和scope，等待用户决定，不把新trace冒充原trace。

结果目录`docs/dtc_l1/review_packs/DTC_HOTSPOT_FORMAT_CLOSURE_V1/`：README、SOURCE_REGISTER.tsv（事实/推断/缺失）、CPU_TEST_RESULTS、DECODER_DELTA、AFFECTED_ROWS.tsv、NEXT_DECISION.md。补丁放本分支，注明Framework/Core/binary影响；不写全局LATEST_REPORT。push并fetch-back核对后交给A；普通读取/parser/build问题自行修复继续，语义不明才停审。
