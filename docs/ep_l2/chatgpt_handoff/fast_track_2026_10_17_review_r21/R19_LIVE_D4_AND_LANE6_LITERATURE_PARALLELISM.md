# EP-L2 / ISCAS2027 r21｜D4正在执行、Lane6的blocked是时序快照；并行吸收R20文献

2026-10-17，北京时间。**只读GitHub交叉审查与短Goal建议**；不是新增实验配置授权、科学认可、后台轮询或修改正在运行进程。用户已对r19 8个首轮应用实验和写作并行作明确同意；此文件不会自动唤醒任何Codex窗口。

## 0. 两个截然不同的时间点

- Lane1原分支 HEAD `605c7b09d78092b9bcc574a27e66c069f9ccde2a`，全部D4/Q4两模式actual affected path(各2)、H0(各1)通过，仍用同一当前官方binary `23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee`，**没有新应用性能结果**。精确索引 `docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane1/HEADROOM_CONDITION_INDEX_R19_R1.json`。D4准确源提交`3cc3660684cad09c5decf2684c62e2c7b26e6b25`，Q4 `31add7b3ae4e7fcc3c251b8ee0fac3f9461d6af3`，不需要Lane1重建binary。
- Lane6 original branch HEAD `75cf0ccf8be56f5bc4f852d20f95547615cfd701`（2026-10-17 07:30:04 UTC），`FT20261017_LANE6_R19_HEADROOM_INTAKE_r1`已经保留了**全部五组H0**论文接收、真实Fig2/3/EN-v6及新增headroom敏感性段落。它依赖检查3次均未找到新`CURRENT_ACCEPTED` D4/Q4，报告`WAIT_FIRST_QUALIFIED_D4_NATIVE_PAIR`并结束Goal，这是**条件尚未完成而非仿真失败**，也不是论文不能继续。
- Lane5 original branch HEAD `42c810cfb02be3c131980f1f62ac85872331b176`（2026-10-17 07:46:17 UTC），其 `STATUS.md`记录D4 **Convolution B/U两条正式模拟器自07:34:53 UTC已启动**，PID 1948412、1948411，已在中央REGISTRY的RUNNING阶段，D4独立2/2真实受影响定向PASS，Q4独立2/2 PASS（Q4应用后排）。精确Q4尚未安装单独V2授权，避免冲撞在途D4审核。**GitHub只是已发布时刻的快照，是否现在仍运行应由Lane5本地进程/registry核对，不能仅从远端PID猜测。**
- Lane5尚无新D4`CURRENT_ACCEPTED`的可靠远端证据，因此Lane6保持0新增数值是科学正确的。**不要重新发起Lane5 Goal、第二组sim、重复构建、停止或重启这两条已在途D4。**

## 1. 现在让Lane6做什么才是真并行？

**R20文献融合是已完成且不依赖D4的工作，应作为新的短Goal由原Lane6窗口主动消费**。来源为独立编辑分支`hrl/ep-l2-iscas2027-english-editorial-v1`提交`222975a65dc1a6aa133d2942612f6d8001a534de`目录`docs/ep_l2/paper/literature_r20/`：
- `README.md`
- `AUDIT_AND_MERGE.md`
- `ENGLISH_MERGE_BLOCKS.tex`
- `references_verified.bib`（14条库；正文按需要不强迫14条全入）。
优先核实4个新项VWQ(ISCA2010)、Decoupled Last-Write Prediction(ISCA2012)、Dirty-Block Index(ISCA2014)、Staged Memory Scheduling(ISCA2012)与当前EN-v6主张的对比：不能声称首次将dirty data留在LLC、首次将地址与数据分离；本稿聚焦独立Tag复用时dirty payload原位所有权、landing slot、WB本地与WAD完成责任。在downstream敏感性中明确queue/credit扩大与调度可见性、DRAM频率不同于纯带宽。
- **不是重写整篇**：以Lane6现有`d3d7b4fe9059d68aa0793eec58b5f32488138c10`的EN-v6以及`75cf0cc...`的r19同步稿为**当前主体**，仅替换Introduction前人引导、Related Work和最多一处Methods范围解释；不覆盖已接收H0五组、Fig2/3、0.16%均值和r19接收表位置。合并重复文句，维持四技术+一参考页，不把R20 source fragment当成Standalone manuscript。
- BibTeX逐条对齐原10个key/现有编译方式，新增4条引用不强制都用；核对书目DOI、页面格式和实际可支持命题，若发现范围不匹配直接标`PARTIAL`并删去不受支持的引文而非编造。
- 在Lane6独立分支以新目录冻结准确文献来源提交/文件SHA和编译的TeX/PDF/截图、引用核验；测试无未解析引用、无overfull、图仍可读；编排合理，别为了4页挤小字号/减margin。
- 完成文献合并就可以**正常结束短Goal**，并在STATUS中明确`WAIT_NEW_D4_CURRENT_ACCEPTED`是结果接收依赖，不等于整个科研/论文停工；**不建立新的十小时后台轮询器**。当Lane5出现第一个D4准确CURRENT_ACCEPTED及原始配对证据后，再以一次事件驱动Goal按已有r19 native intake引擎进入下一版结果图。
- 不改Lane5 V2科学ledger，不在模型缺统计时填0，不混H0的geomean和D4/Q4诊断均值。引用与实验机制可并行，但论文效果只能靠真实新结果证实。

## 2. 其他窗口
- **Lane5原Goal继续**：先D4 Convolution，后D4 FWT，接着Q4 Convolution/FWT，独立资格及64-slice/current V2真实pair接受。遵守原10h deadline、24应用总额/最多2长期sim、8CPU/32GiB以及磁盘/内存/Share保护；不因一个窗口early blocked而停服务。
- **Lane1已交付**：不为了新窗口blocked而重编译/重跑H0。
- **Lane2/3/4以及已关闭Storage-Ops**：不因写作阻塞重启。

**成功判据**：Lane5继续产出有效D4/Q4完整配对，Lane6在等待中将R20高相关近邻一次性整合进当前EN-v6，而不进行无意义轮询和覆盖旧科学成果。
