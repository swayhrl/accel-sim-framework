# 资产优先、公共入口和161项真实进展 — V14

本报告取代V13对“仍需全125正文Native恢复”的默认要求。用户已明确取消全库正文回读，保留按需读取/恢复能力；同时明确要求完成全部161项适配并继续当前后处理。Goal仍未完成。源KEEP、释放0，科学历史、预算及资格不变。这里的CPU候选不等于真实4080采集、模拟器验收或科学资格。

## 已真正完成的资产交付

SM70 Source2精确归档已闭合：611,552,641,085字节、5606成员，同对象COMMIT、同run EXACT、自然监督成功和owned闭合均已验收。503个采用对象已完成关闭重开双整SHA，读43,130,273,350字节，对应21,565,136,675唯一字节；不重跑。

公共125输入（100常规、25裁剪）的真164成员访问已完成：25,149成员边、22,769唯一对象引用。Code500实际修复并通过独立审查：真实NAS路径约束、既有整bundle符号链接只读验证、版本化manifest sidecar；不写永久backing或旧125树。错误的DECLARED草案保留，生产采用READY图。

已实际prepare及publish到真164，实际catalog CURRENT版本af9f3f0f5e17c33ef1b6061260bdfead74301c1cf181ad3aa4db7b73feb04e40；catalog文件整SHA d88257f05865676457afe3ec7106bb5d303248d583d1095e68c4aca5c00897c3。公共工具/root/workspace/assets/traces/tools/trace-assets及/root/workspace/assets/bin/trace-assets已激活，版本50002b810332682cac34f5937d1f42014fb7898b9ad8c64b0eb3fff29db034bb。EP工作树、DTC工作树及/root/workspace三个真实cwd查询均返回同一125项结果、exit0。该结论是元数据发现/共享目标访问，不扩张为所有正文已恢复或所有consumer兼容。NAS实际挂载0777；“只读”描述入口行为，不能宣称OS强制写保护。

用户取消全量正文读回后，Root已确认无自己的恢复worker、相关原锁空闲，精确保留并退役唯一尚未启动的FULL125 RESTORE授权。元数据授权、catalog和入口不变。未启动972GB级全库物化；不得重新生成该授权。按需小资产恢复及具体consumer格式/语义验收仍按实际用途逐项推进。

## 当前4080后处理究竟做什么

streamcluster已有GPU采集及完整f9记录验证：1611个kernel、5,518,423,824条记录，压缩raw共33,504,398,284字节。当前工作是CPU/NAS数据重排，没有重采GPU、没有启动性能模拟。

实际原5d算法：输入整SHA及v7头解析；按64个CTA分区；临时分区用XZ preset1压缩；逐分区解压统计CTA/warp条数，再次解压交给稳定排序；按z/y/x/warp排序并保留同warp指令原始顺序，写grouped trace；核计数、关闭/fsync、整SHA与解压CRC；拼接header和group XZ流，检查最终CRC、SHA和记录总数。中间checkpoint用于断点续做。后续归档仍需receiver读回、COMMIT和CURRENT目录闭合；常规和裁剪分开记账。

保留最终无丢失、无重排错误和存储一致性验证是必要的。64CTA分片、临时XZ、各层重复CRC/解压及当前whole-job串行调度是工程选择，有优化空间；没有采集阶段耗时数据，不能先断言某一项占大头。用户正在审这些方案，当前健康任务未改算法、未绕锁。raw先存档、capture与POST分离并行、缩短catalog锁属于未部署的建议，不应写成现状。当前控制器会因GPU/LOCAL_IO租约占用拒绝继续，不能因为GPU空闲就擅开采集。

V13的CPU8 PID1605418、随后CPU4 PID1619088均因实际资源准入失败安全终止，分别贡献168及160个新闭合kernel；原六个pilot仍复用。失败、半成品和原授权均留证。未推断没有保存的最后资源样本，未把物理门失败说成OOM。

Root在所有旧owned及租约闭合、内存重新满足准入后，实际启动CPU8 V4：PID1630730/start_ticks982256313，复用334个已闭合kernel，补余1277个。8个worker使用CPU500–507，单批至多8个kernel/2小时，原绝对72小时截止1793241315.9269235不延长。28GiB是各进程地址空间上限之和，不是独立硬cgroup RAM额度。所有payload/scratch/runtime在真164，Native payload0、小控制额度64MiB，至少5GiB实际余量。当前进度以本目录CURRENT_POST_PROGRESS.json时间戳快照为准，不能拿旧PID或旧run推断状态。

