# Review method and evidence limits

本窗口仅source/历史收据复核，不做CPU subject qualification。没有compile、fixture、ptrace/guard调用、canary、执行锁或sim启动；不修改BA角色表。历史stdout重新解析、SHA/index/JSON图检查是此准备任务所需的只读postprocessing，不能宣称新的global-R2或CPU角色准入。没有改名脚本、路径通配或用inline包装启动被阻止的测试。

1. 原174 hostname确认；GitHub fetch固定V2与AG3/4/5，BA live branch read-back为`7cdc27a7…`，完整阅读三份V2文档。新branch/worktree/output与旧Goal分离。
2. 两原BASE的stdout各重新解析一次，调用SHA绑定的原纯strict解析函数，仅postprocess已有文本；重新检查完整命令顺序/路径/memcpy、kernel/CTA/instructions、exit、270 options、全部每kernel公共指标和traffic。SHA另与原run index核对，未调用其测试suite或任何trace replay。
3. 每run的重要receipt与run index对SHA；GEMM通过原AG3 published root raw-index链，Gaussian通过原AG4 published RUN_ARTIFACT_INDEX链。48个用到的source/receipt文件与各自不可变Git blob逐字节一致。
4. 12个实际运行文件（含ELF、lib、loader、cache及helper）一次只读SHA与文件身份比对，702项原源文件SHA一致。ELF build-id只用静态readelf读取，没有执行target或loader。
5. 511原trace成员只核已发布SHA来源及当前dev/inode/size/mtime/ctime，全部不变；未重读约1.99GB body，未扫描其它trace。两原list内容及SHA保持。此结论不能覆盖后续文件变化，BA实际预注册/launch还须再核。
6. 两event JSONL各单次流式review：父图/记录PID唯一性、可得ticks、被记录exec的cache出现/unmap/closure、frame digest与immutable run index逐项join，以及exit总体。未重新hash全部旧maps payload；不能把index join称为每份maps当前内容重新解码验证。
7. 原resource日志各单次检查哈希、原成对准入、root PID/ticks、原authority与hard-stop记录。GEMM有9 WARN、host IO最大28.36%，不是全程IO≤25%；原持续R2没有STOP，majorfault=0。Gaussian有一次真实PENDING authority；完整结束时confirmed/pending为空。不能把它改写为每次authority都PASS。

复用裁决是本次新独立、限精确身份的run-specific决定。其依据包含直接记录及冻结源的fail-stop一致性推理，不是新增per-resume generation跟踪。GEMM缺每child start_ticks，明确UNAVAILABLE；Gaussian的qualification gap与synthetic AST counterexample永久披露。没有强制Linux PID复用，也没有证明原performance真实发生PID复用。新BASE eligibility不能回写旧cohort的executor资格或科学终态。

输出中所有新sim、fixture、预算/UUID计数为本AG准备窗口范围；BA published 0/32仅是其旧快照，不代表BA此刻live状态。当前没有AG CPU exact-role资格或正式双采样admission，不能由单次磁盘/PSI观测或用户授权补成。

两处普通file-authoring glue错误（原GEMM raw index字段位置、跨worktree元数据路径）已按实际schema/固定路径修正，没有产生测试/模拟attempt、修改旧收据或改变科学要求。
