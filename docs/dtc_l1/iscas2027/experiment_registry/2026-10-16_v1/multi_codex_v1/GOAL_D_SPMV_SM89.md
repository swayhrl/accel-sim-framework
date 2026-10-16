# Goal: DTC_SPMV_SM89_ADMISSION_FEASIBILITY_109_V1

109新Codex窗口，CPU-only辅助任务；不是重启已经完成的native109 producer。先读本目录README，检查当前活动任务/锁，不抢GPU、不换工具链。

独立结果分支建议`hrl/iscas2027-dtc-sm89-admission-109-v1`。主证据：producer890fb0be7e681a60419c49ca0a7aa85731d8c164；consumer e3dbe3dbf2abb49b923244538d2a3d1828024d4f中的`PRODUCER109_CONSUMER_REVIEW_V1.md`和`review_pack/producer109_v1/`；当前构建Framework18a68dcccd795f1b6cda75504e9450d00c9cee02。只读现有109/164已验证payload，无需重新抓trace。

SpMV四个完整kernel的SM89/tracer5记录已通过生产/消费格式核查，共353256 active-thread instructions，原canary因无binary89 dispatcher退出0但没有执行，被正确拒绝。opcode root在Ampere表里有同名项不等于架构别名正确。LayerNorm仍SM86且跳过CALL，不属于本任务。

## 有界步骤

1. 检查现有AWMA/C16/Accel-Sim兼容资产是否已有**来源可查的**SM89解析/分类支持。配置名SM89、曾在真实4080运行、或者直接case89复用86都不是证明。复用的是source artifact和验证办法，不扩大旧平台资格。
2. 对SpMV全部实际opcode修饰符、寄存器/谓词、数据宽度、地址空间、barrier/reconvergence和branch行为建立覆盖表。区分trace已经决定的动态执行序列与模拟器仍需解释的依赖/资源类型。时序表来源与语义支持分开。
3. 若已有可核的支持代码可直接隔离移植，制作最小候选patch，在独立目录做CPU解析及依赖/分类测试；保留原header=89，不删指令，不把unsupported exit0当成功。若无可信依据，提交具体不支持点和最小需要的验证，不自己假定ISA等价。
4. 本任务允许候选原型及CPU解析测试，不运行正式DTC性能或改变主Framework支持域。候选必须在主线科学审查后才允许一次完整SpMV准入canary；合格后再由A决定配对测量。即使准入，也只是该SpMV输入的有限支持，不等于全面Ada时序校准。

先用约2小时完成源码差异和可行性判断；有可信现成路径时额外约2小时进行隔离CPU验证，否则停止，不升级整个工具链、不重写LayerNorm、不增加第三个负载族、不根据预期性能更换SpMV小输入。原SpMV36 CTA/暖DRAM读0的边界必须保留，修通后也不包装成大规模压力测试。

输出`docs/dtc_l1/review_packs/DTC_SM89_ADMISSION_FEASIBILITY_V1/`：README、SOURCE_COMPARISON、OPCODE_COVERAGE.tsv、CPU_TEST_RECEIPTS、candidate patch、NEXT_DECISION.md。独立worktree、build及临时输出；不修改原native文件、全局LATEST_REPORT、主dispatcher。提交+fetch-back后给A，native GPU锁保持未申请。
