# EP-L2 / ISCAS2027 review_r6｜四Lane静态交付、R0.1源修正和S01源盘回收审查
2026-10-16。**GitHub证据审查记录，不是新Codex Goal；不启动任务、构建、仿真或Storage-Ops，也不覆盖review_r5合同。** 各提交只代表回读时快照；新Lane报告以随后准确HEAD/STATUS/RECEIPT和生产证据为准。

## 1. 科学结论（严格分层）

- 已读四Lane新Framework发布：
  - Lane2 `d1f302c51d3ec7718a22748792a1e610f17eb6d5`，Core `cbdf145314dbe5dcd9006a5de4e94f7b19fbbb71`，包 `FT20261016_LANE2_EXACT62_STATIC_r1`。
  - Lane3 `5b5e6dd49781e97fdac4f120a8a2e652d32508d3`，Core `dfd9d5459f189d4d85a0ff33fc83ed7a75fc3ba2`，包 `FT20261016_LANE3_EXACT_CANDIDATE_r6`。
  - Lane4 `69671a55883f22cd9c7227b6dc0e6b87998f6e05`，包 `FT20261016_LANE4_REVIEW_R5_STATIC_ADAPT_r1`。
  - Lane5 `e8f701995a27154ffcc54cc38245dde8cd7f9bdf`，包 `FT20261016_LANE5_REVIEW_R5_r1`。
- **以上静态/工具交付按其scope可接受为后续精确源集成输入，不是生产资格。** Lane2 10项增量源码、9正向+4拒绝测试准备（0 C++执行）；Lane3 28静态+8 Python（0 C++执行）；Lane4 66 Python runner/acceptance测试（仅合成工具fixture），新R1.1 18格全部NOT_RUN；Lane5 11个独立gate/21条production execution计划（0实际执行），旧六R0科学SUSPENDED，新R0.1 0正式pair。
- 精确Core旧候选 `62dc1d179b5516e68b21b695c7a9c5d0667e9671` 的 `l2cache.h` 同一个`memory_sub_partition::ft_bank_grants_for_test(unsigned) const`有两份**真实相同定义**。独立比较Lane2 `BASE_HEADER_DUPLICATE_FIX.patch`删除第二份、Lane4 `R0_1_DUPLICATE_ACCESSOR_ONLY.patch`与Lane5 `REMOVE_DUPLICATE_BANK_OBSERVER.patch`删除第一份；两选一不叠加，不能拿整TVD/ideal补丁来修R0.1的纯Header缺陷。
- **后续新提交已解决本缺陷**：Lane1 isolated Core **`c948184504d82b80e23eb3f4ff6cdfd328ba9355`**，对外Core branch **`57e1c363aede1a7790bdf94136d832d35ee7b34b`**（tree相同），Framework正式构建输入 **`3ab150b3e99ff3ed759b8cdc5154cfb5744042a7`**，Lane1 Framework执行分支发布 `85534de235345292a153d9983cfd0d24d8033bb2`。直接检查Core差分只有 `src/gpgpu-sim/l2cache.h`单定义移除与 `tests/ep_l2/test_ft_wbuf.cc`测试fixture物理cycle同步两文件；未混合RO/TVD/ideal或改变科学容量/config。已回读 `build_r0_1.py` 的固定 `CORE_CANDIDATE=c9481845...`，源身份pin同步。此仍是**未编译源候选**，binary=null，Lane5 11gate均未PASS；不能将原62的静态19PASS/1FAIL自动升级为此新候选的独立科学PASS。
- Lane2 TVD：原3文件/6 hunk冲突已静态适配62树；TVD源已保留WAD与WB分生命周期、physical bank与host拒绝。**下一阶段需在真正最终官方R0.1父版本上重新检验最小差分**，源更新c948改变Header意味着旧对62的full patch不再自动等价；不要为了这类小修反复在活跃机器做完整编译。Lane1最终集成、Lane5独立资格。
- Lane3 RO：验证新的`ft_try_force_tag_access`直接入口在RO epoch启动/结束后可绕过旧wrapper guard；r6在实际try入口先非破坏性拒绝，相关静态/测试条件合理。仍需真实生产negative/sector/generation/ICNT/offset验证；保留旧完整epoch oracle、FWT空证书，禁止新应用宣称。
- Lane4 ideal：`CORE_IDEAL_TAG_TIMESTAMP_ONLY.patch`将原生Tag touch时间保持为物理cycle+memcpy offset，而FT bank/response保持物理cycle，作为**未编译**合理候选。**独立的科学/数据正确性阻塞**：R0.1允许后续clean/quiescent host prefill，而R1.1 `ReferenceMemory`对它没有相应的版本更新；I_READ_HIT可能读取旧GPU写后版本。建议R1.1设计针对实际成功prefill、精确sector的引用同步，并以producer/Lane5证据验证；若需改成initial-only scope必须明确用户审科学语义。此问题不阻塞R0.1 U_WB16首批应用。
- Lane5 current acceptance V2/generation2仍对旧R0/R1六完成应用的科学用途有否决权。其 `CURRENT_ACCEPTANCE_SOURCE_AUDIT.json`还明确指出**Lane6 r3未完整处理未来动态withdrawn_releases和全部identity/proof closure**（旧六条当前被拒是有效的已测scope）。Lane6后续新revision在**第一个R0.1正式pair入稿前**须采用Lane5 V2 API或等效完整验证；不重绘旧撤回图。Lane6当前窗口在执行，不要打断、不发初始Goal。

