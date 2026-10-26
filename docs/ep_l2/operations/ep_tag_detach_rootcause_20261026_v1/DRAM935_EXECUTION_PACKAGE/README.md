# DRAM935 执行准备包：已授权推进，资源准入 HOLD

本包承接用户2026-10-26的“同意，做吧”，范围为前述 E1 DRAM域服务敏感性优先执行。**当前状态：STAGED_RESOURCE_HOLD；实际模拟器/帮助资格调用0、注册0、消耗0。实验尚未运行，尚无性能结果。**

## 冻结的最小实验

- 新cohort：`EP_NATIVE_VECTOR_DRAM935_SENSITIVITY_20261026_V1`，EP_L2，owner EP-MAIN，有界执行者EP-TAG-ROOTCAUSE；不建立长期Lane。
- 复用已接受Vector r5基线UUID `a6b61f77-2ff6-45ad-897c-df0812d01ae8`，850MHz、75039cycles。Core1093/main e511、Framework9dd、trace与四份基础config保持精确字节身份。
- 新增完整应用预算请求仅1次；不自动重试、不退款、不重跑850基线。用户原话及本次有界解释保存在 [USER_AUTHORIZATION.json](USER_AUTHORIZATION.json)，未声称用户授予无限次数。
- 原四份config按原顺序加载，最后追加 [config-4.config](env/config-4.config)：DRAM850→935MHz；core/ICNT/L2仍1132MHz。唯一有效变化是DRAM域服务缩放，不是纯字节带宽隔离。
- T/M/W/V、保护条件、queue、bank及其它容量保持原值。E2 L1 MissQ控制等待E1信息判断，未注册、未叠加。
- 预期56M instructions、15625CTA、1kernel、64slice及完整drain；cycles、detach、队列与流量变化都是观测结果，不设“必须改善/非零”验收目标。
- 上限：RSS/地址空间9GiB、结果384MiB、总预留1.25GiB、wall7200s、单CPU/nice；最终精确native实现和资格仍须核验，不能直接执行ELF。

规格见 [FROZEN_SPEC.json](FROZEN_SPEC.json)。基线raw、binary、所需库/解析器及config的SHA校验已实际执行；trace大正文仅复用先前关闭重开全SHA证明并核对当前可读性/大小，没有将本轮metadata检查写成新body SHA认证。

## 为什么尚未启动

[PRELAUNCH_CHECK.json](PRELAUNCH_CHECK.json) 于2026-10-26 13:14（Asia/Shanghai）记录：

|项目|字节/状态|
|---|---:|
|当前本地ext4可用|36114812928 B，约33.64GiB|
|运行中DTC预留|35GiB sweep＋1.5GiB repair|
|旧EP资源规则保底|7GiB|
|其它未注册项目headroom|1GiB|
|本实验预留|1.25GiB|
|需要可用空间|49123688448 B，45.75GiB|
|缺口|13008875520 B，约12.12GiB|
|RAM与inode检查|PASS|

该计算复用冻结Vector运行器 `vector_runtime.py::resources` 的保守共享池规则，不扣减或重新解释正在运行任务的预留。注册表全局remaining79不等于EP的79次额度；它属于其它已注册请求，不能借用。本次用户新授权没有覆盖已有任务，也未据此修改旧预算。

当前只看到 /root/data 为可用本地ext4科学热输出池；root/workspace/tmp在同一底层overlay，不能作为另一块独立SSD绕过准入。/root/share不能自动改作新的科研热写目标。未删除源数据、释放其它任务预留或干预DTC/SM70/GPU109。

## 已执行的验证

```bash
timeout 30s nice -n 10 env PYTHONDONTWRITEBYTECODE=1 python3 prepare_only.py
```

此工具只输出检查JSON；不包含模拟器启动、注册表写入或共享入口安装。结果为静态身份/单因素PASS，但disk_pass=false。三项独立临时副本负控制均通过，见 [NONLAUNCH_GUARD_CHECKS.json](NONLAUNCH_GUARD_CHECKS.json)：配置字节漂移、额外核心clock变化、额外关闭Tag detach选项全部拒绝。没有运行CPU simulator fixture。

## 后续仍需完成的执行准入

资源满足后继续本次已授权范围，无需重启旧Goal或借用旧请求：

1. 重新检查共享epoch/registry一致、真实资源和未解决intent；有效资源释放必须有原owner的正式更新，不能只看df改善或自行改预留。
2. 先核对当前sole-entry delegation链。当前入口已由DTC revision18继续扩展，不能恢复10月23日旧wrapper。新exact cohort须做有界透明路由接入并保留其它操作；本轮未安装。
3. 在新spec/config边界下完成fresh native加载/参数资格（最多1次help、无trace执行），不给旧850应用资格换名。
4. 通过当前epoch唯一入口原子登记本次fresh预算1，消费前生成intent；异常不自动重试，不复用已消费Vector请求。
5. 仅经 `experiment run-native <本cohort> --project EP_L2`。目前该route尚未接入，禁止直接调用ELF绕过。
6. 自然退出后核对实际clock回显935及config顺序、source/binary/input SHA、完整指令/CTA、drain、原212/r5及RO/资源守恒。保留所有负结果与NA，不要求writeback字节或detach强制等于基线。
7. 生成同binary控制比较：cycles、真实DRAMbytes/实际DRAMcycle容量、scheduler/ingress/missq、bank与Tag分布。DRAM clock同时改变命令时序物理时间与带宽，不能宣称纯带宽因果。
8. 科学接受后按现有COPY_ONLY真164归档、全SHA及独立native恢复流程处理；SOURCE_KEEP。

当前剩余项是实际准入阻塞与尚未安装的执行工程，不是缺少用户对E1推进的同意。本包不声称已经可经sole-entry启动，也不把准备工作登记成应用接受。
