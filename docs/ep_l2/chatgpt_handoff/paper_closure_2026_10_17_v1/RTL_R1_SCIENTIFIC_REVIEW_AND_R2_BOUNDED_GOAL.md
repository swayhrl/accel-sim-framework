# EP-L2 RTL R1审稿复核与有界R2 Goal（2026-10-18）

## 0. 决策边界与已核验状态

**科学结论：R1是真实、可复现的原型合成/STA负面证据，不是已闭合硬件PPA，也不能直接与冻结SIM应用性能结合计算净收益。** 该文件是向原Lane2窗口发出的可选**新**短Goal合同，不能因GitHub发布而认为任务已启动。Lane5唯一正式应用控制器保持现有RUNNING/队列/registry，不许重启、reset或改写在途run key。

依据：
- Lane2 Framework `09de19579c0708f6542dfd65e1f3aae8a9a8b841` / `docs/ep_l2/review_packs/RTL_COST_OPEN_FLOW_V1_r1/`；RTL源码 `25097f4b6dca4ac3fcc2d3cf615fb97c78c5bf71`；有限SIM规格Core `9bd30ed913c5058b5d952fbeb2e67cb5e4644b3f`。
- Nangate typical 1.1V/25C，同Liberty/SDC/fast-clean映射、0.883392226ns目标：B16面积2069971.036 WNS−13.614565ns；S64面积2121045.696 WNS−13.612103ns；Unified面积2525345.746 WNS−36.605915ns。Unified/B16的控制+访问标准单元面积比 +21.9991%，是**未优化部分RTL相对差**，不代表完整L2。B16/S64/Unified均未达时序，2ns探索也未闭合。
- `PER_MODULE_AREA.csv`显示大规模逐槽metadata/译码、多扇出和free-slot全局组合搜索；Unif最差路径跨metadata generation→tag handle，原生SIM每周期frontend与R1 RTL read II4/write II3、静态copy相位、WB return和仲裁策略不同。部分baseline静态tag-map/owner可在证明不变式后硬连线，不能让B16背上无须的动态控制。
- 四个292×1024bit SRAM边界=146KiB每slice，宏面积/延迟未知；传统Tag/LRU/MSHR/NoC等也排除。RTL pin同沿race旧红新绿、字节参考和有界generation检查真实完成，保留全部R1证据与未解决边界。
- Lane5 Framework `69b0d118ae5295926404522c90fff2b0e5b5b2c1`：当前新binary fb674...的Conv B16=292932、S64=293258、U_CAP16=292544，同源Unified待接受；FWT原binary同源OFF=493189和ALL_DATA=232001先后独立接受，可后验形成2.125805×操作性参考，不能叫EP-L2 speedup。Lane5 FWT/S64在途，原R3队列已含Conv/FWT Unified。不可打断。

## 1. 新Goal：EPL2_RTL_COST_TIMING_REFINEMENT_R2_BOUNDED

**Owner** 原Lane2窗口，独立成本RTL工作树/分支；这是R1结束后的**新**R2短Goal，不是重启旧Goal。目标：在有限时间内验证可降低成本的真实结构变体和缩短最差路径，形成可用于作者后续DC的明确候选。不追求全L2/后布局，不修改正式SIM或Lane5运行，也不改变物理预算。允许普通EDA问题自修；触及微架构服务/周期差异时提交给Lane1讨论，**不自动授权**改SIM或重新进行全应用。

工作步骤按以下因果顺序：

