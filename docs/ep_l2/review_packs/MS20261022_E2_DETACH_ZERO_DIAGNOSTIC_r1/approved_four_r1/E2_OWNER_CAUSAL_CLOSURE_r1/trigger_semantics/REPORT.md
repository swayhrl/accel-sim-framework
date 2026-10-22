# Core9243 detach 触发语义只读审查

结论：未发现能解释当前三个已接受应用 `detach=0` 的确定实现或统计错误。当前 detach 是同一物理 slice/set 全部16路含未完成 RESERVED sector 时的末级 Tag 解压机制；正向 RO 证书、HIT_RESERVED、高占用或大量 cache miss 均不足以触发。三个端点的零 raw pressure 由 E owner 提供，本审查未重读应用 raw，因而不能把零触发归因于下述 requester 覆盖限制。

同时确认一个必须公开的范围限制：普通非 RO native read 在前端遇到全路 RESERVED 时，不会咨询可 detach 的 RO victim。现有 native 中该 requester 的正例通过直接 cache API，而不是生产前端。它不等于当前应用失败，不构成无需审批即可修改机制的依据；当前应用未证明所有潜在 requester 都可触发。

## 身份与范围

冻结 Core 为 `9243f769620653f2a9d4df5599e9581e9dae6067`，源根为 `/workspace/worktrees/gpgpu-sim-ep-l2-ms20261022-a2-detach-observer-v1`。12个被审源文件与该提交 Git blob 字节一致，路径、SHA256、Git blob 和函数对比见 `SOURCE_IDENTITIES.json`。对比 main61 Core `d010911e3174a3764791183cd108fe4664ba8731`，Tag probe、可 detach 选择、new_request、owner conflict、can_detach 五段逻辑字节相同。以下非 RO requester 范围限制不是 r4 observer 引入的新机制变化。未构建、运行 native、执行应用或改动生产文件、registry、资格和资源控制。

## 真实触发路径可达，但条件很窄

`src/gpgpu-sim/gpu-cache.cc:344–426` 的 Tag probe 先处理同地址 HIT/HIT_RESERVED/SECTOR_MISS，随后检查可替换路。只有同 set 所有路都包含 RESERVED sector 才返回 `RESERVATION_FAIL`；普通 clean/dirty 可替换路仍可选择，Tag 高占用不会自行触发 detach。

RO 新请求的 `ep-l2-ro-runtime.inc:251–297` 确实在 raw FAIL 后咨询同 set 的可 detach victim，并把预览结果改写为 MISS；所以受支持的 RO 新请求生产触发没有被 preview 全面屏蔽。`l2cache.cc:1414–1425,1521–1563` 仅在 admission 成功后实际 access；`ep-l2-ft-cache.inc:326–329` 再检查 raw probe，调用 relieve、重新 probe。目录、地址容量、MissQ 等独立门仍可在真实 detach 后拒绝请求，故成功 detach 与随后请求接受不是同一事件。

选择规则见 `ep-l2-ro-runtime.inc:232–249`、`ep-l2-ro-transactions.h:181–223`：同 set、T 开启、attached、没有 sticky reuse，且 required sector 尚未全部 ready。成功 detach 保留 payload 和事务 generation 关联，真正撤销 Tag 绑定（runtime:171–175；store-port:105–109），迟到 fill/响应继续归原事务（transactions:248–264）。本审查未发现不满足 eligibility 的路径能错误 reclaim。

## 已确认的 requester 非对称范围

候选请求限于通过证书的特定 global read（runtime:100–105）。普通非 RO native read 的 `new_request` 为 false，RO preview 直接返回 false（runtime:200–209,256）。随后 baseline `gpu-cache.cc:2726–2754` raw probe 若 FAIL 直接返回，不咨询 detach。前端 line_available 为 false 后不会到达 ft_access。此处特指普通无 TVD 特殊路径的 native read，不泛化到全部 write/atomic/promotion 路径。

现有 `tests/ep_l2/test_detach_diagnostic.cc:217–221` 明确验证：真实前端保持 denied/not-consulted，接着直接 `cache->access` 才真实 relieve，后续因 directory gate 失败。该 native 证明机制底层可处理此 victim/requester 组合，未证明普通 native requester 经生产前端被接纳。压力状态消失后可以继续前进，因此没有据此证明永久死锁。

