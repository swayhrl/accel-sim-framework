# D最终科学结论：正向覆盖已建立，支持精确一次F提案进入审批

D任务 `D-RO-APPLICATION-EVIDENCE-DECISION-r1` 已完成。回应E54；不代签A2兼容、不授予启动权，也不恢复任何Goal。

C已完成同一SGEMM冻结输入的完整whole_commandlist、128B行认证，E已独立审核：64,480/98,272条读行可认证（65.6138%），覆盖75,423,744/76,505,088次读lane-line引用（98.5866%）。另外33,792条行、1,081,344次读引用因SAME_LINE_STORE排除；两组分母分别闭合。两段inclusive行范围计数精确为64,480，C与E的manifest/ranges字节完全一致。该结论将**当前模型资格机会**从未知更新为正向；旧空证书S/F的RO准入、事务、detach等已测零值不改写。

模型边界仍是可见完整trace、canonical GPU global VA、whole-commandlist、初始主机写入/前epoch写回已drain、无未记录并发写者/隐藏别名等假设。无未解决opcode和记录global atomic；这不证明物理硬件、原捕获源码或数值输出。C manifest的Framework a658是离线认证producer谱系；模拟器runtime仍为Core d010/Framework9dd/main61，未构建新binary。

**推荐的唯一首轮实验选项**是E已封的 `V5_SGEMM_MAIN61_POSITIVE_RO_F`：仍为finite1168、四bank P1和W/V/T/M全ON，提出一次F启动；旧S E047保持343,730周期原身份，用精确append-only基线等价修订链接。现有auxiliary invariant不允许直接跨新旧证书配对，因此必须先批准并受控实施提案中限定的三项metadata变化与全部其余不变量相等；不允许全局放松比较器或重写旧Q/receipt/group。提案没有第二S、额外T/M控制、Conv重跑或自动失败重试。支持其**进入用户审批**，不等于批准执行。

科学问题是：正向证书是否在真实生产路径产生RO miss/准入/事务，以及出现合格pending Tag替换时是否有正确detach、返回和退尽。覆盖率高不等于miss比例、准入比例或加速率。Sticky reuse_seen直到事务退休、所需sector已ready以及同set真实替换顺序均可阻止detach；现有资格拒绝原因/逐set时序覆盖不足，故RO准入为正但detach为零也不能证明Tag始终充足。S/F改变完整机制，不能识别T或M独立性能作用。

接受分类必须保留：无RO准入；有RO准入但无detach；有detach且正确退休；以及正确性/身份/drain失败的HOLD。技术正常完成不要求正收益或非零detach；负结果和资源终止均按原规则保留，不提取中途cycles充当完整结果。

C实际worker认证耗时328.775秒、峰值RSS28MiB，新增logical6,933,927B已计费，旧256MiB未使用预留已释放。E当前只提出1CPU、12GiB主机RAM和544MiB新增包络（384MiB端点＋128MiB资格metadata＋32MiB外部collector），不再重复添加旧C256MiB预测；已有E产物在其metadata包络内计一次。此主机资源请求不扩大模拟L2容量，也不是运行峰值或时长上界，须经用户批准及实时资源/lease门禁。

D没有新科学缺口；A2自己的最终绑定、E受控metadata采用与独立资格/实时资源和用户审批属于后续owner门。原MAIN6/7及原七GM UNKNOWN、SGEMM独立探索、93a9容量诊断、所有负结果/HOLD/旧报告及EN-v22母稿均保持原样。只在E以后正式接受新条件后增量分析；本轮无新模拟、native、构建、trace/raw/SQLite扫描、控制器或registry操作。
