# 分批运行、资源与归档准备资格

## 本轮已经完成与仍未授权

准确配置、固定35输入与SHA/ROI、来源/binary、原始配对及纯CPU解析已经检查。A将70候选逐一做最终原DH配置等价检查，官方固定Core option_parser独立fixture有6正例和3拒绝例；777与455是循环断言次数/不变量类别，不是1232次科学观测，更不是模拟器运行。模拟器binary仅计算SHA，没有执行。CPU fixture二进制与临时构建不发布。

真实CH-F128/F256入口生命周期、模型自然完成、strict及archive/native restore尚没有新运行证据。因此总体执行资格保持 `NOT_AUTHORIZED`；不能以本次CPU-only PASS冒充实际模型资格。

## 分批

首批8程序×两个F，共16个固定候选，见agents/A/FIRST_BATCH.json。排序先程序顺序，再F128/F256；未来派发可在成员不变前提下按资源填充。首批完成后逐项strict、同输入配对、负例和资源审查通过，再制定剩余24核心程序×2=48候选批次；本包不预先释放它们。两补充与4暂缓独立保留，禁止静默加入首批或改为原始accepted。

## 新合同资源条件

仅作规划的首16资源预留合计约69.95GiB，单点最大约6.98GiB（A历史估计，不是硬上限或未来实测）。该数字基于同输入原始DONE成功/失败峰值，不能保证CH扩展后峰值不变。首次原生执行授权时必须重新测host/cgroup/affinity/NUMA/IO/磁盘和外部负载，依据可用量与增长估计动态准入、滚动更新峰值，不能机械套旧4GiB预测、16GiB cap或旧CPU范围。

lavamd为独立大内存补充候选：已观测峰值约67.336GiB，旧CH-P0因资源保护终止；需新合同独立审查真实headroom、RSS与AS区分、下游扩张余量和完整运行资格。不能因当前空闲大就声称已通过，也不把失败峰值当完整成功上界。SYRK恢复另需独立科学授权，不以“短程序”假设推进。

资源压力暂停新准入；不把杀死健康模型作为常规内存调度。任何实际启动均要独立合法身份，已消费的失败保留，不悄悄重试。无模型启动的普通工程失败可在未来授权范围修正后继续。不可用旧Goal reset、旧360预算或旧UUID获取额度。

## 入口与owner准备

未来使用174-new epoch2原生入口 `/root/data/ep_l2_dtc_l1_native_v2/bin/experiment`，但本轮不调用启动/登记子命令。计划候选ID不是native cohort/UUID或已批准request。

下一阶段首先完成新的科学request、源代码/binary/输入/config hash、资源与归档合同、严格验收与唯一派发owner的正式授权。owner沿用或替换由该新授权明确：不在本轮修改活动owner，也不允许第二个竞争controller；若未来替换，先合法handoff和排他证明，不能直接重启旧Goal。旧DTC私有动态补丁不自动成为第二阶段合同，不导入旧IR/R2补洞路线。

## 归档

大资产、流式压缩日志与结果在真实164挂载下新命名空间；复用只读trace与已核验binary，174只保留必要native执行/恢复材料和元数据，安全余量以已确认5GiB为规划底线，实际启动时独立核查。不得删除或移动旧资产来满足本Goal。

每个未来点需：精确命令、Core/Framework/binary/libcudart SHA、四配置文件bytes/SHA、完整输入digest/trace Entry/expected kernel+CTA+instruction ROI、唯一UUID、PID/start/boot/affinity、资源轨迹、自然EXIT、strict结果、164 archive manifest/SHA及native restore验证。缺任一关键证据，状态HOLD或明确negative，不是accepted。归档失败仅同UUID前向修复，不伪造完成回执。

本包仅准备这些检查条件和计划估计，没有注册或执行任何一项新科学实验。
