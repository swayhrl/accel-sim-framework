# 公共 SM70 工具 R4 与真实配置准备检查点

本检查点完成最终公共代码冻结、独立审查结果的真164存档，以及真实生产配置的元数据核验。尚未激活公共命令，也未完成全量资产的本地恢复。当前 Goal 保持原范围并继续运行。

## 精确范围与统计修正

冻结清单保持125项输入、22769个唯一内容对象、25149条声明成员引用，去重逻辑字节972603859656。常规100、裁剪25；四套分别为Rodinia64、CUDA Samples18、PolyBench/GPU29、Parboil14。56表示冻结清单中不同的精确(suite,program)组合，不能当作全部源版本的程序分母或科研资格数。

Root独立复算发现旧coverage将历史family/版本分母行误当作所有冻结输入的当前数量，造成多项少计及heartwall误报零。ROOT_COVERAGE_FINDING_V1.json保留发现；EXACT125_COVERAGE_V3.json逐项列出所有bundle ID、原始版本及常规/裁剪分布，Root已独立核验每个bundle恰好归组一次、全部版本计数及两个集合指纹。旧coverage原字节、源版本分母及缺口引用保持；issues引用未变。没有把缺损、空清单或科学HOLD变成新合格资产。

UNRESOLVED_PRODUCTION_TEMPLATE_V3.json是未激活的准备模板，正文读取授权仍false、protected_after_ref仍null。其与前版的唯一数据字段差异是coverage_ref，不可当作可执行生产规格。

## 公共代码与独立性

code/保存精确15文件及CODE_MANIFEST.json，CodeID为e2b1a814a201f7f5dd95c55c61a94f04069690dd18ecfabd89c9f88dc7ae19c7，manifest SHA256为312c2ea4e05ca0bb163d2f8a8abdcdb2676131befc32d5fce061158ac035e392。它是供审阅的字节副本；实际版本目录为：

/root/share/mnt164/huangrulin/traces/tools/versions/e2b1a814a201f7f5dd95c55c61a94f04069690dd18ecfabd89c9f88dc7ae19c7

Root已核对所有文件及自指CodeID，实际公共版本仅执行help冒烟检查。运行时依赖同版本兄弟模块、标准库和原生平台资源授权；历史EP/DTC路径只作为严格的元数据重定位键，不作为私有运行时依赖。

最终独立代码报告对非自写组件有限通过；verification_stages.py由Root独立审阅。原R2/R3/R4小样本验证保留原CodeID，未重新标记为最终R4全量执行。Root对19成员审查包完成gzip EOF/CRC及18声明载荷的全部SHA核对，存档在真164 receipts/sm70_public_suite_review_20261025_v1/。

Root代码审查只允许精确不可变代码存档及元数据准备，不等同于生产安装或激活批准。

## 真实配置核验

ROOT_REAL_BOOTSTRAP_V3_METADATA_ACCEPTANCE.json记录Root实际读取55,453,546字节公共元数据、验证25个SHA引用的结果。核验包括：

- 冻结125输入/22769对象及全部成员边的精确集合、大小和两个原有指纹。
- 442个原始源别名、20项历史资产ID投影及原有issues。
- 四份真实归档审计的receipt SHA、原始路径、完整identity与whole-archive SHA逐项对应；不是仅统计四个JSON。
- 22681个kernel对象的既有SM70 header证据映射；另88个命令清单对象不授予ISA标签。没有重新读取trace header或正文。
- 每个程序、版本、常规/裁剪的精确bundle归组，旧分母和缺口来源仍可追溯。

immutable工具保护范围由Root历史来源显式声明，见IMMUTABLE_TOOL_PROTECTION_SCOPE.json及IMMUTABLE_TOOL_EXPECTED_HASHES.json。原科学epoch/registry是其它获准任务可变的授权状态，不能假称其原始SHA一直不变，也不能重采一个before替代历史。最终实际after快照及合法外部差异说明仍待完成。

## 正在执行与剩余验收

SOURCE_VERIFIED_LIVE_CHECKPOINT.json包含实际/proc PID与start_ticks匹配，并记录本轮接收端新分段事件。Source2继续使用未改的COPY_ONLY V10协议，Source KEEP，释放0。该事件的new_payload_bytes只计当前恢复尝试，不包括既有保留分段，不是完整对象或整树最终SHA。

必须继续完成：

1. Source2完整Source EOF/全SHA、真164关闭重开整树全SHA与真实COMMIT；追加真实最终元数据重定位。
2. 最终四工具after快照、可变科学授权状态外部变化说明、实际当前工具/marker/CURRENT/command preimages。
3. 精确最终规格及独立安装/激活批准，等待现有COPY_ONLY owner自然退出后按锁边界安装未来阶段入口。
4. 公共只读catalog/命令/alias发布；三个真实项目工作目录验证全部25149声明成员，并完整恢复小输入。
5. 全22769对象的完整逻辑内容通过Native有界窗口读回，全SHA及公共proof CAS/ledger，不按文件大小跳过；64MiB窗口和256MiB原生任务上限保持。
6. 全部历史别名、20项旧资产、四归档、工具保护、缺口与回执最终核验，真164存档及精确远端Git发布。

此检查点无模拟、GPU、109采集、Source重启、原始trace删除、科学资格/预算/历史改写。有限元数据修复子Lane已完成。
