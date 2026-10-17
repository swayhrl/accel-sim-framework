# Lane W CPU 只读 trace 访问风险包

入口：[LATEST_REPORT.md](LATEST_REPORT.md)。当前 `DEFERRED_SAFE_STOP`；已完成原输入身份、既有 CPU proof 和源码语义审阅，未进行地址/PC scan。

独立CPU辅助模块和六组合成预检已加入；它们没有原trace读取入口，也不修改原decoder。再次运行合成预检后须重新seal，因为预检结果本身属于封存文件：

```sh
python3 -B docs/dtc_l1/review_packs/DTC_LANE_W_TRACE_ACCESS_V1/scripts/preflight_access_semantics.py
python3 -B docs/dtc_l1/review_packs/DTC_LANE_W_TRACE_ACCESS_V1/scripts/preflight_stream_access.py
python3 -B docs/dtc_l1/review_packs/DTC_LANE_W_TRACE_ACCESS_V1/scripts/preflight_cross_kernel.py
python3 -B docs/dtc_l1/review_packs/DTC_LANE_W_TRACE_ACCESS_V1/scripts/verify_pack.py --seal
```

在本 worktree 根目录验证封存内容（只读取 pack）：

```sh
python3 -B docs/dtc_l1/review_packs/DTC_LANE_W_TRACE_ACCESS_V1/scripts/verify_pack.py
```

如需重新生成本地身份/资源快照（会改写本 pack，不读取 trace body；不启动 scan 或 simulator）：

```sh
python3 -B docs/dtc_l1/review_packs/DTC_LANE_W_TRACE_ACCESS_V1/scripts/verify_pack.py --exercise-builder --seal
```

后者只读取固定 A/T/U git blobs、小型冻结源码、四个原 list、523个成员 stat 与 /proc；不会等待资源后自动执行。审计钩子拒绝 trace body/旧仿真 raw 打开、pack外写入，以及任何非 `git show` 子进程。`FILES_SHA256.tsv` 包含除自身外的所有包文件；`PROVENANCE_SHA256.tsv` 固定所消费 git blob 的SHA。`.g` 文件是原始kernel列表索引，无trace正文；原trace和旧仿真raw不在此包。

`CPU_AUDIT_GUARD.json` 限定于整理脚本重跑的动态行为；不宣称审计了已有外部后台进程。`RESOURCE_PREFLIGHT.json` 中的simulator PID是外部活动，不是本轮attempt。U输入通过不可变提交读取；不读取U当前raw。

`stream_access_scan.py` 默认只做准入检查，并将记录写到独立W scratch；当前返回退出码2表示高I/O/磁盘压力阻止读取。只有显式`--scan`且所有准入条件通过时才读取指定Gaussian/GEMM；不修改trace/decoder，不启动模拟，不自动发布原始地址索引。任何合成预检结果都不是原trace扫描结果。
