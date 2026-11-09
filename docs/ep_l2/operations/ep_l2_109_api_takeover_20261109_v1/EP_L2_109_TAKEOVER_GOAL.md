# EP_L2_NODE109_READONLY_TAKEOVER_V1

执行对象：新本机API Codex会话 `109-EP-L2`。

本任务在用户将其转交给该会话后生效。它授权109侧接管、必要只读现场调查与小型文档交付。它不授权GPU/native benchmark/NVBit/NCU采集、模拟器实验、旧queue续跑、重试、清理、迁移或改变共享调度。

## 1. 你接手什么

你是EP-L2在109侧的固定接入窗口，负责保留和维护历史采集/工具/资产知识，按以后明确任务提供109侧工作。**EP-L2 Main仍是174-new唯一科学调度、预算、验收和科研集成owner；你不是第二个Main。**

科学审查由用户所在ChatGPT窗口承担，明确指令由用户转交，结果由用户带回。两端聊天不会自动同步。不要假设已收到另一个Codex窗口的全部历史，也不要用未发布聊天作为当前运行证据。

用户已确认把当前Base128＋optional CLEAN128五点执行指令给入Main。当前范围是同A Source5的GEMM EXT0/1/2及Stencil EXT0/2，WV_ZERO_RO、G32×8、850MHz/L100、完整283项。Main的登记/实际运行/结果等待其正常回执；本轮不查询或干预活动raw，不发第二份Goal，不重建dispatcher，不为本轮接管给五点增加前置条件。

研究主线Performance-First，主攻有成本的Victim/Payload资源效率。GEMM的0→1是结构代价、1→2是同硬件保留增量、0→2是整体净效果；Stencil仅看0→2净效果。RO为辅助，论文暂停。109的SM89资产不是这些已冻结输入的自动替身。

## 2. 先读固定资料

完整阅读本包：

1. `README.md`：调查结论、工具谱系、历史失败、时间状态与路径。
2. 本任务全文。
3. `EVIDENCE_INDEX.json`：固定commit/path/blob与已读取文本身份。
4. `ASSET_AND_ROLE_LEDGER.json`：资产类别、owner路由、已知与待核项。

按证据索引读必要原件：E01完整交接的§1–3、§13–14；E02接管回执；E04/E05试点与兼容性追加纠正；E06批量链；E08原生准备最终关闭；E09/E10普通producer和C8边界；E15最终Ada9关闭；E16带时间戳的资产快照；E17 Stencil最终关闭；E18/E19/E22存储范围。专项细节按你的现场发现再读E11–E14/E21，无需重做其资格。

旧README顶部若是准备、未运行或7/8，后续实际终态优先。这里7/8到8/8是历史174-new工程consumer campaign的消费账本，不是109 GPU采集次数或当前EP科学预算。E16的10月26 RUNNING和11月4存储ACTIVE_PROTECTED同样只是历史。用户本轮给入Main执行的确认覆盖其更早待授权状态，但不是五点同时运行的证据。

## 3. 工作区和持久上下文

建议新会话工作区：`D:/Codex/Token-API/workspaces/EP-L2/109-EP-L2`。这是建议新建的子工作区，不宣称它已经存在。若用户已把你放在另一个明确目录，保持该目录并回报实际绝对路径，不迁移Main工作区。

在你的实际工作区维护 `CONTEXT.md`；小型交付放 `deliveries/EP_L2_NODE109_READONLY_TAKEOVER_V1/`。CONTEXT必须记录当前角色、Main路由、固定资料、历史/现场状态的日期差异、资产路径、资格边界、关键负例和未决项。每次新交付同步更新结果与固定来源。

Main主项目常用入口是 `D:/Codex/Token-API/workspaces/EP-L2/CONTEXT.md`。本轮不要与Main并发改写同一文件；交付一个 `MAIN_CONTEXT_ADDENDUM.md`，让用户或Main按正常交接导入109路由与最终回执。你自己的CONTEXT立即维护，不等待另一端聊天同步。

ChatGPT不能访问D盘。远端报告应写明你实际维护的入口与内容摘要；不能只给一个D盘链接代替可审阅交付。

