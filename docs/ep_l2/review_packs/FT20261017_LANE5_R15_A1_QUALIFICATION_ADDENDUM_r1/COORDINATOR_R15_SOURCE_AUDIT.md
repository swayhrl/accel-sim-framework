# EP-L2 review_r15：源码独立审查与三项优先修复问题

2026-10-17。**CODE_REVIEW / LOCAL_EXTRACTED_FUNCTION_REPRO，不是正式模拟器资格，不是新Goal，也不修改正在执行的源、进程、资源政策或科学ledger。**

结论：不能宣称当前实现已排除大错误。公共B16至少有一项需要优先处理的跨周期替换一致性问题；RO有两项独立的bank重试前进性问题。下面的局部反例在ChatGPT隔离容器运行，没有在旧174/174-new上启动编译、模拟器或修改任何项目资产。完整cache/partition/应用回归尚未执行。

## 1. 源码快照与审查范围

- 公共Core `c948184504d82b80e23eb3f4ff6cdfd328ba9355`；Lane1发布 `57e1c363aede1a7790bdf94136d832d35ee7b34b`，同tree，终查仍为该Core。
- TVD开始审 `ab413abc2030bfc9aaeea0579b34dfa998671adb`；终查读到 `be5dcbe1fa5b9a501e81a77a6c399e6f6530e536`，其texture-only路由及clean retention修正差分已读，仍是未编译候选。
- RO开始审 `5ae8b06d58b61189140f571ab37b5f6d51228632`；终查 `3f3a8149b1ba18c1421a2a1a7f4073d76ad641f3`。重新读了该版本的bank request、store-port和runtime prepare，下面A2/A3逻辑仍在。不能把它新增的native ownership refusal测试等同于这两类bank回归。
- Ideal `8ff56eb0804a027f1e253e629dd2915b02bc03b5`。
- Framework正式build入口 `3ab150b3e99ff3ed759b8cdc5154cfb5744042a7`；Lane5代码终查 `ebd57580bdae2b9690d3f3e9e8dafa056c510e74`；Lane6 `d99195b5800de404b0f31c9c43742612428a168d`及其固定r4 V2 intake。

已读核心：ep-l2-ft-cache.inc、gpu-cache.h的payload allocator/arbiter/sector状态、gpu-cache.cc的Tag probe/MSHR/fill/dispatch、l2cache.cc的响应/返回/frontend/下层承载，TVD directory/cache/production接线，RO runtime/transactions/store-port/oracle绑定，Ideal reference和真实partition hook，正式build及Lane5 registry/acceptance/run/qualify_r0_1，Lane6 dependency_probe/current_pair_intake。不是整个仓库逐行形式化验证，不涵盖完整RTL/STA或真实数值应用正确性。

## 2. A1 — P1：跨周期未完成替换的victim不稳定（主线优先）

代码：公共 `src/gpgpu-sim/ep-l2-ft-cache.inc::ft_access`；`gpu-cache.cc::tag_array::probe`；`gpu-cache.h::sector_cache_block::fill`。

每次ft_access都会重新probe得到index。初次MISS将victim/index/WAD/staging保存进m_ft_pending；B16 phase0只完成resident读入copy latch便返回RESERVATION_FAIL，native Tag还未安装。后续要求 `assert(p.tag_index == index && probe == MISS)`。

问题是：实际cache_cycle在下一次frontend重试前会处理其它行的Fill。Tag probe跳过RESERVED way；sector fill将它改为VALID，但不更新line last-access/alloc time，因此可替换候选集合会改变。

反例：一个16-way set，way1为唯一可驱逐dirty行，其余way均有pending sector；way0的既有last-access比way1更早。周期t先选way1并开始B16 copy；周期t+1 way0先Fill完成，再probe时选way0；原pending仍绑定way1，断言不成立。新Fill尚有payload pin也不能阻止这次Tag选择，pin不属于probe输入。

**实际局部执行**：同目录 `repro_replacement_target.cpp` 抽取原probe函数体、使用最小block/config fixture建模对应Fill状态，得到pending=1、reprobe=0。显式执行原等式断言的子进程为SIGABRT。不是完整ft_access或全GPU重放。

修复不能只删除断言或只改局部index：native data_cache::access也会probe。必须让preview、已保留victim及native提交使用同一事务身份，或在发现改变时于native修改前完整rollback旧WAD/staging/landing/bank token/generation后再准备。Lane1修复，Lane5补真实多way、copy两阶段之间其它way Fill的回归，B16 C8/C16与匹配U-WB都要覆盖。不要为这一新增边界重跑所有历史校准。

## 3. A2 — P1：RO→RESIDENT使已排队的bank retry键失效

代码：`gpu-cache.h::ep_l2_payload_store::request`，`ep-l2-ro-store-port.h::tag_ready`，`ep-l2-ro-transactions.h::fill`。

Bank的pending/granted按(role,id,write)匹配，选中的旧grant跨周期一直保留到相同tuple重试。request(handle)却每次取slot当前allocation_role。RO最后一个required sector返回时，tag_ready(complete)马上将RO转为RESIDENT，没有同步已经排队的RO response read。

反例：attached transaction部分sector ready，最后一个sector的fill已在等bank，之前ready响应因背压尚未发出。响应阶段先尝试RO读，被已选中fill挡住而留下(RO,p,read)；随后fill完成，将role改成RESIDENT。下一周期bank选旧RO读，真实retry却是(RESIDENT,p,read)，旧grant永远不被消费。

