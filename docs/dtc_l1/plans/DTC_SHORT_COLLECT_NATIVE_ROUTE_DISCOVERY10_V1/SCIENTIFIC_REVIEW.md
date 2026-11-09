# 科学审查｜Short-Collect-First CPU-only候选收尾

## 决定
`ACCEPT_CPU_QUALIFIED_ONLY / RETAIN_FROZEN_CANDIDATE / NEW_NATIVE_SCIENCE_ROUTE_REQUIRED`。固定合同`32cbe43f6975ff6a11cfd1210f88026771656b48`，正式报告`8dc2a33e3037670e157f5ab4237358ec475feabb`。Gate A PASS，Gate B CPU 17/17和独立审查PASS，Gate C1因没有Goal专属native request/UUID/owner、实run guard、新strict、true164归档和typed restore而HOLD。0 request、0科学模型、0预算；20格旧额度只是未使用的旧合同上限，不是可延长余额。本次不是性能负例，更不是已测性能收益。

唯一候选Core：`9a0de9b9f97144f481b3e3637e329ebab01acb74`（从普通生产Core `9eedb3131937748f0492fa83aad37d3691118d70` 派生）；Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`；冻结科学binary SHA256 `a9ec6f231d9491690eb913d1cb69d7d2dae0f769f8854efc4df0512b5f1fd00c`；libcudart SHA256 `43b3dc2f3e04d577e6c682f632691aca637b2670aee52c18b809f4d4c4e64860`。独立CPU审查另有不同的lib构建SHA，不可替代科学lib。私有LD_LIBRARY_PATH绑定已固定，plain ldd的not found不代表已配好实际runtime。

候选仅作用于正常PAPER_OO finite-service已ready cacheable load。OFF保留oldest eligible ready；ON当更老已ready项尚需>4 sectors且ready年龄<8 cycles并未开始collect、没有non-load边界时，至多向后检查3项，挑合法就绪且<=4 sectors的年轻项。collect quota4、retire port、operand WB backpressure、parent/sector/generation/Ref/credit、fence/store/atomic等不变。CPU独立见证：OFF UID201(6 sectors)，ON UID202(1 sector)；OFF decision/effective=0/0，ON=4/1，其中effective仅在成功WB/retire后记录。**这些只证明局部源语义，不能证明GESUMMV自然trace会出现该竞争。**

源码措辞限定：`shader.cc::dtc_l1_oo_select_ready`寻找首个eligible ready项可以遍历PIB，`eligible`还检查此前同warp PROXY_FENCE。所谓“四位置窗口”仅是从首个符合条件的ready项出发的附加lookahead，不能写成整个选择器最多检索四个PIB entry，也不能声称已具RTL面积/时序证明。此限定无需改动已冻结Core，但成本声明应修正为`PPA_UNKNOWN`并精确说明额外比较。

静态4格已经完成input SHA/工作量/271选项/同build配置预审：GESUMMV OFF/ON与vectorAdd OFF/ON。GESUMMV旧OFF的3,145,856 retired loads、38,797,824 collected sectors和132,901 WB waits不证明真实发生可改变的同tick选择。ON自然有效`eligible_choice_different`仍UNKNOWN；如果为0则固定GESUMMV见证被证伪，不能事后换成其他目标来释放第二批16格。vectorAdd为对照，不预设一定0结果。

E1=CORE32三模式受控Oracle固定trace机会，GM M/L2/L1≈1.676759/1.280649/1.939912，L2 11整数精确零+2回退，不是可实现硬件上界。E2=历史真实结构MVT物理扩容改善、BICG反向回退，lower-create/credit full原打印0，不能断言扩容量可解决。E3=本候选有限调度假说，未有自然性能/事件数据。后续如出现E4自然结果，务必以同新build actual OFF为分母，真实零/负及工程失败均保留。

下一科学应优先修复**专属native准入链**，再经独立R0准入完成可执行的C1首4、条件C2 16。无需重新选候选、重做17个CPU测试、再次重跑128 Oracle或启动新的109 capture。严格保留SM70/V100-derived64SM固定trace边界；native数值/capture时ELF/数据绑定、coherence、PPA及CH等成本公平性仍未证实。

109-DTC另有已交付新保全Goal `2e8a7d4fc155f6a8ab041d3b31893abaacac12f2`；最新转来的109文本仍是旧接手`2e009bb7a360054dcebe47c680d64aa16d4a8b88`，不能推断保全已完成，也不要重发。