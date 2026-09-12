# C15 validation test catalog

以下是Codex必须实现/执行的测试规格，不是本次handoff已运行的科研测试。每个receipt记录test_id、command、source/planning SHA、input/output hash、exit code、expected/observed、cost和status。fixture写`SYNTHETIC_TEST_ONLY`。主lane拥有测试，consumer可独立复核。

| ID | 主要owner | 测试与精确通过条件 |
|---|---|---|
| T00 | ALL | branch/worktree owner/输入commit核验；故意错误SHA与受保护out_dir必须被拒绝。无key字段不得推断身份。 |
| T01 | ALL | schema主键/单位/NA检查：缺revision、重复key、bytes/cycles混用、null转0、未知source必须失败或明确UNRESOLVED；不能悄悄丢列。 |
| T02 | A | mocked HTTP 206、200忽略Range、416、断连、错误Content-Range、超长header、redirect到错误revision；200大body在消费整个body前拒绝，重试不超过3。 |
| T03 | A | Safetensors长度/JSON/offset边界与shard index；合法FP16 tensor [2,4]为16B；truncated/负offset/越界/重复tensor错误必须捕获。packed逻辑shape不可机械用dtype乘积替代存储。 |
| T04 | A | 8个4bit值payload=4B，另有1个FP16 scale=2B时总已知存储6B而非4B；tied共享同实际storage只计一份，两个独立storage不得因名称相近去重；runtime repack未知保持NA。 |
| T05 | A | 标准KV：L=2,B=3,T=5,Hkv_local=2,D=4,b=2，K/V相同payload=960B；B/T翻倍线性；滑窗Tresident=3则576B。另测TP复制/切分、K/V维度不同、混合层、unsupported MLA明确拒绝。 |
| T06 | A,C | page/line范围：P=65536，[65530,65542)触及2页；[0,8)与[4,12)并集12B而非16B；按对象alias/global并集口径分别验证；零长度、边界整除、64bit大地址精确。 |
| T07 | B | 实测device/backend/dtype/库版本，缺CUDA、错误模型权重、silent CPU fallback必须不产生NATIVE_PROFILED PASS。合成profiling canary与真实模型结果分目录。 |
| T08 | B | unprofiled/profiled配对及同scenario重复；时间单位一致，median/CV/开销由原始数据复算。mock重复kernel名/不同stream/NVTX异步/graph replay，不能仅凭CPU时序匹配GPU。 |
| T09 | B | 地址复用跨generation、同storage多view、异步释放、KV grow/replace、unknown end、旧generation事件：不得错误合并寿命；无法证明先后时AMBIGUOUS_LIFETIME；readonly观察不得更改部署布局。 |
| T10 | B | tracer filter：只选目标launch，选外无SASS；第二遍更改kernel顺序/shape/backend时must reject旧索引；warmup-target去重；截断trace不能标完整。 |
| T11 | B,C | 地址decoder：active/inactive lanes、压缩编码、向量宽度跨128B行/64KiB页、read/write/atomic、重复lane；手算refs/bytes/unique集合精确。malformed行不静默忽略。 |
| T12 | C | CTA块重排：集合和局部warp序列指标不变；全局reuse若顺序未证应拒绝/标proxy，不可出真实L2 miss。无SM映射必须拒绝真实private-L1汇总。 |
| T13 | C | sketch与stable address-hash样本对exact-small数据；固定seed可重复；同地址全部重复访问按同一纳入决策保留；跨chunk合并与单pass等价；偏差/误差随sample rate记录，不以调seed挑最好结果。 |
| T14 | A,B,C | primary选择器不可读取candidate speedup；将candidate cycle列打乱或改极大值后plan SHA不变。seed/split先发布；历史已见标retrospective；oracle策略单独命名且带真实成本。 |
| T15 | B,C | rate聚合：1/10和9/90合并=10/100，不平均不等权率；unique并集不可相加；并行[0,10]和[5,15] duration sum20不等makespan15；represented与actually sampled coverage均正确。 |
| T16 | C | 全量无抽样adapter identity：每kernel explicit cycle/unique key，C12 22臂索引与同源总量精确闭合；duplicate/missing snapshot/counter reset/missing cycle mutation fail-fast。不替代历史raw验收。 |
| T17 | C | C13旧mode1与wrong effective config/source/hash拒绝；仅EQ通过的mode0输入。cold/full join必须同kernel和可比配置，binary/telemetry不同明示confounding。 |
| T18 | C,A | 统计与结论门：零分母undefined；5%绝对cycle误差不用于裁0.3%机制；区间跨0为INCONCLUSIVE；确定性medoid不得凭空CI；retrospective数据不得贴prospective。已失败策略不得从总表消失。 |
| T19 | C | cold/context/full证据边界：原生warmup不作为sim warmup；只有cold/full来源时不生成STATE_CHECKPOINTED或CONTEXT_WINDOW测量；context bias单列，不并入bootstrap消除。 |
| T20 | ALL | cost账：nested parent/child不双计；加载/采集/解析/预热/重试不漏；历史缺失NA；CPU seconds/GPU-active/wall分开；样本数比例不能标wall加速。 |
| T21 | ALL | temp+原子publish、进程中断、重复resume、损坏cached shard、同名不同hash：只能接受完整manifest；失败attempt和partial保持不可覆盖。消费者hash不一致拒绝。 |
| T22 | A,C | 集成准入：两部署同模型不同dtype不写成两种模型；STATIC_DERIVED不升级native；header-only不含假时间；新指纹接近但无审核窗口不能标已证known class；至少2真实可比部署才写跨模型动态比较。 |
| T23 | ALL | 前后git差分与显式路径stage检查，规划/冻结C12/C13/C14/Core/raw资产不变；fixture不进科研结果；生成器确定性重跑，小表hash一致（时间戳字段独立）。 |
| T24 | ALL | 资源/权限/launch guard dry-run：新simulator调用、全权重下载、full model SASS、超预算capture、无授权GPU、危险环境变更均拒绝；仅自有任务可中断；资源缺口不伪装correctness fail。 |

## Acceptance gates

### G0 身份和保护

T00/T01/T23/T24必须通过。违反冻结身份的输入隔离；不能靠结果接近通过。

### G1 静态正确性

A的T02–T06全部通过；真实元数据字段有来源和revision。目标配置不足可能力受限收口，不能造模型。

### G2 动态目录与对象观测

B的T07–T10必须在对应能力范围通过。synthetic通过只说明工具正确；至少一个真实native canary才可发布新NATIVE_PROFILED结果。profiling开销>10%且无法降下来时，只保留语义目录用途，不默认为无偏时间。

### G3 指纹和样本选择

T06/T11–T15/T21通过。精确集合与有误差sketch分层，cheap selector与oracle分层。coverage目标和误差目标是两个独立gate。

### G4 采样方法资格

T16–T20通过后评估科学目标：页/行估计误差、原始miss计数误差、成对delta/sign分辨率、context偏差。工具通过而精度不达标，必须`SAMPLER_NOT_QUALIFIED`，禁止降低合同。

### G5 集成与下一步

T22/T23及完整cost账通过。下一步详细模拟仅提出申请，不能为凑齐G5启动未授权full ROI。

## 最小交付的测试形式

每lane至少提供一个可直接执行的test命令和一个只读`--validate`或等价入口。可用unittest和临时fixture，不强制pytest/pyarrow等新依赖。最终`TEST_RESULTS.tsv`逐条列实际执行的T IDs；没运行的测试写NOT_EXECUTED，绝不预填PASS。
