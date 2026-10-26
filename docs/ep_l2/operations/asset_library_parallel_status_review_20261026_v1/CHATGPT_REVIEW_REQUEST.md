# 给ChatGPT的只读审阅请求

请先阅读同目录 [CURRENT_STATUS_REVIEW.md](CURRENT_STATUS_REVIEW.md)、[LIVE_STATE.json](LIVE_STATE.json)、[VALIDATION_REPORT.json](VALIDATION_REPORT.json) 和 [PUBLIC_ACCEPTANCE_BOUNDARY.md](PUBLIC_ACCEPTANCE_BOUNDARY.md)，再按索引检查代码与证据。请使用用户提供的精确提交链接，不默认切到main或其他分支。不要运行这些代码、启动实验、修改账本或把这份请求当新的执行授权。

## 需要给出的独立结论

1. 当前完成/运行/等待/未启动是否与证据相符？38普通和38派生是否错误外推成全部程序覆盖？125输入、22,769对象、25,149引用与972.60GB是否一致？无fraction标签是否被误称为完整应用认证？
2. SM70新NAS-only口径是否有足够代码和观测支持零Native payload/log写入？保留5GiB真实floor、64MiB控制上限，但只报告foreign ceilings而不再叠加为自身准入，是否可能干扰其它项目？Python audit边界、ctypes原语、子进程、/dev/null、core和临时目录有哪些未覆盖点？
3. Source inode重绑定是否严格限于本manifest、已完成17.94GB整SHA及唯一inode差异？旧manifest是否保持原字节？未完成partial保留、全chunk SHA、Source/member SHA、整文件关闭重开SHA和COMMIT链是否仍完整？
4. exact36边界切换是否保护当前RUNNING项、旧dispatcher自然结束、公共COMMIT/readback/catalog和原租约？只改worker两字段、远端心跳清理与单次启动是否可信？模拟lifecycle与真正生产首项之间还有哪些必须观察的资格差距？CPU2没有共享硬带宽限额的表述是否诚实？
5. 精确13派生的父bindings、冻结算法、PREPARED文件集合/SHA、不可覆盖COMMIT-last、派生catalog独占/CAS、资源继承和异常保留是否足够？本次全部13完成是否有终态、目录计数及实际退出支持？
6. 公共库三cwd metadata检查、三次小完整物化和单轮全对象Native窗口恢复是否被混淆？读/写/回读的三倍I/O是否必要且预算正确？哪些历史或精确context的已完成证据可复用而不弱化Target证明？当前2–4天估计有哪些不成立的假设？
7. 科学接受、producer资格、资产可读、消费者语义、硬件timing是否混淆？161项专项适配及各测试集分母、版本差异是否被漏报？是否还缺Source2闭合接入公共BATCH/overlay及protected-after的显式步骤？

## 建议阅读的核心证据

- SM70：[Root批准](code/sm70/ROOT_APPROVAL.json)、[源整SHA](evidence/sm70/SOURCE_WHOLE_SHA_RESULT.json)、[partial保留](evidence/sm70/ROOT_PARTIAL_PRESERVED_V1.json)、[engine](code/sm70/library_copy_v12_nas.py)、[监督](code/sm70/resume_exact_v12_nas.py)、[实际状态](evidence/sm70/CURRENT_STATE.json)。
- CPU2：[Root批准](evidence/cpu2_phase/ROOT_PHASE_APPROVAL_V1.json)、[边界控制器](code/cpu2_phase/phase_boundary_controller_candidate_v1.py)、[冻结前36项](evidence/cpu2_phase/FROZEN_PENDING_36_BEFORE.json)、[冻结后36项](evidence/cpu2_phase/FROZEN_PENDING_36_AFTER.json)、[lifecycle微测试](evidence/cpu2_phase/PHASE_LIFECYCLE_FIXTURE_RESULT.json)、[scheduler](code/cpu2_phase/post_app_parallel_109_candidate_v1.py)。
- 派生13：[终态](evidence/derived13/PUBLISH_TERMINAL.json)、[严格prepared闭合](code/derived13/prepared_closure_v1.py)、[发布程序](code/derived13/publish_one_derived_nas_v1.py)、[非特权资源继承测试](evidence/derived13/RESOURCE_INHERITANCE_UNPRIVILEGED_FIXTURE.json)。
- 公共库：[冻结verification stages](code/public_suite_not_activated/verification_stages.py)、[runtime](code/public_suite_not_activated/runtime.py)、[未执行的bootstrap证据](evidence/public_bootstrap/COMMIT_V5.json)。
- 全部workload状态：[当前QUEUE](evidence/rtx4080/QUEUE.json)、[全部76份ASSET索引](evidence/rtx4080/ASSET_INDEX.json)、[SM70完整125输入投影](evidence/sm70/FROZEN_SCOPE_PROJECTION.json)、[各源码分母](evidence/rtx4080/SOURCE_SCOPE_BASE_PROJECTION.json)。

## 输出格式

先给“可继续当前后台工程 / 需修订后继续 / 应暂停哪一项”的结论，逐项写证据路径和准确代码位置。按阻断、高、中、低列问题，区分已经证实的缺陷、证据不足和仅供讨论的优化。对每项给最小修改或补证要求；不要要求无关全量重跑，不把未提供的trace正文视为已独立复算，也不要假称已验证生产未执行阶段。
