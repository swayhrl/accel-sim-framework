# 109-DTC-L1首轮任务：历史资产接手、现场只读盘点与上下文固化

## 0. 授权、角色与停止点

你是用户新开的本机API Codex窗口 **109-DTC-L1**，负责DTC-L1在109的历史native/profile/capture产物、相关工具环境、归档来源和后续明确授权的109专属工作。**本次仅执行历史接手：固定资料阅读、有范围的109只读发现、独立CONTEXT维护和小型GitHub报告回传。** 不把这个窗口建成第二个Main或长期dispatcher。

唯一 **DTC-L1 Main** 是本机API会话“DTC-L1交接-1”；科学窗口负责科学审查与下一步合同，用户负责转交新授权。旧账户Main仅作历史查询。不同会话没有自动共享聊天记忆，以固定GitHub和本窗口实际观察为准。

用户已将科学接受包 `64cd088b2de575157846f07a21ce09748220f7e2` 的Main接收任务交给Main。本任务不重复接收、重发旧Goal、重启owner、修改registry或查询Main实时进度。完成本轮交付后 **STOP_PENDING_EXPLICIT_TASK**；所有后续native/profile/capture、编译/fixture、decoder实现、模拟和HOLD释放均需另有明确任务。

## 1. 新窗口必需科学背景与假设

### 1.1 主线已有何种结论

DTC-L1研究涉及GPU一级缓存路径中的逻辑映射、物理保留、PIB/Ref与事务所有权/生命周期等结构问题。IO/OO来源归赵皓宇博士论文第4章，英文LaTeX v0.23仍是冻结唯一母稿。本次不编辑论文或源码。

当前Controlled Oracle已完成固定32输入×OFF/M/L2/L1=128格，D全128独审PASS、M完整32机会分析冻结、Main连接/复算/发布/总签署完成，科学窗口已接受固定trace范围的收尾。结论限定为SM70/V100-derived 64SM固定trace的受控反事实；不是可实现结构的等量收益、等面积收益或严格数学上界。历史DH-P0不能替代同Oracle build实际OFF，L2的11个精确零和2个回退继续保留。原生完整应用数值、capture绑定、有限机制因果、coherence、PPA与扩展输入证据仍各自独立。

这意味着109新窗口无需重验Oracle128格，不应把109 RTX4080上的native结果合入CORE32 GM。你接手的109材料是具体独立谱系，不能按同名应用替换当前固定trace。

### 1.2 109已有何种成果

2026-10-16的producer在109完成15个native条件：12个诊断＋SpMV small1138_bus主输入＋PyTorch LayerNorm主输入与单一native敏感性输入；完成native数值/计时、NCU和新增算子的nsys审查，以及4个SpMV和6个LayerNorm主输入trace kernel。15是条件数，不是15个程序。

SpMV生产格式PASS之后，174 consumer因不支持cubin89拒绝准入；后续109 CPU审查揭示宽寄存器、常量、uniform/predicate等依赖缺口，结论为 `NO_GO_FOR_DROP_IN_SM89_ADMISSION / HOLD`。LayerNorm实际cubin86，tracer跳过CALL.REL.NOINC，仍NOT_ADMITTED。native正确性、完整grid、exit0、parser可解析分别是不同证据，不能互相替代。

Native指定285成员包有历史164挂载目的端SHA验收；该回执不等于本轮重新识别物理后端或验证今日副本。SM89 CPU小归档只证实109本地。11月4日native整个工作目录归档映射仍TARGET_UNVERIFIED。**本次工作假设只有“历史路径和回执值得作为发现入口”，没有“今天文件一定存在/未变/已全部归档”的假设。**

## 2. 固定输入与阅读范围

以用户转交的本包完整commit为 `TAKEOVER_PACKAGE_COMMIT`，不能以分支HEAD替代。首先核对本目录MANIFEST，然后完整读README、HISTORY_AND_EVIDENCE、本文、CONTEXT_SEED、ASSET_LEADS。