同目录 `repro_bank_retry.cpp` 使用原request控制逻辑：1000次后续重试均失败，原RO grant保持；稳定role对照下一周期成功。

修复应使逻辑操作的重试身份跨role稳定（考虑payload ID+generation/精确操作身份，或显式迁移/取消协议、合适的延后role转换）。不得简单每周期清所有旧grant、添加免费端口或绕过bank。由Lane3处理RO生产回归；若改公共仲裁ABI，Lane1审共同约束，Lane5独立验收。

## 4. A3 — P1：响应重新选择让旧bank grant再也等不到原请求

代码：`ep-l2-ro-runtime.inc::prepare`与`ep-l2-ro-transactions.h::ready_response`。

ready_response每次从cursor扫描slot；prepare只有拿到bank grant后才保存selected=true，bank拒绝时不保存本次候选身份。cursor又只在成功commit后改变。

反例：cursor=0，只有slot4响应ready，slot0 fill pending且二者同bank。slot4读被更老的slot0 fill挡住而排队，随后slot0 fill完成变ready。下一周期bank选旧slot4读，但ready_response重新从0扫描、总是选slot0。slot0等slot4的grant释放，slot4又不再被重试。

局部执行1000次拒绝后，手动重试原slot4立即成功。本反例令slot4角色稳定，所以**即使修复A2，A3仍需独立修复**。应在首次denial后保持候选直到完成/合法取消，或精确取消被放弃token后换目标；不得新增隐含免费数据buffer。必须增加同bank两个transaction交错ready、ICNT full→available与跨周期retry的真实回归。

## 5. 其它已查部分

- 公共WB：已读路径在lower真正接受数据之后释放staging，WAD到set_done；普通descriptor/pin在实际响应入队后才释放。局部稳定requester测试1000周期观测每bank每周期最多1grant，但这不证明前进性。
- TVD：已审共享128目录、mandatory优先、dirty inflight转发、+1cycle查询、read lease/pin、clean promotion与dirty满目录原位复用。未找到独立于A1的新确定数据丢失反例；Lane2新texture-only/clean-retention差分应做其生产回归，不能把旧served bytes当DRAM节省。
- Ideal：完整原 `ep-l2-ideal-reference.h` 本地字节Git blob为 `41da8ec3dfc7a27f2e1c55ff0a4f37d5d03513e6`，与远端一致。以ASan/UBSan编译header测试，selected-sector reset、其它字节保留、snapshot、repeat、producer单调、cold/high-address通过。没有运行真实partition新回归或18格，不升级R1.1资格。
- 构建/验收：正式build检查source/vendor/flags并保存21实际执行，Lane5核真实test/log/clock marker且不把21通过自动变成11-gate证书；acceptance V2拒绝withdrawn Core/binary，将launch与result分离；run前后全输入hash；Lane6使用current V2/native adapter/final ref freshness。已读链路未见仅靠旧COMPLETE_VALID就直通接受的分支，但没有在本轮运行整套Python/并发registry测试。
- 工程检查点：官方build运行中主要看local_resources(/workspace)，实际--out可能落Share；应由原preflight/owner核实输出盘余量。这是需确认的覆盖点，不在本轮直接声称已发生磁盘故障，不新增资源policy。

## 6. 本地执行与不能外推的边界

测试在ChatGPT隔离容器，C++11 + AddressSanitizer + UndefinedBehaviorSanitizer；没有旧174生产编译、真实应用trace、中央lease、源文件删除或科学资格修改。三个程序（Ideal原header测试、原bank函数抽取反例、原Tag probe抽取反例）均实际执行；原等式断言作为单独预期失败子进程关闭core dump。

```text
PASS actual header: selected-sector reset, unrelated-byte preservation, snapshot persistence, idempotence, monotonic producer, cold-prefill, high-address separation
CONTROL stable role and selected requester: grant at next cycle
REPRO role transition: 1000 consecutive denied retries; selected old RO read remains parked
REPRO candidate switch: 1000 denied retries of new slot0; retry of original slot4 releases grant
CONTROL stable requesters: max bank grants in any physical cycle=1
REPRO B16 replacement target: pending tag=1, reprobe after unrelated fill=0; original ft_access invariant is false
Expected original replacement assertion: SIGABRT reproduced in the fixture
```

完整用户交付包另含原header、抽取函数、scaffolding、独立运行脚本、SOURCE_LOCK、全部日志和LICENSE。GitHub同目录提供两个独立C++反例，编译命令见文件头。

## 7. 下一步处理，不开泛化新审计

- Lane1：A1加入真实定向并修复，保留失败证据/旧source，发布新准确候选。新Core必须重绑定正式build与Lane5相关gate，不强制清空/重跑其它历史实验。
- Lane3：独立处理A2/A3，复用已有r14正在执行窗口，无需重启原始Goal。公共arbiter变更需由Lane1集成审查；RO默认OFF主线不必等待所有RO结果，但A1是B16/U-WB首批比较的优先项。
- Lane5：把新增反例加入受影响资格计划，只有真实新binary生产回归闭合后才能给接受。审查文档不是对当前ledger的自动写入或撤回命令。
- Lane2/4：只同步共同父版本的受影响delta和回归；Lane6不提前写所有机制均已验证。

**本报告发布不代表Codex已经消费，不自动停止/重启正在运行的任务，也没有替用户直接改动生产源码。**