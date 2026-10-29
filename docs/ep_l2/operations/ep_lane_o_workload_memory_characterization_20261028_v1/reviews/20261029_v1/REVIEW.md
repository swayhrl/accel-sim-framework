# Lane O V1R1 独立审查

审查对象：`swayhrl/accel-sim-framework` 的 `a0a88408344f8e111952be6ac04fcece59013880`，目录 `docs/ep_l2/operations/ep_lane_o_workload_memory_characterization_20261028_v1`。审查日期：2026-10-29，北京时间。

**结论：四条论文观察方向及零仿真数据复用阶段通过；新增统计与pilot计划有条件通过，尚不是可以交给Main直接启动的执行规格。** 不要求为了本次审查重跑任何应用。未发现抽查数字、冻结验收身份或文件校验错误。R1需在新统计实现前明确；R2只影响精确受阻率的论文表述；R3需在pilot规格登记前闭合。

本轮仅审查文档、当前Source78的相关源码和8个已接受小型validation bundle；没有构建、CPU fixture、新仿真、Trace正文读取或生产代码改动。未更改候选文档及Main账本。

## 必须闭合的问题

### R1 P1 明确 ingress、队列进入、first-head、admission 四个时间点

位置：[采集计划第17行](https://github.com/swayhrl/accel-sim-framework/blob/a0a88408344f8e111952be6ac04fcece59013880/docs/ep_l2/operations/ep_lane_o_workload_memory_characterization_20261028_v1/COLLECTION_PLAN.md#L17)。计划写“L2前端第一次看见一个请求”，附录又使用首次head或队列进入。这些不是同一个观测边界。

Source78的 `l2cache.cc:2692` 附近 `memory_sub_partition::push()` 先接收请求、按sector拆分，再把非texture请求送入ROP delay；`:1749` 在ROP到期后进入ICNT→L2队列；`:1351` 的生产preview及后续MS/LIFE观察针对当前FIFO head。前一个head阻塞时，后面的请求可以已经进入系统，却尚未在head观察器出现。

影响：若用first-head时间称“L2到达间隔”，或者仅在head出现时判断旧RO是否仍未fill，可能把已进入队列、尚未成为head的同址请求漏出fill前重访人口。这会直接影响M的低重叠判断及T的reuse机会表述。已有head统计仍然有效，无需重算成其它人口。

**要求：** 采用两套互不替代的字段：`ingress_*`描述入口请求流，`head_*`描述可向L2资源提出需求的队头请求；T的实际满路准入机会使用head时刻。入口时间在真实入站hook记录一次，普通/texture/ROP以及sector父子身份固定。严格fill前重访至少注明以入口到达还是实际head访问为定义；两者均有研究价值，不能混名。若不愿增加入口hook，则将指标明确限定为first-head重访，删除完整到达流的承诺。

### R2 P2 O2的精确受阻百分比尚需同人口证明

位置：[Observation O2第23行](https://github.com/swayhrl/accel-sim-framework/blob/a0a88408344f8e111952be6ac04fcece59013880/docs/ep_l2/operations/ep_lane_o_workload_memory_characterization_20261028_v1/OBSERVATIONS.md#L23)，及`agents/W.md`中的0.32045%和0.000912%。分子来自MS `SAME_ADDRESS_WB.distinct_requests_first_block`；分母来自FT `model.unique_requesters`。

Source78的 `gpu-cache.h:3136` 将head UID直接交给MS observer；`ep-l2-ft-cache.inc:194–218` 在head地址属于WAD时设置SAME_ADDRESS_WB，没有在此排除L1写回。`l2cache.cc:2811–2815` 的 `ft_record_admission()` 则对 `L1_WRBK_ACC` 单独记absorbed并返回，不增加FT unique_requesters。因此两个计数器在源码定义上并非天然具有相同请求类别人口。

抽查确认分子16,791、390以及分母5,239,872、42,763,048确实存在，算术也正确；**尚未证明这两个具体端点有非零L1写回，也没有证据判定其百分比数值错误**。当前缺少的是足以把计数比称作精确demand受阻率的过滤或零例外证明。需要同时注意：MS记录的是在阻塞观察中出现的同址WB条件，不是全入口同址访问率或该原因的独占因果损失。

**要求：** 从已有终端/解析投影补足请求类型与absorbed人口。若证明例外类别为零，保留原百分比并记录证明；若不能证明，先保留distinct和重复观察次数，将百分比降为“MS/FT计数比，非已证明的demand incidence”，或暂不在论文使用百分比。补证据优先进入Main现有单次解析，不新扫巨型raw、不重跑。

### R3 P2 Pilot的OFF/ON验证范围不能由一个端点自动覆盖全部路径

位置：[采集计划第69–74行](https://github.com/swayhrl/accel-sim-framework/blob/a0a88408344f8e111952be6ac04fcece59013880/docs/ep_l2/operations/ep_lane_o_workload_memory_characterization_20261028_v1/COLLECTION_PLAN.md#L69)。计划最多4个ON和1个OFF，同时提出W写回、V保留、RO合并/retire及T联合观察。一个S端点的应用OFF/ON配对不能直接提供F/WV新hook的不干扰实证；一个host开销结果也不代表所有负载。

这不是要求所有workload各补一对。**要求：** 在登记任何pilot前提交“新增hook/执行路径—CPU控制—已有NI—尚缺应用OFF/ON”矩阵。S、合法F/WV分别定界；只覆盖S的pilot不声称F观察器已资格化。若暂定5次不能闭合实际路径资格，就缩小首批指标/模式，或由Main另审查精确补充控制；不能把5次规划上限当成已经足够的科学资格，也不在此扩大预算。

## 可继续推进的内容

- W的copy工作量、WBUF独立受阻请求及重复观察差异有数据支持；R2不否定这些原始事件。阻塞原因的first-wait是首次block→首次known-clear，只有ANY项必然延伸至准入，V1R1已正确区分。
- V真实response commit、dirty-forward和零响应端点均保留；没有使用install/query作不可靠命中率分母。历史Motivation及Streaming prefinal已带验收与粒度边界，先恢复小CSV/manifest的顺序合理。
- M已区分line容量与同址chain限制，也没有把live merge直接当严格fill前重访。R1闭合后可进一步形成入口流与准入流两个独立观察。
- T补齐Conv237/1,141与Vector27的真实detach是正确修订；三例完整F慢于S不能归因为T，已有表述保留了这一边界。结构候选与T策略开关分开计数的要求也正确。
- 42程序、35冻结代表、历史诊断、不同几何/ELF及四类缺失状态没有被成功子集替代。四个主观察是研究问题与有条件的测量事实，不是四个已经证实的加速机制。

## 本次抽查证据

候选目录SHA256SUMS列出的25个文件全部匹配。额外对以下8个端点读取完整小bundle、核对其现有SHA、冻结CLOSED_ACCEPTED、cycles和独立archive receipt SHA；不重新执行科学验收。详细路径及值见 [SAMPLE_CHECKS.json](SAMPLE_CHECKS.json)。

| 端点 | 核对结果 |
|---|---|
| Conv S REF | copy read720,834；SAME_ADDRESS_WB distinct16,791；cycles331,234 |
| Scan S REF | WB_DATA_SPACE distinct1,737,618；cycles2,162,540 |
| Stencil F REF | V响应4,930,616；dirty-forward20 |
| FWT WV REF | V响应88,069；dirty-forward3,312 |
| Vector4M F REF | RO事务250,087、merges749,913、合计1,000,000；V响应0 |
| SGEMM F REF | RO事务81,582、merges1,054,333、合计1,135,915；V响应0 |
| Conv F 16×8 | detached237、cycles367,152 |
| Conv F 32×4 | detached1,141、cycles425,074 |

这些样本验证相应原始数字与来源一致，不宣称重新检查所有214个冻结点的全部科学内容。

Main只读状态文件另有2026-10-29 **09:14:09北京时间**的快照：222 accepted、23 REF输入配对、110 profile pairs、已注册剩余0；仍为LIVE_INTERIM、full-common-set GM为空。这是状态增量，不回写Lane O原214点冻结表，也不视为整个Main Goal最终完成。

## 建议的下一步

**先做零仿真的证据与合同补齐。** 可直接采用 [PROPOSED_CONTRACT.md](PROPOSED_CONTRACT.md)：固定入口/head字段、请求类型人口、NI路径矩阵和每格数据缺口。Main按已有索引输出一次小投影即可；找不到的历史manifest明确保持UNKNOWN。有限8/32/128 victim容量shadow不是首批必要项，应在需要回答容量问题时再单独冻结替换/回收规则，不能把一般reuse CDF视为victim capture。

R1可通过明确合同或将指标限定为head域闭合，不要求立即新增入口hook；R2未补证前先收窄措辞即可；R3在pilot登记前核实。审查不阻止现有Main实验或改变已验收结果，也不授予新增启动预算。后续代码仍应在Main指定基点的独立工程分支准备，生产Core保持原状态。
