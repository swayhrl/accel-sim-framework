# Future-only memory .95 / 10GiB：候选未安装

## 范围与结果

六个独立source：future_memory.py统一资源算术/绑定，memory_frontend.py双路外层，memory_owner.py现有私有对象接入，memory_extra_strict.py总严格器，joint_padding_strict.py及joint_io_strict.py透明版本化联合回放。

97项CPU检查PASS：noFlag冻结native前缀22，padding冻结native前缀35，owner范围/切换22，组件10，真实入口候选8。冻结native loop确实运行至mockPopen/PID/runtimeFalse；authority、lease、headroom、proc及原performance proof为明确CPU fixture，不是实际模型/数值科学通过。旧padding proof完全等价回放和明确旧.88拒/新.95通过案例都已验证。21项原sourcepins未变，未安装、未登记、未发信号。

## 有效新资源规则

budget=.95*min(max(0,MemAvailable−10GiB),max(0,cgroup_effective_headroom−10GiB))；无限cgroup仅用host项。源provider生成的cgroup净余量/clean-inactive-file credit原样沿用，不添加credit。own/live/claim/peer/candidate增长完整保留，不下调canonical forecast/RSS/AS硬限、disk/CPU/pressure或write ceiling。所有fresh准备、pair前后第二门一致；freshFalse直接返回原provider对象，不改变健康worker行为。

新memory证明保存完整base resource快照，核对未削减的peer+own增长、旧source/policy SHA、旧压力与磁盘边界、新budget。三份INTENT/LAUNCH/PID记录相同additional_future_memory_admission_binding，并绑定FUTURE_MEMORY_ADMISSION_SNAPSHOT.json。原policy8GiB/.88和21pins文件本身不变。

## Canary隔离与广放

ACTIVE_MEMORY.template.json初始status为HOLD、scope_mode=FINITE_CANARY、allowlist为空。Main选择仍未spent且可达E池的一个短点后填唯一cohort；代码不硬编码scalarProd/P0或已accepted身份。初始owner默认res.resources及E预算仍旧值，只在原B选中该canary或原B物理HOLD时，对同传入池中canary再用新policy跑captured完整B；其它原可行decision直接原样返回。它不会从E过滤池外偷加canary，不越protected_R，不为部署抢占自然可启动的Lava。

native memory outer对archive、未allow身份直接调用source-pinned原IO.main。缺失/损坏memory cfg也回到旧IO；该路径若自然完成，只算旧链结果，不能算memory canary通过。真正的memory canary必须实际观察新三binding+snapshot+strict+164archive/native恢复。

实际canary完全闭合后，Main可用新scope cfg与q operational record显式扩大范围，再调用memory_owner.update_scope_in_owner(new_cfg,owner_assert)。允许列表为单调扩展，保留已spent canary作为历史授权条目；q和INTENT仍保证它永不再启动。scope_mode=ALL_UNSPENT_FUTURE时owner provider才全局使用新budget；update只rebase aging.state.previous_C，protected_R及pending completion-release tokens不变，policy上涨不计自然释放。B one-shot旧.88融资应在广放前按Main计划restore，durable token保留。a650 P0偏好按当前callable捕获，保留其内部B5；不替换CPU/FrameGuard/outer chooser。

## 为什么需要版本化联合strict

旧padding_extra_strict硬断言policy8/.88且要求该budget通过；旧IO extra的padding分支又要求旧B5 PASS标签。因此不能把新.95大点的证据伪装为旧B5 PASS。

joint_padding_strict完整复制旧身份、certificate/source、generation、discount、fullcandidate/topup与foreign/claim增长回放；仅预算部分增加显式memory proof：仍核对旧.88算术和旧pass真假，再核验新.95/10及同一未削减增长。joint_io_strict完整保留原IO三绑定、snapshot、source/QA/readback/config检查，仅改其padding依赖为新联合schema。JOINT_VALIDATOR_EXACT_DIFF.json列精确old/new差异与old sourceSHA。

无memorybinding的历史receipt继续整个旧consumer链。新noFlag执行原完整performance strict AND未改IO strict AND memory；新padding执行原完整performance strict AND新联合padding/memory AND完整保留IO校验的版本化联合replay。输出FUTURE_MEMORY_PADDING_EXTRA_STRICT.json、FUTURE_MEMORY_IO_EXTRA_STRICT.json、FUTURE_MEMORY_EXTRA_STRICT.json，明确old_B5_strict_PASS_claimed=false；从不制造旧PASS标签。

## Main审核/发布/实际资格接口

1. 校验MANIFEST/97QA/6source及expected_pins；copy候选源和QA到R/control/operational_amendments/future_memory_admission_v1，原源不改。Main执行真实远端发布readback，再填写PUBLICATION_READBACK.template.json的verified/commit并计算SHA。
2. 生成ACTIVE_MEMORY.json，填六source路径/SHA、QA SHA、真实readback SHA、唯一canary、ACTIVE_FUTURE_ONLY；对应q.additional_operational_overlays[FUTURE_ONLY_MEMORY_ADMISSION_095_FLOOR10_V1]须等于future_memory.record(cfg)并加status ACTIVE。仅operational metadata，不增加科学预算/不重置spent。
3. Main唯一操作现owner：memory_owner.apply_in_owner(config_path)。它动态捕获aging.original(当前a650)，在既有aging.lock下安装res.resources/generic B/consumer.load，保存对象于__main__.DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1；返回JSON标量ACK。当前res.choose_dispatch/CPU/FrameGuard/worker/pool/claims不变。
4. NATIVE_ENTRY_CANDIDATE.sh只替换当前两处IO frontend路径，exact inverse还原NATIVE_ENTRY_BEFORE.bin；Main必须在apply前确认当前entry SHA仍等于ROUTE_CPU_QUALIFICATION.before_sha256。EP及其它DTC路由字节保留。新front保留padding opt-in argv，模型argv不增加flag。
5. 小真实canary必须走完整原科学strict+新sidecar+COPY真164/native2128恢复，再决定广放。未实际完成前不能把CPU PASS说成memory策略真实跑通。若natural Lava先fit照常运行，不为canary/部署暂停健康模型。
6. restore_dispatch_in_owner(owner_assert)只在当前res.resources/aging.original仍是本wrapper时恢复精确旧callable，保留新generation的consumer strict用于收尾；不signal模型。

所有模板中的QA/readback配置在CPU中均为显式模拟，不是生产授权文件。目录CPU_NATIVEPREFIX_*、CPU_MEMORY_OWNER_*、CPU_MEMORY_ROUTE_*仅fixture，不进发布pack。
