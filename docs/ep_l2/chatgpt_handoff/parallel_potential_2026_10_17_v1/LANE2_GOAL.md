# Lane 2｜等预算静态对照、局部WB配额消融与有限Bank吞吐

合同：EPL2_PARALLEL_POTENTIAL_20261017_V1。本文与同目录公共合同、矩阵和Lane5中央调度规则共同执行；不是旧TVD Goal的重启指令。

## 0. 目标、已有工作与执行边界

用户已授权并行检查EP-L2、L2资源及上下游的有效区间，正、负结果都需要证据。本Lane新增工作的优先次序为S64、U_CAP16、有限P2；不等待TVD/RO完成，不以先出现明显应用加速为开发前提。

保留原hrl/ep-l2-ft20261016-lane2-v1及其TVD候选、原common-delta分支、旧失败/通过证据和全部结果。先核查本地已有进程/worktree/任务，复用属于本合同且已在执行的工作，不重启、不覆盖现有候选。新增三个模块使用与Lane4及正式运行分离的Core worktree，从当前正式Core 7b8e6ac70b8fe0f1bd37efca11acb5284938825d建立任务分支；建议hrl/ep-l2-potential20261017-lane2-v1。记录真正base、路径、分支和dirty状态，不假定挂载点。

生产Framework锚点为9bd17f9db3e8cbbc3fdad7283d1e292918546fd5。准确Framework工具/文档分支由本Lane登记，源码与运行身份分开。不要整分支merge旧TVD代码到新WB-only主线，不回退A1跨周期victim绑定、B1/sector修正和当前physical-cycle逻辑。

本Lane负责实现、源绑定定向、patch、manifest和向Lane1交付。全部完整应用由Lane5唯一启动和科学接收；本Lane不能自开S64/U_CAP16/P2应用。全合同最多72个full-application starts、50个seed cells、至多24小时（绝对期限见总合同），统一最多4个长期sim/8 CPU/32 GiB；这不是每Lane配额。既有R19 D2/L25保持原预算、deadline、lease和进程，不能重新发起或混入本合同计数。共享实际宿主资源和中央registry，既有资源保护继续适用。

## 1. 固定共同资源与默认行为

共同：64 slices、32 channels、每slice 1024 Tags、128B line/4个32B sectors、1168 payload slots、4 banks×292 rows、WAD128、descriptor512、Line-MSHR128、per-address32。普通bank服务P1为每bank每物理GPU周期至多1次实际line-sized读或写。共同128B copy latch在pool之外，两模式均计账；L1/DRAM等使用矩阵指定的系统条件，模块不得顺手改变。

所有新增行为默认关闭；P1为默认服务数。具体CLI名称由Lane1接口表统一，但语义值和非法组合必须明确。默认配置在新binary上保持当前B16/U_WB16行为；增加布局或服务参数不能隐式改变总容量。新模式、分区、WB local token、bank服务倍数、source/binary/config身份全部进入feature vector和run-key。

## 2. S64：扩大WB配额、总容量不变的静态重划分

固定唯一首发S64布局：

| 角色 | 全局ID范围（含端点） | 总项数/slice | 每bank项数 |
|---|---|---:|---:|
| Resident | 0..1023 | 1024 | 256 |
| Bypass | 1024..1103 | 80 | 20 |
| WB staging | 1104..1167 | 64 | 16 |

总数1168、4×292不变，bank=payload_id%4。Resident Tag映射保持现有静态映射。Static WB可从WB角色范围选择合法空槽，不额外要求与victim同bank；三阶段真实数据工作仍为resident source read、staging write、staging-to-lower read，各自经过同一个受限bank服务。保持已有copy两阶段和latch协议，不因P2或新布局而悄悄把两阶段合成一次操作。

禁止直接将现有m_ep_l2_wbuf_entries设成64：现构造为1152+wbuf，直接改会变1216项；原验证器也只接受8/16。必须把固定physical budget和static角色范围正确分离，保留历史B16/B8的原语义。任何通用range/helper均需检查bypass ID转译、WB起始边界、free/used/ownership统计和release；不能只修改preview_free然后让其他路径仍用1152作为WB起点。

S64是compute实验中的更强静态竞争参考，其bypass只剩80项；不得宣传成保留128项bypass能力。选择64的依据是现有U最高staged峰值55，属于事先明确的覆盖需求诊断，不保证S64一定非绑定。应用后由Lane5检查实际WBUF-full、等待、峰值、useful service和cycles；本Lane不得先因预期结果加入32/96/128扫参。

必需定向：1023/1024、1103/1104、1167/1168边界；四bank角色计数；64槽占满时第65个WB拒绝且无部分提交；释放后恢复；WAD128保持；同bank/跨bankcopy；lower full重试；所有payload、WB、WAD和request恰好一次退尽。实际生产路径须观测到staging从16以上增长，不能只测试独立数组。

## 3. U_CAP16：只限制本地WB数据并发，原位转权仍保留

U_CAP16沿用U_WB16的1168项动态payload组织、原位dirty转权、合法resident landing、相同bank class、相同仲裁/ownership及lower_accepted释放边界，增加全局每slice本地WB数据token上限16。WAD仍128；不得把WAD改成16，不得按set_done释放local token。

