# AG5 → BA integration review

结论：**BA新提交已完成一体化源码移植，source review PASS；受影响路径运行资格仍待BA完成，不需要重跑AG5全部53项。** 本窗口没有修改BA文件或执行测试。初始commit/blob/SHA在`SOURCE_COMPARISON_SHA256.json`；收口新提交及逐项对照在`BA_FINAL_SOURCE_REVIEW.json`、`SOURCE_SHA_TABLE.md`。源码快照均为惰性`.txt`。

初始审查锚点：AG5 `9793e998d60cb5a7f064a46ecd6be242eda61b7c`，BA `7cdc27a7f4d7f13e11f942d6afdc5529121e6c3c`。该BA版本的`vendor/ownership.py`与AG4字节完全相同；guard已经独立在正常/清理reap时移除`owned/states/parents`，并在resume前检查当前confirmed和same。以下表格描述初始版本及必要变更，不能当作收口时未完成清单。

| 接口 | BA当前源 | AG5差异/必要集成 |
|---|---|---|
| 当前进程归属 | `owned`与`confirmed`双集合，分散retire | 采用一个canonical当前实例owner；retire统一撤销归属、image、inherit和队列项。共享peer view只分类，不成为本地owner。 |
| `Ownership.same` | 检查start_ticks | AG5显式membership、start_ticks、TracerPid、Tgid；guard在stop分派与resume前都核验。保留父GETEVENTMSG及pending ticks一致性。 |
| image身份 | PID索引，无generation stamp | image绑定当前ticks；禁止旧image状态影响新实例；退出历史另按PID/ticks保存，不能只靠PID-keyed退出字典。 |
| fork继承 | child首次stop查父当前states | AG5在真实父事件时复制绑定父/子ticks的继承快照。BA已删除reaped父state，因此合法parent先reap/child后首次stop是实际新增必测路径。 |
| guard启动政策 | BA ROOT、CPU request、SIMULATION capability | AG5发布版本是固定CPU目标、禁止SIMULATION；不能照抄此政策到BA。携带事件/归属修复，保留BA自己的发布能力、UUID、target/argv/env和资源门槛。 |
| observer ABI | `observer(pid, full_hint, local_ownership)`，SharedOwnership只读包装 | AG5的`confirmed/pending`、`tracer`、classify ABI保持；snapshot新增`retired`不授予peer权限。guard始终用local owner做confirm/same/retire/resume。 |
| peer与外部角色 | 当前guard PID/ticks、request SHA、source/argv/exe及≤2秒active快照 | 同步更新所有producer/consumer/request source SHA，验证退休后peer快照及PID复用；CPUContext仅授权CPU，不能改名为fullsim权限。 |
| legacy reviewer | 冻结AG4 reviewer＋exact-role adapter，移除child fallback与退休AG4 prefix权限 | 保留这个精确来源边界。不要整体移入AG5自己的pack-prefix exception、历史EP-L2 PID绑定或basename权限。AG5本地reviewer不是BA共享dispatcher的通用替代品。 |

`review_with_exact_roles`对分类视图移除已核定CPU控制器，但原始全项目资源快照不变；此语义应保持。exact role不允许额外argv、相似路径/目录、任意PPID或新ELF。`SharedOwnership.pending`仍使legacy reviewer非PASS；新`retired`历史不得被序列化成永久白名单。peer view不能用于signal/resume/attach。

收口重拉BA为`25cf0ab03d6cc68f964eeb03f42347452ac23abb`，其`AG5_INTEGRATION_SOURCE_V2.json`已明确消费本窗口早期HEAD `29b1eb5428c42c692e031c65b540b132e208c0f5`。独立源码比对确认：ownership与AG5逐字节相同；post-fork算法仅将AG5 CPU-only的sim-start元数据0恢复为实际purpose计数，其他内容一致；ROOT、固定CPU目标和单独SIMULATION capability前导差异显式保留。

新版本同时移入AG5原reviewer字节，保留BA严格wrapper：source绑定、retired prefix/basename/child fallback关闭，不能由AG5本地快捷权限取得新控制权。shared view新增peer tracer/Tgid/retired实例拒绝；external role在两个identity读取之间重新读取当前argv/cwd/exe；root已reap后仍发布descendant ownership。因此初始表中generation owner、继承、退出历史和reviewer接入的源码缺口已解决；不要求BA重复移植或倒退回AG4 reviewer。`BA_V2_AG5_SOURCE_DELTA.patch`只列与AG5的可审查差异。

BA最新source binding仍声明`AG5_INTEGRATED_SOURCE_PREPARED_TARGETED_REGRESSIONS_PENDING`。旧caller下两真实CPU root与12项synthetic-row观测不能覆盖这些新哈希。之前部分父CPU收据缺host PSI，也不能由cgroup低压补成全球准入。AG5 53项不能替代新caller资格。BA工作树的fixture preparer有进行中修改，本窗口只读取已发布commit，不读取/改写其活动build证据或将未提交内容称为PASS。

最小 changed-path 资格由BA在自身精确角色和真实双采样R2通过后执行：

1. 实际生产wait入口retire→同PID新generation stop，父事件前保持PENDING且不得resume；保留synthetic/真实kernel来源的覆盖区分。
2. 当前ticks、错误父事件、TracerPid/Tgid和image generation变更；在任何不受信ptrace/resume前拒绝。
3. 真实child-stop/observer先于parent event的重排；真实GETEVENTMSG最终确认；缺事件2秒超时。
4. STOP时有pending父事件：只清理已证明自身实例，所有自身进程/FLOCK退出；不signal foreign peer。
5. 合法父先reap、child后首次stop的继承正例；多轮helper exec仍完整验证cache/ELF。
6. 当前producer/consumer哈希下，真实双CPU root与已注册的三外部角色；peer retirement、旧generation、陈旧快照、额外argv、source/ELF/path变更负控。未改的纯映射/legacy测试用原收据，不借机重复53项。
7. 如拟同时运行两真实sim，还须事前固定共享host+cgroup/RSS/IO、独立ledger/cap、跨root hard-stop行为。CPU双root不是双sim资源许可；无完整证据保持单worker，不加sim canary。

以上仅接口审查和资格清单，不是集成实现PASS、当前CPU admission或fullsim发射许可。机制冲突/源码科学身份变化交BA处理；AG不写BA/Core/旧raw。
