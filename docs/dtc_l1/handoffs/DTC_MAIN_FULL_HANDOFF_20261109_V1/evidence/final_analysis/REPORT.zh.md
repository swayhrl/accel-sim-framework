# 完整 CORE32 Oracle 机会分析（只读收尾）

128/128 runtime closer 接受，128/128 通过原 qualified analyzer 的身份与工作量复核；四模式共同输入32/32，缺失0。原派生机会分析与本次 qualified replay 完全相等。最终独立科学审查由D单独给出，本报告不宣称该审查PASS。

S=实际同输入同build OFF/Oracle；H=1−Oracle/OFF。GM=exp(mean(log S))，固定全32输入同集逐模式计算，未挑选最佳模式。整数cycle直接判定正/零/负。

| 范围 | 模式 | N/缺失 | GM S | 正/零/负 |
|---|---|---:|---:|---:|
|CORE32|M_DATAREAD|32/0|1.676758525810|32/0/0|
|CORE32|L2_DATAREAD|32/0|1.280648684508|19/11/2|
|CORE32|L1_DATAREADY|32/0|1.939911577005|32/0/0|
|CUDA Samples|M_DATAREAD|9/0|1.730326206175|9/0/0|
|CUDA Samples|L2_DATAREAD|9/0|1.425064964511|5/4/0|
|CUDA Samples|L1_DATAREADY|9/0|1.767089720629|9/0/0|
|Parboil|M_DATAREAD|7/0|1.254218832335|7/0/0|
|Parboil|L2_DATAREAD|7/0|1.016872243319|6/1/0|
|Parboil|L1_DATAREADY|7/0|1.257538669189|7/0/0|
|PolyBench/GPU|M_DATAREAD|8/0|3.170315498503|8/0/0|
|PolyBench/GPU|L2_DATAREAD|8/0|1.775432921118|6/2/0|
|PolyBench/GPU|L1_DATAREADY|8/0|5.405615309351|8/0/0|
|Rodinia|M_DATAREAD|8/0|1.103593091151|8/0/0|
|Rodinia|L2_DATAREAD|8/0|1.002290635336|2/4/2|
|Rodinia|L1_DATAREADY|8/0|1.129888264569|8/0/0|
|initial8|M_DATAREAD|8/0|3.446285317826|8/0/0|
|initial8|L2_DATAREAD|8/0|2.103432830864|7/1/0|
|initial8|L1_DATAREADY|8/0|5.106115891060|8/0/0|
|remaining24|M_DATAREAD|24/0|1.318793975160|24/0/0|
|remaining24|L2_DATAREAD|24/0|1.085418270304|12/10/2|
|remaining24|L1_DATAREADY|24/0|1.405008733853|24/0/0|

## 逐应用矩阵

完整精度及H、整数cycle、固定input SHA见 APPLICATION_OPPORTUNITY_MATRIX.csv/json。下表按原冻结program记录次序，M/L2/L1均为同一实际OFF归一化。

| Suite | 应用 | OFF cycles | M S | L2 S | L1 S |
|---|---|---:|---:|---:|---:|
|CUDA Samples|BlackScholes|8971|1.096833354|1.000000000000|1.107804396|
|CUDA Samples|convolutionSeparable|800572|2.490270001|2.198709181291|2.496645970|
|CUDA Samples|fastWalshTransform|185317|1.241513529|1.013819061114|1.240018200|
|CUDA Samples|histogram|98202|1.336554427|1.000000000000|1.453122226|
|CUDA Samples|mergeSort|111917|1.116913834|1.000000000000|1.138942034|
|CUDA Samples|scalarProd|411009|1.833576466|1.481967981539|1.826089854|
|CUDA Samples|scan|6648993|3.180808258|3.071965570294|3.204178014|
|CUDA Samples|transpose|237820|1.246318481|1.000000000000|1.248064823|
|CUDA Samples|vectorAdd|217305|3.778691660|2.388518229482|4.053214705|
|Parboil|bfs|4170294|1.000633690|1.000001198958|1.000762157|
|Parboil|cutcp|4490473|1.023377963|1.000000000000|1.023419712|
|Parboil|histo|5865589|1.511480558|1.109387063255|1.520072925|
|Parboil|mri-q|360174|1.004128879|1.001924992072|1.004257668|
|Parboil|sad|114870|1.135550327|1.004099614514|1.137856230|
|Parboil|sgemm|409417|1.073168494|1.006373763593|1.079484063|
|Parboil|stencil|4662889|2.577719855|1.000944082537|2.589712659|
|PolyBench/GPU|2DCONV|462740|2.034862756|1.192751830086|2.035158088|
|PolyBench/GPU|3DCONV|2200332|1.294156120|1.005851342975|1.321602478|
|PolyBench/GPU|3MM|2402871|1.152961538|1.000000000000|1.079704730|
|PolyBench/GPU|ATAX|31880220|6.556675155|2.741552970686|18.593125956|
|PolyBench/GPU|BICG|28685812|5.900413871|2.551461799023|16.723076376|
|PolyBench/GPU|GEMM|826089|1.183715492|1.000000000000|1.113219472|
|PolyBench/GPU|GESUMMV|89502220|10.288070319|4.132224010295|35.851151314|
|PolyBench/GPU|MVT|34687540|7.134045239|2.846955560542|20.230406200|
|Rodinia|dwt2d|73071|1.045978328|1.000000000000|1.047147504|
|Rodinia|gaussian|740717|1.034396707|1.000000000000|1.040157558|
|Rodinia|heartwall|8551|1.125872284|1.009801606046|1.124244018|
|Rodinia|lud|478654|1.071128228|1.000000000000|1.074123194|
|Rodinia|myocyte|145147976|1.000037908|0.999999986221|1.000037908|
|Rodinia|particlefilter_float|2100874|1.130127974|1.010604527838|1.286565515|
|Rodinia|particlefilter_naive|384601|1.280419881|1.000000000000|1.289534213|
|Rodinia|srad_v1|7324411|1.165292307|0.998003559855|1.217253618|