## 2. Storage-Ops最新执行进展（两端独立权威）

- 旧174源侧仓库 `swayhrl/gpu-l2-cache-verilog`，分支 `hrl/ops-174-source-audit-exec-v1`：已发布 `e17f055726e86875b243ff2268fbd93fec8bb884` V6多项目有界inventory与S01 READY。后来发布 **`5e5ca557e35bb4763d2af4bac9752fad3dc0d3bd`**，`STATUS` 为 `V6_S01_SOURCE_RELEASED_AWAIT_TARGET_CLOSEOUT`。S01 52项经完整source/bridge/SSHFS SHA校验后，旧174独立复核并精确释放所列`.vvp`；实测df从**38,039,896,064→38,457,888,768B**，净**+417,992,704B**；52项allocated size总418,152,448B，不混作df净回收。其余5,252非`.vvp`保留、Git pack全部KEEP。S02待目标侧S01 closeout，不应另外新建传输者。
- 174-new目标侧 Framework `hrl/ops-174new-164-archive-exec-v1` 发布 **`50b65787764a927eca0ea9780c46b135c075ca33`**，`20261016_storageops_05/STATUS.md`：S01 `DEST_VERIFIED` 52个文件、418,020,580逻辑字节，close/reopen经SSHFS检SHA，另有**1个8,234,735B抽样恢复**；后者不是整批RESTORE_VERIFIED，不是164-native SSH校验。目标侧其发布回执当时尚未消费后来源侧释放证明；以后应以源侧较新回执核对并闭合S01，再按V5/V6按序S02，不重复nonce或历史36批pack。
- 旧174源侧多项目 `MULTIPROJECT_AUDIT.md` 发现优先审核池：三个历史V3干净RTL checkout共536项`.vvp/.o/.so`约**10.20GB allocated**；另三个C2P/M2D旧checkout对象约**1.43GB**，合计**11.63GB为待证明的候选而非批准回收量**。仍缺per-run源码/filelist/toolchain/唯一binary/owner资格及恢复证明，不能直接删除。814个直下`/tmp/*.vvp`约7.00GB同样未获逐项provenance；老dirty-testbench产物、主RTL postcheck、Decoupled-L2 pretraces/extract、M5 trace和C2P/TLS实验记录默认SOURCE_KEEP，DTC-L1当前7模拟进程及C16活跃资产不得碰。Git `tmp_pack_*` 不gc、不prune、不可删。
- 旧174为多项目共享overlay，S01完成并不代表空间达到资格：源侧S01后一次最新df约38.45e9B free（约35.8GiB），离Lane1的48GiB+2GiB构建准入仍缺约14GiB且有并发写入。S02历史约0.376GiB allocated也无法独自解锁。Ops按V6优先**有出处的低风险历史构建物审计和冷归档副本**，不向DTC-L1/C16或科研raw/trace未经授权释放。

## 3. 科学与工程执行优先级（不立即发新Goal）

1. **Lane1纯源码编译阻断已修复，无需再传三份修复补丁**。新Core c948 / Framework3ab固定pin现可作为唯一下一build输入，但只在真实48GiB+2GiB、64GiB RAM及共享registry准入通过后按原driver唯一构建。实际21条生产定向不因fixture时钟小修减项。
2. **Lane5**须在新c948/3ab/core-pub身份上重新绑定自己的独立11gate/21执行清单，待新binary测试通过后才发新资格/新run keys与五开发负载B16/U_WB16。旧R0/R1仍全部SUSPENDED，0个合格pair。
3. **Lane2/3/4**静态成果保留为候选，等Lane1最终官方R0.1或R1.1的实际SHA后精准replay最小差分，不因当前c948小补丁反复申请大构建、不混生产binary；R1.1 I_READ_HIT参考同步需后续独立验证。
4. **Lane6**等新pair，同时独立准备V2未来撤回/完整identity与proof兼容的fail-closed新revision；写作/PPA照旧并行，不虚构perf或物理面积。
5. **Storage-Ops原两窗口**依序完成S01源释放回执双端闭合与S02并推进V6候选审计；不另建scanners/runners，来源/项目owner不明的科学资产仅可冷备份、不得自动release。
6. 论文核心仍围绕同容量banked B16 vs U_WB16真实有效性，机制copy、容量借用、服务及cycles分开审查；不因ideal旧1.721x或shadow WBUF/旧suspended数据提前写加速。

**审核结论：允许保留Lane2–5此次静态/工具交付作为后续开发输入，Lane1公共编译阻断已源级解决；无新R0.1应用资格、无授权降低空间门槛、无额外数据删除权限。**
