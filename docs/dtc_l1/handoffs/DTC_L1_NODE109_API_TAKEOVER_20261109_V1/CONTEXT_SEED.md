# 109-DTC-L1 CONTEXT种子：接收后前向维护

这是新API窗口的上下文种子，不声称已更新任何本机文件。由109-DTC-L1合并到自己的项目CONTEXT.md；本机实际路径、接收commit、节点观察和交付结果须由该窗口据实填写。

## 角色和当前任务

- 唯一DTC-L1 Main：本机API会话“DTC-L1交接-1”。旧账户Main仅作历史查询。109-DTC-L1负责DTC在109的历史native/profile/capture与资产来源维护，不承担第二Main/dispatcher角色。
- Main已获用户转交64cd科学接受任务；本种子没有它的本机接收完成回执。109不读写Main CONTEXT、活动控制面、registry或结果包。
- 本轮任务：固定GitHub资料接收、限定109路径的只读metadata和小型历史文档发现、归档成员映射、独立CONTEXT维护、小型GitHub回执。完成后STOP_PENDING_EXPLICIT_TASK。
- 新native、profile、capture、GPU锁、编译/安全fixture、simulator、request和科学预算均不在本轮权限内。历史GOAL_109不自动恢复权限。

## 当前主线科学状态

- Controlled Oracle固定32输入×4模式128格自然闭合，96个同build实际OFF配对；D全128独审PASS，M完整32分析冻结，Main整合/发布/签署完成，科学窗口接受固定trace范围的收尾。该轮Goal CLOSED_ACCEPTED；DTC-L1研究继续。
- 范围为SM70/V100-derived 64SM固定trace的受控反事实；Oracle不是可实现收益、等面积收益或严格数学上界。L2的11精确零与myocyte +2周期、srad_v1 +14652周期退化保留。
- 原生完整应用数值/capture绑定、hook重叠、coherence、有限机制因果、面积/功耗/吞吐公平性、扩展输入资格仍独立。109 native材料不能补为本轮CORE32统一producer或数值证明。
- 英文LaTeX v0.23冻结；IO/OO归赵皓宇博士论文第4章；旧F=null、所有负例、失败和SOURCE_KEEP不改。Tag1024/physical640 NO_FREE_LINE安全HOLD保留。

## 固定来源

| 用途 | 完整commit |
|---|---|
| 原Oracle合同/准备 | `18b1ee9d339902e555fc2e04ef51c84f77dfe1b1` |
| 128格运行结果 | `7ffcca7f908a21f45ba1a6ebb3b335ff962f97df` |
| 完整Main工程交接 | `3f0036f2868e20a8d9a4b6244c7c74d940954188` |
| Main最终科学包 | `b9ff89f00ea8ff889e4189136501c714c5d7e345` |
| 科学接受与Main接收指令 | `64cd088b2de575157846f07a21ce09748220f7e2` |
| 109 native producer完成 | `890fb0be7e681a60419c49ca0a7aa85731d8c164` |
| 109 SM89 CPU可行性完成 | `d58e75ce32845a281692f19aeb4057b4c9822a3f` |
| 174 modern-layout提案 | `d6f0a3300972d7b1d9638b8f4b1338c25912a1b3` |
| 109存储整树盘点 | `b290790401e248a19427c26c0dde51e6b55ded67` |
| 跨项目存储使用调查 | `8700af7cd3e0cd530f8efa8dfe5333ebdd9f1d1e` |
| M5 AutoDL V100 / SpMV来源 | `a9cdb3328a346cbc9a76b7ffadae3725b4209ab5` |
| 本109接手调查包 | 接收时填用户转交的实际完整commit |

路径和链接见本调查包SOURCE_INDEX。不要用移动分支HEAD替换固定commit。

## 已确认的109历史

2026-10-16，109 RTX4080上的producer完成12个诊断＋SpMV主输入＋LayerNorm主输入及唯一native敏感性输入，共15条件，每条件7独立进程×10次event样本；有NCU及新增算子nsys证据。这些是stock native行为，不是DTC硬件收益或15个应用。

