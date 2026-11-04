# Historical Node109 report — public review copy

- Source ID: `disk_audit_20261028`
- Original SHA256: `8b2766d681b3a2e89a943ef68ccff13b6587836b97f4befd47a326114a2d2137`
- Status: Historical snapshot, not the 2026-11-04 current-state result.
- Disclosure: Private host/account details were replaced; see `HISTORICAL_REPORT_PROVENANCE.json`. The local original remains unchanged.

---

109 磁盘占用、164 备份与 ImageLab 归档分析
审计日期：2026-10-28（北京时间）。本轮仅分析；没有删除、迁移、上传或启动归档任务。

磁盘与范围
109 根盘 ext4：容量 936.79 GiB，已用约 835.34 GiB，可用约 53.79 GiB，df 使用率 94%。
/data/c16 376.96 GiB；/home/<OWNER> 约 205 GiB，其中 workspace 203.98 GiB，ImageLab 183.46 GiB。
ImageLab 模型 167.57 GiB，环境约 6.98 GiB，缓存约 4.41 GiB，应用约 2.29 GiB，输出约 1.24 GiB。
数据盘主要项目：awma 102.44 GiB；models 72.18 GiB（含少量凭据等）；E1 bounded 43.29 GiB；A26GR1 40.77 GiB；env 27.61 GiB；rtx4080 suite 11.74 GiB；nequip v1r1 10.92 GiB；A61 9.86 GiB；merged gate up 8.57 GiB；capture 8.37 GiB；stagea 8.31 GiB；envs 8.25 GiB。
当前账号能遍历的根文件系统合计约 623 GiB，比 df 已用少约 213 GiB。其他用户家目录、/root 等不可读；差额不能归因于当前用户，也不能直接认定为已删除文件占用。当前用户 lsof 未发现大量磁盘已删未释放文件。无免密 sudo。本次未覆盖其他账号数据。
164：通过 109 的 <BRIDGE_SSH_ALIAS>（174:<BRIDGE_PORT>）访问；/root/share/mnt164 确实挂载 <ARCHIVE_SERVICE_ACCOUNT>@<TRUE164_PRIVATE_IP>:/home/shared。共享盘容量约154 TiB，已用103 TiB，可用43 TiB，71%。109 的 nas_rtx4080 是164远程挂载，377 GiB本地统计已排除它，不可把远端数据算成本地可回收量。

优先核验后清理候选（不是删除授权或已完成清理）
1. /data/c16/models/qwen3-30b-a3b：56.889 GiB。revision ad44e777bcd18fa416d9da3bd8f70d33ebb85d39。26个本地文件全部在164 c16_ai_workload/assets/models 下同版本同相对路径、同大小；归档凭据标记 EXACT_FILE_SET_SIZE_SHA256_PASS。16个权重分片本次扫描前 atime 均为9月26日；配置等可能被10月16日审计读取。
2. /data/c16/models/olmoe-1b-7b-0125-instruct：12.892 GiB。revision b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e。12个文件全部路径大小对应；164存在含逐文件SHA256的MODEL_ASSET_RECEIPT。3个权重 atime 10月1日。
3. /data/c16/models/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08：2.310 GiB。6个文件全部对应；归档凭据标记 EXACT_RELATIVE_PATH_SIZE_SHA256_PASS。权重atime 10月13日。
三个模型合计72.092 GiB。本次未重读约72 GiB权重计算两端SHA256；历史归档凭据+当前元数据是本轮证据等级。清理前必须补当前两端内容校验、恢复路径与依赖检查。
4. /data/c16/capture/transferred：3.044 GiB，4723/4723文件在164 c16_ai_workload/raw下对应同路径同大小。
5. /data/c16/capture/ready：5.296 GiB中仅4.077 GiB、3708/6977文件符合相同检查；余3269文件约1.220 GiB未找到该精确路径，保留。不能整目录删除。
上述同路径同大小候选合计79.213 GiB、8475个不同inode，本批nlink均为1。采集文件只通过当前路径/大小检查，未全部补查历史SHA凭据或当前内容哈希，证据等级低于三个模型。精确文件见cleanup_candidates_REQUIRE_SHA256.csv。权重与采集文件均未出现在本账号当前/proc打开文件、内存映射快照中；其他用户进程不可完整检查，瞬时快照也不能证明未来无依赖。
如后续全部校验通过并释放79.2 GiB，按当前占用推算，可用空间约133 GiB，df使用率约85%；这不是已实现释放量。

