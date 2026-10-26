# Round A80｜A79 Qwen2.5-3B Native-only：GPU锁冲突STOP独立科学审查

**审查日期：2026-10-26；审查方式：GitHub固定提交/原始收据/冻结输入记录/监督器源码与独立SHA256；审查者：ChatGPT／AI-ARCH。**

**最终科学裁决：接受原`GPU_RESOURCE_DEFERRED / STOP`，附`G0_QUALIFIED / G1_G2_NOT_ADMITTED / ZERO_NATIVE_OBSERVATIONS`。** 这是一项按原非阻塞互斥合同执行的资源延期，**既不是软件性能负结果，也不是任何硬件资源限制的测量**。本审查不重新获得GPU锁、不轮询当前任务、不批准原Goal自动重试。

## 0. Git身份和交付完整性（已独立回读）

- 原Goal发布commit：`7094d4b2d29980c2d2d8d97a9abb6fddb3283c9f`。
- A79执行branch：`hrl/aiarch-a79-qwen25-3b-native-workload-sensitivity-109-v1`。
- 第一次科研归档commit：`4213330affef4aae0c82ba036c8f4ee75816589a`，Goal→first ahead1，新增19文件，tree `35c068233ad1b6100bbc8b9f5baf3b59e51bb661`。
- **最终commit**：`1ad28dbe2fe7280aea46a24f6ba9a97c021b08b7`，tree `9ed5906e445923e6ac8ee600093c23acbf0b987b`。Goal→final ahead2，总计19个新文件；final→当前branch HEAD `identical`。
- 第二次提交明确仅更新`FINAL_REPORT.md`、`RECEIPT.json`、`SHA256SUMS`。执行报告披露原本的中文报告经过PowerShell传输变成`?`，后以可读英文替换；实验程序、冻结输入、`raw/ADMISSION.json`和`GPU_RESOURCE_RECEIPT.json`没有发生第二次修改。两次push/fetch-back属于一次**披露的文档发布偏离**，而不是重复GPU锁尝试。
- 本独立审查读取`SHA256SUMS`所列**17份独立payload文件**，用V8纯JS独立实现并先以字符串`abc`已知摘要自测的SHA256，对从GitHub取回的完整UTF-8文件逐字节重算，**17/17完全吻合**。17项包含原报告、原始锁记录、实验冻结合同、校验程序及五个工具源文件。独立读取`RECEIPT.json`中payload hashes并与manifest比对，无不一致。19个Git文件中额外`SHA256SUMS`与`RECEIPT.json`因为清单自引用的关系**未被该17/17的独立清单覆盖**，但已通过GitHub对象/blob与最终tree身份回读；不得写成「19/19独立重算SHA256」。全部执行侧本机`worktree clean`及两次fetch-back由原Codex收据陈述，本审查**没有远程SSH复测本机状态**。

