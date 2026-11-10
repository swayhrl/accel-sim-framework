# Stencil EXT0/1/2 阶段对照

三点同 Source、ELF、输入、100 个有序 kernel、283 项实际选项，只有 `-gpgpu_ep_l2_victim_extension` 为 0/1/2。每点均为 `CLOSED_ACCEPTED`，各自一次确定性完整应用；逐点压缩 raw 各只读一次，并与 Native DONE SHA、接受 bundle、每 kernel 的 64 个 B0/M0 slice 和末尾 106 cycles 守恒。

| 对照 | 应用 cycles | 净差 |
|---|---:|---:|
| EXT0 | 4,768,893 | 基线 |
| EXT1 | 4,787,045 | 迁移包 +18,152 |
| EXT2 | 4,786,427 | CLEAN 策略包 -618 |

总净差 EXT2−EXT0 为 +17,534 cycles。100 个 kernel 的方向数：迁移包 {'slower': 100}；CLEAN 策略包 {'faster': 59, 'equal': 1, 'slower': 40}。逐 kernel、每 10 kernel 箱、按 EXT2 response 有无分组及局部计数见 JSON/CSV。

EXT1−EXT0 识别的是扩展硬件迁移包的净效应；EXT2−EXT1 识别的是同扩展硬件下开启 CLEAN 策略包的净效应，包含查询、spill、占用和服务。局部 B0/M0/Ext 计数可能重叠，不能相加为应用关键路径周期。此对照不能证明物理 PPA、能耗、应用数值 oracle 或跨负载稳健收益。
