# LATPC全文核查与Lane B/E补充说明 V1

日期：2026-09-26。ChatGPT-owned文献分析与协调补充；不是新实验结果，不是新的执行Goal。

## 0. 来源、定位与优先级

原协调：`b977494676f27493c4da0a802f8782319edb76f8`，`COORDINATION_AND_GOALS.md`。

本补充只替换原协调中R4及资料请求部分关于LATPC“未取得全文”的状态，其余任务、节点、预算及已冻结科学结果不变。Lane B/E不因本文件重启、不改活动worktree基准、不新增完整复现任务。

论文：Yeonan Ha et al., LATPC: Accelerating GPU Address Translation Using Locality-Aware TLB Prefetching and MSHR Compression, MICRO 2025, pp.418–431, DOI 10.1145/3725843.3756069。

用户提供文件：`3725843.3756069 (2).pdf`；7,140,417 bytes；15页（1页ACM封面+14页论文）。SHA256：`d7f32ee8c4ac0afa8c7de88056a0f0d67d22a5b295ba26d5e489186820ea6735`。

状态：FULL_TEXT_REVIEWED。阅读正文§1–9、参考文献，结合原图表核对关键机制和实验配置。页码约定：PDF第2页=论文第1页=会刊p.418；下文优先给会刊页码与章节/图表。

论文PDF本体目前由用户提供在ChatGPT附件中；本次未把它传到174/109/node164，不能假定Codex已有该PDF。此文档保存可直接消费的分析和准确定位，不包含整篇论文复制。涉及本说明未覆盖的实现细节，应取得原文再核，不得补猜。

CAC（PACT 2018，10.1145/3243176.3243203）全文状态未因本次更新而改变，仍待补充。

## 1. 最重要的核查结论：基线本身已有warp内页请求去重

来源：§2.1，p.419；§5.1及图10，p.422；§5.2，p.423。

- §2.1明确描述LD/ST端存在按页大小把一条warp指令地址翻译请求合并到最少数量的coalescer，引用Pichai/Power [88,89]。
- 图10把Coalescer放在Regularity Detector与L1 TLB之前；Coalescer不是该图中新增/修改的阴影组件。
- §5.1明确说coalescer输出unique VPNs；新增Regularity Detector接收这些VPN。
- §5.2再次明确：同一warp访存指令按页大小提取unique VPN；输出顺序由thread index决定，可能未按VPN数值排序。
- §6.1说明模拟器建模§2.1所描述的翻译过程。

因此：LATPC论文所描述的基线不等于“无TLB预取且无warp内翻译合并”。“Baseline without TLB prefetching”不能读成“无任何前端coalescing”。

这不是根据摘要推断；是全文直接证据。但论文模型不等于已公开实测NVIDIA Ada内部电路，亦不是本次已运行作者代码的证明。

## 2. LATPC新增的三部分，与同页去重严格区分

### 2.1 Regularity Detector：在去重后的不同VPN中发现stride

来源：§5.1–5.2，图10/12，pp.422–423。

每周期处理一个unique VPN，产生<VPN, Stride, Index>。按动态warp指令重置检测状态，不跨warp switch保留。状态为36-bit Base VPN、36-bit Prev. VPN、9-bit Prev. Stride、5-bit Prev. Index、1-bit Prev. Valid。

组内要求位于相同512-page边界，使用低9位计算stride；可以表示负stride，不能用未经约束的整数外推越过页表边界。stride或高位不匹配时开始新组。当前论文实验不对VPN排序；§7 p.429说明排序虽额外改善结果，但存在15-stage排序成本，因此未采用。

论文所称prefetch目标来自当前warp指令coalescer输出中的VPN规律，不是简单根据全GPU历史访问序列猜未来页；单例组仍是demand。不得把它简化为固定+1预取。

注意：检测器的1 VPN/cycle不是原文对所有已有coalescer形成/登记/广播端口的完整声明；不能把该数字不加区分地塞给Lane B的参考实现。

### 2.2 LATC：一个MSHR表示多个不同VPN的未完成miss

来源：§5.3，图14及Algorithm 1，p.424。

MSHR由单VPN tag变为Base VPN+Stride+32-bit Valid Mask。第i位表示Base VPN+Stride*i对应的miss在途；可压缩最多32个不同翻译miss。原MSHR subentry（等待warp的记录）机制不因该压缩另行改造。

原文例子：0x8、0xa、0xc、0xe均L1 miss；用Base=0x8、Stride=2和四个有效位表示。后续新的VPN仍转发L2，不是共享同一个PPN，不是凭空取消四个不同页面的PTE读取。

