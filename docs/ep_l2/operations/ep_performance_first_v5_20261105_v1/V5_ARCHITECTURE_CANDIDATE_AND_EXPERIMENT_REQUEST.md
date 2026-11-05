# V5_ARCHITECTURE_CANDIDATE_AND_EXPERIMENT_REQUEST

科学基点：[V4最终authority 2572781d43ac](https://github.com/swayhrl/accel-sim-framework/commit/2572781d43ac02779753a16961b75e0baeffcdf2)。V4六点与V3旧八点接受、两项技术失败保持原状态。本Goal完成研究工程、隔离生产实现、CPU资格和精确申请准备：**新增完整应用启动0、科学预算登记0、共享Native修改0**。CPU工程PASS不等于应用接受。

[精确Source5全集](main/EXACT_SOURCE5_IDENTITIES.json) · [机器可读申请](V5_ARCHITECTURE_CANDIDATE_AND_EXPERIMENT_REQUEST.json) · [Main源与封存复核](main/MAIN_SOURCE_AND_SEALED_ARTIFACT_REVIEW.json) · [最终私有prepare](main/MAIN_FINAL_PRIVATE_PREPARE_CHECKS.json)

## 建议审批顺序与准确范围

| 独立范围 | 精确新测量 | 新启动申请 | Host单点硬上限 | 工程与释放条件 |
|---|---|---:|---|---|
| B：Vector1700 Full-F | 同新Source812：原始F、pressure-epoch优化F | 2 | 各900s；RSS2GiB、AS10GiB、结果128MiB | 基线正式接受、完整排空、真164归档及两次独立恢复后释放优化点 |
| A：FWT小Tag | 同新Source7b4：G32×8 S、WV-off、WV-on | 3 | 各3600s；RSS2GiB、AS10GiB、结果128MiB | 三点仅为这一有限参数族；S是同Source参考，WV-off/on只差cold-filter开关 |
| D：3MM长组 | 原Source78：G64×8 S/WV，加缺失G32×8 WV_REF | 3 | S12h、两WV各14h；RSS10GiB、AS24GiB、结果64MiB | 原接受S_REF=1696618复用；WV_REF是三点之一，不以旧F替代 |
| C：CLEAN端口实现 | 当前不申请完整应用 | 0 | — | 全量计数/reader/rollback/cleanup尚未生产集成 |

推荐先审批**B两点和A三点，共5次**；3MM三点可独立批准、与短组并行，不设跨族完成门。数字是本次各自有限申请，不是EP-L2项目累计次数上限。全局EP cap10沿用，按当次CPU、RAM、cgroup、SSD、真164及其他owner剩余承诺动态准入。

A/B私有Host图已由Main审签：新Source严格283项配置、完整43字段、22 Native与5 Host依赖、boot/mount和当前三scope资源映射。实际五次scoped prepare均在**缺少新的精确科学授权/登记**处HOLD。未安装共享Native，批准后仍需Main最终不可变Spec、授权/预算/路由绑定及当次准入。旧282消费者保持不变。3MM保留282资格并提供精确资源激活补充，Main未来激活时应用该补充；原D封存图未改。

[Main资源图与当前快照](main/resource_binding_v1/MAIN_RESOURCE_BINDING_ACCEPTANCE.json) · [3MM精确资源补充](main/resource_binding_v1/D/MAIN_EXACT_RESOURCE_OVERLAY.json)

## A：低成本W/V候选与停止方向

完整生产候选是**lifetime-cold TVD无效查询过滤**：每slice增加1个sticky ever-installed位，只在成功安装目录项前SET；仅构造初始化为false，reclaim、rollback、WB完成、flush和epoch都不清零。false只是“本实例从未安装”的保守负证据，不是通用空目录oracle。第一次安装后永久回到原查询路径。

本候选保持Payload1168/slice、四Bank/P1、128行WAD/TVD、D512、MSHR128及原完成身份。负证据读取合入既有Tag-miss前端，绕过的是已证不可能命中的CAM请求；不新增CAM、ticket、数据阵列或缓冲。新增位、控制选择与Tag-stage组合路径真实存在；物理关键路径/PPA未闭合，不能描述成已证明的零硬件成本。若组合路径不能容入已声明阶段，须以显式新增流水成本的新Source再审，不能隐藏周期。

新Source：Core **7b4c06678923153006b0aa7d6b8ca9db4770cda9**；ELF **1f978f9b0f57ddf49041ac2cab86bd9c1576666870f700240e826166500bf7ec**；静态库 **ff81389a1bdc59f7cc338cdd0376b7c37f5a656d045b923dc07c4b0dd7816380**。Framework9dd1ee57、vendor f90c430c保持精确身份。源在独立Git管理区，接受Source78及原ELF未改。

真实partition三项CPU、目录边界/所有权、模式拒绝以及三种实际283项parser/constructor资格通过。off样例11次query；clean/dirty样例2次query、9次cold bypass，首安装后停止过滤。它们是有界工程证据，不是完整应用cycles预测。

已有FWT两种512项几何零Victim安装却仍付目录查询，可用于先验证无效服务开销。**不能把该结论外推到G32×8，也不能声称cold门已解决Stencil主要保留问题。** 低Tag Stencil已有大量clean/dirty安装和read response，首次安装后cold门基本无效；新FWT三点用于检验实际收益或否定它。

备用统一CLEAN/WB_COMPLETE近期性回收已做真实production-directory C++周期模型。最初“一周期扫描128项”的免费比较网络假设被撤选；有限版本按1 row读lane、1个64bit比较器，付128扫描周期和独立提交/背压。成本过高且尚未接入前端，**停止当前宏周期候选，不申请长Stencil模型**。Bank-aware landing原实现已存在，不再重复造版本。未来若设计更小bank-local/分层选择器，须另列metadata、端口和延迟成本。

[A生产与负证据](track_a_wv/README.md) · [Main审签与物化](main/approved_a/MATERIALIZE_STDOUT.json)

## B：完整F的压力感知RO准入

主候选为**压力触发、epoch粘滞RO准入**。使用已有indexed Tag结果与维护的Native LineMSHR128压力，新增每slice1个运行控制位及配置选择。实际定时前端观察到压力后SET，之后保持原RO路径，直到完整命令列表epoch排空；当前支持构造初始化，不添加中途回切。纯preview不SET。

保持全epoch只读证书及地址/写冲突、RO/native同址所有权、Tag/descriptor/Payload/sector身份、合法背压、有限端口、完成退役和Core862 completion-CAM修复。触发并不授予所有权；RO query仍须真实1端口、完整1物理周期，不能同tick提前access。不新增CAM、Payload、Bank、目录或队列。比较/SET选择折入既有indexed控制路径，物理mux/关键路径和PPA仍未知。

新Source：Core **812fe1e029b4fb09afaf3d8d25d3f909464cc06c**；ELF **a60600a418e6460e7aaf896b62469be0612046d0f4da34ac8c98da2eed3852e1**；静态库 **a7e9c8ce045710c8f3655aebb82a65628a5a18638036af17fa0ec8c755580d3e**。同一新ELF测F_BASELINE与F_PRESSURE_EPOCH，严格283项仅策略开关不同。旧862 S/W/WV/F只作背景，不充当新Source匹配参考。

现有接受Vector F中每slice query约15624、RO事务3916–3918、merges约11706，detach/duplicate为0；这只支持检查服务开销，**F-WV联合差不等于独立T因果**。人工20请求CPU序列query20→0、121→101周期，仅证明可达路径，不作为应用收益预测。

142TU/8静态库构建、断言开启、真实Tag/allocator/MSHR/lower/response、迟到反序返回、同址排斥、ICNT阻塞、Line128压力、same-tick拒绝与实际Vector证书loader均有新CPU证据。原124项不重跑。完整F兼容Host继承原接受F1700运行器，未硬套W-only适配器；Main已补当前资源图，旧错误图作为历史保留、不选用。

先测同Source原始F，再测优化F。若基线出现非预期语义差异，先诊断并保留未消费优化点；若完整应用不改善则保存负结果并停止无证据扩展。B2查询重叠仅作备用，当前不实现第二版本、不申请阈值/频率扫描或WV额外点。1700MHz仍为服务敏感性诊断，不宣称真实GPU校准。

[B交付](track_b_fullf/README.md) · [Main工程审签](main/approved_b/SOURCE283_CPU_HOST_MAIN_REVIEW.json)

## C：真实生产部分实现与禁止越界

已从bf4独立实现lower enqueue前的READ/COMMIT预留，以及WB completion提交前的packet/credit/tracker一致保留。详细DRAM复用原有限returnq，不赠隐藏Ingress；一次付费completion-CAM上下文后复用结果，显式L2 tick防止较快DRAM重复轮询制造服务。

K1为1条目录row读写路径、K2为2条；每批READ/COMMIT非重叠，K2必须承担第二条目录访问路径和仲裁，不能把Payload四Bank当免费metadata端口。每row-intent逻辑字段至少185bit；计数器/有符号净增量、cap、比较与提交路径均有成本合同，但**生产非零CLEAN计数更新尚未接入**。

四项新生产握手CPU：K1/K2 × simple/real DRAM通过，22次row提交及credit/tracker/packet排空。该12-write序列K1/K2分别同为simple139、real140个L2 tick，K2未显收益；不默认增加端口。旧12组、3185组合及旧parser未重跑。

Main审查发现两处必要set_done副作用位于assert内；新后继Source将调用移出assert，并保存原版本。选定修正版Core **fd1a1875e797e59487d5cb6333b2dc79ca28b736**、ELF **02a4669d3cdd8117acabe04d5e6c7872416d61fc9401be899b191bbcd792f4ce**、库 **f076bc4b7142a1815f870d5aa94bfc591bd61711cf5a72775b66e0dfe13f1bb3**。继承原部分实现的四项CPU证据并补两段实际语句的NDEBUG/UNDEBUG调用保存证明；不宣称全Core可去断言。

仍缺完整frontend/read-pin、非零计数、rollback、epoch cleanup、六producer公平及真实CDC/物理时序。独立Python合同从未被称为完整生产实现。原bf4、第一部分实现bf072及修正版fd1分别记录Source5，**当前C不申请科学点**；未来全路径集成后需新Source同Source cap128参考，再独立审cap64/0。

[C边界与成本](track_c_clean/README.md) · [always-call修正](track_c_clean/always_call_fix_v2/DELIVERY_MANIFEST.json)

## D：覆盖、3MM和postrun效率

现有台账为**103条接受实验记录、8个精确输入、8个程序、3组Source5**，不是103个workload。冻结身份、模式、历史成本及缺口分层保存；短FWT/Vector优先，transpose可作零结果背景。Scan当前相关WV资格缺失且长，Conv的Source/模式不同，不为填次数加入扫描或跨ELF匹配。

3MM保留旧未批准草案request/cohort ID，从未登记或消费，并非重发已关闭V4范围。10条命令、3kernel、1813512192 instructions、3072 CTA。S_REF=1696618是精确Source78接受参考；缺失WV_REF由三点中独立1slot测量。WV几何收益在该新参考接受前保持UNKNOWN。RAM估5GiB（旧S约3.53GiB）、S历史约7.11h；WV14h只是工程硬上限，不是假装已测时长。允许长组独立并行，但不阻塞短组。

严格postrun检查器只做已消费、自然完成同UUID的Source/Spec/ELF、launch capsule、PID世代、syscall、raw身份与既有Main审过insert-only快照重核；不覆盖peer Native、不改全局守卫、不签新科学许可。既有闭合Stencil离线核查通过，当前未审新增路由仍HOLD。它是私有工程候选，未部署到共享入口；Main未来只需具体合法插入审查，不能为了元数据再跑原模型。

[D精确3MM申请](track_d_workloads/3MM_EXACT_REQUEST_V5.json) · [候选表](track_d_workloads/SHORT_AND_LONG_EXPERIMENT_CANDIDATES.json) · [postrun候选](track_d_workloads/POSTRUN_V4_REVIEW_REUSE_POLICY.json)

## Main结论与科学边界

优先验证B1能否降低完整F的真实服务成本，以及A的低成本过滤能否在小Tag FWT产生完整应用绝对收益；先用新Source匹配基线获得正、负或零结果。3MM补跨负载Tag几何适用性。C继续补真实硬件更新路径，当前不能混进Source78/862或获得性能资格。

新Source不拼旧ELF，物理PPA/组合时序、应用NI及B0/M0a边界如实保留；不把额外NI或完整综合作为所有候选共同前置门。所有未来接受都要求完整命令序列、真实终态、真164全SHA和两次独立Native恢复。Source KEEP；不动旧台账、不退款、不重试，不恢复论文写作。