1. **以R1报告诊断而不是盲目重新综合。** 从同source/SDC/lib关键路径、fanout及模块面积找到最低成本最高收益的2–3个修改点；确认哪一段是当前全1168槽搜寻、WAD CAM、metadata generation进位、req_ready/req_fire fanout和bank-compatible landing选择。先给简短面积/时序责任账。
2. **等功能优化三模式。** 优先将逻辑上等价的全槽first-free查找改为分层/分bank的有界并行优先编码与局部译码/注册扇出；优化共享increment/select/write-enable路径，减少每word组合控制复制。若要用free-list或加流水，必须证明取槽/仲裁/容量/回滚/前进性不变式，并将任何服务顺序、独立bank并发、额外cycle或II变化作为**新版本明确差异**，不能拿旧SIM结果配新RTL。相同source适用的优化同等施加B16、S64、Unified；固定静态Tag handle/owner能硬连线仅在书面证明不变式后对B16/S64分别实现，防止人为劣化强静态基线。GEN宽度、WAD capacity、数据byte enables、旧数据版本、同沿pin race保护都不得偷减。
3. **真实测试先行。** 三模式用Lane3原10场景+真实RTL输出做byte-mask/line-snapshot和角色/请求/引脚/不同释放事件比对；复用R1的old-red/new-green pin、合法相邻grant、bank3末行、GEN3耗尽、WAD129th/stale event和backpressure，且记录未覆盖dynamic rollback/whole-app numerical scope。规模参数保持1024 Tags/1168 physical/128 WAD、4 banks×292、128B line;缩小容量只作测试，不能提交小规模成本。
4. **统一真实开源综合和STA。** B16/S64/Unified使用同一个Liberty、PVT、SDC、IO loading、ABC effort；存储宏边界、外部Tag/MSHR缺项单列，保留真实raw/netlist/路径、面积按模块对比；0.883ns和2ns两档都运行。如果优化后三者仍不闭合，原样报告WNS/TNS/fanout和可达流水需求，禁止用虚假false/multicycle、降低U时钟、缩窄slot数或将metadata不计费来“闭合”。
5. **SIM/RTL等价性和DC交付**。用一个表逐项说明frontend read/write II、copy相位、response return、bank arbitration、dynamic landing、SRAM read latency、native approval、WAD set_done相对于模拟器的状态。评估必要流水变化，若需要提出只提供Lane1的独立建议，不自行推动性能归因或重启Lane5。生成/核验同一改版RTL的`run_dc.tcl`、filelist、SDC（PVT/units显式）、黑盒memory接口和目标库选择；没有真实SRAM宏、综合未闭合时不可宣称whole-slice PPA。
6. **交付时限**：首个科学有效的优化前/后结果或清楚的阻塞分类在4小时内发布；最多6小时的有界工程探索。超时无闭合也要交付最优已验证候选、关键路径残差和下一步是否值得继续的判断，勿陷入无限迭代/大规模工具重构。

最终发布`RTL_COST_R2_RECEIPT`、三模式真实面积/critical-path表、SOURCE/RTL/SDC/lib/tool/映射身份、功能coverage、严格SRAM/逻辑成本账、SIM/RTL_TIMING_DELTA、DC handoff；在原Lane2和独立RTL分支commit/push、远端回读。旧R1所有raw/patch/log不得覆盖或删除，中央资源lease、12GiB aggregate output和workspace48GiB/Share40GiB/RAM64GiB保护不变。运行时若资源不足则fail-closed，不请求其他Lane让路。**不新起正式应用，不将未定时完成版本性能作为投稿实测。**

## 2. Lane5与Lane6后续处理（不需给运行中的Lane5重发Goal）

- Lane5 R3原队列已登记 `S005 FWT/S64`(运行中)、`S001 Conv/Unified`、`S006 FWT/U_CAP16`、`S004 FWT/Unified`，并有其它诊断点。保留PID/lease/原计数，等待既有队列推进；磁盘预留只给单槽时，不突破容量或删除结果。优先闭合Conv/FWT四模式；若deadline/12GiB触顶，安全STOP并交接，不自动再分配额度。
- 所有单点按本release同source/bin/trace的B16 OFF复用，不拼旧2309的U结果。Conv三点示例：S64/B16=0.998888×，U_CAP16/B16=1.001326×；Unified缺项时不能宣称弹性容量贡献。FWT ALL_DATA=232001 与后接受的同source B16 OFF493189构成可报告的`2.125805×`操作性访存机会，但该数据点属于独立参考，先核实官方group receipt，不可称EP-L2实际加速。
- Lane6可在EN-v10母稿上滚动整理已接受的单点及R1 RTL的`UNOPTIMIZED_TIMING_UNCLOSED`负面成本现状；未取得对应RTL R2或DC证据前，禁止将22%写成定稿全L2面积，亦不把新Ideal当作EP加速。EN-v10是用户此聊天生成的文件，**未在远端Lane6可取**，须明确上传/同步后再替换远端EN-v8；不能暗自从EN-v8重写并冒称EN-v10。

## 3. 论文贡献裁决门槛

同源Conv/FWT四模式若显示Unified≥U_CAP16且优于S64，则才支持“在该有限系统条件下动态容量复用具有增益”；若U_CAP16≈Unified，主张应该收敛为原位writeback/slot ownership而非动态WB容量优越性；若S64≈或优于Unified，则不能主张相比强静态具有性能优势。上述只是后续有条件解释，必须叠加真实银行服务、复制、WAD峰值/拒绝和成本，不以单点方向取代完整证据。开源RTL R1的功能测试和真实负WNS值得披露，但尚不能在未知SRAM/接口成本和未匹配SIM吞吐下作为净收益证据。
