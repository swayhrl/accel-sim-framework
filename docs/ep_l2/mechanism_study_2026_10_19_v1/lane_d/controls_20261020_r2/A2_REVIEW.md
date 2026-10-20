# A2：SAD首WB前与DWT K5/K8的有限源码归因

冻结Core为`d010911e3174a3764791183cd108fe4664ba8731`，main仍为`61aad385…f2dd5`。下列行号对应该Core，完整SHA与编号摘录见`RECEIPT.json`及`NUMBERED_SOURCE_EXCERPTS.txt`。仅静态读源码和既有已接受端点的D阶段数据：不新增配置/Goal、不编译、不运行、不改main/E2。

## SAD：确有首WB前的timed差异，但989周期尚未归因

既有K1：S/F为84641/83652周期（F快989）；copy读写、lower读/WB发出、F直接V读、RO准入均0。F却有27127次V查询；物理data grants仅121916→121904。该prefix的clean/extra retention槽周期均0，因此后续全应用的396次clean安装不能直接解释该prefix。

| 配置/真实路径 | 首WB前可发生的行为与调用链 | 结论边界 |
| --- | --- | --- |
| S与W_ONLY的payload组织 | `l2cache.cc:1550 → ft_access`；`ep-l2-ft-cache.inc:334–351,396–416,495–502`：S冷miss以所选Tag index为landing；W冷miss从`preview_free(RESIDENT,index%4)`选槽。live clean victim在无V保留时复用自身handle/id。host预填同样按S/W分支建立身份（`:61–101`）。 | 可以改变payload id/generation及将来的槽位可用性；**相同index%4仍对应相同物理bank**，不能仅凭ID不同宣称P1时序已经不同。K1尚无landing拒绝证据，S/W_ONLY首WB前是否实际分歧仍缺观测。 |
| F的付费V查询 | `l2cache.cc:1312–1327 → ep-l2-tvd-cache.inc:68–95`：Tag HIT/SECTOR_MISS/HIT_RESERVED绕过；其余miss首次记录lookup并返回TVD_WAIT，后续物理周期才查询。目录为空/查不到也要付该等待；未完成前普通frontend不执行，`ft_access:326–327`也拒绝未查过的MISS。 | 零V直接读不等于零V延迟。它会改变frontend队头、Tag/MSHR占用与response/fill/下游到达顺序；局部加延迟后全程序反而更快只能作为排队重排假设，不能用27127减算989。 |
| **F从初始化就切换bank重试身份规则** | `gpu-cache.h:2882,2888`以`dirty V || RO requested`启用extended identity；`request():2636–2658,2673–2683 → ep-l2-tvd-bank-identity.h:10–15`。S/W_ONLY仅匹配`role/id/write`；F还匹配`client/token(UID)/generation`，并在`:2519`释放handle时取消对应pending/granted项。 | **无需WB、V直接读或RO准入即可改变仲裁。** 例如同一payload上的FRONTEND与RESPONSE均为read时，弱匹配可能消费同一个已有重试grant，强匹配要求实际owner重试。是否在SAD发生、是否改善关键请求尚无证据；不是已证明数据错误。 |
| 共享P1与响应时序 | `ft_response_ready:148–158`、`gpu-cache.h:2927–2941`及`ft_access:481–515`分别请求RESPONSE、FILL、FRONTEND服务；`request():2591–2610`保留未消费的最老grant，`:2665–2699`决定本周期授权/排队。 | 不同队头/重试身份可在无copy时改变谁先消费同bank服务，即使总服务数近乎相同。需要首次仲裁分歧，不能凭总grants减12确定989周期来源。 |

V clean保留的源码分支确实不要求先有dirty WB（`ft_access:379–394,527–531`），但当前K1 retention槽周期为0，不能把它当已触发的prefix收益。RO零查询/零准入也不能把“启用RO”视为整个程序的无效开关：**即使没有实际RO新事务，RO requested仍启用上述extended identity。** 所以F_MINUS_V保留RO时也保留此规则，不能把它与W_ONLY的差异单独叫V lookup延迟。

S与W_ONLY共同走原有弱匹配；F会同时改变查询、身份、保留等。仅切换S→W_ONLY不会自动隔离所有F的时序变化。现有Conv控制不是SAD首kernel观测，不据其结果替代SAD；本次不请求新实验。

