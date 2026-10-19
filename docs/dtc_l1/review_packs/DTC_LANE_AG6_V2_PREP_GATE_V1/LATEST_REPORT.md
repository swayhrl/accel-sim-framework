# AG6 V2 preparation review

**准备审查完成；两份BASE均为`PASS_REUSE_EXACT_V2_AG6_FROZEN_BUILD_ONLY`；BA集成/实际发射资格仍须独立闭合。本AG窗口启动simulator 0、CPU fixture/build/test 0、新UUID 0。**

固定协调提交`f81ca1c5054a78ed2c09f316bac0501c3bbc9322`三份V2文件已完整读取并保留原字节。独立分支`hrl/iscas2027-dtc-ag6-v2-prep-gate-174-v1`，原174独立输出`/workspace/dtc-lane-ag6-v2-prep-gate-174-v1/`。没有重启AG4/AG5/旧六点AG6，没有写BA worktree、Core、trace、旧raw或迁移目录。

| BASE | ORIGINAL_FULL_STRICT | HISTORICAL_EXECUTOR_SCOPE | NEW_COHORT_REUSE_ELIGIBILITY |
|---|---|---|---|
| GEMM，AG3，1,071,405 cycles | 完整1 kernel、4 commands、1,024 CTA、739,246,080 instructions；原始strict与只读重解析一致 | AG3旧observer/继承/PID范围较弱，不能追认为AG5资格；child ticks未记录，保持UNAVAILABLE | 限原精确tuple PASS；2个真实parent event、3个不同PID/exec，完整loader和exit0闭合，未见记录父图矛盾 |
| Gaussian，AG4，3,278,356 cycles | 完整510 kernels、513 commands、65,790 CTA、283,685,120 instructions；原始strict与只读重解析一致 | 原prelaunch CPU gate不足与cohort STOP永久保留；synthetic AST负控不是实测PID复用 | 限原精确tuple PASS；1020个父PID/ticks匹配的child proof、1021个不同PID/exec、33778帧，完整closure与exit0总体一致 |

两次独立裁决各20项identity/原结果/观测一致性检查通过，详见`BASE_REUSE_GEMM.json`、`BASE_REUSE_GAUSSIAN.json`。这不是把旧executor改写成合格，也不是当前BA launch PASS。Gaussian旧cohort性能声明不合格、优化结果0的终态不改；本次只按V2新增run-specific comparator复用决定。

全部270 effective options逐项匹配，全部每kernel公共指标和traffic精确校准；12个实际ELF/lib/loader/cache/helper文件SHA及身份、702项原源SHA、511原trace成员stat与已发布SHA来源一致。没有重复扫描约1.99GB trace body。48个用到的metadata/receipt文件与原不可变Git blob一致，两run index链闭合。旧maps payload没有逐份重新hash；事件digest逐项join原immutable index，覆盖界限明列，未据此声称新增逐resume generation或Linux强制PID复用观测。

GEMM原历史673个资源样本，9 WARN、无STOP；host IO最大28.36%为运行期间波动，不伪称全程≤25。Gaussian147样本，146 authority PASS和1次真实PENDING，最终pending清空。两次原成对准入分别10.204和10.218秒，root PID/ticks记录无矛盾。当前新R2/role准入未进行，也未由这些历史收据授予。

AG5/BA初始审查给出13份源码快照；并行期间BA消费早期交接，收口GitHub HEAD更新为`25cf0ab03d6cc68f964eeb03f42347452ac23abb`。新增11份已发布源码/注册快照确认：ownership与AG5字节相同，post-fork guard算法相同，仅namespace/启动政策和真实sim-start元数据有明确差异；canonical generation owner、image stamp、继承快照及退出历史均已接入。BA shared-role还加强了新鲜度/retired实例校验。**源码集成review PASS，运行资格仍pending**；不能把53项旧CPU结果移作新共享caller PASS。详见`AG5_BA_INTERFACE_REVIEW.md`、`BA_FINAL_SOURCE_REVIEW.json`。

四点提案固定`AE_GEMM → AE_Gaussian → AD_GEMM → AD_Gaussian`，只有一个开关各自从0变1；两个BASE导入，新的4次UUID只由BA登记。提案为**non-executable**，没有dispatcher、启动命令或新UUID。本包的存在并不意味着fullsim已启动。

BA下一步：先闭合集成changed-path、当前精确角色/全项目host+cgroup R2，分别冻结实际输入/ELF/lib/loader/cache/options和四点UUID/strict/资源/机制指标，commit/push/fetch-back后才能发射。默认单worker；双sim须事前完整qualification，AG6+BA合计≤2。缺任一条件即HOLD，不补格、不第五次、不拿BA32填AG6预算；不能自动启用六点替代。

两发现输入、ON-only和UNAVAILABLE、负结果及原selection政策不变。不改稿件、DC、原44行/GM12、K1、AC/AC2/AF、AE+AD组合或其它输入。提交到BA的Git交接见`BA_CONSUMER_HANDOFF.md`；精确publication readback单列，不用移动HEAD当机制基底。
