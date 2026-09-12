# C15 resource, recovery and unattended policy

本文件只管新C15任务。不能停止、修改、renice、绑核或清理其他项目。截图不是实时准入证据；只读采样当前资源。不得因SwapFree很低、load average高或第一次sandbox失败就终止整个Goal。

## 1. CPU/内存/磁盘

默认A最多4个CPU worker，B最多4个CPU worker，C最多8个CPU worker；三lane合计上限16。A/B/C初始分别1/1/2，健康后逐步提升。限制OpenMP/BLAS线程避免隐式超卖；tracer如需编译仅在B隔离build中`-j4`。禁止build新的simulator。

连续3个10秒窗口满足下列条件时可新增低开销worker：CPU idle>=15%，MemAvailable>=48GiB且新增任务预计峰值的1.5倍+2GiB后仍保留32GiB，memory PSI full<=1%，io PSI full<=2%，iowait<=10%，实时swap总吞吐<=4MiB/s。未知峰值先用单worker有界canary，初始按4GiB预算；记录实际峰值后更新。

YELLOW仅不再加worker，已有健康自有任务继续。RED（MemAvailable<32GiB、持续memory full>3%、io full>5%、swap>16MiB/s或OOM）停止新增；必要时只对自己的可安全中断/断点续作业降载，保留partial和失败记录。无权限不得改系统设置、swap、cgroup或外部进程。

磁盘至少保留64GiB；本轮B新增trace+profile总输出上限32GiB，每deployment最多12GiB，单capture硬上限4GiB。达限是`BUDGET_CAPPED_PARTIAL`，不是完整capture PASS。C用streaming/sketch处理，不将整批解压进内存或磁盘。

## 2. GPU与原生采集

只有B可以启动C15原生GPU任务，并只在已有授权连接/设备上执行。首先读GPU UUID/型号/可用VRAM/现有owner/capability；没有实际GPU或不支持当前算子时，不用CPU结果冒充GPU。不会租服务器、建立新的付费会话或接受新模型条款。

每GPU同一时间最多一个C15 profiling/capture进程，默认全C15 GPU并发=1；不能多个profiler互相干扰。使用B自己目录中的owner lock，检查外部繁忙程度，不能抢已有exclusive设备。VRAM按模型+KV+workspace估算，并至少保留max(2GiB,20%总VRAM)；canary后按实测峰值调整。

本轮最多3个本地真实部署，每部署最多8个轻量scenario（不是8套trace）。先一个短B=1 scenario canary，1–2次warmup、3次原生重复和独立profile pass；再按矩阵扩展。decode首步与后续少量step标签属于scenario内部，不扩成大矩阵。

GPU任务累计预算4 GPU-active hours，全lane B记录；这是工作预算而非要求4小时内完成所有代码。单普通原生目录scenario默认上限10min（模型加载单独最多30min），单选择性capture最多20min；超过先保留partial并解释，不把超时当correctness错误。必要时改用已授权更短scenario并新ID，不能悄悄缩输入却保持原ID。captured target窗口最多12个/部署，优先2–4个。达预算后继续离线验证/集成，不继续加GPU任务。

## 3. 网络和环境

A只允许元数据请求：每config/index响应<=8MiB、单Safetensors header<=16MiB、每模型<=128MiB、campaign<=1GiB下载。HTTP Range先读8-byte长度，检查长度、206/Content-Range、revision/ETag再读header；服务器忽略Range时立即停止流，不将完整权重读完再拒绝。最多3次有退避重试；超大header标`HEADER_LIMITED`。

本轮完整Weight下载预算=0。已有本地cache可只读使用。缺访问权/许可证/gated model需留待用户，不绕过，不把API token写入日志。可选公开元数据候选需通过来源和revision核验，不凭记忆补字段。

优先现有环境。确需轻量Python依赖时只在C15私有venv安装已固定版本，不能升级共享CUDA/PyTorch或卸载系统包。默认禁止`trust_remote_code=True`；已有部署若依赖它，先源码固定与人工/既有审计证据，否则只做静态/importer。

sandbox/bwrap失败先最小只读命令重试，再用平台支持的明确权限申请。用户授权任务不是平台权限自动批准。平台拒绝时保留ENVIRONMENT blocker，改做可行离线工作；不得指导绕过隔离。git fetch不是本地已验证数据分析的硬依赖。

## 4. 恢复与失败分类

- `IMPLEMENTATION_ERROR`：parser、schema、path、tracer filter bug。添加可复现测试，修复并有限重试。
- `INPUT_IDENTITY_FAILURE`：隔离该输入及所有派生结果；不得继续晋级。其他独立数据继续。
- `CAPABILITY_MISSING`：无GPU/本地权重/可观测shape/权限。发布有证据缺口与可运行工具，不凭空补真数据。
- `RESOURCE_WAIT`：默认5分钟一次gate；等待时做独立任务，不busy-loop或刷屏。60分钟无进展且所有可行离线任务都完可发布能力受限checkpoint。
- `BUDGET_LIMIT`：保留已完成结果，输出下一工作优先级，禁止无限自动扩容或降阈值凑PASS。
- `SCIENTIFIC_TARGET_NOT_MET`：例如抽样误差过大。保留负结果；在预先预算内加样，否则`SAMPLER_NOT_QUALIFIED/INCONCLUSIVE`。

同类失败最多3次实质不同的合理尝试；不把“不断尝试”解释为重复同一危险动作。长期任务每完成一个小阶段/每30–60分钟有实质进度才checkpoint push。禁止复制巨大raw logs到Git。

## 5. 依赖与并行

A/B/C读取固定git对象和自有只读copy。跨lane只消费发布manifest，不访问对方私有scratch或正在原子重建的TSV。需要较大blob时只读来源路径须获对方manifest明确发布，校验SHA，不能覆盖。

每lane独立推进所有可做阶段。预计30分钟内不会出现的跨lane输入不阻止unit test、历史数据导入、静态分析和报告。最终无剩余可行工作且上游尚未发布时输出`INTERIM_READY_WAITING_INPUT`；不要把partial伪装full completion，也不要保持空转数小时。