所有真实时钟均为`ft_physical_cycle():3–5 = gpu_sim_cycle + gpu_tot_sim_cycle`。空目录扫描、C++函数调用、断言、`new`或host预填函数执行时间本身没有向GPU加周期；只有上述显式WAIT、服务授权、队列/状态依赖可能改变模拟周期。没有用host wall time解释989。

## DWT K5/K8：landing容量/生命周期与P1服务分开

既有相邻累计快照：K5/K8分别慢768/599周期；F V查询68107/65536，新增RO查询和RO准入均0；landing请求/等待和分别718/718、339/339。两阶段额外保留槽周期分别233205866/212266289，clean保留槽周期3210820/9643828。它们均不是关键路径GPU停顿时长。

**提交链：** `preview_access → ms_frontend_blockers → admission → ft_access → payload.request → data_cache::access/RO accept → reply/lower completion`。

1. `ms_frontend_blockers():242–248`只在新MISS、没有既有pending transaction、FT2且dirty或无live victim时检查`preview_free(RESIDENT,index%4)`。`gpu-cache.h:2484–2493`按**FREE、目标bank相符、角色容量许可**找槽，没有请求P1端口。全局有空槽不代表目标bank有空槽。
2. 真正提交`ft_access:396–400`发现无landing时，还会在**同一物理周期**尝试`tvd_reclaim_one(index%4,cycle)`，成功后重新preview；仍无槽才pool_full/RESERVATION_FAIL。`ep-l2-tvd-cache.inc:39–55`先找同bank最老CLEAN，再找WB_COMPLETE；必须reclaimable、payload有效。目录`reclaimable():42–45`要求readers=0；协议同时要求payload pins=0、release时无pending sector（`gpu-cache.h:2516–2521`）。WB_STAGED/WB_INFLIGHT不合格，其他bank的可回收项也救不了该landing。
3. `lower_accept → WB_INFLIGHT`不释放回收资格；实际`set_done → WB_COMPLETE`后才可能回收（目录`:350–363`）。`retention_slot_cycles`还统计WB_INFLIGHT，clean单列（`:372–381`），故大量retention不能直接解释成“全是可丢弃的可选V容量”。同bank回收本身未调用payload服务，不额外占一个P1 data grant。
4. live clean victim无新landing时，optional clean保留可放弃，退回复用自身；不是所有“保留失败”都阻塞frontend（`ft_access:379–416,495–502`）。dirty/WAD保留生命周期和clean可选保留必须区分。
5. **计数归因的重要限制：** landing位在回收前计算（`l2cache.cc:1337–1340`）。若实际同周期回收成功并admit，observer会清除blocked，不计该次等待（`:1558–1562 → ep-l2-mechanism-observer.h:53`）。但若回收成功后又因P1/其他原因拒绝，旧的pre-reclaim landing位仍可随失败一起上报；因此现有718/339不能证明每次最终都因无槽拒绝。P1真正拒绝则来自`payload.request()`的已有pending/granted或本周期bank服务额已用（`gpu-cache.h:2636–2699`），与容量扫描是不同层次。

## 可检验假设与缺失证据（本次不新增采集）

- **H1：SAD由V队头节奏或extended retry identity引起首次分歧。** 需要同UID/地址在三配置的首次admission/grant/response分歧，特别是相同role/id/write、不同client/UID/generation是否相遇。现有kernel总量和快照没有这些记录，无法给989定量归因；也没有SAD W_ONLY的已接受端点。
- **H2：DWT后段由付费V查询及其到达顺序变化拖慢。** K8零直接V读仍有65536次查目录，与源码一致。需要关键load响应/warp依赖与查询区间的对应；查询总量不能证明关键依赖，也不能将768/599全部算作查询罚时。
- **H3：同bank生命周期压力，而非P1吞吐不足。** 需要已受阻头对应bank、free槽数、CLEAN/WB_COMPLETE readers/pins、pending/inflight与reclaim实际成败，才能区别“真无可回收槽”与“回收后在P1处拒绝”。现有总retention/landing计数不提供该交叉状态。
- **H4：K1形成的Tag/payload/目录状态影响K5/K8。** 后段无新RO查询不能排除早期RO的间接状态效应。等待已批准W_ONLY/F_MINUS_R等完整epoch结果时，只比较既有逐kernel快照与邻接背景；不得由等待和倒推模块关键路径，也不重新发配置/矩阵或启动请求。

结论止于源码路径与可证伪假设。未证明SAD的989周期来源，未证明DWT的landing为关键瓶颈；没有变更生产语义或科学验收状态。
