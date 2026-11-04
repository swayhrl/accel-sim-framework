# Historical Node109 report — public review copy

- Source ID: `model_retirement_20261028`
- Original SHA256: `62eb680bdb3e2ef5224f4ca1619e49f33d0ddf051a2eb4623e2881731ea1e0ab`
- Status: Historical snapshot, not the 2026-11-04 current-state result.
- Disclosure: Private host/account details were replaced; see `HISTORICAL_REPORT_PROVENANCE.json`. The local original remains unchanged.

---

OLMoE / Llama-3.2-1B 清理执行完成

用户明确授权后，已完成当前完整SHA、恢复抽检和临删依赖检查，并清理109两组本地冷副本。164权威副本保留且删除后逐文件仍可达。没有清理Qwen、ImageLab、stagea或AWMA。
完成时间：2026-10-28T07:01:04Z。
109控制目录：/home/<OWNER>/non-imagelab-model-cleanup-control/20261028T064442Z_olmoe_llama_v1；持久worker PID 1445446。

逐模型结果
/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e
  已删除12文件；逻辑13,842,594,366 bytes，去重数据块13,842,640,896 bytes；原revision目录已不存在。
/data/c16/models/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08
  已删除6文件；逻辑2,480,783,094 bytes，去重数据块2,480,807,936 bytes；原revision目录已不存在。

合计18文件（OLMoE12含receipt，Llama6），逻辑16,323,377,460 bytes；原文件nlink全为1，按(device,inode)去重后的数据块16,323,448,832 bytes（15.202396GiB）。只逐文件unlink并rmdir已空revision目录，保留/data/c16/models与OLMoE公共父目录。

删除前门槛及证据
1. 109当前18文件完整SHA全部匹配历史payload基线/OLMoE receipt本次小SHA；164当前同18文件完整SHA也全部匹配。两端每文件读前/读后identity稳定；本地unlink前的dev/inode/size/mtime/nlink与验证时完全一致，无额外文件或软链接越界。
2. NAS路由现场findmnt证明174上的/root/share/mnt164是<ARCHIVE_SERVICE_ACCOUNT>@<TRUE164_PRIVATE_IP>:/home/shared的fuse.sshfs；对应164原生/home/shared/<OWNER>。新增NAS仅一个reader16MiB/s，109源SHA64MiB/s；没有停止或调整ImageLab任务。
3. Llama完整6文件从真实164经174恢复到109独立控制目录，完整SHA再次核验；离线JSON解析config/tokenizer，safetensors头部tensor/data_offsets/文件长度通过。OLMoE9个小文件（含receipt）恢复并校验，index引用3个分片与已完整SHA通过的164分片清单闭合。15个测试文件验证后已全部清理，仅清除此worker自己创建的恢复目录，不吃回回收空间；未做GPU推理。
4. 临删查当前cmdline、可读fd/maps、活跃脚本、GPU、system/user running units/timers、crontab及相关queue/config。未发现外部正在使用/待执行这两模型的具体依赖。读取到的OLMoEmanifest引用属于历史文件，无RUNNING/QUEUED/PENDING状态。早期探针唯一fd命中本次worker自己的源SHA读者，已单列解释；正式临删检查在源SHA结束后执行并排除自身PID。
权限边界：临删maps可读352/473，fd目录可读38/473；错误计数{'maps:PermissionError': 121, 'fd:PermissionError': 435}。其他用户fd/maps未全部可读，不能声称全机绝对闲置；依据本轮用户授权，结合全部可读cmdline、GPU、服务及队列无关联后完成清理，没有把一般权限盲区转换成再次确认。

删除后
164同18文件再次逐路径/身份核对，receipt及必要小文件重读SHA通过；完整权重SHA使用删除前当前证据，删除后未重复重读大权重。109原两处literal目录均不存在。
独立复核Qwen3-30B-A3B全部26文件仍在，dev/inode/size/mtime/nlink与审计快照完全相同。ImageLab当前GPU进程仍在；本次删除白名单不含任何Qwen/ImageLab/stagea/AWMA文件。
当前账号的已删除目标fd及maps复查为空；worker收据与独立复核均已留存。没有全局drop caches。

空间
worker前可用：56,699,592,704 bytes。
清理及自建恢复测试文件清除后可用：73,022,570,496 bytes。
当轮实际available增量：16,322,977,792 bytes；文件数据块回收计数为16,323,448,832 bytes。两者差额受控制日志、目录元数据和并发任务写入影响；不可将df差额逐字节全归因于模型文件。

再次使用
109原模型路径已移除。以后重跑引用本地绝对路径的历史脚本，须先从164原生/home/shared/<OWNER>/c16_ai_workload/assets/models下相应revision，经109的<BRIDGE_SSH_ALIAS>读取174真实164挂载，复制回原layout并核SHA。Llama本地布局为Llama-3.2-1B@revision，归档布局为llama-3.2-1b/revision；请按PLAN.json/VERIFIED_AND_DELETED_FILES.csv的精确映射恢复。恢复时需要约16.32GB本地空间；32MiB/s纯传输约8.1分钟，若保持16MiB/s约16.2分钟，另计校验开销。

可审查证据
PLAN.json：明确用户授权、18文件身份白名单、恢复路径和限速。
VERIFIED_AND_DELETED_FILES.csv：逐文件旧身份、历史期望SHA、源当前SHA、164当前SHA、unlink时间及结果。
remote_evidence/SOURCE_FULL_SHA.json、NAS_HASH_RECORDS.json：两端完整当前SHA及读前后身份。
remote_evidence/RESTORE_TEST_VALIDATION.json、RESTORED_FILES.json、RESTORE_TEST_CLEANUP.json：恢复抽检、回拷文件与清理。
remote_evidence/PREDELETE_DEPENDENCIES.json、PREDELETE_GATES_PASS.json：临删依赖与所有门槛。
remote_evidence/DELETED_FILES_RECEIPT.json、FINAL_RECEIPT.json、EVENTS.jsonl：逐文件删除、最终结果和durable日志。
remote_evidence/NAS_POSTCHECK_RECORDS.json、SPACE_BEFORE.json、SPACE_AFTER.json：164仍在与空间变化。
INDEPENDENT_POSTCHECK.json：本地两目录消失、Qwen完整保留及本账号无相关open-deleted fd/maps。
SHA256SUMS_local.txt：本地交付文件摘要；完整109控制目录仍保留证据，不含已清除的恢复权重。