## 关键正例、负例与kernel证据

GESUMMV（1 kernel，16 CTA，190918656 active instructions）OFF89502220，M8699612（10.288070319×），L221659576（4.132224010×），L12496495（35.851151314×）。MVT/ATAX/BICG 的L1分别20.230406200×/18.593125956×/16.723076376×。这些是固定工作量的受控反事实响应，不能直接归为某个可实现结构收益。

vectorAdd M3.778691660×、L22.388518229×、L14.053214705×；scan分别3.180808258×/3.071965570×/3.204178014×。stencil的100 kernels下，L2只有1.000944083×，M2.577719855×、L12.589712659×；保留逐ordinal匹配后才讨论响应分布。

两个L2负例必须保留：myocyte 145147976→145147978（+2 cycles，S0.9999999862209585，H−1.3779041603721708e−8）；srad_v1 7324411→7339063（+14652 cycles，S0.9980035598549842，H−0.0020004338915443165）。不把两cycle回退舍入成零，不将负例排除GM。myocyte完整5993 kernels、srad_v1完整502 kernels；KERNEL_CASES.json逐模式给出kernel正/零/负数量、kernel名分组cycle和最大响应ordinal以及原始引用。非cycle计数器保持打印值，不构造差分。

3MM和GEMM的L2都精确无响应；3MM M1.152961538×而L11.079704730×，GEMM M1.183715492×而L11.113219472×；fastWalshTransform/scalarProd/heartwall也出现M比L1更快。模式没有数学嵌套或单调保证，不能以L1减M或M减L2分解结构贡献。

## 可实现DTC结构工作的证据优先级

E1=本批固定输入、同build OFF匹配、完整kernel工作量成立的Oracle观察；E2=单独历史C1真实结构实验（旧Core/binary/配置/接受状态随记录保留），只能支持已测结构在自身历史条件的响应；E3=待验证结构机制假设。任何优先级都不授权新启动、不等于已证明因果。

1. 下游服务和完成路径协同（E1强响应、E2有限实测、E3实现映射）：优先关注GESUMMV/MVT/ATAX/BICG与vectorAdd/scan的有限服务；保留sector带宽、注入/返回队列、generation与引用生命周期，不能把Oracle sequencer或虚拟驻留写成免费硬件。已有C1的GESUMMV DH-P0=89502220、F128=86464623、F256=90151547；vectorAdd DH-P0=217305、F128=213053、F256=236217，F128正与F256负同时保留。它们远小于Oracle响应且非单调，禁止把容量增加直接许诺为Oracle等量收益。

2. 有限收集/通知/写回及PIB/Ref完成效率（E1计数观察，E3因果与实现）：3MM OFF每retired load ready_to_collect=31.9120682085、fully_ready_to_complete=33.0059149120；srad_v1分别5.3290593322/7.0649849524。此类样本均值只提示值得核查的阶段；不是关键路径时间、不证明PIB饱和。3MM/GEMM历史E/M/Q/F扫描均无响应，可用作限制案例；单纯扩大下游结构不足以解释其Oracle响应。

