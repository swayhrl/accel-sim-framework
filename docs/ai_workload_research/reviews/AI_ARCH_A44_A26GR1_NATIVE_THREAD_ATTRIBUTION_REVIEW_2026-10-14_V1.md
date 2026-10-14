# A44｜A26GR1独立审查：真实原生PASS，线程等待归因需收紧

**审查：ChatGPT／AI-ARCH Discovery，2026-10-14。**

**裁决：** 接受R0/R1/R2/R4，R3为有界真实训练功能与诊断PASS；保留已观察的OMP16下主机服务成本，但不能认定Cache/PCIe/CPU带宽瓶颈、可回收30ms时间或新机制资格。原Lane M已STOP，本审查只读源、Git身份和raw，不修改执行分支。

- 执行HEAD `cf80f6ec07a31eccdaff264c3bce64e0511179f8`，tree `c66008a9da553d06a00195c8c133c3e7ec16692d`，远端branch identical。相对原A26G STOP新增78文件，运行证据子树60、tools源码18。
- 两次从零连续训练到15200步；相机ID全15200步顺序一致；Gaussian最终分别6,672,954和6,684,932，状态非逐bit等价。早期质量API有限PASS，不是200k收敛。
- 修正轨迹窗口14500–14600和15100–15200，后50步未插桩mean分别132.480、133.810ms；前50步诊断mean分别186.431、147.425ms，不能相减推插桩开销。14500单步诊断2.454757s；其他49步描述性均值140.139ms。
- 通过GitHub读取并独立解析raw blob `004e857d14b55c501d9303e11e4102fdef5edda3`的15200条记录，及150条GPU事件。原summarizer把所有 `synchronize` 合为一类，既包含GPU子线程作者源码L728，也包含主线程L1023/L1074；`join@L1075`及D2H则在主线程。
- 两后期50步诊断原跨线程sync+join+D2H区间并集均值30.871/32.128ms，已独立精确复现。**仅主线程sync+join+D2H区间并集为14.084/14.746ms。** GPU子线程同步17.573/17.382ms，其中15.813/17.382ms与主线程CPUAdam重叠。因此原30–32ms并非全部主线程暴露等待，也不是硬件speedup上界。
- 同步host单调时钟比较：14500组有CPUAdam的49步中45步GPU工作子线程先结束；15100组50/50步先结束。CPUAdam结束比worker结束平均晚37.115/40.413ms。CPUAdam调用区间57.746/64.779ms；join后的下一步参数前递Adam调用41.855/45.489ms。**这定位的是当前OMP16下CPU处理分支与数据交接的成本候选，尚不能归因于特定物理资源，也不能把CUDA event span与host时间直接相加。**
- 原源码已有parameter forwarding/deferred optimizer；ASPLOS26 CLM有CPU offload/camera复用/双缓冲/Adam重叠，都是强近邻。后期GPU-only、线程策略、同语义软件对照、CPU/GPU/PCIe真实资源、长期质量与stable Gaussian ID都缺失。
- 资源合同和输入身份收据没有本轮发现的越界。受限CPUAdam源保持`omp_set_num_threads(64)`，但实机运行以OMP_THREAD_LIMIT16限制；不能声称作者64线程软件性能被复现。

**下一步：** 本轮A44已完成线程归因原始证据再计算，无需重派相同CPU审计。若继续3DGS，先用强软件/OMP与CPUAdam/前递时序反证；确有剩余再独立审批有界晚期native/资源诊断。不得从未完整保存的后期状态直接resume；不自动启动GPU/模拟器/新Cache机制。A43点云稀疏卷积和ANNS仍为独立探索备选。

固定证据：[原报告](https://github.com/swayhrl/accel-sim-framework/blob/cf80f6ec07a31eccdaff264c3bce64e0511179f8/docs/ai_workload_research/runs/AI_ARCH_A26GR1_GSSCALE_RUBBLE_109_V1/FINAL_REPORT.md)；`MEASUREMENT_WINDOWS.json`、`FINAL_DECISION.json`、`raw/host_late_verified/raw_steps.jsonl`、`raw/host_late_verified/gpu_event_spans.json`、`tools/aiarch_a26gr1/summarize_native.py`、`tools/aiarch_a26gr1/native_runner.py`，均以最终提交固定。本研究属Git/raw的独立CPU端重算，不是本机新增GPU执行。