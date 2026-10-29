# W/V模式资格及C1接口：给D的独立核查交接

仅追加小汇总/源码只读核查，原B交付不变。Source78 Core78f4b59、Framework9dd1ee57、ELF78d4e96b；五元完整SHA与引用见JSON。

|模式|FT|Vclean/Vdirty|T|M|实际含义|
|---|---:|---|---:|---:|---|
|S|1|0/0|0|0|finite WBUF|
|W_ONLY|2|0/0|0|0|unified WB，尚缺正式模式资格|
|WV_ZERO_RO|2|1/1|0|0|合法W/V，RO runtime关闭|
|F_MINUS_T|2|1/1|0|1|M开启需证书，不等于WV|
|F|2|1/1|1|1|完整机制，需证书|

实际参数名由五模式mode_contract.py:23–26给出，生产注册gpu-sim.cc:283–288/345–346、ro_requested gpu-cache.h:903交叉核对。配置可解析不是native资格。

## exact3没有证明协议失败

所读f79b10ea…/RESULT.json的泛化状态名含FAILURE_OR_HOLD，实际steps只有CPU_HARD_FUTURE_GROWTH_HOLD：RAM余量−10,895,305,938B，disk PASS。在intent、编译、fixture之前退出；0实际构造，未见constructor marker，0model。此单据不能改写为W_ONLY不正确，也不能当CPU PASS。这里只声明这份实际单据，未全盘搜索或否定其他后续试验。

## Host / sole-entry缺什么

五模式Host是DRAFT，不在frontend批准的tools whitelist。缺Main mode CPU资格、new HostQ及其parser/contract精确绑定、new nativeQ四字段、当前accepted精确S anchor复用审查。现有static proof保持6低层函数及原数值验算正文/后缀，但没有执行新的wrapper/native正负控制。具体未执行控制完整保留JSON：五模式flag/history、异常Source/geometry/282/RO证书拒绝、HOLD拒绝、旧HostQ拒绝、同S背景闭合、consume-before-fork/PID/map/peer-preservation等。不能伪造历史F为W，也不能让旧S NI覆盖WV/F。

## C1两个选择器必须独立审

- `ep-l2-tvd-directory.h:148–173` preview_install：空行优先；dirty安装优先CLEAN，clean安装按全体reclaimable年龄。**并非所有当前选择器一律CLEAN优先。**
- `ep-l2-tvd-cache.inc:39–57` tvd_reclaim_one：先CLEAN后WB_COMPLETE，各类按age且payload bank匹配；保持pin0断言。
- `.h:42–45` mandatory/reclaimable定义、`:177–210` revision/commit/incarnation保护、`:309–322` dirty-promotion行重用、`:252–263` 真正response_commit置服务位，是候选必须守住的接口。

service_seen设计仍为HYPOTHESIS。只在真实bank服务与成功enqueue后置位；query/lookup/begin_read/重试/取消均不置。每次incarnation/rebind清零，dirty-promotion不可漏。pending/inflight、mandatory WAD、reader/pin、generation/owner、bank颜色、dirty-forward与RO防护不可放松。两个选择器应先写清同一候选语义与preview/commit契约，再考虑实现。

逻辑1bit×128×64=1,024B只是未padding状态量；物理payload/directory均不增加。额外更新/读取端口、比较器、关键路径与硬件PPA未知，host O(128)循环不能当免费硬件实现证明。收益也UNKNOWN：服务数量没有证明optional容量饱和，Scan阻塞变化不能解释独占性能损失。

给D的上述事实和需要独立验证的问题已发消息，不要求D采信B的性能推论。零模型、编译、生产CPU测试、Trace/raw扫描及Source/Git/controller/registry写入。
