# FWT / SGEMM为何没有Tag-detach

当前直接原因是RO准入为零，无法归因为Tag一直充足。两端T/M在全部64slice都启用，但认证候选、RO准入、RO事务、detach均为0；普通全局读则分别有FWT 5,242,880和SGEMM 2,452,480次。

FWT与SGEMM必须分开解释：

- FWT采用whole_commandlist、128B行级证书。已有完整离线覆盖记录显示131,072条读过的行、41,943,040次读lane引用全部属于SAME_LINE_STORE：同一行在整个epoch内也发生写入，因此没有可认证的RO行。这是当前冻结trace模型与整段epoch内的零资格机会，不是Tag容量观测，也不能推广到其他划分或真实硬件。
- SGEMM使用NO_READONLY_CERTIFICATION安全空回退。已有完整语法/非atomic输入证明，但没有提供可采用的正向行级RO证书。实际RO机会仍UNKNOWN，不能说它没有只读数据。

上一次聊天把二者都概括为空证书下机会未知，未明确FWT已有SAME_LINE_STORE排除证据，本报告予以澄清。原始回执和已接收结果不改写。

顺序是：启用机制→只读行认证→RO_PENDING事务→未返回时存在合格Tag替换→detach→正确返回/退尽。当前两端都在认证/准入阶段没有候选，尚未进入可以由Tag压力决定detach的阶段。main61还采用waiter-aware保护：reuse_seen或所需sector已经ready时不可detach；即使以后有正向RO准入，也不能只凭detach=0就断定Tag充足。

两端导出的TAG_SET_PENDING等待计数也是0，但这不是Tag逐set占用峰值、替换总数或计数覆盖完整性的证明，不能据此宣称Tag始终有余量。

若要补应用级证据，应先由C审核适合输入的正向RO行证书，再查pending Tag替换与资格；SGEMM仅是可审查候选。改变epoch、证书或重跑均须相应资格与授权，不直接缩Tag或放宽只读规则。本次没有raw/trace/SQLite普查，没有新增模拟、native或构建，累计50与主结果保持不变。
