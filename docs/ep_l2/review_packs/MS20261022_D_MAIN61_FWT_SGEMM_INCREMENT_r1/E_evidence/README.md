# 下一阶段四次启动提案与流水交付

**状态：待用户批准；当前新增应用/native/build/Goal/中央变更均0。** 推荐明确批准两个各2次的新范围：原main61 FWT S/F恢复，加SGEMM独立冻结trace探索S/F。批准仍须逐条件资格和原资源门通过，不是直接启动命令。

|优先级|条件|科学用途|资格现状|真实新启动|结果硬上限|
|---|---|---|---|---:|---:|
|1|FWT S/F，同main61|恢复原MAIN缺失配对，零certified-RO负背景|原Q18门有效；93项producer/main/archive/源码/输入小证据/stat复核通过，当前launch内容闭合与原中央新scope接入仍需完成|2|768MiB|
|2|SGEMM S/F，同main61|dense/低旧压力独立探索控制，不替代Btree|37个Git小blob/18通用门已核验，A2完整配置+C独立fallback可复用；还需当前body内容身份与E独立input/profile/parser/fallback封口|2|768MiB|

准确四个condition_id、原始输入/配置引用、runtime身份和操作边界见[PROPOSAL.json](PROPOSAL.json)。只批准这套四端，没有次选并集或自动扩到BFS/Hotspot。全部启动后历史46变50，任何失败照实计费，旧INCOMPLETE/HOLD不退款也不覆盖。

## 需要批准的准确变化

总count/时间限制取消并未使已满的原32桶可重复使用。当前中央policy也只识别十个原容量条件。因此申请两个新的独立2-start batch ledger，以及[原中央受控接入](CENTRAL_ADOPTION_DESIGN.md)，原T0、32矩阵与各原桶、contingency8/8和旧十容量范围完全保留；不通过增加原reservations或第二controller绕开。

四端均用已正式release的main61：Core d010911e3174a3764791183cd108fe4664ba8731，Framework9dd1ee57a83d83b56b7874bc7c716185ab52c8f7，Vendorf90c430c3a1ce8f08c09942a5a1c3a797bb2295b；main61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5，archive3c6ce15b88ae16c17c30718618aedc769495168d6e3d0c371270ba95b7b0aca8。每对两个新端点同binary，finite1168/物理P1、F W/V/T/M全ON，无copy/data-free。原93a9五对容量结果和分母保持。

新条件拟effective_timeout=null，沿用用户取消时间上限的方向；旧FWT冻结spec的10800字段保留为原身份事实，由明确的新操作override承载。没有旧启动/intake截止或固定两路上限。资源守护、真实native wait0、完整命令和指令、64slice及资源退尽不变。

SGEMM已保存全grammar/non-atomic证明可复用，自己的当前2,216,170,035B body仍须SHA与原1b0739908e3aef52cedea68962172ccac55f0c2d4c651623cb8fb0655475db06一致；必要的流式身份核对和前后stat纳入批准后的资格工作，不重做grammar/17项native或构建。E自有配置候选仅重绑RO两个路径，原C manifest/ranges字节、hash/scope不变；不会依赖A2继续修改工作树。空覆盖不是RO实测0，来源/捕获/数值UNKNOWN仍限制为冻结trace模型探索。

## 预算与时间

资源快照：原174 controller STOPPED，无活动模拟或匹配lease；workspace约17.07GiB、Share41.18GiB、有效可用RAM199.44GiB。原门禁只读预测1–4路各1CPU/8GiB均可容纳；四路正好占满共享32GiB预留，实际资格/启动时须逐路事务准入，不承诺必能四路。

四端384MiB各自硬上限合计1.5GiB，另列资格输出最多128MiB、端目录外collector/metadata最多32MiB，整个提案1.65625GiB。现累计new6,899,258,320B、total21,208,834,704B；在10/24GiB原上限下，预留整个提案后仍余new2,059,775,024B、total2,782,584,176B。此处只是预测，尚未预约/分配。5GiB底线、每端2GiB监控余量、Share/CPU/RAM原规则保持；迁移不归零累计生成。128MiB只是输出包络，不授权新的native或build。

FWT历史先验S80–110分钟、F85–120分钟，可同时准入时约90–125分钟；单路滚动约165–230分钟。这些不是终态测量或保证。SGEMM walltime及整批结束时间UNKNOWN；837秒离线扫描不是模拟时长。取得真实进度后再更新ETA。

## 流水安排

- D现在执行既有Conv增量及五容量配对汇总，复用四组缓存，不等本提案或新增应用。
- E2并行完成FWT复用与SGEMM专属资格准备；准确批准及中央接入后，FWT门闭合即可先行，SGEMM继续准备，不设统一全批等待屏障。单路可准入就滚动，有资源才增加并发。
- 每对独立接受即发布精确binary/input/profile/exit/指令/cycles/机制计数和结果位置，立即投递D；失败也立即交精确证据。D按cohort增量消费，不重复已完成缓存。
- A2/C/F已有准备包全部复用；只出现具体新缺口才向责任owner合并派一次修订，发布本人ACK/成果后接下一项依赖就绪的任务。B继续复用已有W/V审查。BFS七项基础缺件保持MISSING，Hotspot备用，不让它们阻塞前两组。
- 原共享队列与批准转发脚本负责去重、投递、回读与真实ACK追踪；不会唤醒IDLE窗口或建立后台poller。用户已负责本次唤醒D，其余lane没有重复准备任务。

本轮独立证据：[FWT](fwt_review/README.md)、[SGEMM](sgemm_review/README.md)、[资源与成本](resource_review/README.md)。本提案的精确新scope/时间请求优先于子审引用的旧spec操作默认值。所有准备不能冒充E科学资格或CURRENT_ACCEPTED。
