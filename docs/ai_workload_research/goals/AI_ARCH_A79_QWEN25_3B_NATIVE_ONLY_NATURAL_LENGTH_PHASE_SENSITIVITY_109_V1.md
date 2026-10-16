# AI-ARCH Round A79｜Qwen2.5-3B BF16真实文本长度×生成阶段：有界Native-only一条连续Goal

**日期：2026-10-16；状态：READY_FOR_USER_DISPATCH；科学负责人：AI-ARCH；建议执行：node109独立Codex Goal窗口。**
**本合同授权的仅是一项新原生GPU现象诊断，不重启C16 Stage A，不运行Accel-Sim、Profiler、抓取trace或开发硬件机制。** 通过GitHub发布本文及独立branch不会自动在109启动进程；收到用户转发本Goal后才可执行。普通工程问题在原累计预算内自行最小修复、继续，只有科学identity/数值/资源边界改变才STOP。

## 0. 唯一科学问题与负结果价值

在**同一个已冻结的主流发行模型、自然文本来源、BF16、B1强compiled/Graph路径**下，比较完整CUDA-event请求时间随自然prompt长度512→2048 token以及请求生成长度1→32 token的变化。第二份独立文本A01作为不参与配置调优的验证。结果用于回答是否存在明显的**自然工作量/生成阶段敏感度**，并为将来真正资源诊断提供有意义的时间边界；**不能根据斜率断言是L2、TC、DRAM、TLB或发射能力瓶颈**，不能据此拟造GPU硬件资源扩展曲线、架构收益、纯Prefill kernel时间或纯Decode ITL。

如果强运行条件不成立、历史参照不再可比、输入不足2048、合法输出不稳定或者预算超限，输出对应NO-GO/DEFER及真实原始记录，不能为取得预期阳性调参数或替换科学对象。

## 1. 科学父证据（只读，不继承C16执行权限）

