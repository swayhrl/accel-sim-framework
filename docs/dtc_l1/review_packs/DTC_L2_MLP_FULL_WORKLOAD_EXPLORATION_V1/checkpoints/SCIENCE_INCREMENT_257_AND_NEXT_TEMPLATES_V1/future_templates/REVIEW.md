# 下一阶段参数模板只读审查

本包为隔离CPU候选，未改变生产生成器、registry、21项sourcepins、已消耗身份、35冻结输入或7 unresolved。不构成阶段晋升、资源准入或新实验授权；未启动模拟。

现有A合同的142项不变量检查、44项真实Core option_parser检查已覆盖E1536/M32/Q256/F512和原始组合，本包直接引用这些收据。仅新增4个高阶组合解析例（E1536_M32及E1536_M32_Q256_F512，各CH/DH），以及3个partition-credit整数边界例；共39项新增检查PASS。fixture只链接option_parser.cc或执行纯Python模板，不构造完整cache、partition或模型。

## 新发现与独立candidate修正

1. 原normalize允许F=INT_MAX，但Core memory_config中F/return/subpartition为unsigned，表达式F+192-(2-1)赋入int m_shared_credit_limit。在本机CPU中F=2147483456得到INT_MAX，下一整数即得到负值。独立safe_parameters增加F<=INT_MAX-191。当前F512及现有350点不受影响；纯二倍序列也不会自然命中最后191个整数，此项修复的是通用dict模板入口的工程边界，不是新的科学停止阈值。
2. 原registry.extend分别接受profile名称与parameters，按生成cohort名称跳过已有点；若调用者给同名不同vector或不完整new_cells，可能沿用部分旧配置。独立candidate只接受canonical profile_name，拒绝同名vector冲突，并始终构造完整35集合；任何reuse还需验证已有配置全部effective_options、输入、expected、build和trace argv一致。未改原registry.extend。
3. 原资源forecast按相同workload/core历史RSS加固定128MiB L2 margin，不按新参数vector给出物理成本保证。高联合E1536_M32_Q256_F512的MSHR request-reference逻辑上界为P0的64倍，不能把旧P0或小配置RSS当作高配置已证需求。本包所有模板明确not admission ready，要求独立host RSS/AS预测及fresh资源准入，不编造物理面积或RSS值。

## 资源语义

| 向量 | MSHR keys | request-reference上界 | miss queue slots | FRFCFS slots | shared credit/controller |
|---|---:|---:|---:|---:|---:|
| P0 |7680|30720|1280|1280|255|
| E1536 |61440|245760|1280|1280|255|
| M32 |7680|245760|1280|1280|255|
| Q256 |7680|30720|10240|1280|255|
| F512 |7680|30720|1280|10240|703|
| E1536_M32_Q256_F512 |61440|1966080|10240|10240|703|

F改变时partition shared credit随F+191变化，不能解释为纯FRFCFS队列效应；每subpartition private credit仍1、每controller共2。所有模板的L2 data capacity保持10MiB，1410/1410/1410/850MHz、DTC-L1、hash、address-map、时序和其它effective options全部保持各自CH/DH P0值。上述slot计数不代表物理硅面积、延迟或实际分配的host bytes。

## CH uniform匹配

四个下一层single、合同允许的五种pair、一个四因子union，每个vector均能在CH/DH分别映射完整35，共20套700条候选映射。额外核对CH/DH P0均35 exact reuse、M16 DH35 exact reuse且CH35待新资格。并未按输入挑选最优profile，未promote unresolved输入，未复用其它cell/build或不同vector。所有expected完整输入计数和trace来源继承冻结P0身份，未重新宣称trace内容或完整执行已通过。

应先按E合同等初轮全terminal并完成同一accepted总体的父方向/组合证据，再由Main选择有限新矩阵；本包没有运行recommend来晋升当前未完成矩阵。

## 交付与限制

CPU_QUALIFICATION.json含18个精确sourcepins、原21pins前后验证、4个新组合解析输出及3个credit边界输出。UNIFORM35_TEMPLATES.json为纯候选映射和manifest；next_stage_template_v1.py无registry写入或启动API。二进制credit_boundary_cpu仅为CPU fixture，不应加入科学runtime。源代码证据为Core l2cache.cc arbitration_metadata构造表达式及l2cache.h signed destination；当前参数合同和科学母版身份均未改变。
