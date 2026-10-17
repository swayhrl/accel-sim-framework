# Lane Z2 — U evidence integration / event-aligned K1 V2

状态：`PUBLISHED_EVIDENCE_CONSUMER_COMPLETE_V1_PRESERVED`。原174容器、北京时间2026-10-18，独立Framework分支 `hrl/iscas2027-dtc-lane-z2-u-evidence-174-v1`，worktree `/workspace/worktrees/accel-sim-iscas2027-dtc-lane-z2-u-evidence-174-v1`，基于Z V1 `ccf208c723f44387160c0edfe9e4d56855dfbafd`。V1全部53个包文件逐blob匹配，78个typed字段、2790行表、413个校验结果未覆盖或改写。

先完整读取固定U `16e56912cfd02f2311a1603a29415dee829fd495` 的LATEST_REPORT、FULL_MATRIX、STRICT_AUDIT、FINAL_CONTRACT_AUDIT与terminal typed证据。公开包绑定两个自然终态、2/2 strict PASS和正式合同审计，满足Z的消费门槛。本轮只复核已发布Git提取物、终态收据与manifest SHA；没有进入raw root，没有PID/后台/partial性能探测，没有重做原raw验收或模拟。

两项交付相互独立：

1. **旧OO→固定T1-C四个逐点描述比较。** T `f520a445436b57c0a0f2494fb858a1636f04d2bc` 的GEMM/Gaussian保留discovery标签，U的DWT2D/BICG保留fixed-holdout标签。生成576行 [typed evidence](U_T_TYPED_EVIDENCE.tsv)、4行 [描述性比较](FOUR_INPUT_DESCRIPTIVE_COMPARISON.tsv)，包含12个有身份的OO/T1-C/C+点。无新总体GM、无按负载选Tag、无原GM12改动。字段的同路径/跨C+资格见 [crosswalk](METRIC_CROSSWALK.md)。
2. **新K1时间合同V2。** [K1_INTERPRETATION_V2.md](K1_INTERPRETATION_V2.md) 显式修正V1的“无live Ref安全kernel边界”描述，采用Lane V `26abd496417d9392245052e54fbd9ba27c6ffd96` 的 `ldst_unit::invalidate()` 源请求线性化点。继承SM范围与重复idle语义，无需global quiescence；保留旧inflight/Ref/generation，最后owner结束才能回收。逐式核对Q32/Q64/T0/T1/I、ln(I)、Δ均保持代数成立，结果见 [CPU公式见证](FORMULA_VALIDATION.json)。不把V1改写为已采用V2。

V2合同已先单独发布：binding commit **`35ff4bc3660dc7653be5d9a3d5a166b610effcf9`**，文档SHA256 **`bad86ae9be5ab7958171fcddf1b9790f8ec1e66d030eb5d490bee9b5a1f67d7d`**，push/fetch-back回执 [K1_V2_BINDING_FETCH_BACK.json](K1_V2_BINDING_FETCH_BACK.json)。AA可绑定这个不可变文档；本轮未读取AA状态/性能，不声称AA已绑定或新性能是否产生。source/build/observer与有效选项仍须由AA绑定；本包没有K1实施验收或模拟执行权。

| 输入 | cycles oldOO→T1-C | lower创建变化 | DRAM read bytes变化 | T1-C较C+周期变化 |
|---|---:|---:|---:|---:|
| GEMM | 1,377,919→1,071,405 | −47.620% | UNAVAILABLE | −29.109% |
| Gaussian | 3,798,174→3,278,356 | −54.110% | UNAVAILABLE | −2.983% |
| DWT2D | 237,887→236,447 | −5.778% | −0.232% | −4.500% |
| BICG | 47,533,116→41,157,397 | −0.148% | −18.652% | **+62.334%** |

BICG whole-run下降13.413%，DRAM read bytes下降18.652%，而new lower创建变化极小；不能宣称单一因果。它较C+慢62.334%的负例完整保留。四输入周期均下降、ready-to-complete条件均值却均上升；GEMM单kernel收益不归因跨kernel retained mapping，其他输入缺直接关联也不做精确周期分解。可选论文修订措辞在 [PAPER_EVIDENCE_NOTES.md](PAPER_EVIDENCE_NOTES.md)，未改写v0.13或晋升T1-C。

CPU消费校验257项通过，29个固定发布源blob已核身份/SHA，V1文件逐字节保留；[CPU_CONSUMER_VALIDATION.json](CPU_CONSUMER_VALIDATION.json)记录范围与全部检查。复核命令：`python3 docs/dtc_l1/review_packs/DTC_LANE_Z2_U_EVIDENCE_V1/consume_published.py --check`，重现生成结果并核包内完整SHA。PASS只指公开完成证据的类型/守恒/身份/算术及保存性，不升级为数值load正确性、coherence/PPA或新机制PASS。

未运行模拟、未改Core、未读大raw；无partial性能或后台PID读取。全部新增修改限定本Z2输出目录。`FILES_SHA256.tsv`覆盖除自身外全部包文件（包括嵌套manifest）。内容发布回执将写入 `CONTENT_PUBLICATION_FETCH_BACK.json`；最终commit/tree、逐blob SHA与clean回执独立保存为 `/workspace/dtc-lane-z2-u-evidence-174-v1/FINAL_FETCH_BACK.json`，不制造自引用commit SHA。
