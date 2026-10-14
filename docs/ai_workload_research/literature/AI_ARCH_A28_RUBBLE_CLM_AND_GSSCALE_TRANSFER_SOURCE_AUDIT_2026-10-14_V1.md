# Round A28｜Rubble是什么？CLM强近邻与GS-Scale静态字节/关键路径审计

**执行者：ChatGPT／AI-ARCH Discovery；日期：2026-10-14。**  
**任务权限：`SOURCE/PAPER_ONLY`。A26GR1在node109下载Rubble期间，研究者**没有访问或干预正在运行的Codex、109/164、文件目录、GPU锁、下载及训练**；仅阅读公开论文和作者固定Git源码，并在独立AI-ARCH协调分支记录笔记。**  
**结论：`REAL_RUBBLE_INPUT_EXPLAINED / CLM_ASPLOS26_STRONG_DIRECT_NEIGHBOR_FOUND / GSSCALE_STATIC_TRANSFER_LEDGER_DERIVED / NO_NATIVE_OR_MECHANISM_ADMISSION`。**

## 0. 实际场景的来源、大小和数据类型

- Rubble（碎石/废墟场景）属于CMU的[Mega-NeRF／CVPR2022](https://meganerf.cmusatyalab.org/) **Mill 19**无人机航拍真实照片集合；Building是工业建筑，Rubble是其附近的施工废墟场地，不是同一场景的时间上连续训练轨迹。原[正式论文](https://openaccess.thecvf.com/content/CVPR2022/papers/Turki_Mega-NERF_Scalable_Construction_of_Large-Scale_NeRFs_for_Virtual_Fly-Throughs_CVPR_2022_paper.pdf) Table1报告**Rubble 1678张4608×3456照片**（原作者论文数字，**不是本机已核tar里实际图片数**）。
- GS-Scale官方固定源[`SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932`](https://github.com/SNU-ARC/GS-Scale/tree/6471e958f7e318f4870234d8107e0aa91c2d6932) 使用`data_factor=4`，故原宽高各除以4应是**1152×864的目标分辨率**；真正派生图片清单/quality仍待执行侧byte级回读。
- A26G执行侧固定[报告`e760f332…`](https://github.com/swayhrl/accel-sim-framework/blob/e760f332ed41c609d3d19548f87d90b3f11357d8/docs/ai_workload_research/runs/AI_ARCH_A26G_GSSCALE_RUBBLE_109_V1/FINAL_REPORT.md)确认官方`rubble-pixsfm.tgz`压缩实体大小**9,773,995,561 B（约9.10GiB）**，另外作者Google Drive COLMAP`cameras.bin(64 B)`、`images.bin(427,380,490 B)`、`points3D.bin(162,597,265 B)`三份合计**589,977,819 B**。A26G时这些只是头部/部分范围/作者目录元数据，**不是完整实体身份PASS**。
- 从照片＋COLMAP相机内外参／照片关联＋SfM点云构造初始Gaussian，经真实camera选取、渲染、反传、参数与optimizer更新得到三维表示。原始大图片字节**不会要求一次性全部放进16GB显存**；GPU工作集由软件、当前相机和真实Gaussian状态共同决定。
- 不允许在正在执行的A26GR1中偷偷切换下载源；本研究新增的任何他人再处理数据集只能作为**不同provenance**的未来选项，不等于作者GS-Scale的官方合并COLMAP。

## 1. 新找到的**直接强软件最近邻**：ASPLOS2026 CLM，而非仅GSArch

- 作者论文：[CLM: Removing the GPU Memory Barrier for 3D Gaussian Splatting](https://arxiv.org/html/2511.04951)，ASPLOS2026。直接核`§2–6`中的`Table1/2`、`§4.1/4.2.1–4.2.3`、`§6.1–6.4`；**这是PAPER_AUTHOR，不是本机实测**。
- 作者公开源码固定快照[`nyu-systems/CLM-GS@1119a10198b8398a81d4fcad0d5d407f8a330543`](https://github.com/nyu-systems/CLM-GS/tree/1119a10198b8398a81d4fcad0d5d407f8a330543)；`README.md` blob`df88b01f4dc9484fff2602ed48e19f1cfdf34187`、`release_scripts/rubble4k_README.md` blob`3ce480e84098d70870b77f20af101074510808cd`、`rubble4k.sh` blob`d06f38b9b34dd6d7f2cb28987bdf3dec37177de3`、`strategies/clm_offload/README.md` blob`278d322dfb278d8e81aef9b22b7df2e348df2fd3`。**2026-10选择的HEAD≠论文实验确切commit已验证**。
- **真正创新碰撞**：CLM已经在真实3DGS训练中实现`selection-critical属性GPU常驻`（CLM`xyz/scaling/rotation/opacity`合计11 FP32字段、SH48字段CPU pinned）、预先frustum选择、**batch内相邻camera的Gaussian交集精确复用**、双buffer/通信stream、CPU Adam与通信重叠、相机访问顺序优化。**“相邻训练视角缓存Gaussian”“用camera顺序增加reuse”“异步CPU Adam/gradient/prefetch”均非无人研究的问题**。
- CLM确实使用同一真实**Mill19 Rubble**来源，但作者固定脚本是**4K、bsz=4、100000 image iterations、10M/28M两个densification设定**，配其自己公开的`rubble-colmap.zip`处理版本/Google或Hugging Face；GS-Scale固定代码是**4×下采样1152×864、batch1、200000 steps、另外的官方合并COLMAP/算法**。两个论文是独立软件系统，**两套Rubble“名字相同”不保证同训练字节、camera顺序、Gaussian规模、batch/optimizer语义和质量门一致**，不能跨平台算`CLM比GS-Scale快/慢`。
- 具体作者公开Rubble4K`RTX4090 + AMD Threadripper PRO 5955WX(16核)+128GB RAM`实验组：`10M no_offload 16.81GB/11702s`、`10M clm_offload 7.05GB/12381s`、`28M clm_offload 13.0GB/24757s`、`28M no_offload OOM`；这**不是109 RTX4080、GS-Scale 1K或本研究原生数字**，尤其不能以显存13GB就断言109上可合法跑CLM 28M。
- 原论文`§6.3`对Rubble/BigCity实际做过CPU Adam和通信/计算重叠时间分解，且有不同view order与batch scheduling消融。故若今后研究GS-Scale的“强软件后剩余等待”并申请新机制，**必须把CLM至少纳入论文最近邻与可替代软件解释**；更换CLM作执行baseline将是**新的软件科学身份/实验合同**，不在当前A26GR1授权内。
- GSArch（HPCA2025）有hot/cold Gaussian buffer和gradient atomic/bank-conflict硬件近邻，但先前只得IEEE摘要；CLM是本轮直接审过全文HTML/可定位具体作者实验组的**更强、实证明确的近邻**。两者都不自动否定“可能还有硬件剩余”，但显著提高新机制的新颖性/软件headroom门槛。

## 2. 从固定GS-Scale真实源码推导的**条件性字节模型**（不是观测流量）

固定源[`simple_trainer_hybrid_optimized.py`](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/examples/simple_trainer_hybrid_optimized.py)的默认`feature_dim=None`、`sh_degree=3`、FP32张量与Adam两个moment；实际任何不同`dtype`、feature_dim/optimizer/压缩/配额都需重算：

| 每Gaussian状态 | 源码字段/推导 | 名义字节 |
|---|---|---:|
| GPU常驻几何parameter | `means(3)+scales(3)+quats(4)`=10个FP32 | **40 B** |
| 对应GPU Adam的两个moments | `exp_avg`与`exp_avg_sq`各10 float | **80 B** |
| CPU常驻外观parameter | `opacity(1)+sh0(3)+shN(45)`=49个FP32；SH系数`(3+1)^2×3=48` | **196 B** |
| 对应CPU Adam两个moments | 每个49 float | **392 B** |
| 不含grad的合计常驻model+Adam | GPU 120B＋CPU588B | **708 B/Gaussian** |
| 全部grad都实际物化时，条件性增量 | CPU49 float+GPU10 float | **236 B/Gaussian** |
| 所有参数＋grad＋两组Adam完整物化的理论上界 | `59×4项×4B` | **944 B/Gaussian** |

额外的CPU计数器（byte）、bitmap、pinned staging、camera/image、可见ID、CUDA中间张量、allocator碎片、实际梯度布局/临时副本等**不包含在708/944B里**。故这些是**结构化标称字节，不是HBM/RAM真实峰值，也不是Cache真实访问数**。它与[CLM原论文Table1/§2.2](https://arxiv.org/html/2511.04951)59参数×(weight+grad+2 moments)的建模形式相符；两软件的CPU/GPU驻留分割不同（CLM把opacity置GPU）。

**每次活跃Gaussian的可见状态跨CPU↔GPU传输“标称payload”**：
- `valid_ids.to("cpu", non_blocking=False)`：假设当前GPU index为32bit，名义**4B D2H**（实际索引dtype由GPU kernel确认，**不能提前认定4B已成立**；若int64则8B）。
- 完整CPU外观字段H2D：`opacity+sh0+shN`，名义**196B H2D**；源码`colorsN`数组全`(N,15,3)`，按180000行左右分片，单块约**32.4MB（十进制）**。
- GPU loss/backward之后的外观gradient回CPU：若三数组均实际物化，名义**196B D2H**；部分零梯度/None或特殊缓冲需要原生确认。
- 因此条件性初值**约396 B / active Gaussian / step**（196+196+4），**不含**额外`info.gaussian_ids/radii/means2d`、真实总线事务、GPU cull、CPU参数读写、重复数据/重叠与传输格式改变。这个系数**不是已测PCIe traffic，不得用于声称带宽受限**。

**尚未测但值得独立区分的软件混杂**：
1. `gpu_forward_backward`用`sh_degree_to_use=min(step//sh_degree_interval,3)`，默认间隔1000步；与此同时`rasterize_splats`准备/上传完整45个`shN`系数，不根据当前启用阶数缩小host→GPU payload。早期是否产生**对渲染未使用的系数上传**是有源码根据的**软件诊断假说**，不是已测浪费，也不是硬件新功能。
2. `cpu_adam/src/cpu_adam.cpp:calculate_update_ids`对`counter`和bitmap作多次**遍历总Gaussian数N**的操作，再结合`valid_ids`；`update_counter`也全体遍历`N`，可与真正`adam_deferred_update`更新的`U`个高斯区分。特别在可见比例低时，**全体计数器扫描`O(N)` != 选择性Adam参数更新`O(U)`**；作者还显式`omp_set_num_threads(64)`，目标node109是16核/24逻辑线程。若看到CPU耗时，先排查**线程/扫描/选择器/内存布局软件因素**，不能直接判CPU内存带宽瓶颈。
3. `torch.cuda.empty_cache()`有条件地在当前`valid_ids/N>0.1`时调用；训练densification时也可能强制刷新CPU状态、重置counter、第二次cull；这些时段和普通稳态step**不能混同分母**。
4. GS-Scale`checkpoint`主要保存`step/splats.state_dict()`，未形成完整optimizer、counter、RNG和数据加载器状态恢复权威；**不能把后期checkpoint读入当作从头连续训练达到后期的科学样本**。

## 3. 下载完成后真正可接受的结果：一张合并审查清单（并不要求新实验）

| 观测 | 必须的结果身份与反例 |
|---|---|
| **真实asset** | 真正完整Rubble原实体SHA、tar安全成员表、作者三COLMAP二进制完整SHA及camera↔image↔point验证；其他HF处理版本**不能自动替换** |
| **强软件** | frozen GS-Scale实现、runtime env、CPUAdam thread上限实际工作、作者源码中的GPU geometry/CPU appearance分布；不能把CLM/GS-Scale不同算法结果当一个baseline |
| **功能与数值** | full camera→cull→param loading→render/loss/backward→grad returning→CPU/GPU Adam→state available，原loss/quality合同；少量step PASS只算EARLY_ONLY |
| **时间与流量** | 先实测`N_total`、`N_visible`、`N_updated`、`sh_degree_to_use`、CPU global counter scan/update、H2D/ID+grad D2H、GPU render/backward和真实`synchronize/join`**未隐藏wall**，诊断版和未插桩版独立；模型396B只作 sanity check |
| **两家族软件近邻** | GS-Scale当前训练与CLM独立实现最少书面近邻对照；若残余可由原有camera reorder/precise Gaussian caching/CPU Adam overlap/早期SHN传输解释，应先标`SOFTWARE_OPPORTUNITY`，**不升级新硬件机制** |
| **GPU预算与有效阶段** | 只以实际从头走到的step和Gaussian规模裁决，早期步数不推晚期；不另开A26GR1分支或加数据/GPU预算 |

**结论：** 下载的Rubble为真实应用输入；**此前遗漏了直接同场景的ASPLOS2026 CLM近邻**，这是最值得本轮立即补入的相关工作。新技术主张需先证明在GS-Scale和CLM成熟状态管理设计之后仍有**完整应用wall的、非软件可吸收的物理资源剩余**。这次未向Codex发送指令，也不会打断正在执行的A26GR1。
