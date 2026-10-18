# AG2_EXECUTOR_CPU_QUALIFICATION_PASS

原174（huangrulin-174），CPU-only。资格仅覆盖本包的映射角色协议、候选解析器以及固定无GPU C probe 的真实系统 loader 启动路径。没有发布可发射模拟器的执行器，没有性能结果或执行预算。机器可读结论见 QUALIFICATION_RESULT.json。

旧 AG 的错误是注册与检查范围不一致：freeze_runtime.py 只注册已知ELF及helper，run_screen.py却要求全部文件映射已注册。事前遗漏 /etc/ld.so.cache；旧attempt继续 HOLD_STRICT_FAILED，绝不事后补清单或追认。

| 验收 | 最终结果 | 证据 |
|---|---|---|
| 原九项离线反事实 replay | 9/9，原失败不变 | evidence/LEGACY_NINE_REPLAY.json |
| 真实系统 dynamic linker 的 C ELF 启动 | exit0；128 个完整停顿 maps | evidence/cpu-final/CPU_TRACE_TERMINAL.json |
| cache 早期映射及解除映射 | mmap出口72；munmap入口123及出口124 | evidence/cpu-final/CPU_MAP_EVENTS.json |
| 正例及拒绝例 | 3/3 正例、31/31 预期拒绝；真实退出码0/42 | NEGATIVE_CASES.tsv |
| Core及旧运行库 | Core固定965dffe0，clean；旧11个runtime SHA全匹配 | evidence/READ_ONLY_SOURCE_BOUNDARIES.json、OLD_RUNTIME_READ_ONLY_SHA_RECHECK.json |
| 本Goal模拟启动/attempt/新UUID | 0 / 0 / 0 | NO_SIMULATOR_STARTS.md |

当前 cache SHA 为026c6716eea796297e7da1e0f63c3439bfa47108cf8a22fae80c59b22e9ec1ff。它由AG2在目标fork前重新读取并绑定设备、inode、大小、时间及角色；与旧事后SHA恰好相同，不改变旧AG在启动前未注册的事实。

工程修正完整保留：首次驱动结果写出时遭遇系统Python没有hashlib.file_digest；改为增量SHA后，在新目录重新冻结并运行CPU probe。第一组34项预期结果中两项fixture未到达预期分支（32/34），保留其退出码和原因；修复fixture后最终34/34。生产校验规则没有为通过测试放宽。两个C probe均自然exit0且已回收；原始CPU资料在独立 /workspace/dtc-lane-ag2-loader-manifest-174-v1/raw/，受控副本及版本差异在evidence/。

真实路径覆盖：系统PT_INTERP启动，没有--inhibit-cache、LD_AUDIT、LD_PRELOAD，也没有loader --list启动目标。仅对自有CPU child使用PTRACE_TRACEME，从exec最初SIGTRAP到每个syscall入口/出口停顿并读取完整/proc/pid/maps，直接调用候选生产解析器。不会将晚期缺少cache视为早期合格。其它架构、无cache主机正例、普通异步采样的瞬态完整性、多线程/子进程以及完整模拟运行闭合保持UNQUALIFIED，未测试部分不标PASS。

旧AG预算1/8、0完整strict、唯一UUID 5de274d3-f296-4ee8-a577-17cc661e718e、0完成kernel均保持。AA5独立1/4、0完整strict及451.4s/67kernel资源STOP保持。旧Framework及Core worktree clean，旧失败收据按SHA前后核验。AG2无新cohort/BASE/K1恢复、组合、论文改动或后续派发。

发布使用独立分支 hrl/iscas2027-dtc-lane-ag2-loader-manifest-174-v1。源码白名单与FILES_SHA256.tsv绑定全部受审文件；push/fetch-back的HEAD/tree/逐blob/clean核验收据保存于独立raw的FINAL_PUBLICATION_READBACK.json，避免自引用提交号。下一轮必须另获用户授权并完整科学预注册。
