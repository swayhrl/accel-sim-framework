# CPU复核和重现

当前任务已经执行并封存，禁止重复启动同名任务或覆盖输出。原执行顺序为：fetch/读授权/重复检查→新建worktree/分支/输出→g0→编译真实生产parser CPU driver→32个单P/P-list unit→derive→独立reference及生产full read→compare→2D有界可行性/六臂静态提案→finalize→文档与文件SHA验证→commit/push/fetch-back。一次性阶段脚本对现有输出使用exclusive-create，故不可在原目录重新执行这些阶段。首次工具宽度错误与精确原代码保留，不能删去或用新版本冒充首次执行。

初始工具/最终工具来源都在本分支util/dtc_l1的 `btree_*_v1.py` 和 `btree_production_parser_cpu_v1.cc`；SOURCE_SNAPSHOTS保存逐字节副本。BUILD_RECEIPT.json提供完整CPU编译命令、源头SHA、实际编译器和ldd。没有编译GPU应用，也没有链接/执行模拟器。完整大型输入和生产parser日志位置由INPUT_IDENTITY.json及BTREE_CONSUMER_EQUIVALENCE.json给出。

在本worktree根目录，以下命令只读复现唯一变换的完整新成员SHA，同时重新核原始/新成员及完整list；不生成第二份输入、不写A、不读性能：

```bash
python3 util/dtc_l1/btree_replay_readonly_cpu_v1.py \
  --identity docs/dtc_l1/review_packs/BTREE_E_LIST_STABILITY_CPU_V1/INPUT_IDENTITY.json \
  --index /workspace/dtc-hotspot-format-174-v1/other-input-risk-v1/FLAGGED_RECORDS.tsv.gz \
  --original-dir /workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/b+tree-rodinia-3.1/file___data_mil_txt_command___data_command_txt/traces
```

预期：PASS_READONLY_BYTE_REPLAY，6000/5792/208，新kernel-1 SHA `6295eb13625bbc8f25a712917b1b92a02ffcd2e1faba542e555f7845a1288722`，bundle SHA `6e59d31e018befcdd8d9244e6c90d09ab8dd51c665c77785857b690f051ed585`。REPRODUCTION_RECEIPT.json保存本轮实际只读重现结果。JSON identity_contract按 `json.dumps(...,sort_keys=True,separators=(',',':'))` 的UTF-8字节取SHA；路径、文件权限和审阅状态不进入bundle合同hash。

要独立重现全部G2证明，在另一个CPU-only隔离输出目录，以BUILD_RECEIPT的完整未改production TU和真实CUDA头编译driver，并调用 `unit <unit.trace-lines>`、`full <派生kernelslist.g>`；stdout和stderr分别保存为新日志，不能覆盖现有production文件。driver按list顺序读完整kernel/TB，两个JSON结果应与BTREE_CONSUMER_EQUIVALENCE一致。独立reference代码包含原/新精确字节白名单、全部指令/geometry/width/memory解码及hash schema。可在另获授权的新隔离工作区调整其**输出位置和重复任务护栏**重演，不得改源输入常量、解释、计数或冻结parser/Core来获得PASS；任何差异保存FAIL_STOP。

文件包完整性：FILES_SHA256.tsv覆盖本包除自身之外全部文件及六个util证明/复核工具，路径相对仓库根。所有SHA应与实际文件一致；文件自身不作循环自引用。GATE.json的proof_receipts另绑定科学门槛文件。SHA/manifest核验与Git HEAD/tree fetch-back回执共同用于交接，不把Git提交SHA写入自身内容形成循环。
