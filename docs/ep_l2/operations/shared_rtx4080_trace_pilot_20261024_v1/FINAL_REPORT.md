# 4080资产核定与单输入采集闭环

本次只执行VectorAdd一个程序，未启动任何模拟器或批量采集。109 RTX4080原生正确性→完整SASS采集→后处理→真164挂载存档→174-new两个工作目录完整重读→父任务独立archive/tar/expanded重读均通过。

## 资产证据边界

|测试集|前轮有trace家族|4080身份有证据|其他家族|
|---|---:|---|---|
|CUDA Samples|10|本次新VectorAdd 4M；固定2022源码版本，不能替代旧9.1输入身份|另9个缺GPU来源证据；CUDA全集尚未冻结|
|Rodinia3.1|19/23|未在已审核记录中确认|19个已有SM70资产来源未知；4个缺齐备展开资产|
|Parboil|9/11|既有109 SpMV small，4完整kernel，SM89|另8个已有资产GPU来源未知（含MRI-Gridding仅裁剪）；LBM/TPACF缺齐备展开资产|
|PolyBench/GPU1.0|15/15|未在已审核记录中确认|15个既有资产GPU来源未知（9常规+6仅裁剪）|

59行证据矩阵见evidence/RTX4080_PROGRAM_STATUS.json及PROGRAM_4080_STATUS.csv：53个前轮已有家族+6个缺口。Rodinia2.0-ft的11组旧输入不并入3.1。SM70只证明cubin/trace ISA，4080可运行旧cubin，不能据此宣称不是4080采集，更不能直接认定必须重采。未见GPU来源证据归UNKNOWN，不归不可运行或不存在。源码可构建性也尚未覆盖所有程序。

既有SpMV的来源证据在EXISTING4080_EVIDENCE.json，包括GPU UUID、原生正确性、固定input/binary SHA、4kernel header、历史164回执。它与本次Vector都仍为SIM_ISA_HOLD；已知旧格式语义缺口不由结构完整性自动消除。

## 精确试点身份

- 官方源码：NVIDIA/cuda-samples db3eea23946bca2e90a75eca2b5b3e07158a9e11，Samples/0_Introduction/vectorAdd/vectorAdd.cu，Git blob284b0f0e332f022ed6789456182238fc2fc6af54。
- 参数：4,000,000 float，srand(1)，glibc rand输入，256线程/CTA，单kernel，无采样/裁剪。
- Host补丁：固定参数、标准头文件、完整数值误差/摘要、显式设备初始化；kernel源码未改。上游源码SHA9a156c7c4f1ab0759d859af95c8dab55f2280d867edca7daee4546d63effb583；最终源码SHA97bf1525281d9288bdadf61f197935db5123828b55c24a4448a44c6468083e78。
- 编译：/usr/local/cuda-12.8/bin/nvcc -O3 -lineinfo -arch=sm_89 source/vectorAdd.cu -o bin/vectorAdd；最终binary SHA1819fe6c9720b417e34a122e9b013bf1b09835850e23606d901fdf1ca8b2227f。
- GPU：GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59，RTX4080，驱动580.178.04；NVBit1.7.5，tracer version5；工具源码HEAD7f38c063fa853525680effd8454d4899c7895ff5。
- Tool SHA14891b344554ff221423f51e970e1d0c92ab78c9375d9f993dafbfd8420af3db；后处理SHA c7691bb9e3d37fe1da491f9f182cfbbe8c657687ecc1fb4992a7fd8dc86270a2。
- 最终capture PID335332，start_ticks343877943，exit0；数值max_abs_error=0，FNV64=0a8162dae8a16ac5；15625 CTA、125000 warp、2125000条记录、64000000 active-lane instruction instances。每warp17条，且1条有效终止EXIT。

## 尝试历史与限制

CPU编译第一次因-arch/-code参数搭配报错，未使用GPU；修正命令后成功。实际共2个原生正确性进程、3个采集进程。前两次采集exit0但没有任何trace，不计成功；第三次直接Popen binary、避免把LD_PRELOAD加载到nice/ionice包装程序后成功。第一次stdout被第二次脚本路径错误覆盖，原始stdout未完整保留；该次PID/start_ticks/exit回执、原源码和binary仍保留。README明确披露，不能声称所有失败原始日志齐全。后续独立attempt目录必须不可覆盖。

共享GPU锁、15秒GPU空闲检查及驻留ComfyUI身份记录齐全。原DTC脚本要求无任何compute进程；本次父任务在用户授权范围内明确允许已知空闲服务驻留，出现新增计算/竞争只停止自身试点。服务未被停止或修改；不使用本次耗时作性能结论。

实际SASS包含ULDC.64/UR、谓词以及宽寄存器依赖；现有trace未完整表达这些域。本次PASS仅为producer正确性、结构完整及归档链路，未给予EP/DTC/AWMA或Ada模拟资格，未修改任何科研预算/入口。

## 存档与读取

真164路径：/home/shared/huangrulin/traces/rtx4080_sm89/pilot_20261024_v1。
174-new挂载：/root/share/mnt164/huangrulin/traces/rtx4080_sm89/pilot_20261024_v1。
expanded/rtx4080_asset_pilot_20261024_v1/capture_attempt3/traces/kernelslist.g为完整输入入口。

payload.tar=13,537,280B，SHA17e4fa4b946ccbd2e3472d37d821bcb5488ed939fc0e0e93cd7bf4dea94dcac3；36个封包payload文件共13,449,949B；MANIFEST SHA c04d34aa09a9642110727ab9e5bd57afbbf291b06767ac8bff36a632a4afc403。归档另含MANIFEST本身，不能把36说成全部tar文件数。sourceKEEP，release0，无SSD payload暂存。

共享SOURCE/TARGET锁单流传输，archive关闭重开SHA及expanded全部成员SHA通过。174-new从/root/workspace和/root/data各独立完整读取36成员及archive；父任务另逐tar成员及expanded SHA通过。验证范围是已确认真164源身份的SSHFS挂载，不声称在164原生执行。COMMIT.json与READBACK_174NEW.json及父回执附在本目录。EXISTING4080_EVIDENCE.json是封包后的补充来源证据，位于NAS同级，SHA69c27a1c11a24b927fe949bc1a7c9ac58ad8b0a9397c603c47ad503cd15f5e34，不改写冻结包。

## 下一轮补齐的先决条件

1. 冻结测试集版本、程序/实现、官方预定义输入完整分母；CUDA源码候选与已验证程序分开。先补每程序完整标准输入，再补各预定义尺寸。
2. 为旧资产寻找GPU UUID/采集日志/原生回执，分别判复用、未知、缺失。不能只看SM号重采所有内容。
3. 修复并冻结Ada采集格式与消费者契约，针对constant地址、UR/P、宽寄存器高半做SASS对照；没有资格的原trace可保留，但不能作为模拟正式资产。
4. 每任务固定source/patch/input/binary/tool/GPU并独立native校验；通过后全kernel采集，attempt目录永不覆盖，失败不自动退款或丢弃。
5. 沿本试点已打通路线109本地→受管单流→164封存→174-new全项目公共目录。常规完整优先；裁剪仅由已验收完整父资产派生，保留比例、kernel/CTA选择规则与父SHA，原SM70裁剪不可冒充SM89。
6. 批量前再核GPU空闲/工具可用与本地/NAS空间，冻结每输入时间/空间限制及总预算。不得启动旧Goal或自动模拟。资产可读与各项目运行资格分开。
