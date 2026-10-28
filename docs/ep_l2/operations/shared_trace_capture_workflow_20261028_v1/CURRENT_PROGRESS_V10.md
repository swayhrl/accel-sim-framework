# V10 当前研究输入的轻量模拟器证据

Root验收时间：2026-10-29T05:15:34.085544+08:00。当前EP29和DTC35共64条精确输入绑定，涉及36个独立SM70 bundle，其中28个跨项目共有。已复用真实历史运行及受限执行证据，闭合“当前研究资产能够进入对应模拟器”的轻量证据层；这不是64个程序，也不是64条完整应用或全部consumer配置均已接受。

| 证据层 | 本次Root验收 | 适用边界 |
|---|---|---|
| 资产精确绑定 | 64条 | 固定input identity、bundle、命令和成员证据，公共125可读验收单独保持 |
| 解码和kernel启动 | 64条 | 每行至少一条已明确绑定的项目、source、binary及config路线 |
| 退休指令 | 63条 | 36个bundle均至少一条实际退休路线；EP SYRK这一行仍UNKNOWN |
| 完整接受的既有运行 | 61条，EP27加DTC34 | 35个bundle至少一条完整接受路线；不覆盖所有S/F模式、配置、consumer版本或科学资格 |

[64行瘦机器投影](CURRENT_64_EXACT_CONSUMER_LAYERS_V10.json)逐行保存input、bundle、层级及spec/source/binary/config证据。完整666,727B审计和原V3审阅入口保留在NAS，精确路径和SHA见[索引](EVIDENCE_INDEX_V10.json)，无需复制整个审计包或重跑模型。

## 三类限制保持原状

- EP particlefilter_naive的07ba精确输入已经解码、启动并退休3,614,144条active-lane instructions；随后因host预填充要求硬件排空且所选owner清洁而拒绝，rc为-6。它不是完整应用接受点，也不能据此称trace格式或ISA损坏。
- EP SYRK的90b0精确路线在Root验收时仍由原模拟器进程运行；已有header加载和kernel启动证据，退休仍UNKNOWN。状态文件CONSUMED_BEFORE_FORK不能解释为未运行或失败，不启动重复smoke。
- DTC SYRK的b518精确路线因资源样本节奏门而保留negative。Root把已归档progress与固定源码和原PID/input/uuid闭合后，确认2,094,276,128条partial retired active-lane instructions。完整科学应用仍未接受；六个IR1规格在该时点仅admitted、未启动，不写成失败。

上述两个partial计数是active-lane退休指令，不与GPU producer声明的SASS records合计。DTC progress的completed单位由shader按active_count递增、framework post-cycle传值和序列化链共同证明，[三处最小源码摘录](SOURCE_UNIT_EXCERPTS_V10.json)仅用于解释单位，不是整源快照或新执行代码。原V2审计的62条退休计数按其历史时点原样保留，63条来自单独Root补充证据，不洗改原件。

## 本轮交付边界

严格SM89公共目录保持71常规与71裁剪对象，独立RAW3另列；原33项有限输入为24对常规裁剪公共资产加3项RAW例外交付，共27完成、6待办。71/71是对象数，不是71个独立程序。其余153项专项继续DEFERRED，全SM70正文恢复至Native已取消。全库Goal尚未完成。

未正闭合的scan没有新增RAW例外，旧alignedTypes和transpose仍按用户要求做完整POST。本版仅补已Root闭合的64条证据，不滚动改写运行中任务状态。相同程序名的SM89输入也不替代当前已绑定的精确SM70输入。

历史科学negative、运行中的点及所有资格边界保持；不跨项目、source、binary或config移植接受。没有新GPU、模型、采集或正文恢复，也没有新科学授权。源KEEP、释放0，外部ChatGPT审稿仍未收到。