| 用途 | 固定提交和目录 | 首轮必须核对的内容 |
|---|---|---|
| 最新Main科学接受/路由 | `64cd088b2de575157846f07a21ce09748220f7e2`；`docs/dtc_l1/review_packs/CORE32_ORACLE_SCIENTIFIC_ACCEPTANCE_20261109_V1/` | README、CONTEXT_INCREMENT。只作为状态依据；不执行其中给Main的接收指令。 |
| 109 native producer | `890fb0be7e681a60419c49ca0a7aa85731d8c164`；`docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/` | README、TRACE_DELIVERY_AND_GAPS、DURABLE_STORE_RECEIPT、RAW_PAYLOAD_INDEX；按具体资产再读身份/小型回执。 |
| 174对109消费 | `b9ff89f00ea8ff889e4189136501c714c5d7e345`；`docs/dtc_l1/iscas2027/service_closure_174_v1/PRODUCER109_CONSUMER_REVIEW_V1.md` | SpMV NOT_ADMITTED、exit0失败、285成员包装/回执边界。 |
| 109 SM89 CPU收尾 | `d58e75ce32845a281692f19aeb4057b4c9822a3f`；`docs/dtc_l1/review_packs/DTC_SM89_ADMISSION_FEASIBILITY_V1/` | README、NEXT_DECISION、CPU_ARCHIVE_RECEIPT、RAW_LOG_INDEX；不执行run_cpu.sh。 |
| 整树归档缺口 | `b290790401e248a19427c26c0dde51e6b55ded67`；`docs/storage/node109/20261104/` | ASSET_INVENTORY与SOURCE_TO_TRUE164_ARCHIVE_MATRIX中精确DTC路径行；本包evidence已附逐字段提取。只消费DTC行。 |

本包SOURCE_INDEX给出上述固定链接及更多可按需展开的资料；不要求全读58份文件。现代容量提案 `d6f0a3300972d7b1d9638b8f4b1338c25912a1b3`、早期M5 `a9cdb3328a346cbc9a76b7ffadae3725b4209ab5` 仅在需要确认归属时读；历史GOAL_109、RUNNING、等待consumer、DTC48/AE旧状态不是当前授权。

完整工程交接 `3f0036f2868e20a8d9a4b6244c7c74d940954188` 和原运行结果 `7ffcca7f908a21f45ba1a6ebb3b335ff962f97df` 是上游背景，本轮无需重新消费全量D/M或raw。若D盘不可访问，以真实可读取的固定GitHub文件为准，不声明读过不可访问的本机文件。

## 3. 项目目录与单写者规则

建议建立独立本机项目根：

`D:/Codex/Token-API/workspaces/109-DTC-L1/`

它是建议新建路径，未被本包验证存在。若本机实际workspace根不同，在一个独占目录完成并记录实际绝对路径。此窗口单写自己的 `CONTEXT.md` 和 `deliveries/DTC_109_READONLY_INTAKE_20261109_V1/`。继承CONTEXT_SEED的事实与来源，加入本轮发现、结果和未决项；后续每次任务都维护这个文件。

所有写操作使用该独占项目的绝对路径或显式工作目录。先确认实际cwd；一次shell中的cd不代表其他工具调用也改变目录。独占目录定位完成前，不创建相对路径的CONTEXT或交付文件。

**不读写Main正在接收的 `D:/Codex/Token-API/workspaces/DTC-L1/CONTEXT.md`，也不更新Main CURRENT_STATE、LATEST_REPORT、registry、预算或正式结果文件。** 给Main的增量通过 `MAIN_INTAKE_NOTE.md` 提供，待Main当前任务结束后由它自行合并。

若需要Git工作目录，使用全新的独立docs checkout/worktree和分支，不在两处历史109 worktree或Main活动worktree中checkout/fetch/reset/stash/clean。不得合并历史producer、CPU或modern分支的全部源码。使用本包固定commit作发布基线，只增加下面的接收目录。

