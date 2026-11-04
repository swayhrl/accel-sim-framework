# Historical Node109 report — public review copy

- Source ID: `model_archive_audit_20261028`
- Original SHA256: `4815ac164c7aade29cd3c5eea3660a14a3a0a5b89d7e63987e20f10dbaff07de`
- Status: Historical snapshot, not the 2026-11-04 current-state result.
- Disclosure: Private host/account details were replaced; see `HISTORICAL_REPORT_PROVENANCE.json`. The local original remains unchanged.

---

非 ImageLab 模型归档只读审计（2026-10-28）

结论
OLMoE、Qwen3-30B-A3B、Llama-3.2-1B 三组在真正 164 的归档目录都存在，109 当前全部 44 个文件逐相对路径、大小对应；共 77,407,564,851 bytes（72.091413 GiB）。配置、tokenizer、index 等 24 个小文件的本次两端 SHA256 相同；20 个权重文件的 safetensors 头部相同且文件长度结构检查通过；两个分片索引所引用的 16/3 个分片全部存在。
这些结果证明“可见文件齐全、当前小文件一致、权重头部和长度一致”，不证明本次已重新读完整权重做 SHA，也不证明已经完成复制回原机/推理恢复。
Qwen3与OLMoE适合在门槛补齐后清理109的本地冷副本，属于主候选；Llama为可选候选。主候选共38文件、74,926,781,757逻辑bytes，预计数据块回收74,926,952,448 bytes；连同可选Llama合计预计回收 77,407,760,384 bytes。本轮没有批准或执行直接删除，不能仅凭旧 PASS 立即删：先补有限全量校验、恢复抽检及临近清理时的使用检查。所有源文件 nlink=1，已按 (device,inode) 去重，没有把另一硬链接重复计入。此回收值不含目录元数据，实际 df 差额还受并行任务和未关闭的已删除文件影响。
没有执行删除、迁移、上传模型、恢复复制、停止服务、启动推理或修改项目代码；未读取私钥/API 密钥。

一、真实位置与当前核验
109: <OWNER>@<NODE109_PRIVATE_IP>，UID <NODE109_UID>；源文件系统 /dev/nvme0n1p2 ext4。
109 的 <BRIDGE_SSH_ALIAS> 连接 root@<ARCHIVE_BRIDGE_PRIVATE_IP>:<BRIDGE_PORT>；在 174 上 findmnt 证明 /root/share/mnt164 是 <ARCHIVE_SERVICE_ACCOUNT>@<TRUE164_PRIVATE_IP>:/home/shared 的 fuse.sshfs。
因此下述 /root/share/mnt164/<OWNER> 路径对应 164 原生 /home/shared/<OWNER>，确非 174 本地副本。
源快照 2026-10-28T06:16:37Z；归档快照 2026-10-28T06:16:38Z。完整逐文件恢复映射在 restore_file_manifest.csv，包含 inode、nlink、大小、mtime、当前小文件 SHA 和历史大文件 SHA。

源：/data/c16/models/qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
164：/home/shared/<OWNER>/c16_ai_workload/assets/models/qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
文件 26；逻辑 61,084,187,391 bytes；去重数据块 61,084,311,552 bytes。小文件 SHA 本次 10 个；权重头部 16 个；缺文件/大小差异/小SHA差异/头部差异均 0。归档额外证据文件：MODEL_ARCHIVE_RECEIPT.json。

源：/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e
164：/home/shared/<OWNER>/c16_ai_workload/assets/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e
文件 12；逻辑 13,842,594,366 bytes；去重数据块 13,842,640,896 bytes。小文件 SHA 本次 9 个；权重头部 3 个；缺文件/大小差异/小SHA差异/头部差异均 0。归档额外证据文件：无。

源：/data/c16/models/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08
164：/home/shared/<OWNER>/c16_ai_workload/assets/models/llama-3.2-1b/4e20de362430cd3b72f300e6b0f18e50e7166e08
文件 6；逻辑 2,480,783,094 bytes；去重数据块 2,480,807,936 bytes。小文件 SHA 本次 5 个；权重头部 1 个；缺文件/大小差异/小SHA差异/头部差异均 0。归档额外证据文件：DESTINATION_INVENTORY.tsv, MODEL_ARCHIVE_RECEIPT.json, SOURCE_INVENTORY.tsv。

Qwen：16 分片完整；index 有 18,867 个 tensor 映射。OLMoE：3 分片完整，index 有 3,219 个 tensor 映射；12 文件中包含 MODEL_ASSET_RECEIPT.json，实际模型 payload 为 11 个。Llama 是单个 model.safetensors，没有分片 index 属正常布局。
这次读取每端的权重头部合计仅 2,745,456 bytes；未读取张量主体。头部相等不能排除中间数据位损坏。原始 atime 已在读前记录；这次头部读取可能改变 atime，后续不可再把新 atime 误认成业务使用。

