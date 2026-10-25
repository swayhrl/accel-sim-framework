# Parboil histo DM 失败诊断

点：`E2-AEV100-2c506bf13c81ff5d-DM`；UUID `221010cd-8185-4a85-a380-9eaecff8de8b`。

直接触发已经确认：首 kernel `_Z20histo_prescan_kernelPjiS_` 进入统计时，冻结 Core `shader.cc:6038` 的 `assert(total.oo_pib_occupancy == 0)` 失败并 SIGABRT。前一行 inflight==0 断言已通过。它不是 deadlock_check，也不是外层资源终止；缺少 NATURAL telemetry 是 assert 之后的下游结果。

full raw 113313 bytes 已全量解压校验，SHA256=`19a33649857f4a23cde1dacdae3f2677bce1e17041bfe3ae06d02cf195878eef`，与 NATIVE_EXIT/classification 对齐。实际只处理第1 kernel；完整输入有 80 个 kernel，不能把已打印的首 kernel 8310 cycles 当作全输入结果。首 kernel 已打印6197568条线程指令，恰等原始 fullbody 审计与本次新读首 kernel 统计；service_retired=8192，也恰等8192条cacheable global load。

首 kernel 仅10232334 bytes，本次完整只读并重新散列，SHA=`a2d46bf42d4bbca872daf4e74952cd933c4833277f8f9bd0699756e64c223c95`，与先前 qualification/kernel_1.json 完全一致。grid64、每CTA512线程，共1024warp；264832条warp记录。共有64条`RED.E.MIN.STRONG.GPU`和64条`RED.E.MAX.STRONG.GPU`，均目标寄存器数0、mask=`00000001`，每CTA各一条（总计两条）。没有global ATOMG。直接trace样本是 PC0x0c60 和0x0cf0。这是完整首 kernel 统计；此次没有重读其余79个 kernel body。

这些 RED 与 BFS 的 ATOMG、hybridsort 的 RED 共用同一冻结解码和完成缺口。Framework `trace_driven.cc:274,332,422–431` 清零 out[]，按 reg_dsts_num 写目标，RED 强制为global、LOAD_OP、atomic=true、CACHE_GLOBAL；不是按 opcode map 的初始 STORE 类别直接走 store 出口。Core `shader.cc:3933–3947,2621–2642` 先为atomic建立M4 OO-PIB和external dependency；`4543–4590` 的writeback_complete没有zero-dest atomic完成分支；`4652–4655` 已递减architecture atomic count，但`4687–4688` 仅在completed=true时调用M4 completion。dispatch LOAD_OP的退场分支也没有M4 completion，dtc_l1_retire对OO直接返回。

因此 architectural instructions 可以全部完成，而M4侧条目仍不ready/不能退休。BFS目录的CPU fixture原样抽取冻结函数体、链接真实OO header，已分别证实zero-dest RED/ATOMG都返回false；returning atomic/fence控制返回true，128条未关闭externaldep堵住129准入。这里每CTA只有两条RED，远低于每SM128槽，因而与“没有先堵住，最终统计发现残留”一致。**历史dump没有输出残留owner UID/type/count，不能声称恰有128个历史残留，或已经观察到每SM恰2个残留。** 源码缺陷确认；将该点归因于同一缺口为高置信链条，仍保留其他生命周期贡献未被现场逐项排除的边界。

仅7条progress，远低于1048576上限。捕获资源采样中RAM/disk均通过，原策略为CONTINUE。DM的hash关闭，global RED又绕过L1；当前失败不能归为XOR/AE特有原因，不形成性能正负证据。

下一步最小验证是CPU层RED.MIN/RED.MAX分片响应汇合、一次性完成、防重复关闭与2条/128条drain控制，再决定是否安排独立不可变诊断构建。此次没有重跑、修Core、改classification/INTENT/账本；原资产SOURCE_KEEP，accepted cycles仍为null。

证据SHA、全首kernel计数、资源与progress细项、Core/Framework commit和逐文件SHA见`HISTO_DM_DIAGNOSIS.json`、`RAW_PROGRESS_RESOURCE_SOURCE_FACTS.json`、`FIRST_KERNEL_FULL_READ_FACTS.json`。共享CPU fixture仅被引用，其BFS目录原文件未改动。