## 4. 首轮目标与允许动作

### A. 完成资料接收

核对本小包成员、bytes/SHA256；记录实际消费的固定commit/path及来源。复用已验收报告和原SHA回执，不为接手重做native正确性、NCU、trace语义、完整parser审查或归档成员hash。

### B. 通过既有109入口做一次只读发现

允许使用用户本机已配置且明确指向109的SSH/连接入口。先读回hostname、user、cwd和时间确认观察对象；不要猜IP、扫描网络、改SSH配置或输出密钥/令牌。入口不存在或连接不可用时，完成GitHub接收与可做的本机工作，列出准确缺项后回传，不借道操作174-new。

首轮主体范围仅为以下专属路径；全部是历史入口，当前存在性需据实际填写：

1. `/home/huangrulin/workspace/worktrees/accel-sim-dtc-native-coverage-109-v1`
2. `/data/c16/dtc_native_coverage_109_v1`
3. `/home/huangrulin/workspace/worktrees/accel-sim-dtc-sm89-admission-109-v1`
4. `/data/c16/dtc_sm89_admission_feasibility_109_v1`

可做的现场工作：

- 用stat/readlink/realpath等读取上述路径和ASSET_LEADS指定文件的metadata；对已存在挂载读取相关mount来源/namespace，避免alias重复计副本。无需运行GPU状态或CUDA程序来确认历史设备身份。
- 对两处历史worktree读取HEAD、分支、remote名称/不含凭据的URL、dirty文件路径概况和DTC相关小型未提交报告。设置 `GIT_OPTIONAL_LOCKS=0` 或等价只读方式，不刷新index，不改工作树；不输出无关项目差异或凭据。
- 在两处DTC专属raw根内进行一次有界文件名/类型/大小/时间索引，优先现有seal、manifest、index、receipt、环境记录和失败日志。不要读二进制payload内容，不跟随symlink递归跨出专属根，不递归扫描整个/data、home、NAS或其他项目。
- 如果旧根不存在，可检查其直接父目录中的DTC命名入口，以及已读DTC回执明确指向的新路径。记录查找范围；没有精确线索就记未定位。不要以“接手所有历史”为由全盘搜索。
- 读取有明确DTC引用的共享依赖的小型metadata/版本回执：`/data/c16/env/c16-py310`、历史AWMA tracer文件、CUDA/disassembler/NCU的已记录路径。优先既有环境文件，不激活环境、不import torch、不调用工具做工作负载。共享依赖只记引用，不改归属。
- 只在明确需要区分两个小型文档/回执身份时做小文件SHA，并记录实际范围；旧archive、trace、GPU库、binary和285成员payload不在重hash范围。

上述操作可由少量本地分析脚本实现，但脚本只处理小型文档和文件metadata，写入独占交付目录。若确需在109落盘小型盘点输出，使用独立新报告目录并记录路径，不写历史root，不覆盖已有文件。

历史RUNNING、旧锁回执、preflight及旧进程记录本身不证明当前活动。如果本轮已有metadata确实提示某个子目录可能正在变化，保留观察、停止该子目录内容读取并记录未核；其他明确历史/关闭子目录及只读metadata盘点继续。不新增进程、锁检查或轮询，不碰活动raw，不停止/重启任何进程，不访问Main活动控制面或request。

### C. 解决最有价值的归档成员映射

将固定native RAW_PAYLOAD_INDEX的285成员、CPU RAW_LOG_INDEX的45成员，与当前专属root的**路径/大小metadata**作映射。分开记录：索引成员可见、指定旧路径缺失、大小不符但原因未知、目录额外文件、不可访问/未检查。只有metadata一致时只能称METADATA_MATCH，不能称当前payload SHA PASS。

