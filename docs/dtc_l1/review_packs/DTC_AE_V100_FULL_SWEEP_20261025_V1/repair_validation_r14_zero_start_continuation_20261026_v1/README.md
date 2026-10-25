# R14 zero-start engineering continuation

冻结时间（UTC）：2026-10-25T16:26:16.052996+00:00。本小包为R13交接包的源/元数据增量，176个文件、4242650 bytes，逐文件SHA见`HANDOFF_COPY_MANIFEST.json`。前一完整operations包为commit **`7db6292af24c690553cdaaaffb3c9fe3496dca98`** 中的`repair_validation_20261025_v1`；其214个文件保持原字节，39个诊断文件不在这里重拷。

## R13实际工程故障

R13已经后台执行原矩阵继续派发，但独立repair请求的23点均在模型fork之前被工程检查拒绝。原native `run_native` 的第163行对 `control/<cohort>_SPEC.json` 进行实际SHA读取；新repair specs存放于 `control/specs/<cohort>.json`，缺少native仍要求的兼容路径。此前仅mock高层入口的CPU资格未覆盖这条真实落盘路径契约，因此没有发现该错误。

这不是23个模拟失败：保存的repair q在本次续接前仍为budget=23、remaining=23、consumed=0，且没有INTENT、NATIVE_LAUNCH或科学模型启动。pre-INTENT工程RESULT保留为失败排查证据；没有借此创建新的预算、refund、清零或补造DONE/EXIT/PASS。

## R14的限定修复与继续点

RSS提供23个精确字节兼容alias及真实fake-root运行至`Popen`前的CPU集成资格，验证native实际要求的路径、spec内容SHA、INTENT顺序、运行时输入/输出路径与预算边界。R14使用新controller源路径，冻结的R13源码不编辑；R14只承接原同一请求、同一23个从未启动的cohorts。

R14对existing repair request做zero-start join：0 consumed、23 remaining、0 INTENT及23 exact alias必须同时成立。既有约8.125 GiB写入预留承接，不再额外重计。旧pre-INTENT工程RESULT若需移出阻塞路径，只能由已资格验证的continuation保存到`prelaunch_engineering_preimages/R13_zero_start`并记录精确SHA；不是模型重跑，也不改变历史科学账本。

旧profile、plan、authorization和q的精确字节已保存在`preimages/`。q文件为共享锁下registry内对应request JSON对象的原字节子串，未重序列化；其源registry内容SHA及请求身份见preimage manifest。发布时新profile/plan/alias/资格为新证据，旧版本继续可审计。

## 科学与运行边界

同一新增验证仍为 **23=13修复点+10非正式组件sentinel**，与原72×4=288历史矩阵保持source和账本隔离。此前Core/FW/observer三条修复及既有RAM修复均引用前一发布包及其独立源码commit；本续接不重新设计Core/cache/performance参数，不改论文最后确认英文母版v0.23。旧两个observer缺失回执仍UNACCEPTED，原矩阵不因此完成。

并行上限继续为原矩阵40路加独立验证23路，实际派发受新鲜真实RAM/写入余量限制。初始4 GiB工作集预留、16 GiB运行硬上限、174-new至少5 GiB本地余量保留；结果仍需真164归档及独立native恢复核验。上限不是当前实际运行数量。

本包只有工程续接及CPU/source资格，不是23个验证模拟已通过的声明。新模型启动必须在source发布readback与最终资格门控之后；完成结论要求真实whole-input/NATURAL、严格人口/sidecar/source/runtime核验和归档恢复。零启动修复不能用来填旧结果、refund或标记全部PASS。

这里不包含raw、日志payload、二进制、build树、trace、dataset或前一诊断大包。源工具与JSON保留原字节；候选文件的原status仍为候选，执行应遵循最终资格绑定的profile/plan/alias与源manifest。