第二批冷数据与暂缓项目
E1 formal_d1_d3_20260924_v2 37.42 GiB，v1 5.53 GiB。mtime为9月24~25日，最近文件atime上界10月16日。v2的TERMINAL_RACE_REJECTED_NOT_SIM_INPUT.txt明确标记失败且禁止拼接。尚未证明这些失败版本有完整164副本；不能拿已归档成功v3替代失败v1/v2的逐文件备份。建议保留代码/日志/失败凭据并核实是否仍有调试价值，再归档独有内容或作为明确可重建失败产物单独决策，不计入79.2 GiB。
旧环境值得后续精简：env/c16-awq-v6 5.47 GiB、c16-qwen3-v14 5.17 GiB、c16-qwen3-30b-hf451-gpu 5.17 GiB（atime上界10月1日）；merged_gate_up_native_v1/env 7.41 GiB（10月1日）；awma/r19_fp8_readiness 10.82 GiB（10月2日）、r17_graph_search 7.76 GiB（10月2日），其中包含环境、缓存、原始数据，须拆分，不能整体当缓存删除。尚未证实164完整备份。
AWMA r26检查点24.48 GiB，r27系列含多份约2.45/4.91 GiB检查点、r27r3原始输出5.87 GiB，虽mtime较老，仍未证明164完整归档；先保留并列入后续独有资产归档。
A26GR1约40.77 GiB、nequip约10.92 GiB、A61约9.86 GiB，未获得逐文件164恢复证明，暂缓。
rtx4080 suite及其工具链、NAS路径、sc_derive控制目录存在运行中进程，保留。ImageLab ComfyUI、gateway、ollama正在运行，H3 bf16编码器今天有读取迹象；不能因同时存在量化版就删除bf16版。
时间判断局限：ext4使用relatime；atime是文件系统线索，审计/校验也会更新，mtime更不能代表最近使用。本轮尽量以扫描前stat时间与当前进程交叉判断，没有应用级完整访问历史。

ImageLab归档结论与下一步计划
164现有专用归档 /home/shared/<OWNER>/image-lab-archive/2026-10-27，仅RealVisXL 1个文件、Flux2 3个文件，合计18.058 GiB，历史收据为源/目标SHA256一致。对应源文件昨天已经移除，不能再次计入109清理收益。本次验证目标文件仍在且大小对应，未重新做18 GiB全量哈希；历史收据未做copy-back恢复测试。
当前109剩余模型约167.57 GiB，在检查到的ImageLab归档和研究模型资产库中没有找到对应完整、可验证归档。因此“大多数尚未在164归档”的判断成立；已有约18.1 GiB，待补约167.6 GiB（占两者字节总和约90.3%）。没有对164上所有其他人的目录作全盘查重，此结论针对已发现的本人归档体系。
优先级：H3 129.43 GiB；Flux3 16.53；LTX 8.96；提示词Ollama 6.13；修复3.75；TTS 2.33；inpaint 0.38；水印OCR 0.06。H3占待归档量约77.2%，近期仍使用，应先补副本但继续保留本地。
建议目的地：/home/shared/<OWNER>/image-lab-archive/2026-10-28-full（仅提议，未创建）。通过109->174->164单路断点复制，初始20~30MiB/s并监控现有任务；109只剩54GiB，直接逐文件传输，不在109生成模型tar或额外完整副本。
归档包含权重、tokenizer/config、Ollama blobs+manifests、LoRA/VAE、模型来源和revision、现有验证凭据，并补extra_model_paths.yaml、工作流、ComfyUI/custom-node版本和依赖锁定，避免仅保存裸权重。运行缓存、日志、密钥与用户图片视频不混入本模型归档。
源文件清单->确认文件已完成下载且无写入->逐文件源SHA256与稳定性检查->incoming暂存区断点传输->164完整读回SHA256->文件集/总量/分片/引用闭合检查->有限恢复读取测试->正式目录和总收据。Ollama应包含所有manifest引用的blob，TTS应包含tokenizer与配置；相同大小不同精度的模型不能互相替代。可能重复的VAE只在SHA256一致后复用旧归档。
本轮已保存原始清单、逐文件交叉表和计划；下一步先核验并释放老研究副本，再补ImageLab完整归档，ImageLab当前在线模型保留。
