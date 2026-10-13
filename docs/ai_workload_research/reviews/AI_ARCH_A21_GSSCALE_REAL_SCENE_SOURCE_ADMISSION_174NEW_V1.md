# Round A21｜GS-Scale 真实 Rubble 场景 source/input 准入

**执行者：Codex Lane T / 174-new / Round A21；2026-10-14（Asia/Shanghai）。**
**性质：CPU/source-only；CODE_ONLY、PAPER_AUTHOR_NATIVE、OUR_INFERENCE、UNKNOWN 分层。未运行训练、GPU、模拟器、安装或场景下载。**
**裁决：SOURCE_INPUT_CONTRACT_FEASIBLE_PENDING_ASSETS；实际输入仍为 INPUT_IDENTITY_PENDING，109 平台为 PLATFORM_UNQUALIFIED，硬件 headroom 为 UNKNOWN。**

## 1. 固定权威与资源边界

本工作从 A21 独立分支初始 HEAD **d3d5e235db0822a2404e05dcdb705ffc942e70ec** 出发；20h 协调权威为 **47acc712aff232bbb4685746ea68e9cb12bcc0a9**。先核其 [A20 三家族审查](https://github.com/swayhrl/accel-sim-framework/blob/47acc712aff232bbb4685746ea68e9cb12bcc0a9/docs/ai_workload_research/literature/AI_ARCH_A20_REAL_AI_WORKLOAD_REDISCOVERY_THREE_FAMILY_AUDIT_2026-10-14_V1.md)与 CURRENT_STATE，沿用其 GS-Scale/GSArch 近邻边界，不重做 HSTU、MLIP 或三领域检索。

174-new 预检：512 逻辑 CPU、load 408、CPU pressure some avg10 3.70%、full 0；RAM available 337 GiB、swap 2 GiB 已满；根盘剩余约 11 GiB。A21 worktree 约 2.4 MiB，未下载/解压场景。所有源文件为作者固定公开实现 [SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932](https://github.com/SNU-ARC/GS-Scale/tree/6471e958f7e318f4870234d8107e0aa91c2d6932)，此 2026-10 选定快照**未证明等于** [ASPLOS 2026 论文](https://arxiv.org/html/2509.15645)实际运行 commit。只读以下恰好八个源文件的相关位置；blob SHA 为 GitHub 固定 ref 回读。

| 文件 | blob SHA | 核查 symbol / 行锚点及用途 |
|---|---|---|
| [README.md](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/README.md#L7) | 3785173f83be3e95515bbc67a959ae5e8f4dbaf8 | L7–13 Intel-only/CUDA；L14–59 Rubble 资产和处理；L60–90 三路径与 split |
| [install.sh](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/install.sh#L1) | 8d793af62397fae2385a74ef186267b0342f2466 | L0–6 Python3.10、torch2.2.0+cu121、IPEX2.2.0 与扩展构建 |
| [examples/simple_trainer.py](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/examples/simple_trainer.py#L184) | c16b7b34e277401f675d0f6c9554f73c88df6660 | create_splats_with_optimizers L184–264；Runner.train L484–680；Rubble preset L1100–1123 |
| [examples/simple_trainer_hybrid_baseline.py](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/examples/simple_trainer_hybrid_baseline.py#L223) | 9993a462219d32aa5bd372b3d520f24bdb5fdd28 | CPU frustum_culling L223–271；host create/rasterize L273–590；train L590–760；Rubble preset L1265–1288 |
| [examples/simple_trainer_hybrid_optimized.py](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/examples/simple_trainer_hybrid_optimized.py#L239) | e37d13e3f7514aa81320994dab9853b06a9bb275 | host/GPU 参数与优化器 L239–344；GPU cull+gather L534–611；GPU forward/backward L614–674；prologue/train L677–1229；Rubble preset L1512–1534 |
| [cpu_adam/src/cpu_adam.cpp](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/cpu_adam/src/cpu_adam.cpp#L188) | f1b40eb4283cfd95c9b26b01448d7275f5aa0958 | calculate_update_ids L188–250；update_counter L253–271；adam_deferred_update L274–346；OpenMP/计数/ε |
| [examples/datasets/colmap.py](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/examples/datasets/colmap.py#L21) | 3177754aefffca799d03e40817d40cf0358ee705 | Parser L52–245、缩图 L29–50、文件名排序 L147–155、train/test L330–390 |
| [examples/requirements.txt](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/examples/requirements.txt#L1) | 992108e9ec5d6a074c32eb2d5edfe5d5840f6570 | L0–22 pycolmap 固定 Git、fused-ssim 固定 Git，其它部分宽松依赖 |

## 2. 一套真实 Rubble scene×software×time/quality 合同

**自然来源已定位（CODE_ONLY / PAPER_AUTHOR）：** 作者 [README L14–52](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/README.md#L14) 指向 Mill-19 **Rubble** 的 [rubble-pixsfm.tgz](https://storage.cmusatyalab.org/mega-nerf-data/rubble-pixsfm.tgz)，而非合成 MatrixCity。2026-10-14 本窗口只用 HTTP HEAD 见 200、Content-Length **9,773,995,561 bytes**、Last-Modified 2025-09-22、ETag **f9702b00013597490519bdea8f922a68-1865**；ETag 带分段后缀，**不是可宣称的 SHA256**。未下载或重算档案 hash；展开大小 UNKNOWN。作者另称采用 CityGaussian 预处理的 COLMAP，并把 train/test images 与 COLMAP 合并成单目录，在 Google Drive 提供合并文件；本窗口无法读取该 Drive 文件清单，合并包大小、版本和 SHA 均 UNKNOWN。原始 9.77GB 档案单件就大于本任务累计 200MiB 新增预算，当前剩余磁盘约 11GiB 也不支持无界解压。

**期望目录与处理（CODE_ONLY）：** data/colmap_results/mill19/rubble-pixsfm/images 与 sparse/0 下 cameras.bin、images.bin、points3D.bin；需要对原图做 4× downsample。README 的 colmap_results 路径与三份 preset 的 data/mill19/rubble-pixsfm 默认路径不同；源码 CLI 支持显式 --data_dir 指向实际合并目录，不能把两条路径误判为两套已核资产。作者三条 Rubble preset 都指定 data_factor=4、test_every=83、test_after=-1、max_steps=200000、eval/save/ply 在终点，batch 默认 1；实际启用的 densification 为 grow_grad2d=0.0002、grow_scale3d=0.01、refine_stop_iter=15000，position_lr=1.6e-5、scaling_lr=5e-3。Parser 按**文件名排序**相机/图像后以排序索引模 83 划 train/test；并读取 COLMAP points3D（除非改 init_ply），缩图用 BICUBIC，规范化相机和点。优化版默认 init_type=sfm，初始点在 rank 分配后又按 Morton 顺序排列。以上源代码定义的是**待冻结处理规则**，不证明实际场景文件与图像映射已闭合。

**输入身份缺口：INPUT_IDENTITY_PENDING。** 未来正式 scene manifest 至少应列：原档案 SHA256 与许可/版本、合并 COLMAP 的 cameras/images/points3D 每文件 SHA、图像文件名/相机内外参/点云对应表、train/test 合并与排序后的列表、4× 输出文件 hash 与缩放实现版本、实际初始 splat 顺序、训练 dataloader 每步相机 ID 序列、RNG 状态。源码 set_random_seed(42+local_rank) 与 shuffle=True 只能给种子/采样机制，不能替代真实相机序列和资产字节；当前没有一个可回放的样本 manifest。Rubble 论文评估分辨率为 1152×864、Real World Outdoor；这仍非本地已验图像大小。任何小帧或随机 Gaussian 代理都不等于完整自然训练。

**动态 Gaussian 身份：** source 的 GPU frustum_culling_gpu 得到当前数组 valid_ids，再 gather 活跃参数、CPU Adam/回传；DefaultStrategy 在 densification/prune 后可能改变数组长度与位置。故 row index 不是跨创建/删减永久稳定 ID。要比较可见集时间寿命，必须随 step 记录 stable ID、出生/删减 epoch 与 camera ID，不能从作者“大场景平均 8.28% 活跃”推跨步 reuse。未经实际 scene/step 运行，active-set 分布为 UNKNOWN。

## 3. 三条强软件路径与三个不相混的分母

| 路径 | 源码/作者给出的能力 | 科学使用范围 |
|---|---|---|
| **原 gsplat GPU-only** | simple_trainer.py 的全 GPU splats/Adam、render→loss→backward→optimizer；作者 README 推荐小场景或不 OOM 时优先 | **强比较基线**；同场景同 Gaussian 数/初始化/相机序列、同 rasterization 和质量合同才可比 step/epoch wall。真实目标若 OOM，仅记容量失败，不能给其时间比 |
| **naive host offload** | hybrid_baseline.py 以 host 参数及 CPU frustum_culling 选活跃 ID，再拷 GPU，主要用于定位朴素卸载代价 | **历史消融**，不能单独作为新硬件 headroom 的弱对照 |
| **完整 GS-Scale optimized host** | selective offload：means/scales/quats 留 GPU，opacity/SH 和其 Adam state 在 CPU；GPU frustum、活跃 gather、pinned H2D、gradient D2H、parameter forwarding、CPU deferred Adam/thread overlap。densification step 另有同步与重排 | **必须保留的强 host 对照**；作者软件已解决普通 host offload、cull、重叠和部分 CPU 内存访问。split-mode 是另一策略，未并入本报告的普通完整 host arm |

**分母一：同工作量性能。** 同一 Rubble 版本、训练相机/初始点及 Gaussian 数、步数/增密策略、loss/optimizer 与精度，在完整训练 step/epoch wall 内纳入 data prep、GPU render/backward、CPU Adam、H2D/D2H、同步、checkpoint/eval 的明确包含规则。作者论文按 epoch time 报吞吐，当前源码有训练终点 ellipse_time 与 GPU max allocated/reserved 字段，但没有本窗口能读到的真实每步 host wait/PCIe 字节或 109 时间，皆 UNKNOWN。不能把局部 kernel 时间相加当 wall。

**分母二：16GB 容量可完成性。** 固定目标画质与训练规模，报告 GPU peak allocated **和 reserved**、host RAM/pinned peak、实际 Gaussian 轨迹和是否 OOM。论文 Table 1 的 RTX4080 Super 16GB 与目标 RTX4080 16GB 不是同机；论文在该 desktop 报约 9M→40M Gaussians 是作者系统容量结果，不是 node109 fit。GPU-only OOM 条件下仅比较“能否完成/质量前沿”。

**分母三：达到画质时间。** 同一评估相机集合与 PSNR/SSIM/LPIPS 门，报告第一次达门的实际完整 wall、最终质量和 Gaussian 数；论文 Table 3 Rubble Original/GS-Scale PSNR **26.63/26.62**、SSIM **0.808/0.808**、LPIPS **0.194/0.194** 为作者质量对照，**并非**逐参数 bitwise 或本窗口 time-to-PSNR 实测。作者 deferred Adam 在预计算恢复项中近似处理 ε，虽然最终 Adam denominator仍含 ε，故不预设与原 GPU Adam 严格同一步状态等价。需独立规定容差、长期画质与相同 scene/相机/增密轨迹；若数值路径改变造成 Gaussian 数变化，吞吐与画质不能混写为同工作量因果。

## 4. 平台与最近邻：能推什么、不能推什么

论文 §5.1 的系统为 Intel i7+RTX4070 Mobile、Intel i9+RTX4080 Super、双 Intel Xeon+H100 PCIe，使用 gsplat v1.5.0、CUDA12.4、torch2.2.0；公开 install.sh 为 Python3.10、torch2.2.0+cu121、IPEX2.2.0 并构建 cpu_adam，README 称当前仅支持 Intel CPU。两版来源不同，不能把公开快照当论文确切执行环境。**109 CPU 厂商/ISA、隔离环境、IPEX 可用性、torch/CUDA/gsplat ABI、剩余 RAM/disk、完整 Rubble fit 都未由本 174 任务检查：PLATFORM_UNQUALIFIED。** 本任务不 ssh 109，不安装，也不从单张 16GB 推可运行。

A20 已登记 **GS-Scale** 自己具备 selective host state、GPU cull、parameter forwarding、deferred Adam/image split；**GSArch** 已提出冷热 Gaussian 与 atomic/bank 近邻，非本机 GS-Scale 强对照；原 **gsplat** GPU-only 在可放入内存的小场景可能更快。论文报告 PCIe 在作者条件下只占小部分时间，且优化 host 在 desktop 相对 GPU-only 的吞吐几何均值为 0.84×（排除 OOM），这些是作者多场景结果，不能从单点断言未来 109 的 PCIe/Cache 余量。只有强软件后剩余可观、可归因完整 wall，才可能讨论物理资源问题；目前 **P13_HARDWARE_HEADROOM_UNKNOWN**。

## 5. 裁决、下次最小合同与 UNATTENDED_20H_CLOSEOUT

**SOURCE_INPUT_CONTRACT_FEASIBLE_PENDING_ASSETS。** Rubble 是真实公开场景，官方 URL、处理路径、三套软件入口与三个评价分母可以写成未来可证伪合同；但资产 hash/合并 manifest/训练相机顺序及 109 平台资格仍未闭合，因此**没有**已可运行的场景、数值 PASS、容量 PASS 或新 GPU 授权。最小后续工作是经单独审批后获取/冻结真实 Rubble 与合并 COLMAP 的 SHA/列表及所需约 9.77GB+未知展开/合并空间，另由 109 原窗口只读核平台，再设计有预算的完整训练数值与性能资格。若这些不可得则 INPUT_IDENTITY_BLOCKED；若强路径无额外 wall 或必须改变数学语义才产生差值，则 SOFTWARE_ABSORBED/STOP；都不启动 cache 机制。

**UNATTENDED_20H_CLOSEOUT（A21阶段）：** 独立分支 hrl/aiarch-a21-gsscale-real-scene-source-174-v1；起点 d3d5e235db0822a2404e05dcdb705ffc942e70ec；2026-10-14 约 01:48 CST 开始的轻量源审，结束时间以提交回执为准。仅本报告写入，场景/权重/依赖下载 0，GPU/模拟器/109/164 接触 0；新增 worktree 约 2.4MiB、报告文本约十余 KiB，实际 commit/tree/blob 以发布后远端 fetch-back 回执及最终回答为准（报告自身不能包含自身 SHA）。A21 发布后停止该阶段，仅按总 Goal 转入独立 A22。