token生命周期必须覆盖真实pending/retry：

1. dirty replacement所有precheck通过后，在可能跨周期的pending状态形成前原子预留一个token；同一请求重试复用原token，不重复获取。
2. pending持有的token记为reserved；dirty ownership/packet实际commit时reserved转live，总占用不变。
3. native提交前合法rollback/cancel释放reserved token恰好一次；已提交WB不能按普通rollback清除。
4. lower_accepted真正交接数据后释放live token恰好一次。WAD继续到set_done；set_done不再次释放local token。
5. 始终reserved+live<=16，日志分别记录reserved/live峰值、quota refusal、retries、rollback、lower accept和最终0/0。

token是诊断容量门控，不新增免费data array，不移动dirty bytes，不改变WB到下游的承载。原位bank位置、替换时序等仍与Static不同。因此B16→U_CAP16是“相同本地WB配额下原位组织/copy去除这一组变化”的消融，不称为严格pure-copy性能贡献；U_CAP16→U_WB16才隔离放开该local quota的边际作用。

必需定向：第17笔dirty拒绝；16个reserved/live混合；bank denial多周期重试不多占token；A1受影响victim绑定重试；native失败rollback；lower full；WB先lower accept、后set_done时token可复用而WAD仍有效；同地址hazard保持；完成和epoch drain后token/WB/WAD/读引用均闭合。

## 4. P2：有限的两次真实bank服务

固定P2=每bank每物理GPU周期最多2次实际line-sized操作，bank数、映射和1168容量不变。对B16和U_WB16共同施加，作为额外服务资源的系统配置对照，不能宣称零成本机制。P2不等于把四bank改成八bank，不等于只把统计分母乘2，也不能仅修改busy判断后让同一请求重复完成。

仲裁中必须真实发放并消费至多2个不同合法操作；第三个竞争操作拒绝/等待，跨周期grant/retry身份保持，store/copy/fill/WB readout的真实状态更新只发生一次。仍使用gpu_sim_cycle+gpu_tot_sim_cycle识别物理周期；native Tag timestamp/memcpy offset或额外函数调用不能刷新bank预算。保持旧P1回归，不删除公平、generation、ownership或clock断言。

最低定向：同bank同周期两读、两写、读写；第三个拒绝；不同bank独立预算；重试/cancel不多grant；实际fill、响应read、resident write、copy和WB readout竞争；P1旧控制一致；physical-cycle内多次调用和native时间变化不会超发。报告实际bank grants、逻辑ops、重复完成检查、等待和每bank每cycle峰值。端口/阵列/仲裁额外成本记为待物理核算，不能把P2值写成已实现硬件频率。

## 5. 滚动交付，避免等待整包

S64先可用即发布，再交U_CAP16，再交P2；实现可并行准备，不要求一次大合并。每模块交Lane1最小patch及以下内容：

- 准确base/parent/core commit、变更文件与blob/sha256、CLI/模式语义和允许/拒绝组合。
- 受影响生产路径与资源账；默认OFF等价范围、真实directed旧/新结果、compiler/binary身份及未运行项。
- 编译/应用测试入口、数据版本/ownership/token/port/rollback/drain断言、counter字段定义及分母。
- 建议应用点只引用中央矩阵；列明未运行、禁止自行代填结果。

Lane1在每个模块闭合后可以滚动发布独立准确release，Lane5按受影响scope资格后立即排应用，不等剩余模块、TVD、RO或整个Ideal套件。多个模块触碰gpu-cache.h/.cc时先给准确patch/接口冲突说明，不并发编辑同一生产worktree。发布仅限自己任务分支、正常非force push并远端回读；不得修改Lane5 ledger/中央接受证据。

## 6. 结束条件及科研解释

结束为三个可接入模块及对应有界生产定向/manifest交付，或某模块有明确源级正确性阻塞并留下可复现证据。普通编译、fixture、配置覆盖或包装问题自行修复继续；没有应用收益不是工程失败，也不取消剩余模式。需要扩大总资源、改变ordering/trace/原子scope、靠删除assert过关、超合同或资源不足时，只停止受影响部分，继续其它可交付工作。

不把token/generation的软件字段sizeof当硬件面积。S64用于问静态重划分能否替代动态容量；U_CAP16用于分离local quota边际；P2用于问bank服务是否限制收益转换。三者都必须保留正、零、负结果，并与当下合法相同系统条件的B/U比较。

## 固定源码参考

- https://github.com/swayhrl/gpgpu-sim/blob/7b8e6ac70b8fe0f1bd37efca11acb5284938825d/src/gpgpu-sim/gpu-cache.h
- https://github.com/swayhrl/gpgpu-sim/blob/7b8e6ac70b8fe0f1bd37efca11acb5284938825d/src/gpgpu-sim/ep-l2-ft-cache.inc
- https://github.com/swayhrl/accel-sim-framework/blob/1db2ff7a1aa2eb3b221e6184b9abf149c7e178de/docs/ep_l2/chatgpt_handoff/fast_track_2026_10_16_v1/COMMON_CONTRACT.md