3. admission/下游并发与服务容量联合设计（E2有正负，E3映射）：历史ATAX E384/E768=30987395，M8=31438336、M16=32527908，Q64=32321602、Q128=33774401（历史DH-P0=31880220）。改善与回退并存；必须保留原协议和公平仲裁，不按retry下降直接认定吞吐瓶颈。

4. Tag Hash/Tag/Physical容量（安全HOLD；E3实现收益）：Oracle保留512 logical Tag、640 Physical、128 PIB、13-bit Ref及真实Tag bank/admission。即使L1_DATAREADY响应很大，也未隔离Tag结构贡献。Tag安全HOLD保持；有Ref的活跃生命周期不得被危险驱逐或复用，不能以Oracle结果解除HOLD。Physical均值包括Ref-free retained cache，不能等同活跃资源压力或自动推导扩容收益。

5. 宽人群与保守对照（E1）：bfs/mri-q/myocyte等近零响应和L2全部11个精确零必须保持。它们限制总体可泛化幅度；5993 kernels不等于5993应用迭代或已接受求解步。

## 资格与解释边界

Oracle是受控反事实，非数学严格上界、非免费DTC同量收益；模式差额不可相加。历史C1只作为独立背景，不填Oracle OFF、不混入Oracle GM；不计算跨应用best-mode GM。全局cross-warp issue order未证明相同。

保持预装与HtoD/source-event范围：perf_sim_memcpy=1，flushL1=1、flushL2=0、OO source-event invalidate=0。声明HtoD顺序及sidecar/strict不证明原capture ELF/input内容、上传实际时序/重叠、跨kernel coherence或native全应用数值正确性。固定trace与原input SHA不修补、不扩大为全应用认证。

32B L2 sector/DRAM atom与request object不是同一单位；writes/atomics/bypass/instruction/constant/texture/fence仍按各模式保留路径解释。零DRAM不证明compute-bound；未报告计数为UNKNOWN/null，来源推导0与打印0分开。Counter reset/cumulative/delta不推断；sample/item均值不是active-SM峰值、占用历史或因果关键路径。面积差异UNKNOWN，无面积归一化结论。

## 固定身份与完整引用

authority=18b1ee9d339902e555fc2e04ef51c84f77dfe1b1
Core=e6b41ab8992e7d41651501c4d34cfe24195c4f96
Framework=02775fd795cde5aae1480d81cee6eb481d0a08f4
binary SHA256=3f8e547d87893aaf7319e337883a2bcc1f5717138296e3e6d1425cc75d055283
libcudart SHA256=174f53a02223ae69e4a549e60a310f7e69a9334748e719fd48c40640c2a0af43

INPUT_PROVENANCE.json逐一列固定input binding、四模式配置、Core source、binary、RESULT、strict、spec、execution-plan及128个kernel-cache实际读取SHA与字节数。CELL_EVIDENCE_REFERENCES.json按128 cell连接每个RESULT/strict/counter-cache、UUID与164 archive/native restore receipt。QUALIFIED_CORE32_ANALYSIS.json.gz完整保留全部kernel事实、source路径、计数器原值、source-derived0证明和独立C1背景。原始raw的SHA只从既有缓存引用，本次未读/解压raw。

本包只在独立代理目录写脚本、分析产物、MF。CPU-only，scientific starts=0，未改request/owner/registry/Git/英文v0.23；不恢复owner525725。独立D审查状态保留分离。

## Kernel负例与缺失计数补充

myocyte L2的5993个同名kernel中5992个精确相等、1个慢2 cycles；M/L1均为32个更快、5961个相等。srad_v1 L2为215正、13零、274负：prepare合计−1503 saved cycles，reduce−2869，srad−11304，srad2+1079，compress−55，extract0，合计−14652；M虽整应用正，仍有3个kernel负，L1有21个kernel负。stencil L2为52正、2零、46负，应用小幅正不能抹去kernel回退。以上只对明确每kernel cycle做合计，未将其他打印计数器作差分。

全部128 cells共29192条kernel事实：averagemflatency、avg_icnt2mem_latency、avg_icnt2sh_latency各100条显式null，avg_mrq_latency有21156条显式null；这些条目的值继续UNKNOWN，未补0。缺键的计数器也保持未报告UNKNOWN。ARTIFACT_QA_RECEIPT.json记录产物自身的一致性校验及source-derived零的源文件SHA复核，不能替代D最终独立科学审查。
