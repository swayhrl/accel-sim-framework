# EP-L2协作公共面板

当前索引由E2维护；owner STATUS仍由各lane本人发布。此页不是进程心跳或实验授权。更新时间：2026-10-21T16:49:59.471221+00:00。

## 已完成科学交付

五组新93a9 binary容量/data-service OFF/ON均CURRENT_ACCEPTED，最终独立审查COMPLETE_PROVEN，原controller STOPPED、历史actual46。准确最终证据：E2 `092b6396b5b1c628807572badb39ea8b82871de6`，`MS20261021_E2_CAPACITY_DIAGNOSTIC_r1/FINAL_RECEIPT.json`。Conv292932/268117cycles；保留CFD负例，全部ON分类UNKNOWN，不作无限/硬件/容量单因果结论。原32矩阵/旧失败/HOLD/累计生成不变。

D待办 `D-CAPACITY-FIVE-INCREMENT` 的正式Conv依赖已满足；E2-00000019已投递。用户本轮负责唤醒D。D应fetch E2并复用四对缓存，仅补Conv及五对图/汇总；E2未推断D已ACK或完成。

## 当前并行流水

|Owner|当前具体工作/触发|已知本人状态来源|
|---|---|---|
|E2|FWT/SGEMM四条件资格成本提案已准备，等待用户批准；当前0新应用/native/build/Goal/中央写入|本轮E2本人STATUS|
|D|已有Conv增量+五容量对汇总；未来每个接受配对立即增量消费，不等待所有workload|最后核对D `1acb29bd3e88eb6f96ce1140dabbee9e446e4d5d` 自报IDLE、旧Conv依赖待更新；不替本人改STATUS|
|A2|main61 SGEMM配置与18门复用映射已完成，具体producer缺口才合并请求|最后核对 `d45d0a5532dfdd7489d0e5a76b99de432a27bfdd` 自报IDLE|
|C|SGEMM空fallback/BFS host边界已完成，具体语义缺口才合并请求|最后核对 `52ed0e2f18774c12054b10cb21390f7b4a9768bb` 自报IDLE|
|F|有界输入包已完成；BFS精确MISSING保留，不重复空搜/部署|最后核对 `ab8e04dce031aee26e9f92e1b9cebe88fd9f8c2f` 自报IDLE|
|B|复用现有W/V结论，无新增任务|此前已核对本人IDLE，不要求重复无变化回执|

## 待批准准确下一批

[提案报告](../review_packs/MS20261022_E2_WORKLOAD_PIPELINE_PROPOSAL_r1/README.md)及[机器提案](../review_packs/MS20261022_E2_WORKLOAD_PIPELINE_PROPOSAL_r1/PROPOSAL.json)：FWT原main61 S/F恢复2次，SGEMM同main61独立探索S/F2次。当前未授权、未采用、未启动。FWT原Q有效；SGEMM仍需当前body身份和自己的E资格，不能冒充PASS。原32桶已满且现policy仅准旧10容量条件，因此提案包括新精确scope/独立batch计费和原中央受控接入，不扩大/借用旧桶。

整个提案最多4次、1.5GiB端结果+128MiB资格输出+32MiB外部metadata，守原10/24GiB累计生成及5GiB+2GiB监控、Share/CPU/RAM门。当前预测1–4路可容纳，实际每端事务准入；无固定两路cap、无旧时间截止，新四端操作timeout=null须准确批准。FWT约80–120分钟/端只是历史先验；SGEMM及整批ETA UNKNOWN。

批准后E2在唯一原中央接入/验证并逐条件运行；FWT门闭合可先行，SGEMM资格准备并行。每对独立接受立即交D；失败保留且计费，无自动retry/替换。BFS/Hotspot不在此批。原main61 MAIN、SGEMM探索、新93a9容量cohort分别统计。

## 协调方式

E2暂任协调owner；A2仍负责producer，D负责科学解释/图表。用户在E2窗口批准准确方案后，E2前台脚本转发给受影响lane并核对真实ACK/成果；已有授权工程不重复审批。各lane在安全边界读取队列，完成即发布成果/本人STATUS并接下一项依赖就绪且已授权的任务。没有后台poller、第二controller或自动唤醒IDLE窗口；用户无需再次复制科研材料。

旧准备r2所有A2/C/D/F交付均已Git核验，来源见 `intake/E2/PREPARATION_BATCH_r2_DELIVERIES.json`；旧面板快照保留在Git历史。本页更新不重开任何旧Goal。