正式 f786 producer 的 E_ACCEPTANCE_ENTRY 约束 F/W1V1T1M1 与实际 descriptor/payload 容量，要求 observer 判别 pressure/eligible/consulted/commit/lifetime，没有承诺任意 requester 均调用 relief。INTERFACE 未找到这种承诺；正式分支保留的 SUPPORTED_PROFILES 仍是旧 R28/main773 元数据，不能拿来扩张9243资格。架构路线图 `ELASTIC_PAYLOAD_L2_ARCHITECTURE_AND_ROADMAP.md:861–907` 的 victim 优先级建议明确未冻结，不允许直接固化。故结论是科学范围需显式审查，不自动判成 bug 或改机制。

## Mixed sectors、payload pin 和 HIT_RESERVED

`gpu-cache.h:397–410` 对 sector line 的 reserved 判定为任一 sector RESERVED。不同地址的替换不会选择 mixed VALID/RESERVED 路；同地址优先 HIT_RESERVED/SECTOR_MISS 属正常事务路径。全部 ready、响应尚未退尽的 pinned payload，其 Tag 可以 VALID，可成为 MISS 替换候选，但 `ep-l2-ft-cache.inc:340–357` 会通过 pin/pending 门保护它。此时不满足 missing-sector 的 detach 资格。既有 `test_detach_diagnostic.cc:201–205` 明确覆盖这种 ready/pinned 等待，并注明没有断言 raw all-reserved。

如果被选 victim ready/pinned 而其他路有可 detach pending RO，当前 raw MISS 路也不会尝试 relief。这是策略机会范围，不是已证明的不安全回收或当前零触发原因；E owner 提供的三个应用 denied_pin 均0。

HIT_RESERVED 只需匹配的一个请求 sector RESERVED，与16路全 reserved 不同。DWT 的7250 raw HIT_RESERVED 是当前可见前端 head 按 cycle/uid 采样的周期数（gpu-cache.cc:2996–3029），不是7250个独立 merge 或 Tag 压力机会。实际成功 merge 的 sticky reuse 更新见 runtime:313–325 和 transactions:197–199。

## 统计和已有 native 证明

observer state 在 runtime 创建前登记（runtime:372–375），事务成功 detach 与诊断 success 在同一成功路径累加（transactions:220–222），ro_print 核对两套成功计数（runtime:399–408）。未发现 epoch begin/end 重置事件累计或丢失已发生 detach 的确定路径。原始 probe observer 的域是可见前端 head；TVD 特殊处理等在此前消费的周期不在该域（l2cache:1313–1324）。raw pressure=0 的准确解释是该冻结观测域内没有压力，不能扩张为整个应用所有缓存状态始终富余。

仅复用并阅读小型既有独立 native 回执：48次真实 native、1589 checks；PRESSURE_ELIGIBLE 对应2次成功 detach、2次最终退休，包含真实同 set pending 填充压力、迟到返回及资源退尽。NATIVE_REQUESTER_RO_VICTIM 的1次正例具有上述直接 API 范围。它们证明受控状态下机制可达和生命周期安全，不能代替应用64slice完整输入的发生率或性能证据。本轮 native 重跑0。

## Tag 压力为什么可能稀少

批准四输入配置为 `S:64:128:16`，64 slices，每 slice64 sets×16 ways，共65536 Tag（128B line 对应8MiB Tag 数据覆盖），payload1168 slots/slice。Tag 压力需同时集中在同 slice/set 且16路都有 pending RESERVED；一般容量 miss 可直接替换。`gpu-cache.cc:179–187` 在 set index 前剥离 partition bits 并应用配置 hash，因此虚拟地址的表面 stride 不能证明真实 slice/set 冲突。native 刻意同 set 压入16个 pending RO、扣住 lower return，第17个新地址才形成机会。

现有证据支持先报告“实际观察域没有触发机会”，而不是声称应用正向证书失效、Tag 永远充足或机制失效。如果要扩大 native requester 支持，或用更小 assoc/sets、不同延迟和 victim 优先级制造压力，应先明确科学比较和机制语义，再做 source/new binary、针对性 native 和独立完整应用资格；本审查不授权这些变更。
