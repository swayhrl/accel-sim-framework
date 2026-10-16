# EP-L2六Lane统一续行指令V2

**本目录替代尚未下发的review_r1/CONTINUE.md。**保持原6c136e2a的科学机制、主配置WBUF16／敏感WBUF8、1168/1160项等预算、TVD额外一拍与RO whole-commandlist oracle。不要重新运行初始Goal；不重置任何worktree/trace/结果；所有动作先检查真实活动进程/registry与自己分支的最新提交。

用户已交付Lane1 r2和Lane4 r2；完成后仍发新revision与准确STATUS、RECEIPT、review pack、push回读。所谓PASS只对应实际测试过的边界。普通工程问题自行修正，协议、资源预算、oracle scope变更才停受影响部分。

## Lane 1：冻结R0，协调独立接入

1. 冻结并保护release：Framework发布02982b65e87f170103b44c6dbd562a8ffb03841e，生产Framework 37dec04d223ae65167c5584e56887c74f6540d27，Core 126394be46b15f55b9756d43eb9ca9a9baae1c84，release binary SHA256 0b504f5573ea0721709bc3439334f7f97a177286eaf73a36876403c7c9228698。已完成3/3新旧all-OFF七CSV精确等价，不要重跑它们，不重编译或覆盖冻结R0 binary。
2. 立即把R0已发布的BASELINE_CONTRACT_V1.json交Lane5独立资格与B16/U_WB16。不得等待其他模块或新的ideal开关才放行这个首轮比较。若Lane5发现真实资格缺口，只针对缺口增量修复并新SHA、新binary；旧release保留。
3. 可以在另一个独立集成worktree，从准确Core R0父提交接入Lane4 r2中经过验证的CORE_MINIMAL.patch，并单独发布诊断R1（all ideal OFF时保持R0行为）。此阶段不能覆盖或强行替换已冻结R0实验二进制。R1随后交Lane5独立资格，Lane4共享准确R1/B16 matched baseline spec，不从R0冒用。
4. Lane2/3从最新R0接口编写各自生产接线最小补丁、定向测试与消费版本记录；你负责最终按顺序合入、冲突校验及逐功能资格，不是替其代写所有Tag/cache/memport hook。新TVD/RO生产版本另冻结为R2/R3，不能把R0基线身份覆盖。
5. 不扩大AI/graphics trace资产、没有证据不改变root预算和bank配置；共享配额由Lane5控制。若R0主实验已在跑，不得为集成分支打断它。

## Lane 2：真实TVD而非目录测试

1. 不重复已通过的七组clean/dirty目录fixture。消费Lane1精确R0公共allocator/pin/role/bank接口，适配后交付实际l2_cache victim、Tag miss后+1cycle lookup、WAD拒绝前dirty read-forward、bank read/ICNT response、WB lower_accept/set_done、promotion和epoch的最小生产补丁。
2. 先交clean真实入口的测试与事件证据，再补dirty/写atomic等待/forward；实测production hook触发且数据/版本reference正确。一个成功的module test不是FULL TVD证据。
3. 修复TVD统计语义：按response累计requested sectors称served sectors/bytes；实际lower/DRAM减少另用匹配OFF/ON事务与字节对照。保留旧字段时显式deprecated，不假装原物理字节已减少。
4. 新接线在Lane2独立worktree测试，按准确R0父SHA发布patch；由Lane1最终集成，Lane5独立验证。缺公共符号才报准确版本/符号，不再笼统报告“Handle ABI尚未发布”。

## Lane 3：RO实际Tag/路由

1. 冻结已完成5个开发负载whole-commandlist oracle资料，不重算已通过的input hash或擅自缩epoch。empty FWT证书是负覆盖证据，正路径用另一个证书非空负载。
2. 在Lane3隔离分支消费Lane1准确R0父版本及已交付r3 Core ddedbf0fabd46c6e35358c9a0e78b77f52cab2c5的最小模块变更，补Tag generation/visibility、GLOBAL_ACC_R request判别、actual memport lower/sector return、L2->ICNT同周期response commit、epoch/certificate校验、结束排空及两个默认OFF开关。
3. Attached merge使用实际Tag pointer；detached bypass下同地址新事务由真实Tag miss重新分配，不能用全completion地址扫描冒充免费硬件CAM。同地址旧/new handle都能独立完成，late fill不污染reused Tag。
4. 用真实生产入口测试four mode路径、错误证书、sector乱序、背压及共享D512 descriptor容量；可减少不变的oracle重复测试。向Lane1发最小接线补丁，Lane5独立验证r3后的变更；不要把旧版Lane5模块PASS当新runtime PASS。
5. 完整版本的ro_tag_detach与ro_line_mshr_bypass分离资格；运行时已接受请求范围与oracle合格候选覆盖率两个分母都报告。

## Lane 4：旧ideal交付完成，新B16另版本配对

