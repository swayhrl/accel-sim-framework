# Window B host resource inventory（`SPECULATIVE_DIAGNOSTIC`，脱敏）

- 逻辑 CPU：512；物理核心：256；插槽/NUMA：2/2。
- B0 校准只使用 B 专属 worktree、binary 与 scratch；该包不含也不查询 Window A 进程或私有路径。
- closeout 观测 MemAvailable：26876648 KiB；SwapTotal：2097148 KiB；SwapFree：40 KiB。
- 常规恢复线保持为总内存 20% + 4 GiB；当前采用有效并发 1 的动态低资源 gate。