SpMV是Parboil small1138_bus、1138维/JDS4448、FP32、grid36/block32。4个cubin89/tracer5完整kernel为3warmup＋final。原生数值有效、warm DRAM读0且underfill。Producer格式PASS后174 consumer因unsupported89拒绝；109后续CPU审查发现64条宽寄存器高半依赖缺失等问题，最终 **NO_GO_FOR_DROP_IN_SM89_ADMISSION / HOLD**。不再沿用早期PENDING消费者状态。

LayerNorm为PyTorch2.5.1+cu124 F.layer_norm FP32 `(1024,1024)`，width1024/seed109/eps1e-5/affine1、0；native对FP64参考逐元素PASS。6个capture kernel含2初始化和4个LN实例。设备SM89但实际cubin86，29条静态CALL.REL.NOINC被忽略，**SASS NOT_ADMITTED**。`(8192,1024)`仅native/profile敏感性输入，未capture。

原固定12/629成员在10月16日109本地根不可用是历史快照，不能说今天丢失，也不推翻174或后来CORE32。新SpMV/LayerNorm不代填原12。早期M5 medium_bcsstk18/50 capture来自AutoDL V100，不是109 small1138_bus/4 capture。

## 历史资产定位（今日状态全部待填写）

- Native worktree：`/home/huangrulin/workspace/worktrees/accel-sim-dtc-native-coverage-109-v1`
- Native root：`/data/c16/dtc_native_coverage_109_v1`
- SM89 CPU worktree：`/home/huangrulin/workspace/worktrees/accel-sim-dtc-sm89-admission-109-v1`
- SM89 CPU root：`/data/c16/dtc_sm89_admission_feasibility_109_v1`
- 共享PyTorch环境历史入口：`/data/c16/env/c16-py310`
- 共享tracer历史入口：`/home/huangrulin/workspace/worktrees/accel-sim-awma-simcompat-v1/util/tracer_nvbit/tracer_tool/tracer_tool.so`

Native归档历史在174-new/root的164挂载namespace：`/root/share/mnt164/huangrulin/dtc_native_behavior_workload_coverage_109_v1/20261016_v1/dtc_native_coverage_109_v1_20261016.tar.gz`。85,512,354B，SHA256 `af5c6ec76179f881f689f486829c025055764bd9e564e598c0dc18560865f984`；285成员/174,081,218B；2026-10-16目的端逐成员SHA PASS。

CPU小归档：`/data/c16/dtc_sm89_admission_feasibility_109_v1/DTC_SM89_ADMISSION_FEASIBILITY_109_V1_CPU_RAW.tar.gz`；576,292B，45成员，SHA256 `95f3e6d6e3a986bdc7d9d2468374275e2e008b81cbd88d0ec026315117a6f28f`。已读来源只证109本地，没有自动证明true164副本。

2026-11-04整棵native root盘点为TARGET_UNVERIFIED，logical437,757,580B、allocated439,816,192B，完整归档映射/恢复未闭合。与指定285成员包PASS范围不同；不得相减得“未归档字节”、宣称丢失或可清理。

## 未决项（接手后逐项更新）

1. 四个专属历史root/worktree今日存在性、实际路径、HEAD及有无未提交DTC小型材料。
2. 285/45固定成员与当前路径metadata映射；整树额外文件范围及已有回执，未重hash的事实。
3. CPU小归档是否另有已建立的持久化回执；native指定归档当前可见性/namespace。仅跨跳174才能核时保留REFERENCED_NOT_RECHECKED。
4. 共享env/tracer/工具入口是否仍可见；当前版本与历史测量版本分开，不修改环境。
5. 新发现的DTC独立历史、精确来源和owner；不推断其他项目同意接管/清理。

## 接手交付后填写

实际本机CONTEXT绝对路径、接手日期、109观察范围/时间、固定回执commit和远端readback、MAIN_INTAKE_NOTE入口、已解决/剩余项、零新增执行计数、STOP状态。不要把未完成字段预写为PASS，也不要等待所有UNKNOWN消失才交付。
