# 固定 AC/AE 集成与 HOLD 决策

最终 AG Core：965dffe04366e665626de4afeb7ffebca8622b5f，tree b089d5838ca554679edd46476050b6d3885432d0。固定 X2 基底 e32afdcf44be3374ff36d22568ed01a075459b6f。先以 adbcc8ec 纳入固定 AE，再合入固定 AC；不从移动 HEAD 取源。

| Lane | 固定 Core / Framework | 决策 |
|---|---|---|
| AC | 83aca449135703c176cfab29ae43e1245d00a557 / 2bdadeb5942f90a3216cbf6afbda9dc784d7dfce | 有界 CPU PASS，AG独立复现并完成组合CPU资格后纳入 |
| AD | 731be8548ad0fcc167ebfc49d5f1867f22034b4c / aa08d184d3e7a141c207ba6ea42f139245561334 | PARTIAL/ON acceptance STOP；两格HOLD_UNQUALIFIED，不合入、不静默修复 |
| AE | ae83cc510f301cfe7937ad77318e332b2ab324e8 / 3b7c8bca8186add520987f864dd2f67abde87ef3 | 有界CPU PASS，AG独立复现后纳入 |
| AF | 19dafca6b5636ee26f4c35e566c24e17e645edaf / 001e569f146db4a7ef759ba2c3ce574a74d0d70f | 仅独立机会/状态安全，不合入、不新增arm；真实输入机会UNAVAILABLE |

共享shader.cc/shader.h/CMake有三处文本冲突：初始化guard、两个独立bool声明、CPU测试注册。均保留双方原样增量；COMBINED_SOURCE_REVIEW.json逐字节验证“固定AC + 固定AE原样增量”的精确并集，14个受保护X2函数体不变，其余路径等于原固定对象。common.h完全等于固定AE；AC无common.h改动。没有机制合同冲突或生产Lane源修改。

AC ON仅OO whole-line finite+ordinary L1D。每LDST一个collector、一个WB result owner，仍占原PIB、Ref、generation、ledger。两块有限raw-sector数据bank，每块4P×32B；P640时各81920B，两者额外163840B/SM（160KiB）、64SM额外10MiB。不是免费PIB payload，也不是equal-area。bank角色交换无整块免费复制；collection仍4×32B/绝对周期，retire仍cacheable或sidecar共1/绝对周期，WB严格晚于collect_done。实际RFU denial、原arbitration、same-warp fence/full admission/late waiter/old generation全部保留。OFF不配置结果数据容量、不打印新frame。

AE唯一预固定hash：line=address>>7，S=2^s；set=4*(((line>>2) XOR (line>>s)) AND (S/4-1))+(line AND3)。ON仅OO whole-line finite、B4、S≥4且2幂；bank=set%4=line%4完全不变。grant/find/victim一致，完整line比较、历史will_new_miss的LRU副作用保留。OFF为原modulo，不收紧旧几何。XOR适配既有Tag index时延是模型假设，非综合时序证明。

提交集成代码前：原X2原7 CTests和正常导出5例先通过；AE独立137例、56组逐请求OFF对照/四旧几何通过；AG独立AC80进程（75正例、5合法拒绝）、16 parser负例、17组OFF逐边界对照/51正常打印边界通过；68个AC×AE四组合CPU交错用例在screening64×8/640/PIB128/lower32768通过；新15/15 CTest、实际LDST8例、正常导出5例和全生产parser echo通过。后提交965dffe0。AD未达到CPU资格，其4 waiter/cycle及独立ready合同未被AG改变；AF仅独立重现15 standalone witness，不冒充其17 composite checks。

CPU probe使用合成指令、受控lower packets及准入对齐；调用实际LDST/RFU/ledger/正常gpu_print_stat，覆盖乱序sector、真实WB bank阻塞、partial admission、source-defined K1与旧generation、same-warp fence、sidecar。AE差分fixture含三个空闲GPU clock ticks，无kernel/canary/full模拟；AC fixture GPU cycle()/kernel均0。无payload值证明。

新AC frame只作ON非比较诊断；OFF未打印为UNAVAILABLE。完整64SM最后正常frame与共同collected sectors/finite retire/sidecar/frontend人群严格关联。人工prime()的CPU pair会多计frontend seed retire，必须拒绝该不等人群；无人工prime的64SM双generation实际LDST用例通过，完整输入严格等式未放宽。
