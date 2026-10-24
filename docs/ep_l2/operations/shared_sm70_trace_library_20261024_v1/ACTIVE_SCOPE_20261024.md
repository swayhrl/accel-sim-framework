# 2026-10-24追加授权与完整工作范围

用户已明确授权立即并行补齐全部workload资产缺少的4080 trace，安装隔离依赖，并验证解决模拟器语义兼容性；可处理I/O与存储安排，164已有经验证资产时可安全释放本Lane在174-new的副本。原SM70公共资产库Goal全部要求继续有效，不以单Vector试点或较小子集替代。

## 并行执行

- EP-MAIN：SM70全SHA、四归档核查、去重COPY_ONLY、公共入口和恢复验收。
- 有限4080资产子任务：Rodinia3.1/2.0-ft、Parboil的源码/输入/构建，以及整体GPU队列。
- 有限CUDA/PolyBench子任务：源码完整分母、版本/参数适配、构建与原生正确性。
- 有限Ada语义子任务：新producer、typed register/constant/mask契约、消费者修复和受限native兼容性验证。

GPU作业持合作锁串行；CPU构建、输入准备、只读索引及主库校验可并行。采集attempt必须独立新目录，失败仍保留计数和实际可用证据；不复用历史科研Goal或旧预算。已有4080 GPU证据不自动解除旧producer语义HOLD。

## I/O与存储

本任务由整段I/O等待改为低优先级自适应推进：full PSI avg10低于5时读取上限30MiB/s；5–10为10MiB/s；10–20为4MiB/s；更高或压力数据不可读时1MiB/s。payload传输仍不超过15MiB/s；原sender/receiver锁、分块、全SHA、关闭重开和COMMIT-last协议保持。

四个已命名归档的有限只读索引可与源SHA或冻结payload拷贝并行。索引不是payload sender；Target私有inventory独占lease防止重复，源不写文件，实际payload传输仍持原锁。并行读取同样自适应限速。保留其他科研进程的进度新鲜度、内存、磁盘和预留核查，不终止foreign进程或ComfyUI。

174-new基础余量5GiB，另保留登记预留、1GiB其他项目余量与64MiB控制余量。164为正式冷主档，174-new/109为热层和有界暂存。仅在全SHA、持久化关闭重开、174-new可读且确认不再使用后释放本Lane本地副本；不能把授权写成已释放。原174源、foreign资产与旧冻结科研工具不作删除对象。

## 完成标准

SM70仍须覆盖全部已知常规与裁剪exact input、四归档新增有效输入，跨项目公共入口可读，完成全内容校验与恢复，保存真实缺口和回执。

4080须冻结程序/实现/版本/参数/外部数据的完整实际目标清单，分别验收构建、原生执行与数值、采集结构、producer语义、各consumer/profile资格。73个SDK4.2源码候选不是73个现成可运行GPU workload，10个旧trace程序也不是CUDA全集。Rodinia2.0-ft与3.1独立；不同源码版本或输入规模不能因同名合并。

原默认输入发生NaN/参考退化或数值错误时保留canonical输入及真实状态；修复初始化必须独立variant，不替代原身份。能够完整执行的原输入仍可保存其真实GPU trace，数值资格不因trace结构完整被提升。

producer契约须经针对性微程序、逐PC静态SASS覆盖和实际采集验证，缺域fail-closed。producer冻结后可生产原始资产，consumer资格继续独立等待真实native验收。若消费者使用aux-memory模型，原SASS计数与内部uop计数分开，不宣称硬件指令或性能已标定。当前EP的V100研究配置不因4080采集被替换。

新native兼容性试验使用独立spec、binary/lib/config/input SHA、新有限预算与epoch2请求；不改旧57/2历史或旧迁移cohort。数据可读、producer完整、consumer语义、科学接受和4080性能标定均须各自证据。