## 4. 首轮动作：一次只读接管对齐

### A. 确认连接与当前owner

复用本机已经配置、可合法访问109的SSH别名/认证；先确认实际hostname、账户、boot identity、时间和GPU UUID/driver，日期报告用Asia/Shanghai。只读 `nvidia-smi` 查询不算GPU采集，但不执行任何CUDA程序、warmup或性能测试。

对本包明确109根及相关控制进程做一次必要观察：PID、starttime、cmdline中的非敏感身份、cwd、owner、任务control/receipt。必要时补一轮定向核查以解开具体矛盾，不建立循环watcher，不持续轮询。

检查已有GPU lock/lease的路径与owner证据，**不获取、重建、截断或释放锁**；不修改心跳、STOP、服务、资源承诺、Native registry或dispatcher。ComfyUI、AI-ARCH、AWMA、DTC和其他合法owner不因你的新窗口而改变。

若发现仍在运行的共享RTX工作，先记录真实身份、所属授权/owner和目前已发布状态。保留其运行，不接管控制，不发送信号；这不阻止你完成其余只读资料整理。历史PID与当前同号PID必须分开，不能用旧数值认领进程。

### B. 有限路径盘点

优先顺序：

1. `/data/c16/rtx4080_suite_fill_20261024_v1` 的control、已关闭receipt和manifest；其 `nas_rtx4080` 的真实现有挂载来源。
2. `/data/c16/rtx4080_asset_pilot_20261024_v1`。
3. `/data/c16/ada_trace_semantics_20261024_v1` 和 `/data/c16/ada_trace_extensions_v8_20261024_v1`，冻结工具、小型契约、最终校验与归档引用。
4. `/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1` 的 `manifests/`、`native_control/` 和最终关闭证据。
5. 由上述小证据明确指向的109 worktree、私有工具和true164对象；更早DTC SpMV仅登记共享来源。

用定向文件列表与文本搜索查 `STATUS/RECEIPT/COMPLETE/CLOSEOUT/COMMIT/MANIFEST/REDIRECT/CURRENT` 等小记录，优先 `rg`，限定control/文档/索引目录。不要递归遍历整个NAS、模型/raw树，不解压所有trace，不对大资产做fresh全SHA，不重跑全部CPU/profile/恢复资格。

若发现匹配Git仓库，读当前HEAD、branch、status和相关文件历史；旧工作树不reset、不checkout改写、不清理。需要文档checkout时创建你自己的隔离工作区。Git default branch搜索不到文件不能当作文件不存在，固定commit优先。

路径状态使用明确分类：PRESENT、ARCHIVED_WITH_RECEIPT、REDIRECTED、MISSING_AT_OBSERVED_PATH、ACCESS_DENIED、NOT_CHECKED。区分“原热目录不在”与“canonical资产丢失”；不得为凑接管完整而自动恢复、重新下载或重采。

### C. 核对最后一个可证明状态

重点解开：10月26 transpose后处理和exact36有限批次是否自然完成、停止或有失败；当前是否只剩SSHFS/reader而非GPU producer；是否有晚于该快照的closeout。读取已封闭控制文件，不读取活动raw正文。

队列中的pending、旧余额、历史批量授权、工具资格和本任务均不能授予你续跑。查不到尾部回执就写精确UNKNOWN及最后证据，不把旧running改为closed，也不为了“收尾”重启publisher。

对能通过现有挂载只读访问的true164目录，核mount source/remote身份，再读取小COMMIT、MANIFEST、immutable catalog/receipt。不能只按 `/mnt164` 名字认定真实后端。不建立新挂载，不复制大包，不运行公共CLI的 `verify --all` 或 `restore`。优先读取已存在的验收回执。

174-new仍由Main负责；本轮不在174-new运行Main的preflight、扫描其模型或操作资产控制器。109视角无法确认的接收端事项写入给Main的待补问题，继续完成可访问范围，不让它阻塞五点。

### D. 分类并保留科学边界

逐资产最少记录：

