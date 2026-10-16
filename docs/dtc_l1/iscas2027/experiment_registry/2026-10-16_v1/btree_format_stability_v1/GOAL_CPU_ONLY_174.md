# Goal：DTC BTREE FORMAT STABILITY CPU 174 V1

**仅CPU、有界、独立worktree；此Goal不启动仿真或GPU。** 用户已批准科学决定中的Btree先行与2D全kernel可行性门槛；阶段边界以同目录SCIENTIFIC_DECISION.md为准。

执行前按顺序：
1. 在**原174的DTC账户/容器**操作（不是174-new）。确认原A的Goal、simulator、唯一launch authority仍在，不对其进程/锁/输入/manifest做任何改变。
2. fetch swayhrl/accel-sim-framework 的文档分支 hrl/iscas2027-dtc-experiment-registry-v1；回读最新HEAD，完整阅读此Goal与同目录科学决定；核真实Git SHA/文件内容。交接锚点A e52d3eac、B d46cce26、原台账V10 41d20058仅作为已审证据，**不将活动A重置到锚点**。
3. 在原174另建隔离worktree和新分支 hrl/iscas2027-dtc-btree-format-stability-174-v1（若同名存在则先核身份并fail-closed，不覆盖）。引用原B LEGACY_FORMAT_SOURCE_BINDING_V1报告与104476风险索引，不能将B旧分支直接当活动任务恢复。

执行内容：
A. CPU上对Btree原固定1-member/PC1c40的6000条单P/full32模式做精确合同检查；根据已核历史E-list serializer的ascending E lanes语义构造至多**一个**合法条件性E-list派生候选。不能用旧运行收益/地址合理性挑lane。输出每条old/new地址及sector/line变化，核6000/5792/208；原trace只读。
B. 用独立实现的地址解码与**现行冻结生产parser**读取候选的完整Btree member、ordered kernel/list/指令范围，对所有memory records和active-lane地址流做可验证SHA对照。新输入不允许改指令、active mask、同步、opcode/width或kernel范围；有多余变化即fail-closed。所有回执标注原capture producer未绑定和native输出不等价尚未证明。
C. 独立CPU评估2DConvolution是否能凭有来源支持的producer build 或全kernel source/SASS/dynamic-E模型产生科学自洽解释；只形成可行性与最小证据缺口，不选逐行锚点，不生成2D正式输入/仿真。
D. 输出G0-G3逐门PASS/FAIL、详细证据摘要、immutable input SHA、来源与消费链、严格科学适用边界、最多6臂的新输入预登记提案。**本CPU窗口不运行六臂**；有PASS时只交审ChatGPT，再由原A唯一launcher按决定的条件与资源安排。在未取得A独立登记与调度许可前不能向原A混入任何job。
E. 把报告、源代码与必要小校验包提交到本新分支的docs/dtc_l1/review_packs/BTREE_E_LIST_STABILITY_CPU_V1/；对用户报告分支HEAD、成果和STOP/PASS结论，push并fetch-back验证。大型成员、原始日志和模拟器binary只存既有174/164目录，不进Git。

普通解析/索引/manifest工程问题允许确定性恢复并继续；触及原输入身份、解释、opcode/ISA、冻结parser/Core、实验定义/资源合同或科学claim，或预期的6000/5792变化不闭合，STOP并记录原始失败。严格禁止reset、重启A/B/C/D、运行新GPU、另起第二仿真调度器、扩展整套12程序重采或试性能选解释。