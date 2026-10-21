# EP-L2 lane collaboration v1

这是一层前台消息与交付索引，用于减少各lane反复复制上下文。它复用现有Git分支和原174的轻量mailbox；不建立调度器、后台轮询器、第二controller或新Goal。E2暂任协议owner，A2/B/C/D/E2/F各自写自己的状态和事件。BA/S/T仅列为inactive support，不自动加入。

用户已通知其它lane活跃，但这不等于协议已注册。公共面板在收到本人真实STATUS/ACK前显示`UNENROLLED`，不显示“已加入”“离线”或“失败”。本协议不能唤醒idle Codex；只有正在执行的lane或下次恢复的lane能前台消费消息。

科学/执行权威仍是[E2现有STATUS及accepted artifacts](https://github.com/swayhrl/accel-sim-framework/blob/hrl/ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261021_E2_CAPACITY_DIAGNOSTIC_r1/STATUS.md)与原中央账本。该链接用于发现；交付必须另钉精确commit/path/SHA。本协议不另定或重置任何预算、截止、T0、资源策略、结果生成量或科学身份。REQUEST、DELIVERY与ACK都不授予完整应用启动、重试、构建、科学接受或合同修改权。

## 文件与单owner

所有repo路径相对于`docs/ep_l2/lane_collaboration_v1/`：

|路径|写入者|含义|
|---|---|---|
|`events/<OWNER>/<event_id>.json`|该OWNER本人，在其注册分支|不可变REQUEST/DELIVERY/ACK/STATUS事件|
|`status/<OWNER>.json`|该OWNER本人|最近一次有实质变化的任务/阻塞/交付状态|
|`state/<OWNER>/cursor.json`|该OWNER本人|已消费ID、dedup key和各sender序号游标|
|`CONTRACT.json`、`PROTOCOL.md`|E2协议owner，经发布|统一字段与边界；不代写别lane状态|

原174本地mailbox是`/workspace/ep_l2_ms20261019_shared/LANE_COLLABORATION_V1/`。每owner只创作其`<OWNER>/events`和`<OWNER>/state`；消费方可在自己的`<consumer>/inbox/<sender>/`缓存外来事件的原字节及来源证明，缓存不变成sender的原始发布或ACK。mailbox只对同一实际文件系统可见，绝不假定F所在机器能读它。

事件以不覆盖的方式创建；相同ID和相同字节为幂等no-op，相同ID但不同字节为冲突，保留证据并拒绝覆盖。STATUS/cursor是每owner单writer的投影，以本地owner传输锁保护原子替换。这个锁仅保护消息文件，不是E资源/运行lease，也不触碰原controller锁。一个owner跨host也只能有一个实际writer；序号碰撞或Git非快进不能用force push掩盖。

CLI只在当前真实cwd等于`git rev-parse --show-toplevel`所得canonical根、origin归一后为本repo、当前branch精确匹配owner登记分支时写入。CONTRACT中的绝对worktree路径只是原174已知参考/default，不是跨host真实路径断言；F须显式指定当前host的真实worktree，并通过同样检查。共用Linux账户下这些检查防误写，不宣称密码学agent认证。不得进入别lane工作树代写、代ACK或修改其AGENTS/旧HANDOFF。

## Envelope、引用及去重

机器字段以`CONTRACT.json`为准。事件至少包含schema、owner-prefixed event_id、owner单调sequence、kind、UTC时间、campaign_id、明确recipients、subject、body、refs、dedup_key。kind只有REQUEST、DELIVERY、ACK、STATUS。UTC时间用于展示；顺序依赖sender sequence，不以机器时钟或文件mtime代替。

DELIVERY至少含一个不可变受信引用；REQUEST/STATUS可没有artifact引用。ACK只能由原事件的真实recipient发出，并须有非空source_commit。

每个受信refs含`repo, commit, path, sha256, role`。commit为完整40hex已发布Git对象，path为无目录逃逸的repo相对普通文件，sha256绑定准确blob字节。producer release、accepted pair、endpoint receipt、analysis及request context必须分清role。外来绝对路径只能作解释，不能充当跨host交付。大raw、trace和二进制不通过消息复制或自动扫描；事件≤64KiB、body≤8,000字符、refs≤32，单次check最多扫描512个传输metadata文件，正常与late-unseen条目合计最多返回128个新事件，只有正常返回条目可consume；cursor≤1MiB/4,096条。默认check/import-event仅验证refs格式，输出`FORMAT_ONLY_NOT_CONTENT_VERIFIED`。VALIDATED/APPLIED另须本人显式确认审查，并由CLI校验本Framework中docs/ep_l2允许的小型文本metadata的普通Git blob及SHA，合计上限16MiB；APPLIED还须输出证据引用。这些校验不证明科学语义或工作实际完成，超界/不支持引用应保留RECEIVED/BLOCKED。

event_id识别一次不可变投递；owner-qualified dedup_key识别同一逻辑交付；可选`correlation_id/work_key`把旧通道与新通道关联到同一科学工作，不能据此合并冲突终态。消费cursor同时记ID、key及sender最后序号：已经确认的同一交付不重做分析、不再次ACK；相同key不同内容不能默默作为新交付覆盖，需明确的新revision/key或保留冲突。修订用新事件和`in_reply_to`连接，不改旧事件。发现尚未见过但序号低于cursor的事件时，列入`late_unseen`保留待明确核对，不consume、不标seen也不推进该sender cursor。

ACK由接收lane本人发回自己的events目录，`ack_for`精确引用原owner、event_id、event_sha256及source_commit。RECEIVED只表示已接收，VALIDATED表示本人已核对artifact引用内容，APPLIED表示本人已完成相应非运行处理；这两者须显式`--confirm-reference-review`本人声明，CLI的限定metadata字节校验不能替代科学内容审查。BLOCKED/REJECTED附准确原因；这些都不等于E科学验收。未经远端发布/独立blob回读的本机预览可以显示，但不能伪装成已发布交付、被ACK或CURRENT_ACCEPTED。

## Git跨branch / 跨host流程

1. Sender在自己原分支创作事件，引用已存在的不可变artifact commit/path/SHA。先保留origin事件，再由原工作流程commit/push；远端回读事件与引用blob。事件不内嵌“包含它自己的未来commit”，避免自引用哈希。
2. Consumer在自己的工作树以`git fetch`取sender精确注册分支，在不checkout/merge/reset其主工作树的情况下，用`git show <commit>:<path>`读取新事件及受信小metadata。检查owner分支来源、event hash、campaign、recipient、sequence及dedup；check/import-event对artifact refs只做格式检查；VALIDATED/APPLIED按上述限定metadata校验，科学内容仍由原科学/分析读取流程另验。Git fetch不代表已经处理事件。
3. 核验和必要处理完成后，consumer只更新自己的cursor/status并发自己的ACK，commit/push且回读。Sender看到该ACK后才可把相应交付显示为真实已收/已消费。没有ACK继续标UNACKNOWLEDGED，不能推断对方退出、失败或已执行。
4. 同174 mailbox可加快发现，但Git仍提供跨branch/跨host持久发布与独立回读。远端F必须走Git消费流程；不能仅给F一个原174本地路径，也不让本地镜像冒充跨host可见性。

## 安全边界和工作节奏

现有lane在本轮恢复、完成一次实质交付、准备依赖工作或到达原任务安全边界时前台检查新消息。运行中的native/app继续由原监护流程管理，消息处理不重启/终止它、不替换其source/spec/协议，不抢占E controller职责。新接收信息可登记为下一安全边界的待办；涉及科学身份/范围变化仍由原审批和门禁处理。

没有新事件或任务变化时，不重复发“无变化”事件、不反复改STATUS、不建立为等待消息而运行的poller。检查达到本轮消息/metadata上限就保存自己的cursor并继续主任务或报告具体阻塞，避免交流索引淹没实验和分析。

## 各lane交付关系

- A2交producer source/build/native/artifact身份；E2独立资格与终验仍必需。
- B/C交机制证据、输入完整来源与候选语义；candidate不自动变正式输入、HOLD不因消息解除。
- E2每接受一对，立即DELIVERY准确CURRENT_ACCEPTED索引及endpoint/identity/cycles/机制结果引用给D；旧FAILED/INCOMPLETE及原始费用不变。传输层不自行验收或重算已有结果。
- D真实ACK intake，随后交增量分析/图和缺证项；分析不能把旧binary锚点混成新binary配对，也不能通过ACK升级科学状态。
- F按其实际host交环境/来源/可恢复性事实；不存在本地路径共享承诺或跨host执行授权。

首轮由E2发布本契约和JOIN请求。其它lane从E2精确发布commit取回协议、CONTRACT和CLI的原blob，在自己的metadata目录保存校验后的副本；从自己实际git根运行，不checkout E2分支、不覆盖旧HANDOFF/AGENTS。各lane在自己的真实窗口/分支自发初始STATUS并ACK。E2可汇总真实事件生成面板，但不代填本人状态。旧HANDOFF、历史通知与原lane工作指令不被本协议覆盖。
