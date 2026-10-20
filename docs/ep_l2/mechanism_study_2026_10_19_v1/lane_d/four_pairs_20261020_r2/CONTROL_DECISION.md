# 最小控制需求：先身份与范围，后运行

本文件只向E2/A2提出可审查需求，D不启动模拟、修改代码/台账或授予资格。准确机器请求为MINIMAL_CONTROL_REQUEST_TO_E2_A2.json，逐项预测见CONTROL_INFORMATION_VALUE.csv。

## 信息价值顺序

1. **SAD W_ONLY：1个条件。** 三类直接功能未触发，而主要989cycles改善发生在复制尚未出现的首kernel；这是区分组织/时序变化与简单copy解释的强约束。若W_ONLY复现该prefix改善，支持W组织净作用，仍不能叫动态复制消除；若不复现，则V相关驻留/查询/排队时序的净影响需要解释。该点不凭SAD加速较大挑新输入，而是对原已登记输入的零触发反例作证伪。
2. **DWT W_ONLY与F_MINUS_R：2个条件，共享已有S/F。** 完整S→W→WV→F阶梯可给相邻背景下的W净作用、加入V净作用及R净作用。K5/K8是主要退化段，RO查询只在K1发生，landing等待98.9%也在较快K1。因此重点是V查询/landing与跨kernel状态，而非给148372或39836计数换算GPU停顿。只报告各背景边际对比，不能当唯一无交互的模块分摊。
3. **Conv原矩阵F_MINUS_R、WV_M：2个条件。** 这是当前四输入中有实测S line-MSHR-full的已登记背景，T关闭时M对照的信息更直接。该两点本来就在原32矩阵内，但尚无profile资格；若超矩阵范围补充未获批准，优先合法推进这两点的资格准备，不自动开跑。F vsWV_M再检验T添加的净作用，不能由detached0假定完全cycle等价。

**主请求最小共5个唯一条件，最多新增5次完整启动（仅若获批并真实启动才计数）；其中3个超原32矩阵。** 当前20/40只表示剩余容量，E原投影仍有20个原矩阵格子（Btree2 HOLD＋18消融/诊断），所以3个新控制不能占用“空闲额度”自行插入；需要明确科学范围及内部预算替换决定。禁止再加40、扩contingency、复位失败计数或重跑已接受端点。CFD的WV控制仅作为后续候选，不计入首批5项，不无限扩矩阵。

## A2先做的零启动工作

准确d010源中，bank-compatible landing是index%4对应free payload的容量/生命周期条件，不是P1服务端口忙。请静态复核同bank回收CLEAN/WB_COMPLETE的谓词、pending/inflight/pin保护，以及SAD首WB前W_ONLY/S/F的timed路径差异。query增加的函数调用CPU开销不是模拟GPU周期；只分析已建模的查询等待、payload/Tag身份、队头与bank/response时序。

优先在冻结main61上给参数overlay及准确config SHA、oracle绑定和受影响production检查清单。W_ONLY为W1/V0/T0/M0；WV为W1/V1/T0/M0；WV_M为W1/V1/T0/M1。V关时不偷偷保留可选victim；R关时按A/E合法OFF scope处理，不能复制其他输入证书。P1/四bank、1168payload、128WAD/TVD、512descriptor、line128、per-address32、全部理想化OFF及原队列/顺序/版本生命周期保持。

如果当前runtime不支持某点或需要代码修复，单独报告新runtime/source身份，不能沿用旧资格或以旧S/F跨binary配对；本请求不授权为此绕过资源入口编译。E独立决定profile/输入/native门禁及原资源准入；D/E分析控制测试不充当生产正确性。

## 最小输出：不加冗余观测框架

完整应用cycles/instructions/身份/正常退出和64slice闭合沿现有E流程；另保留已有逐kernel gpu_sim_cycle＋最终剩余、copy/物理bank/grants、V真实response/promotion与dirty子集、RO准入/merge/line分配避免/detach/duplicate lower、各原因首次请求/等待和/max。使用已有counter和raw快照即可，不重扫trace、不重新实现验收器。

关键路径UID/等待区间交集目前缺失，因此没有给出“查询造成N周期”结论。只有上述控制仍不能辨别而A2/E2另行审阅后，才讨论有界新观测；任何新runtime都需独立身份与资格，不假定新增事件接口免费。
