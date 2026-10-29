# 可复用R2采集后处理归档与读取流程

本流程把四份实际R2交付的经验与[重复缩减方法](WORKLOAD_REPETITION_REDUCTION_METHOD_V1.md)、[填写模板](WORKLOAD_REPETITION_REDUCTION_REVIEW_TEMPLATE_V1.json)连接起来。它是执行者的检查顺序，不是可绕过准入的独立launcher。逐项真实proof见[最终引用表](FINAL_R2_PUBLIC75_EVIDENCE_REFS_V15.json)。

## 1 先定义新研究身份

先读真实source loop，区分计时冗余、device微基准、batch、遍历、stage、时间步与收敛。优先保原N／shape、类型、路径、warmup和算法链，只改证明确实可独立控制的重复。冻结source diff、compiler／flags／headers、新ELF、argv、输入或seed／libc和用途；2轮不自动等价于稳态或原计时统计。

空间缩放是另一条明确用途轴。N262144 scan pilot是工程smoke，不能当原N6815744研究输入；新R2通过也不把旧默认输入标成完成。GPU原生、插桩采集与模拟器耗时分别记录，不用GB推模拟时间。

## 2 CPU离线构建与image预检

沿原Make方式先object再link，保持目标sm89／compute89和明确线程数；不做install复制。CPU离线cuobjdump -lelf预枚举必须验证全部image名字唯一，再冻结新job身份。出现directbuild同basename歧义时修构建，保旧产物，不放松mapper。

静态device指令或section比较支持其明确范围。scan新旧section的字符串表差异不证明运行时cache等价；transpose同工具链控制与R2的8个kernel一致，但历史diagonal仍不相同。coarse／fine原自比较弱QA不升级成独立完整transpose oracle。

## 3 原native QA与单GPU采集

复用精确同ELF／argv／input／用途且已有owned闭合的真实QA，如scan的17项gold PASS；其他新身份独立验证。采集保持单GPU队列、canonical Comfy共享锁和实时queue、LOCAL_IO、GPU及Native四资产租约。忙时等原范围自然闭合，不开第二controller竞争，不因旧PID退出或观测超时自动重启。

完整采集后绑定原graph、launch数、header、参数和producer计数。只有真实final、wait、owned／lease闭合才能进入下一层；增长文件、prefix ROI和统计声明不能替代完整资产。

## 4 F9和GROUP使用独立CPU数据资格

使用冻结F9／F4／tap／5D原算法，在独立CPU／I/O范围内完成所有记录、warp／CTA形状、group CRC／wholeSHA、feature与索引绑定。scratch是磁盘临时预算，不是RAM或peer reserve，按实际展开量与并发峰值核预算；不要照抄tiny上限。

资源事件中断后先保失败及owned闭合，再固定原F9、闭GROUP、输入／source／index／stat和新pending集合。本次只补scan12与卷积1个GROUP，已接受的数据不重算。共享算法字节不变也仍需新scope接受这次执行数据。

## 5 单CTA ENTRY与裁剪分别声明

有必要时用一个完整源CTA取得启动／执行／退休证据，所有原有退出与退休检查保持。单CTA入口不是full-feature、whole-input或性能接受；aligned旧28CTA OOM不因新ENTRY成功消失。是否扩大覆盖由具体研究风险决定，不默认全配置／全模型或重写oracle。

裁剪按冻结规则抽完整CTA，并验父体相等性、CRC／记录、实际比例、binary／input／ENTRY引用。ordinary与derived有各自的manifest及sender plan，derived引用真实parent COMMIT和必要binary／input，避免重复大输入；parent ENTRY不伪装成derived模型执行。

## 6 COPY与公共发布分两步

COPY前用实际manifest核成员数、逐文件与总量上界。超过旧小包默认上限时，只对精确ID／manifest／count／total建立新实例bound，不全局放宽，也不修改transfer和receiver全SHA。正式COPY取得全成员closed-reopen SHA、不可变COMMIT、真实parent绑定及owned闭合后，才申请公共发布。

发布用新鲜旧catalog CAS、同NAS移动、旧行保持、全metadata／成员stat及Main／DTC实际读取验收。私有路径移动后消失应按relocation map解释。对已验收wholeSHA只复用其精确绑定，不为报告再做全正文回读；旧源仍KEEP。

## 7 从公共入口读取

共享入口为/root/workspace/assets/traces。已有Main／DTC实际命令证明，下列facade可从当前严格catalog读取新75目录中的精确ID；先show检查身份和限定资格，再path取得index，verify核其声明范围：

    /root/workspace/assets/traces/tools/trace-assets sm89 show SCAN_CUDA118_ORIGINAL_N6815744_R2_ALL17_SEED2009_SM89_V1_ORDINARY_V1
    /root/workspace/assets/traces/tools/trace-assets sm89 path SCAN_CUDA118_ORIGINAL_N6815744_R2_ALL17_SEED2009_SM89_V1_ORDINARY_V1 --which index
    /root/workspace/assets/traces/tools/trace-assets sm89 verify SCAN_CUDA118_ORIGINAL_N6815744_R2_ALL17_SEED2009_SM89_V1_ORDINARY_V1

这些实际读取是metadata／成员stat范围，不重新全正文SHA或授予运行资格。取出的index仍需按该项目精确consumer配置使用。当前统一快照也已接受75／75与RAW7。历史阶段图与当前有效处置分开读取；不可把历史as-of字段当正在运行的队列。

## 8 统一发现与范围收尾

严格75常规／75裁剪与独立RAW7分别计数。统一快照更新必须单独接受，不能因为catalog已变就宣称collector已公共发布。记录层、ENTRY层、科学／数值／性能层逐项保界；空witness不推导没有opcode。

最终保留原33分类、153专项延期、大RAW重POST缺口、两个工程pilot POST gap和取消全Native SM70回读的有效范围。只发布必要的实际源快照与小proof／NAS全表引用，保原bytes与CRLF属性；不把实际scope、nonce、FROZEN_JOB、ELF、trace、全headers及全部失败中间版本塞进Git。Root最后核真实终态、Git ref／tree／文件读回，外审未收到就不称已审。

## 9 SM70读取与逐资产恢复边界

公共125输入的NAS访问已验收，Native执行器可以直接读取164。metadata-only前端已安装；full_library_activation:false不是“无公共入口”。全库正文搬回Native仍按用户要求取消。

当前旧R5默认物化入口因退休authority及缺失全对象ledger受门控，不能拿它当可用恢复API。隔离的restore-one正在准备，须绑定已COMMIT资产、选定member与独立chunk、精确目标和字节预算，保持传输与closed-reopen整SHA；只有实际单资产恢复和退出／资源闭合后，才可发布其可执行用法。本版本不声称该修复已经安装或通过。
