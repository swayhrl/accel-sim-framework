# C16 G/P2/P3 外发六文件：未应用的最小可回滚提案

按协调 `3a7ea422d3f4301688bd3cb7bcf4431b97f08e90`，本轮只准备 **G外发六文件供给退役**。A原模型六文件继续ACTIVE_KEEP，监督器不变。用户本轮没有批准C16退役、恢复写入、模型传输或unlink；没有实际G负责人签收。状态 `C16_OUTBOUND_RETIRE_NOT_APPROVED`。

本提案取代先前把A/G同时退役的建议范围；旧 `92f6dc160` 请求及两selector保持历史。仅外发selector `2c258b589bff3eb0e7154e775bc2973c932ec94144075edb5060b0a2d5205581` 进入本提案，原模型selector `0ce1ab80f4be37b5be29d8d82fcc25a6fc94e1d9efea83df0f99a65e966ef235` 不授权、不修改。没有重新stat或hash12模型文件。

## 具体补丁与控制验证

`C16_G_OUTBOUND_FIRST_UNAPPLIED.patch` 绑定G源码 `73850d93a4c97537976d799759b9440112eadea9`：

- 修改 `util/vm_tlb/c16/lane_g/runtime_package_transfer.py`，前像SHA256 `728b1bbbd266f08b6bb6eb3b89e2ff2d8de8e056ace0b10827349604c5726d91`。
- 新增 `c16_outbound_supply_guard.py`。`materialize` 读取小metadata并验证原包身份后，在遍历payload/创建目标前拒绝退休的历史P2/P3；直接 `payload_bytes` 入口也在任何payload/Git读取之前判定。远端 `verify()` 函数字节不变。
- 护栏识别精确外发六路径及包含它们的父目录传输；旧producer和P2/P3 manifest绑定用于拦截历史包重新物化。其他模型、A本地模型读取、新版本非旧路径供给保留原语义。
- 默认 `TRUSTED_POLICY_SHA256=None`，提案不会激活。真正G发布需把常量绑定到实际批准且签收的policy全文摘要；部署该policy文件与新代码必须另有准确执行授权。policy缺失、摘要错、scope扩大、缺签收引用或本地六文件被退役均拒绝受限请求。policy引用的格式验证不能认证owner签字，真实授权与回执必须独立核对。
- `C16_G_OUTBOUND_POLICY_UNAPPROVED.json` 是PENDING_APPROVAL模板，五个批准/签收/清退/接管/回滚引用均为空，不能用于激活。

实际执行16项小fixture单测与4项临时副本集成检查：两个历史包和全部六路径拒绝、父目录不能绕过、未签收/错selector/错digest失败关闭、其他模型/新版本保持可用、未批准不激活、真实补丁在payload调用及目标创建前退出、远端verify不变、控制撤销回滚。`git apply --check` 与应用均只发生在新建临时fixture，未进入生产G工作树；没有读取任何真实模型内容。这些是控制测试，不是native科学或模型恢复结果。

## 必须由实际G owner闭合的生产调用者

当前helper是transport-agnostic，本身不启动rsync。改它不能拦住外部旧版launcher或直接shell rsync。**真实上传launcher/定时队列路径和版本尚未签收，仍HOLD。** G须提交准确任务列表与消费者承诺：

1. 明确历史P2/P3是否终止外发原六路径供给；列明未开始、已预约和正在读取的任务。未开始任务取消或改为新的164/109版本；在途消费者逐项清退。不得由S擅停。
2. 在实际launcher启动任何scp/rsync之前调用 `check_transfer_sources`，将精确、完整、规范的展开source列表传入；拒绝通过旧版本工具、symlink或未展开相对路径绕过。包含退休六文件的混合批次整体拒绝，其余模型另开原合法任务。绑定launcher代码、队列定义、激活版本与负向运行回执。
3. 未来164权威RAW/AWQ固定revision不变；109 owner提交其真实本地副本路径、当前六文件manifest和使用责任。未经证实的109 locator不得填充。P2/P3原收据和包metadata保留，新增操作状态不能重写历史科学结论。
4. 激活前审阅实际用户/owner批准与G签收回执；必要的T六内容校验、当前/未来消费者、未来供给与回滚证据均绑定版本。S不代签、不把不存在打开FD当作没有未来计划。

## 回滚与后续释放

批准后实际G才能按命名版本部署上述控制。源仍保留时，回滚为撤销受信policy绑定/回到前像版本；核对旧原件身份和消费任务后再允许旧供给。不得以回滚名义自动下载、重传或从别的路径静默取用。保留操作日志及新旧摘要，A监督器完全不参与本外发优先策略。

若以后另获源释放批准：先完成外发六文件原布局的真实native独立恢复和内容/数值metadata验证，当前源SHA、所有权、真实及未来读取者、资源和逐文件持久INTENT/DONE都通过后，才由源owner按精确selector执行；本次没有任何C16 unlink权限。源已释放后的回滚须先经另外获准的恢复验收，不能只重新打开旧供给开关。

仅外发集合历史可见分配上界20,802,138,112B（约19.3735GiB）；当前授权回收0B、净回收承诺0B。不得加上另六原模型的空间。尚需一次明确外发退役决定及实际G签收；不在本轮重复要求用户回答旧的A/G捆绑请求。
