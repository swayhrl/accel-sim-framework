# r5补齐目标set联合观测：精确四端修订（尚未批准）

E2直接承担producer、独立资格、唯一中央执行和归因；不需要D/A2任务作为前置。r4四端授权不自动覆盖本次新binary/新条件，当前没有实施build或增加完整应用启动。

现有证据已定位‘必要Tag失败触发未出现’，但r4没有同一时刻reserved占用×新Tag需求×requester/候选/gate联合分布。满set可能遇到的只是同line命中；不能以零FAIL推断从未满。为彻底回答这层，申请纯被动observer修订，不改变原机制。

申请一次批准：

1. E2在隔离树实现、构建并正式发布新observer，完成新源/新schema/新binary和必要native资格。原r4/main61树与binary不改。
2. 同一新binary依次最多执行CFD、DWT、Vector、Conv各1个完整F诊断，55→最多59。四者复用各自准确完整输入、oracle与原F资源参数；只有逐条件资格及实际资源门通过才启动。CFD先接受并交付，再按门滚动。
3. 不新增S、性能配对、机制/Tag优先级/内存参数变更或扫描；失败计费，无退款、自动重试或替换输入。

新增frame保留全部旧212记录与旧decoder。新记录按原frontend once在真实同cache/slice/cycle/UID处计数，snapshot仅const读16way；保存真实联合而非边际拼接。重复preview不计数，skipped/runtimeoff保持NA；表满、溢出、context错绑或输出超限就不能接受。设计和独立预审都是未编译未测试草案，不冒充release/qualification。

预算：每端硬cap384MiB，四端1.5GiB，collector/metadata另640MiB，总预留2.125GiB。当前新增生成7,901,614,638B；为尚未收尾Conv再保守预留306,305,679B后，加上本提案仍比10GiB少247,796,547B；总生成仍比24GiB少970,605,699B。未来启动前按真实账重新核对，绝不重置生成量。

资源：每端CPU1、RAM保守预留9GiB（原8GiB加最多1GiB新host观测余量；设计计数器约128MiB，正式sizeof/分配证据仍需通过）。新build scratch预估≤1GiB；保留原全局CPU/RAM/Share守护和workspace5GiB+活动2GiB余量。当前df不保证四端都可启动；只按实际门滚动，必要时合法STOP，不额外迁移历史资产。只允许在保留正式main/archive/native/build证据后清理本轮新产生且明确列出的编译临时对象，不释放旧资产。

单路成本从当前r4收尾、工程资源实际准入后计算：新producer/资格20–45分钟；CFD10–20、DWT15–30、Vector15–30、Conv50–90分钟，整批约110–215分钟，首份CFD补证约30–65分钟。这是成本估计，不是新的超时或截止；资源允许则并行。

见[精确提案](PROPOSAL.json)、[设计冻结](design/FROZEN_R2.json)、[schema](design/SCHEMA_DESIGN.json)、[未编译接点草案](design/isolated_hooks.patch.txt)、[独立预审](INDEPENDENT_DESIGN_REVIEW.json)。已批准r4的Conv继续运行，本修订等待用户批准。

身份口径：JSON逐行保留旧r4完整identity只作source applicability参照；新条件冻结输入/config/profile/model字段，必须替换为正式r5 Core/main/archive身份。旧r4二进制不能冒充新源。
