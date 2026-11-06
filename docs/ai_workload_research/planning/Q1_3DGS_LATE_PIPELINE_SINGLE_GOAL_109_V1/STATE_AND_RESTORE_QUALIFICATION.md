# Q1完整训练状态与恢复资格

适用状态：提案，未执行。与[一次性Goal](../../goals/AI_ARCH_Q1_3DGS_LATE_PIPELINE_SINGLE_GOAL_109_V1.md)一并批准、同一Goal内实现与验收，不单独建立状态修复Goal。旧splat-only与A26GR1 pending-gradient终态不改。

## 必须有的状态，不只是模型state_dict

| 类别 | 至少保存/恢复 | 验证方式 |
|---|---|---|
| 来源 | source/tree及运行文件SHA、私有补丁SHA、环境/扩展ABI、输入/相机/预处理、完整配置 | 固定来源与实际文件对应；变化字段逐项登记 |
| 模型 | 所有Gaussian参数与训练buffer、dtype/shape/stride、SHdegree、requires_grad、param-group顺序 | 分块规范字节hash，名称/行身份/结构一致 |
| 身份 | stable Gaussian IDs、增密/剪枝membership映射、next-ID、当前行顺序 | 唯一性、所有消费者索引映射与更新frontier核验；新ID bookkeeping不参与数学 |
| 优化器 | Adam moments、每参数/行counter、step、epsilon/beta、学习率、稀疏/可见更新mask、CPU扩展内部有效状态 | 不能凭Pythonoptimizer字典推断C++对象完整；source mapping覆盖全部读后写状态 |
| 流水 | pending/deferred gradients与索引、转发参数、metadata、已提交/计算完成/已apply/已publish/未消费各代frontier | 记录credit IDs和producer/consumer序号；恢复无重复/漏apply |
| 随机 | 所有实际使用的Python、NumPy、Torch CPU/CUDA、worker generator状态 | 类型/字节精确；恢复在下一次取样前完成 |
| 输入 | camera cursor、epoch/permutation、sampler、预取队列及其RNG、原始camera ID/position | 不靠重建loader后“跳N个”猜相同状态；实际next-camera序列对应 |
| 调度 | next_step定义、LR/SH/densification/reset、refine与累计梯度统计 | schedule与全部累计buffer精确；不能提前停增密 |
| 存储关系 | CPU/GPU镜像、alias/views、stride/offset、所有权与生命周期 | 规范storage ID与view图，不把pointer跨进程当身份 |
| 运行对象 | CPU worker、队列、CUDA stream/event重建计划及已完成未消费标志 | 句柄不序列化复用；用已保存frontier重建，不能重新执行已完成更新 |

额外字段以真实source为准，表非裁剪清单。若某内部状态无法序列化/观察，先在本Goal内做最小工程修复与CPU测试；不可证明完整就不得late恢复。不得把missing字段补零或用默认optimizer替代。

## Safe point与写入

1. 禁止新提交，暂停在真实算法允许的边界。等待已经提交的CPU/GPU工作完成至可序列化frontier；“等待完成”和“额外apply尚未scheduled梯度”严格区分。
2. 记录谁已经算完、谁已经消费/发布、谁仍待以后步骤使用；pending可以合法存在，必须完整保存。
3. 分块序列化；chunk≤256MiB，全部专用staging目标≤512MiB，不全量clone主存state。GPU数据保持原dtype，不能转低精度节盘。
4. tensor内容、storage/view关系、队列和非tensor字段分别建manifest；每块和整体hash。信任来源仅为本Goal产生或明确合法登记的checkpoint，不自动加载陌生pickle。
5. 写入新generation临时目录，完成所有文件+manifest+fsync后原子发布；旧generation在新generation验收前仍可恢复。
6. 最多两个完整state存储槽加预算内日志；C_D/C_V与临时恢复generation的轮转必须记录。只删除本Goal标记的已不再需要的临时文件，不删除旧研究资产。必要时先完成发现并冻结、再生产C_V，避免三份full state同时驻留。
7. 实测单state大小S，以2S+8GiB≤64GiB判断磁盘资格，不从参数N猜checkpoint体积。超限保存可完成的上一代和receipt，不压缩精度或删moments凑数。

## 验收顺序

- CPU mock：自然/异常退出、alias、noncontiguous view、dtype、RNG/cursor、完整pending队列、counter、write failure、半文件/坏hash、发布回滚。对象schema变化不等于可自动迁移旧state。
- 本轮真实早期小state canary：保存前frontier、恢复前首次forward之前精确比对、正常continuation，测试队列应用一次且仅一次；没有另造训练矩阵。
- late C_D重复验收：完整规模同样流式hash，实际restore验证设备/主存值和frontier。不能仅相信loader返回成功。
- 连续参考与restore A/A：同policy、camera和next_step，保留每个已返回真实结果再判定，最早偏差、实际updated集合/参数/moments、loss、图片统计等可取得字段单列。observer观测本身会同步时分池注明。
- 控制变量臂必须从相同已验收C_D/C_V开始；initial-state equality与endpoint equality分别记录。

## 预冻结的数值分类，而非临时阈值

1. STATE_ROUNDTRIP_EXACT：内容、计数、随机/相机/队列、alias和frontier精确，必要硬资格。
2. CONTINUATION_EXACT或ACCEPTED_TOLERANCE：只有适用已接受规则才可以判Numeric PASS；不能借CPUAdam synthetic fixture或Qwen的阈值。
3. CONTINUATION_SENSITIVE_NOT_ESTABLISHED：起点/数学映射有效且值有限，但同策略也不逐bit或没有已接受容差；保留误差分布、损失/更新差异与workload，不自创宽容差。可采集描述性同起点自然窗口，严禁等价/同质量加速措辞。
4. OBSERVATION_OR_RESTORE_DEFECT：缺字段、漏/重复更新、错camera、错位置、起点不一致等真实实现错误；本Goal内修复再验，不以“非确定性”掩盖。不可恢复则STATE_AUTHORITY_NO_GO。
5. NONFINITE_OR_IDENTITY_INVALID：立即停止相应执行，保留错误及已完成结果。

Gaussian轨迹/visible/updated集合不同则不认定严格相同工作。不同线程归约可能改变后续状态，即使起点一样也须披露。没有完整质量/收敛实验，不把短窗PSNR/SSIM/LPIPS有限当质量等价。

## 完整工作与drain

将每个目标camera产生的梯度/update credit一路关联到apply/publish。优先调用原语义的合法drain；没有接口则在原算法自然后续camera中完成closure，记录实际lag L和共同追加camera前缀，并把完整尾部时间及额外工作计入所有臂。

若后续camera又产生pending，它们是明确登记的窗口外未来工作，不可标“所有更新清空”。目标窗口自身的credits必须闭合；不能通过额外Adam step、丢梯度或隐藏等待伪造完成。无法建立这个边界则只报body描述，不发布完整更新时间加速。