- A78已接受独立审查：[W77/S77资源配对不成立](https://github.com/swayhrl/accel-sim-framework/blob/50a7269df1ede4616c3539219e4eaa1f7a44e2b5/docs/ai_workload_research/reviews/AI_ARCH_A78_A77_W_S_RESOURCE_PAIRING_INDEPENDENT_REVIEW_2026-10-16_V1.md)。W77 [原报告](https://github.com/swayhrl/accel-sim-framework/blob/4fa849b16ff7828959486ccafe404c86a9115918/docs/ai_workload_research/discovery/A77_W_NATIVE_WORKLOAD_AUTHORITY/REPORT.md)与`BASELINE_CARDS.json`包含身份和原生参考，S77的0个模拟资源轴结果保留。
- 原生vLLM Mode A旧合同：[C16 DQ2 PREEXEC_CONTRACT.json](https://github.com/swayhrl/accel-sim-framework/blob/a12bbfa4609ece57fadde107f9fd2e3bc0380cdf/docs/vm_tlb/review_packs/C16_DQ2_NATIVE_RECOVERY_109_V1/PREEXEC_CONTRACT.json)，[原版runner源码](https://github.com/swayhrl/accel-sim-framework/blob/a12bbfa4609ece57fadde107f9fd2e3bc0380cdf/util/vm_tlb/c16/dq2_native_recovery/runner.py)，[历史正式计时与数值](https://github.com/swayhrl/accel-sim-framework/blob/ccd6928bfb420d1e4c554ec0e377bb8fbe377501/docs/vm_tlb/review_packs/C16_STAGEA_TERMINAL_INDEPENDENT_CONSUMER_174NEW_V1/DQ2_INDEPENDENT_RECALCULATION.tsv)。
- 输入authorities：[输入选择和tokenization合同](https://github.com/swayhrl/accel-sim-framework/blob/a12bbfa4609ece57fadde107f9fd2e3bc0380cdf/docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_MEASUREMENT_CAMPAIGN_EXECUTION_PREFLIGHT_174NEW_V1/TOKENIZATION_CONTRACT.md)，[输入manifest](https://github.com/swayhrl/accel-sim-framework/blob/a12bbfa4609ece57fadde107f9fd2e3bc0380cdf/docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_MEASUREMENT_CAMPAIGN_EXECUTION_PREFLIGHT_174NEW_V1/INPUT_SOURCE_FREEZE.json)，[原token receipts](https://github.com/swayhrl/accel-sim-framework/blob/a12bbfa4609ece57fadde107f9fd2e3bc0380cdf/docs/vm_tlb/review_packs/C16_MEASUREMENT_CAMPAIGN_STAGEA_ASSET_INPUT_CLOSURE_174NEW_V1/TOKENIZATION_RECEIPTS.tsv)。
- 冻结模型：`Qwen/Qwen2.5-3B-Instruct@aa8e72537993ba99e69dfaafa59ed015b17504d1`，BF16、无量化、TP1；历史模型绝对目录`/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1`只读；历史运行环境`/data/c16/envs/c16-vllm-v0.30.0-sm89-v1`只读；旧vLLM源码commit`ced6857afa0ea7b2e3f0846a62e1394e90f15607`。当前实际是否仍存在需G0核实，不自动下载/重新安装。
- 当前输入两份：`TRAIN_A_DISCOVERY_00`（A00，41,457字节，SHA256`423f9086b24eff32fdd8f34630f841fa10ed34e34a33e1e18db02b97a3cdb60f`）；`TRAIN_A_DISCOVERY_01`（A01，53,757字节，SHA256`02516fbeb13a2b9c0e0dfbfcc8a1942e9b7e5a555edca5ac9b86f49070912394`）。512-token文件已有独立SHA；A01是另一**discovery文本控制**，不是 sealed holdout。全部`TRAIN_B_SEALED_*`与PG-19完全不访问、不展开、不参与配置选择。
- 历史MP02 A/Mode A BF16 B1 512+32正式5次CUDA-event中位`354.59820556640625ms`、MAD`0.28192138671875ms`，Graph Mode B 361.4565ms；旧Mode A/B请求有32-token及logprob合同。当前**只做Mode A**，不做旧Mode B/B4也不运行旧C16 runner。
- WikiText-103公开数据卡标CC BY-SA（元信息出现`cc-by-sa-3.0`、`gfdl`，卡片正文另外写CC BY-SA 4.0），因此G0应留存版本与许可披露差异，研究仅在许可允许下**本地只读使用已冻结小文本**、保留source attribution、Git不公开复制prompt/语料，不能把卡片信息冲突静默写为“版本已确定”。如无法明确合法使用STOP，绝不另下载数据补救。
- S77结论`MODEL_AUTHORITY_NO_GO`：旧AWMA 0.5B T1 SASS trace与此3B compiled请求不配对；不要启动模拟器、更改TC/L2参数或调用Profiler。C16 Stage A四DQ及旧observer错误均冻结，任何新活动只写本A79专用路径。

## 2. G0：CPU静态输入、版本、资源与新运行器准备——无CUDA

**先一次性完成CPU资格并冻结所有点，再申请GPU锁。** 以独立sparse worktree和受控私有tmp/output建立本Goal的新runner/supervisor/validator/后处理；只能参考原DQ2 runner，不复用原DQ2主脚本进行数据写入。不得更改旧Git branch、raw、既有`/data/c16`缓存/模型/环境、C16/AWMA/ISCAS工作树或共享manifest。不得全盘扫描164、运行全库模型资产hash、强制git clean/reset/gc或自动升级依赖。

1. 只读历史assets/model/config/tokenizer及冻结A00/A01 text/512-token JSON的内容SHA/长度，注意路径可优先从本A79 worktree的版本化Git文件获取，而非读取旧私有worktree。模型大safetensors允许G0用已发布SHA/大小与本机stat/有限头部初筛，**若要宣布完整资产SHA PASS才可流式逐文件计算原SHA并计入CPU wall与IO预算**；若旧相同manifest/path/可信staging无法核，标`ASSET_AUTHORITY_NOT_REQUALIFIED`并STOP，不下载。
2. CPU tokenizer仅使用本地已固定模型revision/library，强制无CUDA初始化。512输入须原样使用历史A00/A01 `token_ids`，复算文件SHA/标准紧凑token数组SHA，**不能为512重新选择前缀覆盖原冻结身份**。2048只允许按历史规则从各自相同源UTF-8文本在字符边界选择“完整chat-template后不超过目标token数的**最长文本前缀**（平局取最短字节前缀）”，冻结新token ID/源SHA/byte offset/tokenizer/模板、脚本SHA；不能拼接、复制、填充或从其它文件补够。要求**恰好2048个token**；若原文本不足/算法跳过确切长度，则该源对应2048点明确`SOURCE_TARGET_LENGTH_NOT_REACHED`，不放宽为任意更短窗口；其它独立点可有界完成并降级结论。
3. 输入许可/来源归属、model许可来源与local use资格必须有凭据，Git仅发表hash、索引与匿名长度，不提交源文本、生成文字或敏感内容。旧A00/A01发现集不能改称独立封存holdout。
4. 冻结新runner的强路径：原版本`vLLM 0.30.0`、`dtype=bfloat16`、`quantization=None`、`model_impl=vllm`、`tensor_parallel_size=1`、`skip_tokenizer_init=true`、`enforce_eager=false`、`compilation.mode=VLLM_COMPILE/backend=inductor`、`cudagraph_mode=FULL_AND_PIECEWISE`、`cpu_offload_gb=0`、`enable_prefix_caching=false`、`seed=0`、`gpu_memory_utilization=0.92`、`max_num_seqs=1`；采样`temperature=0/top_p=1/ignore_eos=true/detokenize=false/logprobs=20`，`max_tokens`为指定1或32。任何返回eager/fallback、不同attention/linear backend、Math/量化或未知graph mode→身份NO-GO，不做弱路径替代。
5. CPU检查当前环境对**本A79专用编译cache根**的合法接口（vLLM/torch compile提供的显式env/CompilationConfig local_cache_dir等），确认生成文件严格在新的私有预算路径内；**不清空/重建/覆盖旧C16 compile cache，不强制旧AOT root hash匹配本轮新cache的字节**，生成新cache的身份应记`NEW_MODE_A_COMPILATION_IDENTITY`并不冒称历史binary一致。若软件不支持隔离新cache且会写旧原路径则`CACHE_ISOLATION_NO_GO`直接STOP。
6. CPU语法、自检和时序终点独立审查：pre-sync、CUDA event start→单次`llm.generate`→stop→post-sync→read elapsed；host wall独立诊断，不做semantic module hooks/NVTX observer、Graph破坏、NCU/NSYS/NVBit、SASS、CUDA timing replay。不得更改模型源码和第三方依赖。
7. 在收到GPU锁前冻结点阵、采样次数、旧时间参照、通过判据与顺序到`FROZEN_SCIENCE_CONTRACT.json`。G0完整就绪才GPU；资源冲突则`GPU_RESOURCE_DEFERRED`，不轮询、不打断其它项目。

## 3. 实验点矩阵：先历史参照，再“同一容量配置”比较

### G1：单独历史条件复现，fresh model process（第一个GPU模型上下文）

**H0 = A00，512输入，32输出，B1，Mode A，engine max_model_len=544、max_num_batched_tokens=544**。与旧MP02的强配置相同；2次warmup（第二次只作为数值canary）＋**5次formal**，fresh process、无侵入CUDA-event/host wall，全部raw保留，输出32个token及20 logprobs的hash、finite、正确性收据。新GPU上只保留新编译cache根；如能读取同一历史接受的输出/reference且可验证SHA，按旧冻结规则`exact32 tokens + atol0.05/rtol0.01 sampled logprobs`核同输入。若旧reference不在用户允许的本机只读文件中，标`HISTORICAL_OUTPUT_NOT_REVERIFIED`，不得按当前run自己成为自我reference假称历史数值PASS。
- 记录R0中位/MAD及和旧354.598ms相对漂移。事前门槛：新5次`MAD/median <= 5%`，新median相对旧差`<=15%`仅用于是否保留**与历史时间的比较资格**；该阈值是保守诊断，不是设备科学普适误差或统计显著性。超过15%时不宣称旧分母可链接；若有清晰的独立新运行身份证据和5次稳定数值，**可以继续G2，但所有结论严格标为NEW_NATIVE_ONLY_UNLINKED_TO_HISTORICAL**。若后端/数值/资源资格失败则立即STOP，不为了凑图继续。
- 不用任何结果来改采样温度、dtype、backend、GPU利用率、模型修订、编译模式或token数。

### G2：统一max_model_len配置下的自然工作量响应（第二个GPU模型上下文）

仅G1已通过必要正确性/后端与非侵入计时门、2048输入资格至少有一个源PASS后进行。新fresh model process一次初始化，固定**engine max_model_len=2080 / max_num_batched_tokens=2080 / B1**，所有点共享该配置和编译/Graph模式（但实际shape graph dispatch差异需记录）。不能将G1的`max_model_len=544`时间直接用作G2中`L512`的替代；因容量配置本身会改变capture/cache/计划。

在G2单个模型上下文，按**固定先验顺序**运行下表；每点2warmups＋5formals，不基于性能调序或挑选： 

| Point | Source | Prompt tokens | Generated tokens | 身份 |
|---|---|---:|---:|---|
| C01 | A00 | 512 | 32 | 同容量配置的短mixed |
| C02 | A00 | 2048 | 32 | 同文本、长mixed |
| C03 | A00 | 512 | 1 | 短prefill-dominated request |
| C04 | A00 | 2048 | 1 | 长prefill-dominated request |
| C05 | A01 | 512 | 32 | 未调参的独立文本控制 |
| C06 | A01 | 2048 | 32 | 独立文本长mixed |
| C07 | A01 | 512 | 1 | 独立文本短prefill-dominated |
| C08 | A01 | 2048 | 1 | 独立文本长prefill-dominated |

若某个2048源资格未通过，仅省略对应长点；依然不能把2048替换成任意更短文本、pad/resize或外部数据。若G1历史参照失败但科学结构/数值合格，G2可成为**新独立强软件同配置工作量实验**，明确历史不可比。A01不参与阈值、后端或图优化，只作事前冻结的跨文本可重复性检查，**不称真正sealed holdout**。至少需两种长度在同一个源下完整通过、且两个输出长度可合法取得，才对该源报告二维交互；否则仅报告完成点和受限解释。

严格保持`ignore_eos=true`，每个response长度必须等于对应max_tokens、每点5个formal返回token IDs（同一点同seed deterministic且重复一致）及采样logprob finite/可复核；任何数字非法、输出数变动、模型编译/Graph变成非法fallback，停止对应源/点并报告，不能反向微调数值阈值或静默丢弃样本。当前无独立完整长文本数值oracle：同点重复性只能标`SCOPED_SELF_REPEATABILITY`，不能说已被另一backend验证数学正确或终端质量。

所有初始编译、warmup、模型转移、cache创建、tokenizer、CUDA上下文建立与CPU等待**单独预算**，不能偷偷纳入formal或当免费服务。请求级CPU wall与GPU CUDA-event保留两种不同边界，正式主指标`median GPU-event request wall`，MAD和每个raw值完整保留。

## 4. G3：一次性自动分析/STOP

- 按source分别报告实际`T(L,output)`及MAD（毫秒）、输入/输出实际tokens、前后端配置、Graph实际dispatch或无法观测状态、完整进程/设备使用收据。**不是纯Prefill/纯Decode**，不得将`T(L,32)/32`称ITL。
- 对每份源在G2同一`max_model_len=2080`内计算`Delta_prompt(output)=T(2048,output)-T(512,output)`、`Delta_generation(L)=T(L,32)-T(L,1)`和`Interaction=Delta_prompt(32)-Delta_prompt(1)`；这些变化包含必要计算增量、KV规模和graph dispatch，不是硬件resource-only效应。可以给吞吐率但必须以有效输出token和**完整请求**分母明确其局限。
- A00发现、A01独立文本验证分别呈现，不平均掉不同文本的误差；对于两份输入在方向上不一致，标`INPUT_DEPENDENT`而非发掘“性能膝点”。最多2×2两长度/两输出矩阵，只是一阶特性曲线，不能声称找到了饱和点。
- 保存null/negative/数值STOP结果和全部真实raw，包括G1漂移、编译/模型身份、资源压力/外部GPU PID、lock/supervisor状态、资产复核限制。必须区分`SCIENTIFIC_POSITIVE_WORKLOAD_SENSITIVITY`（仅现象）和`NO_STABLE_DIFFERENCE`、`IDENTITY_OR_INPUT_NO_GO`、`RESOURCE_DEFERRED`。即便出现明显非线性也不自动启动硬件设计或Sim/Profiler。
- 将实验解释成`NATIVE_ONLY_WORKLOAD_CHARACTERIZATION`；没有被校准的资源轴，因此**零个GPU hardware headroom/projection claim**。若无完整新实验则可科学STOP。
- 最终报告应回答“下一步如果确实要归因，是哪个**一个**新的资源可观测问题，强软件下还需什么测量”，不要再给一个泛泛最新文献列表或自动发布下一Goal。

## 5. 强资源预算、独占与工程自主权

**本Goal一次性预授权的最大边界（所有正常工程补丁含在内）：**
- 节点：仅109 RTX4080 SM89、固定历史UUID`GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`，用户共享GPU campaign lock`/data/c16/locks/c16_gpu_campaign.lock`。
- GPU锁**非阻塞**获取，冲突直接`GPU_RESOURCE_DEFERRED`，不等待、轮询、抢占、修改其它锁/进程/驱动。**锁必须在任何CUDA调用、编译或模型实例化之前取得，并覆盖两个新模型上下文与所有GPU子进程**；GPU持锁累计墙钟上限**720秒**，全Goal墙钟上限**45分钟**，GPU最多2次模型初始化（G1与G2）和此次明定的1＋8个点；最多2warmup/5formal每点，无额外探索性GPU重跑，不用多进程并行。
- GPU任务自身峰值NVML占用目标≤**15,400MiB**；CPU任务进程树RSS峰值≤**16GiB**；新建disk（worktree/tmp/日志/新compilation cache）累计≤**3GiB**，Git公开结果raw加source总追踪文件建议≤**10MiB**。无新权重/真实数据下载（0字节）、安装/升级（0）、模型替换、显存共享任务打断、164读写（0）。
- supervisor单独进程负责实际owner pid tree、启动/结束/超时与GPU PID NVML持续采样（尽可能每2秒一次），独立识别OWN_LIVE_PID/EMPTY/UNKNOWN；出现外部GPU进程、PID归属未知、VRAM cap、GPU时间/CPU RSS/disk超额立即按fail-closed受控结束本任务树。terminal child退出码、NVML设备进程清空与释放锁之后才称`EXCLUSIVITY_EVIDENCE_COMPLETE`；不把无PID的历史A65缺口补成本轮“通过”。支持观测如果当前NVML不可用，标`GPU_EXCLUSIVITY_OBSERVABILITY_NO_GO`，不猜。遇超时先SIGTERM自己的process group、短grace后SIGKILL并观察GPU context退出；**绝不杀别人的PID**。
- 并行原则：CPU-only source prep、独立审查与论文工作可并行，但109只有本Goal一个GPU owner；后台驻留其它项目未知时不抢；不要借“高效率”引入多轮模糊授权。
- 基础环境、模型和原有编译缓存只读；所有新runner、编译/cache、报告写在此A79分支私有tmp或自有代码目录。可自主解决两次以内的小工程修复（依赖接口选择、路径、缓存隔离、日志、有限内存释放），**不得**改模型数据/输出质量合同、时间边界、操作精度、engine graph模式、GPU cap、实验点/选择标准，不清缓存或改共享环境；修复失败如实STOP。
- 新的A79运行器和分析工具仅写`util/ai_workload_research/a79_qwen25_3b_native/`（若父目录不存在则本分支新建）；科学交付统一写`docs/ai_workload_research/runs/AI_ARCH_A79_QWEN25_3B_NATIVE_WORKLOAD_SENSITIVITY_109_V1/`。第三方依赖绝不打patch；运行期间大raw/private日志可留专属忽略tmp但须保证科学必要精简raw受控commit。
- **环境参数**`HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1`、`VLLM_ENABLE_V1_MULTIPROCESSING=0`及本A79适用隔离路径；仅设置到本任务subprocess env，不改用户全局shell。禁止模型网络回退，禁止为兼容最新软件而silent升级vLLM。若实际缓存身份/graph调用变更，记录并限制结论范围；无法保持强Mode A则STOP。

## 6. 四门交付与远端闭环

首次执行前CPU预冻结`FROZEN_SCIENCE_CONTRACT.json`、`INPUT_RECEIPT.json`（仅hash、无源文本）、`SOURCE_AND_RUNTIME.json`；GPU执行后生成原始逐点`raw/*.json`，`FORMAL_SAMPLES.tsv`、`NUMERIC_AND_IDENTITY.json`、`GPU_RESOURCE_RECEIPT.json`、`ANALYSIS.json`、`FINAL_REPORT.md`、`SHA256SUMS`和`RECEIPT.json`；若STOP在G0/G1也应保留可追溯最小negative报告。为避免自引用receipt只记录commit前文件hash，最终Git commit/tree及远端readback来自独立的最后回执。

Git提交只允许新runner工具目录和**本A79结果**，不能修改`CURRENT_STATE.md`、旧A79以外的计划、C16、AWMA、ISCAS或旧benchmark样本。检查源、测试、相对路径及Git所有修改后，commit→push一次→fetch-back**精确commit/tree/每个交付blob**→worktree clean，向用户回报实际终态及科学收据，然后STOP。没有当前运行权限，不许后台继续任何重测；用户再交报告由ChatGPT独立审查。

**预期结果分类：**`NATIVE_WORKLOAD_SENSITIVITY_COMPLETE`、`NATIVE_ONLY_SCOPED_PARTIAL`、`NO_STABLE_DIFFERENCE`、`IDENTITY_OR_INPUT_NO_GO`、`GPU_RESOURCE_DEFERRED`、`BUDGET_STOP`、`ENGINEERING_STOP`。任何终态下，**新模拟器、Profiler、C16 Stage A修复与机制开发都没有获准**。