二、历史 SHA 凭据的力度
Qwen：164 MODEL_ARCHIVE_RECEIPT.json 声明 EXACT_FILE_SET_SIZE_SHA256_PASS；payload_inventory_sha256=20b21f889daf61d7362d4e0042ff7f3b2517cc1f0a917d3e0667654ded8cb30a。新发现并读取 109 的 /data/c16/qwen3_30b/bringup/Q30_S0_RESUME_V1_20260916T044412Z/receipts/CANONICAL_SOURCE_INVENTORY.tsv，其原始字节 SHA 精确等于该值；同目录 LOCAL_FULL_INVENTORY_VERIFY.json 为 PASS，列出当前109源路径、26文件及逐文件历史SHA，16分片均有基线。它是一份历史验证记录，而非今天的权重重新读取。
OLMoE：MODEL_ASSET_RECEIPT.json 包含 11 个 payload 的逐文件 SHA，3 分片都在其中，revision/hub_resolved_revision/tokenizer_revision 一致。这是可用于重新校验的资产凭据；其字段本身不能替代今天源/目标重新全量读回，也没有把它当作新发生的双端校验回执。
Llama：归档 MODEL_ARCHIVE_RECEIPT 声明 EXACT_RELATIVE_PATH_SIZE_SHA256_PASS。SOURCE/DESTINATION_INVENTORY.tsv 本次读取一致；DESTINATION 的文件 SHA 符合 receipt 中 faf1ad814cd4a6f415925c6b7f812449f6f379db849e483bb27cdfe4284de2f0，内含 6 个 payload 的逐文件 SHA。旧回执 source_path 是 /root/share/c16_recovery_v3/...，并不是当前109，所以不能把旧 PASS 表述成今天109与164做过全量比较。
已整理 43 个 payload 历史 SHA 至 historical_sha_baseline.json；当前源第44个文件为 OLMoE receipt，已本次小文件两端哈希。所有可本次小读核验的历史 payload SHA 也都相符。更早10月19日的其他 Qwen2.5 六模型校验没有用于证明上述三组。

三、使用依赖：有历史引用，未看到可读范围内正在用
进程快照检查 472 个进程；cmdline 472 个可读，maps 349 个可读，fd目录 36 个可读，三组模型相关 cmdline/fd/maps 命中 0。123 个 maps 和436个fd目录因权限不可读；sudo -n 需要密码，未尝试交互提权。因此结论仅覆盖当前账号可读范围，不是全机绝对无使用证明。模型完全加载后关闭文件描述符、未来排队任务都不能仅靠 fd 空结果排除。
当时 nvidia-smi 只列出 ImageLab Python（354MiB）和 CUDA scan（400MiB）。系统/用户 running units、timers、当前账号 crontab 已检查；没有发现指向这三组模型的在跑服务，当前用户无crontab。已读取可达 systemd/cron 配置与用户 transient unit 文件，三组路径/名字匹配为0。当前用户其他在跑工作主要为 ImageLab 归档、streamcluster copy、CUDA capture；未停止或改动它们。
两轮有界文本扫描共读取约478MB小文本；首轮400MiB预算耗尽，另做针对服务/队列状态和仓库 configs/util/scripts/docs/ep_l2/operations 的补扫（58,591,436 bytes）。共3,383个文件含模型名字/本地路径类引用，绝大部分是历史脚本、结果或回执；没有与已识别活跃进程脚本对应的引用。完整位置/行号见 dependency_references.csv，未保存含凭据的整行文本。
明确仍依赖原本地路径的例子：
  /home/<OWNER>/workspace/accel-sim-framework/util/vm_tlb/c16/qwen3_30b/e3_q30_routing_diagnostic.py:10
  /data/c16/awma/moe_skew_20h_v1/skew_runs/run_0.5_601.py:6
  /data/c16/awma/ai_translation_native_atlas_capture_20260926/capture_M2/IDENTITY.json:5（OLMoE历史capture身份）
  /data/c16/awma/ai_translation_native_atlas_capture_20260926/capture_L2/IDENTITY.json:5（Llama历史capture身份）
这些引用不是“正在用”的证据，却说明以后直接重跑会因本地模型路径缺失而失败，需先恢复。未遍历所有二进制队列/调度数据库；扫描排除了环境、模型、trace、raw、logs、部分runtime/source目录及大文本，明确保留此边界。不能用mtime/atime旧来判闲置。