归档outer holder发现的具体进程身份误判已逐个修复。V4只增加两处boot元数据读取错误转HOLD，避免把boot文件不可读误判PID消失。Root独立查看完整最小差分、验证其他AST不变、重放原六场景及两个反例并另作真实live-child反例/自然退出检查，CPU组件通过。尚未生产部署，仍需全1611 POST、真实owner/lease/epoch、receiver和Root精确准入。没有用候选测试替代真实归档。

## 161项实际完成了多少

161/161行已经进入真实CPU流程，118/118 binary身份已核实。**全链路适配合格仍是0/161**。现有自动化负责身份、元数据证据及等待阶段分类，不是已经可自主改代码并完成GPU采集验收的流水线。CPU证明数、编译次数、trace对象数都不能当完成workload数。

最后正式接入回执的主要等待为：ISA117、实际输入19、source/runtime14、mapping5、精确GPU4、variant1、SDK1，共161；269条非独占证据请求。最近10项CPU元数据闭合同时发现24项必要动态证据，所以等待总数并未相应下降。71项static reopen、3项route决定、4项static修复及4项mapping修复是证据项目，不是82项适配完成。

19项输入等待主要是生成输入的来源/实际字节与生命周期证据，并非19份缺失下载文件。有限CPU审计已核52份binary/source引用，21项相关规格无外部文件argv；C8现成default50000实际数组可精确复用，但不能推导其余argv/input/profile相同。这些候选尚未正式注册，不能改写完成数。

真正推进每一项的步骤是：
1. 固定binary+argv+输入、loaded image和producer profile，选择可复用的现有证据。
2. 对实际缺口修改producer及对应consumer：ISA解码、目标/返回帧、实际输入观察、mapping或runtime接线。
3. 用CPU小例子排除格式和实现错误，再在109受租约保护的有界窗口运行该精确输入。
4. 检查实际launch、完整记录、输入/输出、正确性及限定条件；零动态CALL只能在独立观察和校准证据下说明该精确执行未走CALL路径，不能解除通用CALL/RET资格。
5. 真164常规/裁剪归档、receiver读回与CURRENT目录闭合，再对声明的实际consumer配置验收。未经实际调查验证的未知HOLD不能作为完成例外。

当前首个真实代码候选为Rodinia Gaussian -s16：完整NVBit tracer derivative、HtoD及同步DtoH字节采样、独立于trace channel的CALL/RET计数和EXIT校准，以及完整CTA/warp/record/EOF/XZ读取。源码已实际修改、离线编译。最终SO为bd2723b387aef31343608440a76a0ccba6b276fc046f4e70f306f8f2ea2a8668；旧c764588在执行前因bool数组越界被撤销，修复重编译，旧记录保留。

当前作者7项完整reader和2项IO CPU模拟通过，但仍是候选：尚无真实GPU见证，尚无完整Gaussian runtime/receiver组合，尚无实际数值及动态observer闭合，更无模拟器/性能资格。Root已启动有限CPU任务补实际运行组合，并由另一有限任务独立审源码与反例；未启动GPU，也未用静态PASS粉饰161结果。未来首批实际动态结果才能校准全161工期，目前不能可靠承诺全部完成时间。

## 其余仍需完成及审阅边界

已提交目录最近为41常规/41裁剪；它们是精确资产/输入对象，不是41个互异benchmark程序。242历史队列为41已提交、5失败保留、33待采、161专项、2superseded。旧SDK controller失败，default50k窗口没有执行，也没有原33恢复ACK，不能沿用旧“已armed即将自动恢复”叙述。streamcluster POST完成后仍需真实归档和正确继任边界，保留原deadline及历史STOP证据。

全部161适配、原33与失败项、尚缺的对应裁剪、统一SM70/SM89公共读取/按需恢复及consumer资格、最终全量目录/差异/例外仍未完成。公共125元数据激活已完成，不再笼统说“公共工具从未激活”；全库正文恢复已取消，不列为待办。

用户正在审核：中间重复解压/CRC是否整合；raw是否先归档；GPU采集和CPU POST是否采用不共享可写目录的流水线及短catalog提交锁；精确输入的限定兼容验收边界。这里只提交事实和建议，未将待审建议当批准。现有健康POST保持运行。所有科学资格、预算和历史不变，近期/计划/未知复用缓存保留，源KEEP/释放0。

SNAPSHOT_MANIFEST.json记录逐个原路径、整SHA和原始字节快照。候选source和正式资产证据分开标注。没有收到外部ChatGPT审稿，不能声称已审。
