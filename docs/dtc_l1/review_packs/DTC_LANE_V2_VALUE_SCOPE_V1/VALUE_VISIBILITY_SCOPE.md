# Lane V2：值可见性支持域与证据分层

2026-10-18，Asia/Shanghai。**VALUE_CORRECTNESS_UNPROVEN；本包完成值语义规格/CPU见证，不给生产load值、全ISA一致性或K2实现PASS。** V1已完成，原分支与文件不改、不重跑其Goal。V2只新增独立目录；不重扫任何实际trace body，不启动模拟器或性能任务。

## 已固定的裁决和四个不同概念

**遵守用户已选定的K1：原 `ldst_unit::invalidate()` 的source请求入口。该选择已定，本包不重新解释或重开入口选择。** K1只撤查询映射，旧physical/generation/PIB/Ref/return保留；不把它改成ordinary延迟Tag提交或无活跃Ref的统一kernel-end。

|概念|精确定义|与值可见性的关系|
|---|---|---|
|K1-source-request，E|原source调用到达所选SM的LDST invalidate；继承idle-cluster、MEMBAR、config-change调用者的条件|撤该SM的DTC查询映射；新查询不能用旧Tag；不执行write payload发布，不改变旧消费者读值|
|ordinary pending-commit，C|ordinary invalidate已pending，自己的miss queue/owner/MSHR排空后退休该请求|ordinary Tag动作；C可晚于E，可为unused Tag no-op；不是DTC的新线性化点，不等于write visibility|
|真实kernel-done，D|kernel完成检测更新finished/end-cycle记录|不凭该记录推选中E或同步、lower排空；不能造统一无Ref事件代替E|
|无选中E的写后读，R-no-E|S/atomic/bypass沿原路走后，cacheable L仍可查到旧DTC映射|K1没有被触发，不能声称它修复了这类写后可见性；VV01/15/20等给合成风险见证|

四者分别记事件，不用完成次序代理替换其中任何一种。V1的源事件细节不重复推导，增量源路由和X实现快照见 [SOURCE_ROUTING_CROSSWALK.md](SOURCE_ROUTING_CROSSWALK.md)。

## 固定输入与发布快照

|对象|本轮固定SHA|如何使用|
|---|---|---|
|冻结Core|`6fba0136f8465b59fe5858a950fa39efb265f654`|从origin按SHA fetch，读Git对象；冻结行为基准|
|Framework build|`18a68dcccd795f1b6cda75504e9450d00c9cee02`|冻结SASS trace consumer/parser代码身份，不冒充V2文档HEAD|
|Lane V V1|`26abd496417d9392245052e54fbd9ba27c6ffd96`|fetch/read-back完全一致；V2分支以此为base，原V1零diff|
|Lane Y V1|`b673d046b38f61159b5db67a477d58d1afa4662f`|固定FAIL_CLOSED；它验证的是X旧Core `f8b34dd7…`，不是下行新Core；不重跑Y|
|Lane X Framework最终快照|`49fb5d1b62b6f2387abc2d568bc8ae7543dc0df4`|发布前复核远端更新后再次fetch/read-back；OO default-off已实现、本地CPU检查通过、Lane Y独立验证仍pending|
|Lane X Framework历史快照|`0c8fcb571977303f3e87ecb0cac6cf7bd25d3cfc`|初次远端回读为旧STOP，后续报告已将其列为历史；另是X新trace binary的build-source commit，不冒充最终review HEAD|
|Lane X Core|`c0a5e2c31e407c57e3a4af3ce529c921e8059a05`|远端fetch/read-back已含OO source-request K1实现；仅据已发布common header追加本V2小型桥接见证，不改Core、不替Y全门禁验收|

**发布进展与验证版本差异须保留**：初读X Framework旧STOP，发布前复核发现新报告并回读至`49fb5d1b…`，现与`c0a5e2c3…`一致；Y V1仍是旧Core验证快照，不能自动改写其结果。用户已裁决的入口不再是本V2开放问题；实现全范围安全、时序资格与值正确性仍是不同命题。X新开关默认0、只准PAPER_OO，IO/modern/base的K1不可由本包外推。冻结build18、X trace-build `0c8fcb…`与X最终review中所审5份Framework路由源码已逐字节核同，但不据此断言binary/runtime相同。[SOURCE_SHA256.tsv](SOURCE_SHA256.tsv)逐文件绑定输入。

## 值判据：先定义需要哪次写的哪些byte

对每个load L，至少需身份 `(地址空间/规范化地址范围、活动lane、width/byte mask、线程/SM/kernel、cache route)`；对写 W还需payload、byte覆盖、动态UID、原子操作及其返回值、order/scope、真实发布/序列化点。physical generation只区分allocation，**不是memory value版本**。

本包合成域D-syn明确限定：单一规范地址、给定初始byte、外部按事件注入write payload与publish点；每个read-from快照由fixture指定；需要fresh的读另有外部顺序断言，没有竞争写或未解析alias。其规则为：