原native成员索引和archive内PAYLOAD_FILES.json是同一个索引角色，后者不是额外的第286个科学payload。保留历史consumer首次包装误判及更正回执；不要为了对齐数量修改索引。

对当前额外文件只做分类与路径记录：失败尝试、额外日志、生成物、归档文件自身或未知。没有可靠证据时不判可删除/可再生，也不计算“已安全归档的整树比例”。如有后续小型归档回执，可核其来源/成员范围；没有回执则继续TARGET_UNVERIFIED。

Native历史164路径位于174-new/root挂载namespace。若109已有可读、明确映射到同一后端的挂载，可以查看指定归档路径及小型receipt的metadata；若只能通过历史109→hrl174new→164路线查看，记 `REFERENCED_NOT_RECHECKED`，本轮不自动跨跳174-new。CPU归档只证本地；是否另有持久化副本按发现填写，不能按native路径类推。

### D. 整理GitHub未包含的必要DTC历史

允许从上述专属根与其精确DTC文档引用中补充未提交报告、原命令/构建回执、工作树状态和工具路径。把新增事实绑定当前观察时间、节点/namespace、原文件路径与小文件SHA或引用；把解释与证据分开。涉及AWMA/C16/AI-ARCH/EP/Image-Lab材料，只登记依赖和原owner，不接管其任务、环境或清理权限。

原12在10月109不可用只作为旧快照。若现场有后来materialize的同名材料，需保留其独立身份和来源，不按名字认领为原固定输入。本轮不要求搜齐12根或重验629成员。

## 5. 本轮禁止启动/修改的具体工作

- 新native计时、GPU profiler/NCU/nsys、SASS capture、CUDA样例、deviceQuery、torch工作负载、任何科学模拟或canary，均为0。
- 不获取/试获取GPU协作锁；即使 `flock -n`“探测一下”，成功时也会获取锁，不能作为只读盘点。旧GPU_LOCK_RECEIPT不证明当前空闲。
- 不运行历史campaign.py、capture.py、build.sh、run_cpu.sh、asset ensure或环境激活/安装脚本；不编译、装包、升级driver/tracer/decoder、下载新数据/模型。
- 不改SM89 header/dispatcher、不补CALL语义、不应用candidate_fail_closed.patch，不修改平台容量、Tag/physical/PIB/Ref或kernel/input清单。
- 不清理、移动、压缩、恢复、解压或批量传输科学资产；不修复/重挂载存储。SOURCE_KEEP、失败和负例均保留，metadata盘点不授予存储回收资格。
- 不重跑Oracle128格，不使用旧OFF/DH-P0填新配对，不复用旧UUID/request/预算，不启动10输入/20格草案，不解除任何HOLD。

如果仅靠上述允许动作不能解决某项，就记录明确的证据缺口和最小未来动作建议，交付后STOP；不把建议当成执行许可。

## 6. 状态和交付要求

每项资产至少分开以下字段，不用一个PASS覆盖全部：

| 字段 | 内容 |
|---|---|
| identity/ownership | asset_id、DTC专属/共享依赖/外部producer副本/其他项目/未定；workload/shape/设备SM/实际cubin（已知时） |
| historical_evidence | 固定commit、原路径、原观察日期、原bytes/SHA与证据范围 |
| current_observation | 观察UTC、节点/namespace、实际路径/alias、存在性、type/size、metadata或小文件hash范围 |
| integrity_scope | INHERITED_SHA_RECEIPT、CURRENT_SMALL_FILE_SHA_MATCH、PAYLOAD_NOT_REHASHED等；不伪称重验 |
| scientific_admission | HISTORICAL_NATIVE_VALID、SIM_NOT_ADMITTED、NATIVE_SENSITIVITY_ONLY、MODERN_DTC_HOLD等 |
| unresolved | 具体缺件、影响、最小后续建议及需要何种新授权 |

