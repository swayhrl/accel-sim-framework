# Lane 6 r3：撤回旧应用证据，保留机制与成本，强制当前科学接收

续行authority：a41bfb55934303a4d4a342762f74a16d137d0316；同Lane/分支/Goal。
先读PAPER_DRAFT_ZH_V3.md与RETRACTION_APPENDIX.md。r1/r2保持不可变。

当前正式性能pair=0、应用run=0、均值null、主性能图为空。旧sad图及“基本持平／
无容量收益”解读均撤回科学效力。三组旧应用六次原始执行保留，另外四条未执行。
不删除旧图，不修改raw/CSV/二进制/输入/终态。图表清单只保留独立历史诊断和locality。

PPA账保留146/145KiB数据与双方128B/slice latch、RO配置容量N的修订，明确旧
代码违反physical-cycle服务合同，不能把代码/算术账当成已合格硬件或应用效果。

当前入口：acceptance_gate.py + result_intake.py + native_pair_intake.py +
plot_qualified_pairs.py。无CURRENT_ACCEPTED禁止汇总/绘制正式结果。精确在线
契约见RESULT_INTAKE_CONTRACT.md。REJECTED_OLD_SAD_ADAPTER仅供拒绝回归验证，
不是可运行的正式应用/制图spec。没有自动复用r2 adapter或旧证书的默认项。

离线合成测试：
```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 PATH/test_result_intake.py
```
真实只读撤回审计（需要GitHub及已fetch精确source，不运行模拟器）：
```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 PATH/audit_retractions.py --framework-repo REPO --output-dir NEW_DIR
```

所有论文、PPA、撤回索引和审核结果在本pack；STATUS/RECEIPT在原Lane6目录。
当前磁盘free已在registry锁下实测，未更改48GiB门槛、未清理或构建；官方R0.1
由Lane1冻结、Lane5独立资格后才能接新结果。不阻塞修复流程。
