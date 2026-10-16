# Lane B：三项有界producer来源核查收口

授权：`5248a5ed482156450a3baa2799f26ebae02e1d93`。已fetch并核对远端，完整阅读授权的SCIENTIFIC_DECISION/GOAL_B及上一包三程序报告；[授权快照及读取收据](AUTHORIZATION_READ_RECEIPT.json)绑定精确字节。本轮续用原174独立Lane B分支/worktree，Hotspot V2调查没有重做。

**三项结论均为 `UNRESOLVED_FORMAT_APPLICABILITY`，有界核查完成后STOP。** 没有一项被标为SOURCE_BINDING_PASS。已验证的源码、Git对象、稀疏原行检查和源码模型一致性分别标明证据域；这些局部检查PASS不能替代实际采集producer绑定。

| 程序 | 审阅报告 | 本轮新增证据 | 最小未闭合点 |
|---|---|---|---|
| Btree | [BTREE_SOURCE_BINDING.md](BTREE_SOURCE_BINDING.md) | 6000条full32原行SHA/列表关联复核；已检查P-only合同不能产生其单P/32字形态；三个保留ELF的sm70 PC1c40均为BRA，排除作为原LDG来源 | 固定采集采用的实际列表合同/producer绑定；旧E-list家族相容仍不是capture绑定 |
| 2DConvolution | [2DCONVOLUTION_SOURCE_BINDING.md](2DCONVOLUTION_SOURCE_BINDING.md) | 从2021年fork真实Git对象证明version3源码仍打印P、按E编码；包内postprocessor不重编码地址 | 当前trace与旧E或修复后P合同的绑定；version3/NVBit/日期不足以区分 |
| LUD | [LUD_SOURCE_BINDING.md](LUD_SOURCE_BINDING.md) | 40个global PC、19840条记录与历史源码模型全部一致，支持冻结firstP16地址；40个首样本标签之外19800条通过核对 | 原producer、编译宏/SASS/predicate/执行区间与固定输入的绑定；源码模型不能独立认证capture |

## 工作量与复用边界

复用已登记65-member元数据及104476条风险索引，验证原index压缩/解压SHA。没有再次顺序扫描65成员或完整629成员正文。仅对Btree6000条及LUD global19840条按旧偏移读取原行，合计25840行、5345970字节，涉及32个原trace成员；每条都核对原行SHA。2DConvolution的40940条与LUD shared37696条只复用原索引/报告，没有重扫其正文。

局部资产核查限定为：原launcher精确目标路径；一个保留的、可seek外层tar的header；其中约76KB源码/元数据；一份394604504字节Git pack/index和18167字节loose objects；一个45793177字节validation二进制子包及三个Btree候选。外层header使用seek跳过大成员；**没有打开内嵌的大trace归档**、没有读取整个40GB包作hash、没有重建或迁移工具链。Git pack用于验证已有源码对象，ELF只经cuobjdump11.8反汇编，没有执行ELF、GPU或模拟器。搜索缺失的结论仅限已记录范围。

原源码和Git证据见 [ARCHIVED_GIT_SOURCE_PROOF.json](ARCHIVED_GIT_SOURCE_PROOF.json)、[APPLICATION_SOURCE_RECEIPT.json](APPLICATION_SOURCE_RECEIPT.json)、[ARCHIVE_ASSET_RECEIPT.json](ARCHIVE_ASSET_RECEIPT.json)；producer条件比较见 [PRODUCER_POLICY_COMPARISON.json](PRODUCER_POLICY_COMPARISON.json)。[INDEX_AND_SOURCE_MODEL_RECEIPT.json](INDEX_AND_SOURCE_MODEL_RECEIPT.json)明确区分直接原字节、历史合同条件与未绑定原编译物的源码模型。SOURCE_REGISTER.tsv、PRODUCER_SOURCE_LOCATIONS.tsv提供逐条证据索引。

## 保持的科学与运行状态

按授权，原Btree/2DConvolution/LUD的terminal PASS保留，科学适用性为FORMAT_APPLICABILITY_REVIEW_PENDING；本报告不改写Lane A台账。没有认定既有结果错误，也没有标为已证明不受影响。原trace、主parser、运行binary、Lane A状态/44行注册表/launcher和既有HOLD均未由B修改。

本轮没有选E/P或某个动态锚点作新的科学输入定义，没有生成正式派生输入或配对性能结果，不根据地址合理性、bank冲突或性能选择解释。Hotspot的有条件新输入准入授权仅归Lane A执行，本报告不承担或重新执行该工作。不能把本包的任何局部一致性升级为无条件native/GM12结论。

每项最小缺口与后续选项已经给出。缺少充分来源时按授权停止本项扩展；无需继续搜整台机器、解压其他大trace包或无界重建编译器。若将来补到可绑定证据，或用户另审一个明确的新派生输入定义，可再开有界工作；本轮不自动推进到该阶段。

## 复核

FILES_SHA256.tsv绑定本包、CPU证明工具及复用的小型证据；VALIDATION.json记录保护与范围检查。本轮提取的候选ELF、源码资产、Git对象和反汇编保留在独立输出 `/workspace/dtc-hotspot-format-174-v1/source-binding-v1/`；原trace仍在原只读路径，这些大资产均不提交Git。工具重现说明见 [REPRODUCE.md](REPRODUCE.md)。
