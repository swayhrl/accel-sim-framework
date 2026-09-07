# C5：full speculative replay 资源闸门

状态：`SKIPPED_POLICY`，不是语义或实现失败。

执行 C5 判定时，`/workspace` 可用空间为 76,804,456 KiB（容量使用率 98%，约 2% 可用），
低于 farm policy 的 15% scratch 空间要求；swap 仅剩 216 KiB / 2,097,148 KiB。尽管
MemAvailable 约 63 GiB，空间和 swap 闸门均不健康。

因此没有启动 prefill/decode1 的完整连续 ROI 比较，也没有启动理想诊断的 full replay。
这保护 Window A 优先级及宿主机健康；受限 C4 结果仍明确标记为 speculative，不能替代
被跳过的正式/完整运行。