存在性使用 `PRESENT_METADATA_ONLY`、`MISSING_AT_OBSERVED_PATH`、`INACCESSIBLE_PERMISSION`、`UNKNOWN_NOT_INSPECTED`、`REFERENCED_NOT_RECHECKED` 等明确值。未定位不等于丢失，UNKNOWN不填0。

本机交付目录应包含：

1. `READONLY_INTAKE_REPORT.md`：职责确认、完成范围、核心发现、归档范围差异、实际查找边界、未决项、STOP。
2. `ASSET_DISCOVERY_INDEX.json`：逐项历史来源/今日观察/完整性/准入分离的索引；可附一个只含DTC路径的metadata成员映射表。
3. `SOURCE_INDEX.json`：实际读取的固定GitHub文件及本轮小型现场来源；不要把只看到文件名写成已读内容。
4. `MAIN_INTAKE_NOTE.md`：给Main的短增量，含本轮交接基线commit、报告相对路径、109实际CONTEXT路径、可复用资产、仍待核的最小项；明确Main当前任务不需被中断，不自行向其他窗口派发。该文件不自引用其所属最终commit；发布后的最终SHA由用户回复、本机CONTEXT和独立回读回执提供。
5. `ACCEPTANCE_RECEIPT.json`：实际接收结果、固定来源、动作计数和STOP，不能预填未发生的成功。
6. `MANIFEST.json`：交付小包的实际成员、bytes、SHA256，不包含自身；远端回读收据单独保留，避免自引用。
7. 自己项目的 `CONTEXT.md`：写入本轮结果、固定来源、今日观察日期、执行/科学边界和未决项。远端可提供不含本机敏感配置的 `CONTEXT_UPDATE.md`，本机CONTEXT保持窗口单写。

至少报告下列动作计数：

```json
{
  "window": "109-DTC-L1",
  "main_owner": "DTC-L1 Main / DTC-L1交接-1",
  "main_context_written": false,
  "new_scientific_starts": 0,
  "new_native_timing": 0,
  "new_gpu_profiles": 0,
  "new_captures": 0,
  "new_simulator_runs": 0,
  "new_requests": 0,
  "scientific_budget_consumed": 0,
  "gpu_locks_acquired": 0,
  "historical_source_mutations": 0,
  "historical_payloads_rehashed": 0,
  "next_action": "STOP_PENDING_EXPLICIT_TASK"
}
```

这段是必须如实确认的合同字段；若误做了不同动作，保留事实，不通过填0掩盖。

## 7. GitHub回传与最终回复

本轮授权把上述小型文档/索引提交到 `swayhrl/accel-sim-framework` 的**独立新文档分支**，建议 `hrl/dtc-l1-node109-asset-intake-20261109-v1`。若分支已存在且来源/owner不明，另取唯一名称，不覆盖。基线为用户转交的本包完整commit。

唯一新增远端目录：

`docs/dtc_l1/handoffs/DTC_109_READONLY_INTAKE_20261109_V1/`

若同名目录已有其他交付，使用独立带版本后缀的目录并记录；不修改本调查包、历史producer/SM89封包、b9/64cd接受包、Main工作分支或仓库全局状态。只提交显式列出的新文件，不用git add .或-A，不force push、reset、clean或merge。执行git diff --check，核对diff仅落在独占新增目录。raw、trace、binary、library、数据集和凭据不得进Git。

发布后按固定新commit回读小包，检查bytes/SHA256和文件集合；记录实际回读结果。本机CONTEXT补上发布commit和未决项。若GitHub发布能力受阻，不扩大权限或改目标仓库：完成本机交付、说明精确阻塞，不能声称已发布。

最终回复给用户：固定commit、报告与Main增量的链接、实际CONTEXT位置、两处root/两处worktree的定位结果、285/45成员metadata映射状态、未解决的少量项目以及全部零启动计数。然后STOP。接手是否完整以资料责任、资产位置和未知项都明确为准，不以重新执行科学任务为准。
