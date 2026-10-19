# Goal: DTC_COV1_INPUT_AND_COVERAGE_174_V1

职责：为固定最终方案补足可靠输入覆盖，避免用应用名字数量替代代表性。无完整模拟器派发权，无EDA或109 GPU自动任务。遵守README的AG4同容器进程门禁。

分支 `hrl/iscas2027-dtc-cov1-inputs-174-v1`；独立worktree/raw/review pack `docs/dtc_l1/review_packs/DTC_COV1_INPUTS_V1/`。从本计划commit派生，只写自己的目录。源码/文档准备可以先做；CPU脚本或重I/O执行须有不影响AG4的资格。

## 任务

1. 以A/T/U/M、AG3/AG4固定来源为基础，整理八主体输入ATAX/BICG/GESUMMV/GEMM/DWT2D/Gaussian/NN/MRI-Q。对每个记录完整源/生成或capture信息、kernel/command/CTA/active-instruction计数、每kernel并行度、读/写/atomic类型、数据规模、trace ABI/ISA/decoder身份和既有完整控制。将三种不同qualification分列：回放完整、native/capture适用、值语义支持。不要沿用文件名推断维度。
2. 建立REUSE_MATRIX.tsv：F/C+是否有完整旧控制，关键身份/公共选项/初态是否可比，哪些新点确需启动。能由已接受证据修复的manifest包装自行确定性重建，不能补造trace payload、逐load值或不存在的结果。大输入一次顺序扫描生成共享索引，避免多Lane各自重复读盘。
3. 按MASTER_PLAN的预固定规则寻找N1更充分并行的BICG/ATAX、N2大工作集GEMM、N3来源明确的不规则读。资产最多每类考察3个候选，选择不看DTC周期；一次有界盘点，不陷入全盘无限找文件。每类固定一个输入，不能看到speedup后改尺寸或矩阵。
4. 优先已有合法captured输入；CPU编译/生成算法输入和独立结果参考允许。若真正捕获资料缺失，交付精确source/native producer recipe、所需ISA/环境与状态BLOCKED_CAPTURE；不直接启动GPU，不换109 SM89 trace别名，不自行租机。合成访问模式分析必须单列，不能当新增真实应用。主线八输入的准备不因三新输入缺失全部停下。
5. 向SEM1共享不可变的源码/地址/访问类型索引。若需要body扫描，仅对已固定输入做单次有界流式扫描，保留alias/未知范围；没有值/对象边界时不能由地址未重复推断真实数值正确。新输入全部建立完整kernel边界与参考结果，不以prefix作为可用应用。

## 交付与验收

LATEST_REPORT.md、INPUT_COVERAGE.tsv、REUSE_MATRIX.tsv、NEW_INPUT_SELECTION.md、每输入manifest及小型CPU参考/测试、BLOCKED_ITEMS.md。选择说明先给覆盖问题，再给资产匹配，不倒因为某模型已下载就选它。

首次CPU批次限一个2小时wall-time工作窗口进行盘点与资格，重用既有工具；时间不足给出已获得的确切材料/缺口，不无限扩大工作。常规脚手架修复自行完成，不重跑已验全部测试。不修改科学模型、旧输入/历史HOLD、主图或GM。

完成后独立发布commit并回读，告知协调者可直接使用的SHA；不要自己发起性能点。只有真实执行收据存在才报告测试PASS/RUNNING。