- 任务/asset ID，原producer owner与EP关联类型；观察时间和证据。
- source/input/binary/tool/map/GPU的已有身份引用；原生attempt/采集attempt与失败历史。
- 原生exit、数值oracle、实际输入字节、全记录producer、特定consumer、hardware timing分别是什么状态。
- full与derived父子关系、trim规则与原SHA；派生不等于旧crop，不用于当前五点替换。
- 109现存源/工具、true164 canonical对象、174接收/恢复回执、Source KEEP和任何后续合法迁移记录。
- 当前进程/owner是否已明确；缺失证据与下一责任方。

只对本轮读到的小文件按需计算SHA用于回执。继承的大资产哈希标 `historical_receipt_reused`，不宣称fresh验证；权限不足/没有检查的字段写UNKNOWN，不能以exit0、已传完或文件名推断PASS。

E17 Stencil已闭合的CPU恢复链直接继承。早期DTC SpMV和其他项目工具复用仅作依赖映射，不把DTC/C16/AWMA的GPU任务、模型和预算移入EP。C16 bounded D1–D3只有找到精确EP消费者绑定后才列EP共享依赖，不接管其原项目。

## 5. 允许动作与本轮终点

允许：读取固定Git资料；109必要现场只读；读取已有可达挂载的小型证据；在自己的工作区写CONTEXT/调查脚本/报告；在本包独立文档分支的新增交付目录发布小型证据索引与接管回执。可以修正自己新报告的错误。对共享源、producer和已经封闭的原始收据保持原字节。

本轮不得启动GPU/native程序/NVBit/NCU/模拟器；不登记或消费科学预算；不重试、退款或挪用旧余额；不建第二dispatcher；不停止/重启任何旧进程；不改Main五点、科学Source/ELF/配置/输入；不部署新producer、更新CUDA/driver、重建工具环境；不新采Trace、迁移、降温或删除源。历史清理白名单不继承为本轮权限。

旧161专项项及任何未闭profile只记录，不在本任务补齐。发现缺口给出已有证据、影响和最小后续动作建议；除非用户另有明确指令，本轮止于接管回报。

## 6. 交付要求

在本包下新增独立 `takeover_receipt_v1/` 子目录，至少交付：

1. `TAKEOVER_RECEIPT.md`：实际连接/时间、Main与109路由、现场状态、已复用资格、完整/部分接管判定、未决项。
2. `CURRENT_STATE.json`：逐项证据时点、当前观察与未知；真实本轮动作计数（预期GPU0、SIM0、科学登记0、消费0、删除0）。只填实际发生的值。
3. `ASSET_INDEX.json`：主要目录与asset/对象引用；区分历史hash、当前小文件核验、producer/consumer/timing资格。
4. `OPEN_ITEMS.md`：具体待核字段/来源、影响、责任方；无未决项也明示，不发新的科学Goal。
5. `MAIN_CONTEXT_ADDENDUM.md`：可由用户转交Main的简洁109路由、固定交付链接和重要未决项。

同步更新本机实际 `CONTEXT.md`：结果、固定Git来源、当前角色、关键反例、未决项与下一步授权边界。不要声称Main的CONTEXT也已同步，除非确有其更新回执。

仓库 `swayhrl/accel-sim-framework`；准备包文档分支 `hrl/ep-l2-109-api-takeover-20261109-v1`。先fetch当前HEAD，在你自己的文档工作树只增加上述交付；如分支已被他人推进，读差异后正常整合或使用独立receipt分支，禁止force/reset覆盖。不要改Main的科研执行分支。只上传小报告和必要脱敏metadata，不上传大trace、模型、密钥、完整私有环境或无关进程参数。

发布后回读远端分支HEAD、固定commit与交付文件，核文件集合/内容/身份。聊天回报给用户：固定commit、接管判定、109当前有没有本项目活动工作（带观察时点）、共享owner边界、主要资产可定位性、是否有需单独决策的事项。**报告发布后结束本轮，不开启后台轮询。**

接管完成不要求所有旧unsupported/pending都消失。若109无法连接或owner边界仍冲突，完成所有可做的Git/上下文整理，明确PARTIAL及唯一具体阻塞；不伪称现场已核，不用重新采集来补证据。
