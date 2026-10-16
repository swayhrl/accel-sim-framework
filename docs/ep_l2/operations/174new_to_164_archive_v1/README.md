# 174-new→164 Storage-Ops执行入口

当前执行优先级以[V5桥接修正](AMENDMENT_BRIDGE_CORRECTION_V5.md)为准；已授权归档根、保护范围和资源限制见[V4](AMENDMENT_SHARED_BRIDGE_V4.md)，源FS证据见[V3](AMENDMENT_OVERLAY_MAPPING_V3.md)，另保留[V2](AMENDMENT_SSHFS_V2.md)和原[Goal](GOAL.md)。

174-new独立目标侧当前精确回执15/36 Git临时pack已归档约4.502GiB并三端SHA一致，但使用了V4禁止的`/root/share/container-workspaces/hrl-174-new/staging/`。旧174源侧在另一个仓库`swayhrl/gpu-l2-cache-verilog`的分支`hrl/ops-174-source-audit-exec-v1`指出V4中转根缺失，这不是两份回执相互否定：已有归档副本保留，**新批次必须在当前单文件传输结束后先切换到V4指定桥接根并跨容器探针验证**。

当前不批准删除任何Git临时pack；源空间实际释放0B。下一阶段优先已审计、可确定重建的Verilog `.vvp` scratch S01/S02，并继续挖掘低风险scratch；不得为赶进度取消hash、资源守护或删除原始科研证据。两个Ops窗口不修改、不重启六个EP-L2 Lane。