* L被明确要求在W发布之后观察且没有后续冲突写时，只对W覆盖且与L重叠的byte要求W的新值；未覆盖byte保留其前值。相同128B/32B行号不是byte重叠的充分条件。
* 跨byte/sector的值由fixture的字节序列明确给出，不推整warp/整sector原子性；byte31/32是分割覆盖见证，不证明硬件会整体原子更新。
* 写之前接纳的旧load，其允许读值集合必须单独定义。VV22把旧read-from=7作为输入假设，不能凭晚返回时间把它改为9或自动判成ISA错误。
* 无HB、scope、发布点或原硬件规定时，允许值集合写 `UNSPECIFIED`，科学状态UNPROVEN；不能随意把观测旧值认定错误，也不能任意宣称旧/新都合法。

这些是**合成正确性规格**，不是完整PTX/SASS模型。原硬件依据要求另补：NVIDIA PTX 8.1区分scope/causality与读值约束；cache operators不改变其memory-consistency规则，不能单靠绕L1的路由推一致性；mixed-size race还另有适用性限制。仅以这些规范界定缺失材料，**不建立冻结SASS到PTX条款的完整等价绑定**。[PTX memory model](https://docs.nvidia.com/cuda/archive/12.1.1/parallel-thread-execution/index.html#memory-consistency-model)、[cache operators](https://docs.nvidia.com/cuda/archive/12.1.1/parallel-thread-execution/index.html#cache-operators)、[mixed-size限制](https://docs.nvidia.com/cuda/archive/12.1.1/parallel-thread-execution/index.html#limitations-on-mixed-size-data-races)。

## 实际路线能证明到哪里

|问题|SASS时序/生产header可支持的命题|不能推出；需另补|
|---|---|---|
|L→S→L，无E|首L可留visible映射；S只ordinary/bypass+sidecar；后L可VALID_HIT同identity|后L实际值；同线程相关寄存器依赖/编译映射、write propagation/forwarding和byte oracle|
|部分byte/sector写|coalescer生成byte/sector覆盖；ordinary cache更新自身mask/状态；DTC128B引用保持|覆盖byte新、非覆盖byte旧的实际payload组合；跨sector切分与mixed-size竞争资格|
|atomic|全局ATOMG/ATOM/RED在冻结consumer设CACHE_GLOBAL；不进入DTC read merge；source completion保持原路|真实RMW一次效果/旧返回值、atomic order/scope与后续普通读一致性；trace should_do_atomic=false|
|bypass|可观察旁路请求与DTC路径分离；旁路写/读不自动改变旧DTC映射|旁路读到新值不能说明随后cacheable读也新；cache op路由不是coherence证明|
|MEMBAR|source scoreboard判据、flush guard和选中SM的E可定位|不能据注释或pendingWrites==0推所有store ACK或真实ISA fence已完成；E后的lower值仍需证明|
|PROXY_FENCE|source async规则与OO同warp年轻候选退休过滤|不能充当全局写发布、读值判据或跨SM同步；不得把它借作K2屏障|
|跨SM|source E的SM作用域可定位；另一SM可以保留其Tag|写何时对目标SM可见、远端映射处理、GPU scope/HB；单SM E不是写广播|
|跨kernel|D与E可分别识别；E条件受cluster/配置/guard控制|stream/API的真实同步、地址复用与下层值；D不是所有SM E，也不是payload oracle|
|pending fill与store交错|旧返回绑定旧identity；finite metadata晚于lower响应；K1保留旧Ref到最后退休|旧请求在哪个时刻采样哪次写；E前后新请求是否都满足fresh谓词；晚到旧payload不能投给新consumer|

冻结trace schema存在可选 `reg_dest_vals/reg_src_vals`，不能说“trace格式没有值”。但当前普通load/store consumer没有用这些字段形成通用store payload内存和逐load期望值比较；个别BAR/SYNCS路径用值不闭合一般访存。本轮只读源码，不检查真实trace是否含这些字段、不统计实际风险频次，相关body资格归W。

## 本轮CPU证据与主张停止线

[CPU_VALUE_WITNESSES.json](CPU_VALUE_WITNESSES.json)：25个独立合成序列，8个满足显式字节规格、13个按预期拒绝错误值/错误完成代理、4个缺值谓词保持UNPROVEN；每例另有错误期望退出1的负控，共25次。程序正常退出0表示**观察到预期的PASS/REJECT/UNPROVEN**，不是生产值正确性。`semantic_exit` 0/1/2分别表示合成有条件符合/违反/未定。

header桥接程序分别对冻结和X新发布header编译运行：无E时IO/OO可沿原identity命中，外部单byte合成写与该映射旧byte可不同；X OO pending-return→E→新同址allocation可保持旧identity直到最后Ref。7/9由桥接fixture注入，header本身从未返回它们。本例只补“结构状态兼容哪些外部版本组合”的见证，不给K1全范围独立验收，也不实施写处理。

**STOP-VALUE**：没有生产payload/read-from oracle，停止数值正确性主张。**STOP-ISA**：没有明确指令、scope/HB与硬件绑定，停止全ISA主张。**STOP-K2**：只交未来最小规格，未经独立授权不改任何生产写路径、可见性协议或服务模型。若实际值验证必须新增Core数据模型/插桩，本轮只记录缺口，绝不改Core。V1/Y/旧A/T/U结构守恒、终态strict与性能均不能替代这些证据。