对比AWMA：当前PREL1合并相同exact translation identity的请求，在物理L1 launch之前去重；32 followers/entry表示同一翻译的等待请求数。LATC的32-bit mask表示不同miss VPN槽，不是同一个容量含义。不能因都有32就称机制等价。

### 2.3 LATP：批量处理同一叶级页表内的不同翻译

来源：§5.4及图15，p.425。

扩展PW Buffer，利用相同512-page区域的VPN规律，把多个walk请求放进一个批处理条目；论文采用x86-64四级页表，从根到叶称L1–L4。共享L1–L3前序遍历，L4仍逐个发出PTE读取，利用同一4KB DRAM row的局部性。中间级遍历期间可追加兼容请求，L4期间亦可继续追加。

所以它既不是“一次DRAM事务取回所有任意页面”，也不是“同VPN请求合并”的另一个名称。512-page区域、4KB row、根到叶四级等是该文建模条件，不能直接替换AWMA已接受配置或宣称是4080事实。

## 3. 机会与证据口径

- §1 Fig.1 pp.418–419：39.37% page-table-walk与53.09% MSHR reservation failure是该文address-translation latency分解，非kernel runtime比例。
- §2.2 Fig.3 p.420：75.32% warp指令访问多个页；28.86%达到32个页。是作者所用评估负载/配置中的统计，不是所有GPU或所有LLM的普遍比例。
- §4.1 Fig.8 p.421：平均1.96种VPN stride；regular/irregular分别1.42/2.49。
- §4.2 Fig.9 p.421：平均80.20%相关翻译落在同一L4页表；regular/irregular分别93.38%/67.02%。这讲多个不同页的页表局部性，不等于同VPN命中率。

AWMA历史对照（非该论文结果）：`6441fe9f.../TARGET_OPPORTUNITY_MATRIX.tsv`里七点unique_pages_max分别2/2/2/1/1/2/2。这个低页分散现象提示不能把LATPC的高分散MSHR/PTW瓶颈直接套上来。它不是“LLM一定低分散”的证据：两边page size、程序实现、工作集和观测边界不同，必须先在各自原合同内报告；本轮不把AWMA 64KiB改成论文4KiB。

## 4. 实验组与配置核查

### 4.1 主模拟实验

来源：§6.1，Table 2/3，p.426；§6.2，p.427。

- Accel-Sim，RTX2060-like，30 SM，GTO，1365MHz。
- 主实验4KiB；L1 TLB 32 entries、16 MSHR entries、20 cycles、4 ports；L2 TLB 1024 entries、128 MSHR entries、80 cycles、16 ports；16 PTW，128-entry PW Queue。
- 2MiB配置在Table2另列：L1 16 entries/8 MSHRs；L2 128 entries/128 MSHRs。
- 24 workloads来自CUDA SDK、Lonestar、Pannotia、Parboil、Polybench、Rodinia；不是完整LLM推理集。作者按>4MB footprint和/或高MPKI主动选取VM压力样本；再按规律性与MPKI分类。不能写成无偏覆盖所有GPU workload。
- 1.47x是24点相对其已有合并、无预取baseline的IPC几何均值。LATP单独1.28x、LATC单独1.20x；不能相加，也不能与AWMA单kernel cycle-reduction百分比直接横比。
- 主实验为Regularity Detector与LATC tagging分别建模1-cycle附加延迟。

引言举例中的12个MSHR不是Table2主实验16个MSHR；后续对照以Table2为准。Fig.11是机制示意时间线，不是一个真实benchmark测出的5.67x主结果。

### 4.2 真实GPU小实验

来源：Fig.2b及p.420脚注1。

NVIDIA RTX4080 Super、CUTLASS GEMM、NCU；修改driver中force_4k_ptes条件比较页大小和footprint。这只支持该小实验的page divergence动机，不是LATPC机制在4080真机实现，不能把它和主模拟平台合并叙述。

### 4.3 大页与资源敏感性

来源：§3.2 pp.420–421；§6.6–6.7 p.428。

§6.6中Regular+High类增大footprint，平均1.14GB，其他类未同时扩大；2MiB实验GMean1.18x。因此1.47x和1.18x不是只改page size的一对固定workload单变量结果。资源敏感性改变L1/L2条目及PTW数，不自动证明与另一真实GPU架构完全等价。

### 4.4 硬件与其他比较

来源：§5.5 Fig.16 p.425；§6.5 p.428；§7 p.429。

