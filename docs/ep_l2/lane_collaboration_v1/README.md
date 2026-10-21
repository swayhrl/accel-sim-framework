# EP-L2各lane协作入口 v1

E2临时维护协作协议；A2继续负责producer源码及发布，E2继续是唯一正式实验执行/验收owner。协议与CLI已通过24项有界工程检查，不改变既有科学合同、身份或中央控制。

## 本次接入

1. 继续自己现有任务，在安全边界读取本目录`BOOTSTRAP.json`、`PROTOCOL.md`、`CLI_USAGE.md`。E2已收到用户确认；这不代替其它lane本人ACK。
2. 从自己实际Framework工作树显式fetch E分支，使用`git show <commit>:<path>`取回协议版本 **63566312c4dcf03f18c04c5d3db75ab2000a8aed** 的协议/CONTRACT/CLI小文件，核对BOOTSTRAP refs中的SHA，保存在自己的本目录。不要checkout/merge E分支，不改自己的旧HANDOFF/AGENTS。F必须使用当前机器真实worktree和`--worktree`。
3. 在自己的真实branch/git根以本人lane运行CLI。下面将`D`换成自己lane；F加真实`--worktree`参数。源事件已发布并远端回读：

```
python3 docs/ep_l2/lane_collaboration_v1/coordination.py --lane D import-event --source-lane E2 --event-id E2-00000002-ca1c31760483 --source-commit f54f9b40cccf11258b5cf5209466889070384a84 --event-sha256 13bcfecf2834755ad12e0eb22c177d3ee15795a3733db5a3d24a22e587a4d519
python3 docs/ep_l2/lane_collaboration_v1/coordination.py --lane D status --set --body-json '{"activity":"JOINED","current_task":"继续本lane现有任务；采用协作v1","blocking_dependencies":[]}'
python3 docs/ep_l2/lane_collaboration_v1/coordination.py --lane D ack --source-lane E2 --event-id E2-00000002-ca1c31760483 --source-commit f54f9b40cccf11258b5cf5209466889070384a84 --event-sha256 13bcfecf2834755ad12e0eb22c177d3ee15795a3733db5a3d24a22e587a4d519 --ack-status RECEIVED
```

ACK RECEIVED只表示真实接收，并非科学验收或执行授权。按自己原流程commit/push本人events/status/state并远端回读；不要把别lane状态写进自己分支。处理/登记待办后才显式consume，不让check代替任务完成。

## 日常节奏

- 在任务开始/恢复、实质交付后、依赖切换的安全边界和任务结束时前台check。没有变化不重复写状态，不建后台轮询器。
- 本机可发现原174mailbox中的新事件；跨host先显式fetch对方注册分支并按精确commit/path/SHA导入。BOOTSTRAP包含各分支登记，后续DELIVERY包含准确artifact refs。
- 完成交付后本人发DELIVERY并push/readback；接收者本人发ACK。用work_key/dedup_key防止旧/新通道重复执行或重复分析。
- E2 accepted-pair交D增量分析，A2 release交E2独立资格；B/C/F交输入/机制/来源证据，D协调科学候选和分析。REQUEST/ACK不自动授予运行、重试或合同变更。

## 初始接入面板

本面板是2026-10-21T14:25:18.056432+00:00的bootstrap快照，不是实时进程/lease监测。E2已发布本人WORKING状态；A2/B/C/D/F尚无本协议本人ACK，均为UNENROLLED/UNACKNOWLEDGED。没有ACK不能解释为离线或失败。实际接入后依各lane本人分支状态与事件更新，不代填。

该机制不能唤醒已结束/暂停的Codex窗口；本次请用户一次性通知其它lane读取此入口。活跃且已接入的lane后续正常交付无需用户逐条转发。
