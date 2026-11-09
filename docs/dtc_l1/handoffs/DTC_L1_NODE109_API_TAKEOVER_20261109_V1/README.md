# DTC-L1：109历史资产与API窗口首轮接手

日期：2026-11-09。状态：`GITHUB_HISTORY_REVIEW_COMPLETE / NODE109_INTAKE_NOT_YET_PERFORMED`。

本包回答“DTC-L1有哪些工作在109做过、成果在哪里、能证明什么”，并给新API窗口 **109-DTC-L1** 一份可直接执行的首轮接手合同。用户已授权本次历史调查、远端资料发布，以及新窗口对必要109现场材料的整理。本包只授权有范围的只读接手和小型文档回传。

## 先更新状态与路由

- **DTC-L1 Main** 唯一指本机API会话“DTC-L1交接-1”。旧账户Main仅作历史查询。本窗口是109历史native/capture资产的维护窗口，不是第二个Main，也不是新增dispatcher。
- Controlled Oracle固定32输入×4模式的128格、D/M/Main最终包及总签署已完成；科学审查接受记录为 `64cd088b2de575157846f07a21ce09748220f7e2`。仅该轮固定trace范围的Goal关闭，DTC-L1研究继续。
- 用户已把64cd的Main接收任务交给Main执行。编制本包时尚未收到其本机接收回执；109窗口不重复派发，不代写Main的CONTEXT，不等待或查询其活动控制面。
- 下一阶段结构建议仍待明确任务。109的历史GPU/native/capture授权不随窗口接手恢复；本轮新增科学模拟、native测量、profile、capture、GPU锁获取和预算消费均为0。

## 调查的核心发现

| 已确认的工作线 | 固定来源 | 当前应继承的结论 |
|---|---|---|
| 2026-10-16，109原生行为、NCU/nsys与SASS producer | `890fb0be7e681a60419c49ca0a7aa85731d8c164` | 12诊断条件＋SpMV主输入＋LayerNorm主输入及一个native敏感性输入，共15个条件。原生与capture确已执行；不能称15个程序或DTC硬件收益。 |
| 同日，109 SM89准入CPU可行性审查 | `d58e75ce32845a281692f19aeb4057b4c9822a3f` | 已完成，`NO_GO_FOR_DROP_IN_SM89_ADMISSION / HOLD`。SpMV不再只是“等待consumer”；LayerNorm仍NOT_ADMITTED。 |
| 2026-11-04，109存储盘点中的DTC专属目录 | `b290790401e248a19427c26c0dde51e6b55ded67` | 整个工作树归档映射为TARGET_UNVERIFIED。与10月指定285成员归档包的PASS范围不同，须现场区分。 |
| 早期M5/Paper-10的SM70采集 | `a9cdb3328a346cbc9a76b7ffadae3725b4209ab5` | producer是AutoDL V100，不归为109 RTX4080采集。若109有副本，只能记为外部producer资产的本地副本。 |

这是已找到并确认的历史工作线，不是“109从来只做过这些”的穷尽证明。尚未提交到GitHub的DTC小型报告、当前路径和环境状态，交给新窗口在明确范围内补查。

## 新窗口阅读顺序

1. 完整读本README、[HISTORY_AND_EVIDENCE.md](HISTORY_AND_EVIDENCE.md)、[GOAL_109_DTC_L1_TAKEOVER.md](GOAL_109_DTC_L1_TAKEOVER.md)、[CONTEXT_SEED.md](CONTEXT_SEED.md)。
2. 读取 [ASSET_LEADS.json](ASSET_LEADS.json)，按其中历史路径开展现场盘点；全部今日状态初始为UNKNOWN。
3. 核对本包 [MANIFEST.json](MANIFEST.json)。按Goal的固定阅读清单，核对producer、consumer、SM89结论和存储DTC行；不要求重读58份来源，更不重审历史raw。
4. [SOURCE_INDEX.json](SOURCE_INDEX.json)提供本次已读取来源的固定commit、Git blob、bytes、SHA256和用途；[evidence/](evidence/)放少量原回执及明确标识的提取结果。

## 第一次交付的价值与停止点

建立“原来源 → 109今日可见资产 → 已有归档回执 → 科学使用限制”的可核查索引，维护109窗口自己的CONTEXT，并给Main一份短接收说明。归档成员映射不闭合、节点不可达或部分材料未找到，均可明确记录后完成接手；不通过重跑旧任务消除未知。

建议独占本机项目目录为 `D:/Codex/Token-API/workspaces/109-DTC-L1/`，这是建议新建路径，未声称已经存在。其他本机根目录可按实际环境选择并在交付中记录。Main的 `D:/Codex/Token-API/workspaces/DTC-L1/CONTEXT.md` 由Main单写。

回传应在独立文档分支和独立接收目录中发布，固定commit、核验回读后 **STOP_PENDING_EXPLICIT_TASK**。首次接手不释放SM89、LayerNorm、modern DTC或Tag安全HOLD，不启动任何新科研执行。