作者使用OpenROAD的45nm/7nm技术库与CACTI 22nm估计存储；报告额外面积0.2581mm²、功耗35.78mW、存储约2.48KB。这些是作者的技术模型结果，本次没有重跑；不能将它们当真实TU106测量，亦不能直接和AWMA generic proxy不同口径的总状态量相减。

Avatar比较：LATPC 1.47x、Avatar1.40x、组合1.64x；这是作者的同平台比较，不是我们已复现。§7把L2 TLB MSHR subentries改为1后Valkyrie结果从1.03x变1.20x，强调已有返回传播能力会影响增量基准；不能据此擅改AWMA的subentry配置。

## 5. 对当前新颖性判断的更新

结论一：LATPC不是当前AWMA PREL1的逐细节相同实现。其新增贡献是unique VPNs之后的规律检测、多VPN miss跟踪压缩和批量walk。

结论二：全文明确把warp内同VPN去重当已有基础能力，进一步强化“先补最近基准”的必要性。不能因为与LATC/P不同，就反推AWMA同页合并具有新颖性。

结论三：聚合followers与warp内冗余数相等仍只是推断，待Lane B做请求来源集合比较。本文没有代替该实验。

结论四：本论文能提供的基线证据，并不意味着立即要完整复现LATPC。若Lane E候选落到相同warp stride、多VPN MSHR压缩、同L4批量walk范围内，先当已知参考；新机制必须说明在该能力之后剩余什么限制。

结论五：全文没有给AWMA所需的全部ASID/generation/invalidation/原子访问兼容语义，不能把论文未写误读成硬件无这些限制或把补合法性字段当新创新。

## 6. Lane B补充：不增加原定执行预算

1. 把本文件作为原R4已取得全文的补充证据，原任务范围不变。
2. 参考实现继续叫WARP_VPN_DEDUP_REFERENCE，不叫LATPC复现。
3. 在SOURCE_AND_ADAPTATION记录§2.1/§5.1/§5.2；页请求去重与cache-line/sector数据事务分开，不丢逻辑UID。
4. 说明unique VPN输出次序。若AWMA采用现有accessq顺序而非按thread index输出，记录为适配差别，不冒称周期级复现；不为本次文献更新强制重排正在运行的实验。
5. 优先在已有来源映射中报告每动态指令unique VPN分布、合并来源分类、L1/L2真实launch、MSHR失败/占用与walk等待。已有统计足够时不新增hook，不为本文件重跑全矩阵。
6. 不把旧pre-L1的physical launch骤减与LATPC的MSHR压缩率混成相同指标，不拿literal lookup_requests当真实服务量。

## 7. Lane E补充：筛选不同问题，不复述LATPC

1. 删除LATPC全文缺失的阻塞标记；CAC等其他最近邻状态保持原样。
2. 先在B的去重参考结果上判断残余压力，不强迫出现MSHR/PTW瓶颈。
3. 以下内容已明确是LATPC现有能力：基于当前warp unique VPN的stride识别；Base+Stride+Mask多VPN miss压缩；同L4区域的batch page walk；用已生成地址关系组织预取。不得改名当新机制。
4. 若筛选新的请求调度/释放策略，应区分request生成、translation-ready、head观察、地址apply、data-cache接收；与LATPC、MASK等比较具体规则，不用“更智能”作为差别。
5. 可用既有数据建立需求检查：去重后多页分散、同L4局部性、真实MSHR reservation失败、PTW排队、head暴露与数据侧压力。集合局部性不是驻留命中率，等待计数不是可加kernel时间。
6. 未来涉及page-table locality或walk scheduling的候选，其最近邻核查还应包含LATPC参考文献[60] Marching Page Walks (HPCA2025)、[97] Scheduling Page Table Walks (ISCA2018)、[98] Neighborhood-Aware Address Translation (MICRO2018)；这里仅核到参考文献条目，不冒称已读这些全文，不在本次扩大实现范围。
7. 原最多两个候选、最多六个candidate回放预算不变；没有明确剩余问题时允许无候选结论，不为了模仿论文人为增大压力。

## 8. 当前动作与边界

本次只发布文献核查与协调补充。未运行174模拟、未通知或重启Codex执行、未改冻结源码、未启动109、未采trace、未上传PDF到节点。

已有B/E任务继续；用户只需将本文件一次性通知两个原窗口。原b977协调提交仍是任务依据，本补充与之共同阅读。今后结果可用于选择新机制，但本文件本身不宣布新颖性通过或论文就绪。
