# AA2 Gaussian: execution HOLD, zero full starts

收口时间（北京时间）：2026-10-18T00:51:01.675575+08:00。状态 **STOP_WITH_FOUR_HOLD_CELLS_NO_STARTS**，AA V1+AA2实际full starts仍 **0/4**，canary0。
当前决定性阻塞是存活旧DTC自动派发authority及其FLOCK；不因U早已结束或内存/IO探针数值通过而绕过。完整可执行预注册未发布，四份spec仍明确为DRAFT_HOLD。

| Point | Inherited UUID | Final state |
| --- | --- | --- |
| K0_32x4 | d0a29a82-c171-46e4-b077-d7ccfd2c4b7a | HOLD / NOT_RUN |
| K0_64x8 | aba7a8eb-e82c-4a18-b410-5d568f819f27 | HOLD / NOT_RUN |
| K1_32x4 | dd65b440-dc75-4632-9f7b-3e8a1062d5a1 | HOLD / NOT_RUN |
| K1_64x8 | a9d64a6f-4fb5-4e3d-883c-ae75f1ac5f89 | HOLD / NOT_RUN |

已从远端回读绑定真正K1 Core `c0a5e2c31e407c57e3a4af3ce529c921e8059a05`、X trace executable SHA `2cd45b1b91985b19255ff5c9db3b49a3ee46b5a479272eacd2a42fb2bf9ac9ae` 与实际shared library SHA `06957c897f8248fa2b08a5c18823207db8dda954c218337ba399ba70e7f97b56`。CPU parser探针复制到AA2，ldd确认加载同一X库，未执行accel-sim.out。Framework build source为`0c8fcb571977303f3e87ecb0cac6cf7bd25d3cfc`，与AA2 orchestration分开记载。不是历史f8b34dd7文档STOP Core。

V `26abd496417d9392245052e54fbd9ba27c6ffd96`、Z2 V2合同（SHA `bad86ae9be5ab7958171fcddf1b9790f8ec1e66d030eb5d490bee9b5a1f67d7d`）及Y2发布 `9a0d374df215e4878774ec2e3f9e49d1eda67b38` 均已绑定。Y2裁决为 **PASS_K1_OO_MODEL_SCOPE**，生产option默认/OFF/ON和CPU K0等价检查通过；资格仅限披露的OO逻辑/API及生产语句夹具，不含完整GPU/NoC、真实operand collector、数值load或PPA。没有把旧Y1 FAIL_CLOSED改写成新Core裁决。

原Gaussian list SHA `6dc7caba6733657293e8c517467bac28890ae4eb97c732ffd245d7fd1c479fb9`。Gaussian明确510成员、513命令（3 HtoD）、283,685,120 active-thread instructions；全部510成员重新SHA256，约877MB读取限64MiB/s。511仅是T中GEMM+Gaussian合计，不当成Gaussian成员数。两个时点的UUID扫描未发现预留UUID实际RUN_START。

有效配置固定OO128、physical640×128B、ordinary16KiB、shared96KiB、64SM、原4bank/finite服务、cap32768、1410MHz和flush_l1=1，唯一预设变化为K与Tag。四点各有267项预期profile：230项用精确X库CPU parser回读，23项runtime和14项Framework字段由接受echo与逐字未变注册源码绑定。省略K0和显式0的完整Core profile相等。剔除旧echo抽取器误收的7项trace header元数据，旧AA/T证据未改。完整实际simulator echo仍须在未来full strict中再次核对。

旧authority **PID1425986/start_ticks584741606** 仍存活；`fdinfo/9`明确FLOCK，target为`/workspace/fast64-primary-r4/.fast64_4_2d_core41_autodispatch_v1.lock`。它的脚本具有未来派发路径。全局/proc/locks未显示该锁，补充fdinfo后不能声称已释放。见FINAL_AUTHORITY_WITNESS.json与LOCK_FDINFO_SUPPLEMENT.json。AA2未获取旧锁、发送信号、删除其它文件或建立新模拟authority。

两次10秒资源探针中host/cgroup内存、disk、memory/IO PSI、swap和OOM差分均通过；其它项目sim/RTL/编辑器等全部计入。执行权检查仍关闭，未核DTC控制helper也保留，不用数值资源余量代替科学与authority准入。EXECUTION_RESOURCES.tsv和raw快照保留实值，最后快照不冒充新的10秒准入probe。

X仅在K1路径观测并打印source-event summary，K0缺字段保持UNAVAILABLE；X/Y2的零额外模拟cycle模型、host bookkeeping成本及共同observer合同不能混称。AA2-OBS-001保留具体条款审查，不请求第二套Core或增加计数器来修平。W完整地址扫描为UNAVAILABLE机制归因缺口，按用户AA2指令记录W_SCOPE_CLAUSE_REVIEW.md，不作为本次不执行的原因，也不声称已测复用或值正确。

已在新性能之前固定物理守恒完整项：new_misses=allocated+immediate_reclaims+final_ref_reclaims+source_reclaimed_at_event。K1 Ref0 source回收不进入旧immediate counter，持live Ref者最终释放已进入final_ref，不能重复扣减。独立CPU生产header正反例通过，属于计数合同校核，不代替Y2或full-run strict。

未有新K0，历史3798174/3278356仅校准参考；以后须两新K0先于任意K1且精确通过，差异即STOP，不retune或补跑。每点7200秒、一次实际启动，合计AA+AA2仍最多4；不重置预算。所有full natural exit、510kernel/CTA/instructions、Ref/credit/PIB/physical/ordinary/sector、finite及真实event验收目前NOT_RUN。四格、主效应/交互、类型化机制字段均UNAVAILABLE，完整保留HOLD。

小文件最终commit/push/fetch-back、全部文件blob比对和clean由AA2 raw root的FINAL_PUSH_FETCH_BACK.json闭合。旧AA83文件逐字未变，旧raw/Goal未覆盖、未重启。CPU guard的--execute按预期退出3，无simulator启动；本包没有生产runner或后台自动派发。STOP后不启动T2、新Tag、新Core、其它输入、GM12、主配置晋升或论文修改。
