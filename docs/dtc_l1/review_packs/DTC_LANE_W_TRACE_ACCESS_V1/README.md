# Lane W CPU 只读 trace 访问风险包

入口：[LATEST_REPORT.md](LATEST_REPORT.md)。当前 `DEFERRED_SAFE_STOP`；已完成原输入身份、既有 CPU proof 和源码语义审阅，未进行地址/PC scan。

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