1. 你提交的Framework96fbcb612773900fd75268ffe4e00ed9f13d3d42/Core b8b3d55b392fcff793d0aec684bddb73ba3065a9已包含I_WB/I_META/I_READ_HIT/I_WB_META及历史旧静态vectorAdd 73873->42918（1.721259x）。不重复重跑3次旧完整应用、不新造更激进理想化点。
2. 将CORE_MINIMAL.patch在精确R0父提交126394be适配作为最小集成交付给Lane1；配合Lane5新诊断R1 binary的独立资格、R1 B16 matched baseline spec和registry，严禁把R0不同binary B16当R1 ideal精确对照。
3. R1合格以后，依Lane5配额滚动四工作负载的I_WB、I_META、I_READ_HIT，I_WB_META仅convolution/FWT。先完成的格按准确manifest发布，不等待全18格齐全才提交有用结果；缺失仍NOT_RUN。
4. I_WB保留实际copy和WAD，I_META保留排序与真实回填，I_READ_HIT是乐观读参考非严格数学上界；报告解除容量后是否真正non-binding及新的blocking移动。旧历史1.721x不填新B16表。

## Lane 5：本轮最优先：独立资格与正式B16/U_WB16

1. 立即fetch Lane1发布02982b65...及BASELINE_CONTRACT_V1.json、review_packs/FT20261016_LANE1_WBUF_RELEASE_r2。runtime_ready=true、binary/config齐全，老的c603a563报告“依赖无binary”已过时。先确认真实registry是否已有相同任务；无重复任务再用已冻结R0 binary执行独立production-driven gates。
2. 复用Lane1已完成的三对all-OFF历史等价证据，但须独立检查输入身份、七CSV与必要production correctness，不能只接受Lane1自报PASS。SASS无数值payload的限制如实记录，利用独立reference sector版本和requester/response/token/WB/终态不变量，不因没有不存在的数值输出自动卡住整个资格。
3. 对确实通过的R0发布INDEPENDENTLY_QUALIFIED与逐feature向量资格，立即启动B16_BANKED vs U_WB16五开发负载配对，最多两长模拟/8CPU/32GiB reservation并受真实系统资源限制；不用等待TVD/RO/ideal。每完成一个有效pair即可冻结对应CSV/manifest交Lane6，均值只有声明完整集合后计算。
4. R1理想诊断另有Core/Framework/binary身份。独立验收Lane4 patch整合后的新binary并提供同R1 binary的B16 baseline给Lane4；不要把R0 B16作为精确R1 baseline。不要反向阻塞R0主结果。
5. 对Lane2/3生产接入的R2/R3只重验证新增差分及必要组合边界，现有独立模块旧SHA不自动覆盖新代码；RO位向量需显式区分detach与MSHR bypass，schema迁移映射旧R0记录，不重算已合格R0。
6. 真正有U_WB局部效应后，选择代表点测试相同1168总项静态重分区和copy归因；不能把“bank/copy减少”冒充“动态借用产生性能”。低效和退化必须保留。scan保持独立长任务。

## Lane 6：同步精简论文并提前准备结果接收

1. 保留r1和所有源证据，产生新revision中文投稿结构；主线优先真实WB池等预算比较，TVD/RO是待验证扩展。删除正文中的大段项目管理、Lane、用户确认、hash/status与NOT_RUN说明，移到补充证据文档。绝不提前写新机制加速。
2. PPA更新Lane1 STORAGE_AND_PORT_LEDGER：1168/1160数据项、双方共同的128B/slice copy latch、真实bank服务、WB metadata。按绑定当前实际代码字段、参数化假设、未知RTL/工艺三列呈现；RO T_RO=128不是实现真实容量。
3. 将Lane4旧静态vectorAdd乐观读参考（1.721259x）在独立diagnostic图/讨论中正确标注；不写成EP-L2新结果、严格天花板或全负载平均。
4. 历史Streaming 13行checkpoint的准确source/hash可复用，RO closed-world、TVD +1cycle、SASS不含数值仍需如实表达；修复TVD served-bytes≠lower/DRAM saved。
5. 随Lane5正式pair、Lane4正式ideal分别接入完全绑定的CSV，保持失败/未完成行；生成目标版式的简洁图，验证可读性而非仅验证可重复生成。

## 共有终止/记录约束

- 本指令不是运行/重启命令的执行证明。所有lane在已有窗口延续，先查看本机/registry；不要stop/kill/rebuild已被其它任务占用的binary，不覆盖旧结果。
- 各lane保持各自hrl/ep-l2-ft20261016-laneN-v1（N=1..6）Framework执行分支；Core需改时用同名独立Core分支，不对协调分支push。
- 准确source/build/config/trace/feature/ideal/结果与review gate状态作为receipt，push并远端回读。普通工程细节修复后继续，改变协议/预算/科学输入边界才停止受影响部分。
