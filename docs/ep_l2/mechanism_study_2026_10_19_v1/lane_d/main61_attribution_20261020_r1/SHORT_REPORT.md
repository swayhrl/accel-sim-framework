# Conv main61：实验决策短报 r1

仅使用E2正式接受配对 `V2_MAIN_convolutionSeparable_S_F_MAIN61`。E2最新远端HEAD `498426c672739bb0ff681287374e49df74dc0361`。本版先交机制证据，候选独立画像合并及图表随后发布。

**实测程序时间**：S 292,932，F 291,469 cycles；减少1,463 cycles（相对S减少0.4994%；S/F加速0.50194%）。两端714,547,200条指令、完整2kernel输入，正常结束且64slice闭合。main61 binary `61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5`；Core `d010911e3174a3764791183cd108fe4664ba8731`；Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`；输入 `620f80f945d8ddbcef639e7e374fd2cb7122f8b07f239c82ccd32a2c4d90e79f`。准确config、run-key、两项独立资格、F重新验证回执及哈希见随附JSON。没有使用旧main773或F原始FAILED回执。

| 范围/实测量 | S | F |
|---|---:|---:|
| 逻辑复制读/写（各） | 546,865 | 0 |
| 实际物理bank授权 | 9,217,033 | 8,118,075 |
| 下层读次数 / bytes | 2,359,526 / 75,504,832 | 2,359,460 / 75,502,720 |
| 下层WB bytes | 69,787,264 | 69,826,496 |
| V真实读取响应 / dirty转发 | OFF，无记录 | 36 / 0 |
| V promotion / clean安装 / dirty安装 | OFF，无记录 | 1,152 / 499,725 / 546,813 |
| V clean / dirty在途及完成态保留slot-cycles | OFF，无记录 | 495,404,215 / 1,778,784,962 |
| V目录查询 / 查询等待计数 | OFF，无记录 | 1,181,110 / 1,181,110 |
| RO实际准入 / 新事务 / merge | OFF，无记录 | 1,251,551 / 371,495 / 880,056 |
| RO避免line-MSHR分配 / 成功detach | OFF，无记录 | 371,495 / 0 |
| RO lower sectors / 同时重复lower sectors | OFF，无记录 | 1,179,774 / 0 |
| RO查询 / 查询等待 / 查询端口拒绝 | OFF，无记录 | 1,251,627 / 1,251,627 / 0 |

等待为各请求/各slice的计数，**不是互斥GPU停顿分解**：COPY_PIPELINE请求等待和546,865→0；WB_DATA_SPACE848,913→0；DATA_SERVICE433,239→357,749；LINE_MSHR_FULL40,088→150,118；MISS_QUEUE_FULL180,063→590,686；SAME_ADDRESS_WB638,854→538,426；新增BANK_COMPATIBLE_LANDING81,928及WAD_FULL5,987。V内部WB等待538,426与SAME_ADDRESS_WB是同一来源，不能重复计算；RO/V查询等待与对应原因也不能再相加。所有字段逐项保留，不把等待和除以slice数或程序cycles当停顿比例。

**源码推导**（冻结Core d010）：W所有复制请求走真实P1 bank记账，当前无copy_free/data_free豁免；两次复制服务消失能降低本地服务需求。V保留计数是payload槽位×时间积分，不是命中数或面积。RO bypass避免line分配数不等于避免MSHR阻塞次数；detach=1是配置，detached=0才是成功事件。RO重复lower计数仅覆盖同时重复sector，不能解释为整个程序无重复读取。V响应36不包含promotion后的所有后续resident命中。

**受支持结论**：复制服务确实消失，bank总服务减少1,098,958（11.9231%）；净下层读仅减少66次/2,112B，WB反增39,232B，不能声称明显减少DRAM流量；V在此输入的直接读复用很少；RO准入/merge/bypass真实发生，但T detach机会未出现。新增查询及更高的MissQ/MSHR等待与收益较小相容。

**因果假设，尚未证明**：查询及队列压力可能抵消部分W收益；只有同binary的remove-one/控制配对才能量化各模块边际cycles。当前S/F总对比不能把1,463 cycles分摊给W/V/RO，亦不能用服务次数差推出GPU关键路径。

决策建议：继续既有FWT正式S/F，等待E接受再做增量对照；优先审查传统S下具有独立读复用/RO/MSHR压力且完整合法的候选，保留低压力独立验证样本。七输入仍仅1/7配对；Btree HOLD；七输入几何均值UNKNOWN。累计12/40来自E现场，本窗口启动0次应用。EN-v20未修改。
