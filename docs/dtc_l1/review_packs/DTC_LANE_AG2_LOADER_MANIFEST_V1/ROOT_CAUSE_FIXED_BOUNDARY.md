# 修复边界

权威Framework为cc5f51ea068e5a234811d2fbe79a5ccdbab21769，Core为965dffe04366e665626de4afeb7ffebca8622b5f。旧AG所有历史文件、运行输出及冻结清单保留原样；分支从固定Framework提交创建，仅新增AG2目录。Core零修改。

| 旧行为/缺口 | AG2候选处理 | 证据/限制 |
|---|---|---|
| loader --list解析ELF，未预声明cache | 目标启动前精确注册cache及四类角色 | CPU_MAPPING_PREREGISTRATION.json；无事后补录 |
| path+SHA清单无文件角色 | 明确ELF_EXECUTABLE/INTERPRETER/SHARED_OBJECT、LOADER_DATA_CACHE | mapping_roles.py；角色与来源必填 |
| maps路径resolve后仅比SHA | 严格maps解析、canonical path、dev/inode、fd前后stat、命名文件stat、SHA及类型 | 同文件可多段映射；不通配、不忽略非ELF |
| 等到libcudart出现后采样 | CPU目标自exec最初停顿，每个syscall入口/出口完整快照 | 真实系统loader捕获cache并确认munmap；未实现正式模拟启动适配 |
| OSS Python --inhibit-cache测试缺早期覆盖 | 固定C ELF经系统PT_INTERP加载libc及私有CPU .so | 无GPU、无trace，无--inhibit-cache |
| 旧9项仅反事实 | 原样保留输入/源码，最小import/output重绑定后重新运行 | LEGACY_REPLAY_ADAPTATION.diff；其结论仍仅反事实 |
| 旧映射检查失败 | 永久保留HOLD_STRICT_FAILED与1/8消耗 | history/STOP_EVIDENCE.json及evidence/historical-attempt-receipts/ |

MAPPING_ALGORITHM_REVIEW.diff为旧collector/attestation与新候选算法的审查差异，不是对旧发射器的可应用启动补丁。SOURCE_ALLOWLIST.tsv限定新增代码；未更改模拟CLI、runtime_stat、K语义、Tag/finite/clock、输入、statistics、模型、Core或既有资源合同。没有将AG2的CPU PASS回填旧AG或AA5。

普通工程修正：便携SHA helper替代Python3.11专有API；两处测试fixture修正。所有先前CPU资料保留，源码旧版本逐SHA复原核验。没有变更科学合同、减少任何拒绝条件，未重跑性能。