四、其他非ImageLab资产
stagea：/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1 -> /root/share/mnt164/<OWNER>/c16_ai_workload/assets/models/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1；13文件，6,183,467,318 bytes；完整同路径同大小、所有小SHA/权重头部相同。DOWNLOAD_RECEIPT含12个payload逐文件历史SHA。本次未全量重哈希。
stagea：/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct-awq/3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd -> /root/share/mnt164/<OWNER>/c16_ai_workload/assets/models/qwen2.5-3b-instruct-awq/3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd；11文件，2,698,209,551 bytes；完整同路径同大小、所有小SHA/权重头部相同。DOWNLOAD_RECEIPT含10个payload逐文件历史SHA。本次未全量重哈希。
stagea 两组共 8,881,676,869 bytes；不自动加入本次三组的清理白名单。
/data/c16/models 下 .incoming/.transfer 当前未发现权重载荷；保留隐藏目录及 .provenance 证据，不规划删除父目录。
对 /data/c16/models、stagea assets 和 AWMA 做元数据盘点，共9,103目录，无元数据扫描错误。AWMA共 249 个符合权重/张量/图索引后缀的文件，54,141,921,743 bytes（包括许多很小的实验输出，不应全称“模型权重”），nlink全部1。其中 22 个大于100MiB，主要包含r26/r27系列COMMON_POST_BOOTSTRAP和trajectory、numeric attribution B0_a/B0_b、Fast_dLLM、Qwen3_5_0_8B、r19 fastweight、VLA模型；另有派生张量和CAGRA图索引。
这些大文件在164 canonical模型池里未发现同名同大小候选；对 /<OWNER>/awma、c16_ai_workload/legacy/awma、c16_ai_workload/recovery/awma 三种直接映射的逐文件stat也均未命中。164的/<OWNER>/awma仅列出r21a_oeq_graph_readiness_109_v1。未扫描所有tar/archives/异名归档，因此只能说“尚未证明归档”，不能说164绝无副本，更不能说164已全部有。
AWMA checkpoint可能含实验独有状态，不能因存在同系列公开模型就删除。全部保留，后续单独按实验身份、文件清单、SHA、恢复依赖建立归档。详见 awma_full_weight_tensor_inventory.json、other_weight_candidates.csv、awma_nas_probe.json。
本盘点不是109全机所有缓存/所有实验目录的穷举，未检查qwen target_states等全部/data/c16目录的张量载荷；清理计划只覆盖明确三组revision目录。

五、有限的后续执行计划（仅规划）
1. 等主线程ImageLab全量读回结束后，再串行安排大读；NAS同一时间只用一个最多32MiB/s读者。这次不并发重读72GiB权重。
2. 按historical_sha_baseline.json，对43个payload同时要求109当前内容和真实164当前内容匹配历史SHA；OLMoE receipt另验当前小SHA。每端读前/读后stat须稳定，保存逐文件结果、时间与挂载身份，变化即不产生PASS。不再扩大为其他模型。归档侧总读约77.4GB，32MiB/s理论约38.5分钟；109侧再读约77.4GB，串行或限速协调，不影响已有任务。
3. 紧临清理前重查服务/任务/进程并解决不可读进程的使用证据边界。若发现运行/待执行任务直接引用某模型，则该目录延期；不能仅凭本次快照支持日后随时删。
4. 从真实164经174复制Llama完整6文件到109新建空的恢复测试目录（2.48GB），完整SHA比对、离线解析config/tokenizer、打开safetensors元数据；Qwen和OLMoE分别复制配置/tokenizer/index小文件，按清单验证分片闭包。不启动GPU推理，不改变消费者配置。该抽检不等于Qwen/OLMoE整模型已恢复推理。
5. 对照白名单再验证精确目录、inode/nlink=1/size/mtime：主候选Qwen+OLMoE为38文件；可选Llama另6文件，合计44文件。出现额外文件或身份变化先停该目录的清理；保留本地报告、manifest与164 receipt。后续被授权清理时只作用于选定的literal revision目录，不作用于/data/c16/models父目录、AWMA或stagea。stagea另批，AWMA暂保留。
6. 清理后记录df差额、未关闭的已删除文件并验证164归档仍可达。没有清理前提已补齐的逐文件新PASS就不把状态升级为可删。

再次使用的实际影响：本地原路径不存在时，现有local_files_only/绝对路径脚本需先从164复制回109，恢复完成前不能直接重跑。按restore_paths_<model>.txt和restore_file_manifest.csv，通过109的<BRIDGE_SSH_ALIAS>从174的真实164挂载只读拉取到新的本地staging目录，按历史SHA与新PASS校验后再放回原绝对路径；Llama目录大小写和“@revision”布局尤其要按manifest还原。不要改成直接在SSHFS上跑模型来省空间，这会改变I/O性能和故障依赖，当前报告未验证这种运行方式。
当时109可用56,699,777,024 bytes，小于Qwen完整61,084,187,391 bytes，也小于三组77,407,564,851 bytes，因此清理前不能无条件再放一份Qwen或三组完整副本；Llama恢复抽检可放得下。清理后再恢复三组将基本吃回回收空间。32MiB/s纯传输下Qwen约30.3分钟、OLMoE约6.9分钟、Llama约1.2分钟，另加校验与连接开销。

关键交付
ANALYSIS_zh.txt：本报告。
FOLLOWUP_EXECUTION_PLAN.json：可审阅但未执行的有限步骤、精确三目录白名单和恢复路由。
restore_file_manifest.csv / historical_sha_baseline.json / restore_paths_*.txt：逐文件恢复映射与完整历史SHA基线。
model_verification_summary.json / source_current.json / nas_current.json：本次核验原始证据。
dependencies_current.json / focused_references.json / dependency_references.csv：使用依赖快照与边界。
stagea_verification_summary.json / awma_full_weight_tensor_inventory.json / other_weight_candidates.csv：其他模型范围与保留依据。
SHA256SUMS_local.txt：本地交付文件摘要。目录内.py仅为此次只读采集/本地分析脚本，无自动删除或迁移程序。