[原始FINAL_REPORT](https://github.com/swayhrl/accel-sim-framework/blob/1ad28dbe2fe7280aea46a24f6ba9a97c021b08b7/docs/ai_workload_research/runs/AI_ARCH_A79_QWEN25_3B_NATIVE_WORKLOAD_SENSITIVITY_109_V1/FINAL_REPORT.md)；[原始RECEIPT](https://github.com/swayhrl/accel-sim-framework/blob/1ad28dbe2fe7280aea46a24f6ba9a97c021b08b7/docs/ai_workload_research/runs/AI_ARCH_A79_QWEN25_3B_NATIVE_WORKLOAD_SENSITIVITY_109_V1/RECEIPT.json)。

## 1. G0完成的资格工作：真实但严格限于CPU

- 固定模型为`Qwen/Qwen2.5-3B-Instruct@aa8e72537993ba99e69dfaafa59ed015b17504d1`，BF16、未量化、TP1；执行者对现有本地模型12个manifest文件（含两片权重）报告完成**只读完整流式SHA256 12/12 PASS**，软件vLLM 0.30.0两个固定源码文件SHA一致。该大模型本地6GB级权重不是本审查重新读入容器验证的，保留`EXECUTOR_REPORTED_HASH`证据水平。
- A00/A01源字节hash以及原始512-token ID文件和标准紧凑ID数组SHA与历史完全相同；2026-10-26 CPU新生成的2048-token每源各精确一组：A00源前缀9445 UTF-8字节、A01前缀8954字节；保持冻结原文本/同tokenizer/chat template，未拷贝、填充、拼接或访问sealed B/PG-19。2048行为是CPU tokenizer资格，**不是模型生成的任何output或GPU数据**。
- 历史MP02_A合法输出参考文件的本地SHA与原收据相符，**仅确认参考资产存在**；没有新的H0模型输出与历史reference进行数值核对。
- 安装版本记录为vLLM0.30.0、torch2.13.0、transformers5.18.0、tokenizers0.23.2、jinja2 3.1.6。第一次CPU tokenizer接口返回`BatchEncoding`容器，明确抽取`input_ids`后两个旧512数组全部一致；不构成原tokenizer数值变化。另一个metadata HTTPS timeout用固定README的受限license字段披露补足。两项均属于预算内非科学工程处理。
- 模型许可记录为研究与非商业使用；WikiText官方README元数据CC BY-SA3/GFDL与正文CC BY-SA4之间**版本声明不一致**，此事实未被消除；本地受限使用及署名由执行者陈述，不能将材料来源写成通用正式许可法律鉴定。
- **冻结合同**`FROZEN_SCIENCE_CONTRACT.json`在实际lock attempt之前形成：G1=512/32一项、容量544；G2=A00/A01×(512,2048)×(1,32)，统一容量2080；2warmups＋5formal/点，精度/强compiled Mode A/资源上限/判据均不变。新cache隔离接口进行了静态准备，但**GPU编译、cache创建和compiled数值路径从未触发**，不能把准备好接口升级为已运行PASS。

## 2. GPU资格真实终止：无GPU意味着不能评价性能

独立读取`raw/ADMISSION.json`与`GPU_RESOURCE_RECEIPT.json`：

| 门/指标 | Git原始记录 | 独立科研解释 |
|---|---|---|
| 非阻塞`flock`尝试 | **1次**，状态`SINGLE_NONBLOCKING_LOCK_CONFLICT` | 依照合同碰到占用就退出；**没有等待、轮询或第二次锁尝试** |
| lock ownership | `lock_acquired=false`、`lock_released=false` | 根本没取得锁；`lock_released=false`**不是忘记释放已持有的锁** |
| CUDA、NVML、模型初始化 | 各 **0次** | 无自己的GPU上下文、无模型、无CUDA编译 |
| G1/G2 | `NOT_ADMITTED` | H0及C01–C08全部未运行 |
| formal TSV | 仅列头，**0条样本** | 完全没有GPU时间、输出token、性能斜率或数值PASS/FAIL |
| GPU持锁时间 | **0秒** | 没有消耗GPU预算 |
| GPU独占完整收据 | `EXCLUSIVITY_EVIDENCE_COMPLETE=false` | 未获得锁就不能记GPU独占PASS；没有GPU PID/NVML样本也不能推断谁占用GPU |
| STOP | `GPU_RESOURCE_DEFERRED` | 合法的资源中止，不是`ENGINEERING_STOP`或`PERFORMANCE_NEGATIVE` |

本独立审查直接核`supervisor.py`：通过`fcntl.flock(lock.fileno(), LOCK_EX|LOCK_NB)`唯一一次取锁；`BlockingIOError`立即将`GPU_RESOURCE_DEFERRED`写入receipt并return，路径位于`nv.nvmlInit()`、CUDA子进程`Popen`之前。因此从源码结构上支持`zero CUDA/NVML/model`陈述，但实际主机运行情况依旧由执行者提供的原始收据承担证据。该代码首先`import pynvml`仅载入Python模块，不等于`nvmlInit`。

冻结时间追踪：开始epoch1792983527（2026-10-26 10:58:47 GMT+8），G0冻结约11:13:20（约873s后）；最终RECEIPT记第一次归档前目标约1401s总耗时，用户报告约24分钟合理。监督器`whole_Goal_elapsed_seconds=873.19`仅至lock-conflict归档，**不能误写成最终Goal只运行14.6分钟**。进程树RSS仅helper样本与终态快照，没有持续全树峰观测，不宣称严格的16GiB RSS实测PASS；新增worktree终态文件体积有snapshot而非连续峰。

## 3. 数值、科学目标和当前资源条件

`NUMERIC_AND_IDENTITY.json`的`numeric_result=NOT_MEASURED_NOT_ADMITTED`，`ANALYSIS.json`的`phenomenon_classification=NOT_MEASURED`、`hardware_headroom_or_projection_claims=0`；这与正式TSV空表相互印证。

**没有任何A79 Native performance结论：**
- 不能与旧MP02 354.598ms计算新漂移；
- 不能比较512/2048输入，不能给生成长度1/32的wall、interaction或KV访存；
- 不能对比cache、TC、DRAM、TLB/SM资源压力；
- 不能断言新VLLM compiled路径或新长文本的GPU数值正确性；
- 不能将`GPU_RESOURCE_DEFERRED`算作`NO_STABLE_DIFFERENCE`、`INPUT_OR_BACKEND_NO_GO`或硬件无加速空间。

本轮没有现场观察锁owner/PID，也**没有证据判断目前109仍被相同任务占用**；只证据化当时的锁冲突。不要擅自检查、抢占、重置或杀死其他工作任务。

## 4. 对未来复跑的明确意见

**接受STOP，不允许同一原Goal隐式续行或后台重试。** 如果用户同意再安排一次新的A79R1/续行，应复用**已冻结的科学输入、数值判据、G1/G2点阵和独立A79程序**，而不是重新设计问题或提交第三次C16 Stage A。首先仅做当前本地资产/cache/source SHA及执行环境变更检查；已完整校验的6GB权重通常不必为准备文档再额外归档一轮，但是否可复用原冻结收据必须基于同一受控路径和文件未变、记录恰当证据强度。若旧`.private`输入没有保留或身份无法核验，就STOP/单独资格审查，不能从Git的哈希凭空重建隐私输入。

若启动一条新Goal：
- 用户新的明确GPU任务许可与资源预算必须独立发布，不能自动当作本次未消费720s预算延续；
- 仍然单次非阻塞锁，冲突可再DEFER，不能为“保证成功”在109后台定时轮询、排队或侵占AWMA/ISCAS/GPU；
- 一次性在真实空闲窗口运行H0和条件G2并保留全套正式原始收据；任何实际compiled Mode A/fresh cache路径未通过数值或控制门就STOP；
- 不自动Profiler、simulator、调整低层资源或发布新机制。

**建议优先级：** 既然G0已经完成，A79R1只值得在可合理确认的空闲GPU窗口进行一次轻量续行；无空闲窗口时不必重复占用Codex做没有新科学信息的文献审查。其他主线可独立开展科学工作，但不能混成A79跑过GPU。

## 5. 项目归档与边界

- 本A80只在`hrl/ai-workload-research-coordination`保存独立审查和主线状态，不修改A79执行分支、19个原交付/源码、不merge其HEAD。
- C16 Stage A四DQ与B4/Observer旧STOP、AWMA翻译模拟器身份及独立任务、A67 GNN软件负结果、A74-C iso-PPA PARKED、A77 W/S不配对等科学终态全部不变。
- **A80终态：A79_G0_QUALIFIED_LOCK_DEFERRED / SCIENTIFIC_EXECUTION_ZERO / REVIEW_ACCEPTED / NO_GPU_NEXT_GOAL_AUTHORIZED。**
