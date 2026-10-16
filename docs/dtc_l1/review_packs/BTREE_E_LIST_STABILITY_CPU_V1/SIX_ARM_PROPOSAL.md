# 同一新Btree输入：最多六臂预登记建议

状态：**PROPOSED_NOT_REGISTERED_NOT_RUN**。本目录配置快照仅供审阅，未生成attempt、UUID运行清单、launcher或调度请求。每臂完整effective config、全部共同项/差异、输入范围、来源spec/config/Core/binary SHA见SIX_ARM_PROPOSAL.json；实际input bundle以INPUT_IDENTITY.json为唯一绑定。

| arm | 实现 | 数据/逻辑资源 | 有效PIB | 有效MSHR | 服务 |
|---|---|---|---:|---|---|
| B16-N | 原traditional Core | N型32set×4way×128B=16KiB | 8 | 32 | 原常规服务；finite指标UNAVAILABLE |
| TC80-N | 原traditional Core | N型32set×20way×128B=80KiB | 8 | 32 | 原常规服务；finite指标UNAVAILABLE |
| TRAD96/C+ | 原traditional Core | N型32set×24way×128B=96KiB | 256 | 512 | 原常规服务；finite指标UNAVAILABLE |
| IO256 | 原finite Core | 32×4逻辑tag，640×128B物理pool=80KiB | 256 | 常规MSHR不参与cacheable load路径 | 已资格化有限服务 |
| OO128 | 原finite Core | 同一逻辑tag/pool，13bit RefCount | 128 | 同上 | 已资格化有限服务 |
| IO128 | 原finite Core | 同一逻辑tag/pool | 128 | 同上 | 已资格化有限服务；与OO128同深度比较 |

传统cache配置字面MSHR512由PAPER_BASE的shader.h::init按DTC mshr参数覆盖，所以有效值为32/32/512；没有把字面512误当所有臂资源相同。finite的常规cache配置和inactive选项仍完整披露，不将未使用字段称为新增数据容量。IO/OO保留tag4 bank、1/bank/cycle、4总/cycle，allocation4/cycle、32线程coalescer；create/inject/refill/retire各1/cycle，collection4 sector/cycle。保留原ordinary store ACK路径，没有新side path。IO/OO同128深度不表示等总metadata/面积。

六臂共同64×1 SM，clock `1410.0:1410.0:1410.0:850.0`，原ICNT/L2/DRAM完整配置及shared-bank/sector/line规则不变；差异仅为明确设计参数。**统一下行cap32768**在任何新性能前固定；两原Core均以OPT_UINT32接收并要求cap>0，32768合法，且原Btree finite/TRAD96固定spec已有此值。B16-N/TC80-N的新臂显式覆盖为共同32768；不改其旧8192历史attempt。合法性不代表宣称cap永不绑定。

两原设计族使用不同合法Core/binary：traditional `6582b9d171330d88b17e8d5294c97704229e3823` / binary `4fcac62cd7bdccc5a49cc77950ffc45c60d5fce7c4ee44bba877e1fef2d07ef9`；finite `6fba0136f8465b59fe5858a950fa39efb265f654` / binary `fe2d2737ebaed01680ebfc2346f727306c8db58ee0ca20b1e1f038056e99833b`；共同build framework `18a68dcccd795f1b6cda75504e9450d00c9cee02`。不创建新binary。

进入下一阶段的最小范围是科学审阅确认G0-G3后，由原A唯一authority独立接收同一bundle、完整两kernel/444467849活动线程指令，生成新lineage和每臂UUID。A按原任务资源/配额安排新增臂，原六job不暂停重启；没有资源则等待。不得覆盖44行、解除旧Hotspot HOLD、复活旧B/C/D或创建第二persistent launcher。

每臂须自然terminal、身份/输出SHA及完整有序kernel/ROI检查、资源credit/reference/physical/PIB/lower/回填/收集/退休/普通路径排空审计。全部新输入臂完整匹配后，再报告新B16-N/TC80-N/C+对新IO/OO及IO128/OO128比值；传统有限服务统计缺失保留UNAVAILABLE。新旧输入不可交叉取比、代入原GM12或声称native/等面积。任何科学失败、退化或排序反转保留并STOP扩大，不调cap/clock、扫参数或另造解释。完成最多六臂即停止。
