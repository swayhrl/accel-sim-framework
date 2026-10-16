# DTC_MODERN_128K_LAYOUT_FEASIBILITY_174_V1

结论：**128KiB 内可写出有限、无字节重叠的候选组织，但现有实现没有表达这个组织；固定 80KiB DTC 与原平台完整 shared 支持域不能同时保持。本轮建议现代证据继续 baseline-only，不做现代 DTC 主结果。**

状态：`CPU_LAYOUT_PASS / STORAGE_SERVICE_DESIGN_PROPOSED / MODERN_DTC_HOLD`。本文不是配置或启动许可。原 64-SM 实验及已发布证据不受此报告变更。

## 身份和工作范围

2026-10-16，原 `huangrulin-174` 容器，独立 worktree：`/workspace/worktrees/accel-sim-dtc-modern-128k-layout-feasibility-174-v1`；分支 `hrl/iscas2027-dtc-modern-layout-174-v1`。先执行 `git fetch --all --prune`，检查全部本地 worktree、远端分支及同任务提交；当时只有任务说明，没有同任务实现或结果，故建立本 worktree。文档锚点包含 `7112a2242c81bc6aed82a1077b3e68abd6771ea3`。

完整阅读任务 README、GOAL_C、固定容量决定、现有容量报告与 V2 审计资料。实际源码以外置 Core `6fba0136f8465b59fe5858a950fa39efb265f654` 为准；构建 Framework `18a68dcccd795f1b6cda75504e9450d00c9cee02`。既有构建的 CMakeCache 确认 `GPGPU-Sim_SOURCE_DIR` 指向该 Core worktree，Framework 构建目录来自 `accel-sim-decoupled-l1-fast64/gpu-simulator`，没有把本协调文档分支误认为运行 binary。固定容量决定 `e13266ba207d8b8e47b56d62dfdb8bd04c8e2c5b`；4080 资产 `8d1f14a32f5538660d74da86ccb03a2c504c5735`。

主执行证据读取至 `07503e6d`，包含 `e3dbe3db`。仅将其已提交的派生表/报告复制到 [inputs](inputs)，逐字节验证与提交内容一致；身份收据在 [INPUT_IDENTITY.json](INPUT_IDENTITY.json)。不重新读取任何 trace payload，不重新扫描 629 成员。没有改主 Core、主 Framework、可执行配置、运行 binary、环境、44 行队列或全局 LATEST_REPORT。只编译一个小型 CPU oracle，产物在自己的 `/workspace/builds/dtc-modern-layout-174-v1`；不构建模拟器、不启动性能行。

## 首选候选 A：固定池，分段 word banks，独立且计费的端口

这是可审查的**假设架构**，不是 RTX4080 实测结构，也未获实现批准。

- 每 SM DTC 数据占 `[0,81920)`，四个 20KiB bank，每 bank 为 160 行 ×128B；`bank=physical_id%4`、`row=physical_id/4`，任意逻辑 Tag 都可映射任意物理槽。各 bank 提供 4 个独立 32B 读口和 1 个 32B 写口，另有全池 4-read/1-refill 每 core-cycle 的 R1 总配额。这样最坏四次读落同一 bank 仍可完成，既不绑定 Tag bank，也不增加 R1 未声明的 bank stall。4R1W 是昂贵但明确的供给假设，必须计价；没有复制四份数据容量。
- 其余 `[81920,131072)` 是**同一块** 48KiB 尾部存储：32 个 word bank，每个 384×4B。每 bank 的前 `8C` 行给普通 L1，后 `8S` 行给 shared，其中 `C=48-S`，`C/S` 单位 KiB。每 bank 始终共 384 行；不是同时实例化最大 48KiB 普通数组和最大 32KiB shared 数组。普通 sector 横跨一组八个 word bank，四组对应原四个 L1 bank/延迟队列；shared 使用原 `(address/4)%32` 映射。
- 尾部每 bank 配专用普通 data 1RW、普通 fill 1W、shared 1RW，共 **2RW+1W** 端口。共享的是存储 bank 及每个 bank 内互斥的行容量；三种角色不争用同一个端口。候选A为普通路径明确规定总计每core-cycle一个32B data访问及一个32B refill，shared沿用原bank-conflict服务；不伪称既有源码已建模共同端口。若要求各角色共用更少端口，就必须增加仲裁、地址化 collection 游标和重试时序，已经超出本候选的最小路径。

完整容量、地址解码和端口向量在 [LAYOUT_AND_PORTS.tsv](LAYOUT_AND_PORTS.tsv)。在 S=0/8/16/32 时，分别为 `80+48+0`、`80+40+8`、`80+32+16`、`80+16+32`。普通 L1 保留 sector 类型、4 sets、128B 行，ways 为 96/80/64/32；16KiB 是继承已有提案的设计下限，**未证明它是语义最小值或已批准合同**。shared 原有占用率、CTA 限制、地址和 bank-conflict 算法不改。

普通写、atomic、`.cg`/配置旁路仍由 `memory_cycle` 的原分流处理；不会因为容量分区而把它们变成可合并 DTC 读。SASS atomic 在已读 Framework 中标为 `CACHE_GLOBAL`；Core 仍保留非合并分类和原路径，不能概括为“所有 atomic 必经普通 L1”。DTC load 的 miss/return 继续由物理槽及 generation 识别，普通路径的 MSHR/fill/ack 继续存在。这里只确认接线方案；没有新增数值正确性证明或跨路径一致性协议。

## 新发现：普通端口配置不是已经执行的限流

逐调用核查发现 `L1_latency_queue_cycle` 的四bank循环直接调用 `m_L1D->access`，没有 `data_port_free()` 检查；`ldst_unit::cycle` 的普通响应分支调用 `m_L1D->fill`，没有 `m_L1D->fill_port_free()` 检查，循环条件中的 `m_next_global.size()` 也不限制普通fill个数。`l1_cache::access` 委托 `data_cache::access`，后者记录busy cycles，不在那里拒绝超额服务。源码事实及函数hash见 [CPU_SOURCE_FINDINGS.json](CPU_SOURCE_FINDINGS.json)。这修正了复用报告中将普通32B端口描述为完整有限服务的过强解读；原审计快照保持原样。该观察没有测量实际负载的超额频率，也不自动否定全部旧结果。

因此A的32B普通data/32B fill供给需要新增显式opt-in绝对cycle配额：在延迟队列访问前保守限制一次32B普通访问尝试；在普通fill分支前限制一次32B响应处理，未授予则保留FIFO头，不改变返回所有权。MISS等不触发实际data读也可保守占一次访问尝试；这就是新时序假设，不能冒称原吞吐。默认OFF和冻结结果不修改；若以后启用，所有配对modern baseline/对照也需同服务版本，不能直接除以旧baseline周期。DTC原R1配额不变，但原路径新增限流也跨越服务合同。

## 支持域和最小影响

当前可声称的只有**单个分区 epoch 的字节与端口供给检查**。A 的候选域为 S≤32KiB、whole-line PAPER_IO/OO、LD/ST multiplier=1、原 R1 已接受的指令/引用边界。完整平台的 64/100KiB shared，以及混合 kernel 并发、分区切换、缓存状态清退，都没有资格。

`max_cta` 目前更改共享的配置对象，而 `ldst_unit::flush/invalidate` 只处理 `m_L1D`；不能据此认为 DTC tags、pending returns、PIB 或 retained mappings 已清空。A 的落地需要按 SM/epoch 持有并核查分区、在合法边界清退并防止有活请求时重映射。不能仅把 `m_unified_cache_size` 改成 48，也不能仅改 `set_assoc` 就将仍按最大几何实例化的普通对象记作裁剪后的物理容量。现有模拟器按所有权/就绪状态建模，并不保存完整 architectural data values；这不是要求另建数据值阵列，而是必须让最大可用槽、活动槽与共同物理容量一致。

改动清单和局部验证见 [SOURCE_IMPACT.tsv](SOURCE_IMPACT.tsv)、[LEGAL_DOMAIN.md](LEGAL_DOMAIN.md)。至少涉及 Core 的 shader 配置/构造/分配/清退、cache 最大几何与索引，以及 Framework 的 opt-in spec/严格检查；不是 config-only，也不是单个函数修复。A 不改 IO FIFO、OO Ref/Shadow Ref、partial allocation、generation、retire 规则，但会新增存储/端口合同、普通路径限流及候选域限制，必须先交审。

唯一备选 B 是动态池 `P=min(80,112-S), C=128-S-P`。其 S=64 为 48+16+64；S=100 为 12+16+100。它改变 pool/进度条件；12KiB=96 行小于原 128 个映射，已经有实际前端反例，不能靠旋钮直接实现。B 不建议本轮推进，详见 [LEGAL_DOMAIN.md](LEGAL_DOMAIN.md)。

## CPU 验证与交付

[CPU_LAYOUT_CHECK.json](CPU_LAYOUT_CHECK.json) 验证：7 个已有派生证据快照的 SHA；629 行逐 key/member SHA 与原清单一致；shared 分区 0/8/16/32KiB 分别 524/87/14/4 项；四种布局的 2560 个 DTC sector 地址、全部普通/shared word 地址唯一且无重叠；256 种四读 bank 分布和 2048 种尾部端口角色组合。四读分布中 232 种不能由“每 bank 单读口”兑现，故不能将四 bank 等同四个任意地址读口。

[CPU_SHRINK_ORACLE.txt](CPU_SHRINK_ORACLE.txt) 来自未修改的生产头文件：96 次已返回、已退休的单行访问占据每 set 三个 ways，随后访问第 97 行（set0 空闲第4 way）。96 行池的 IO/OO 均连续 64 次 `NO_FREE_LINE`；640 行池两个对照均可分配。逻辑空槽没有可回收的物理 victim，且没有在途请求能解开状态。测试只验证结构性阻塞；不把 64 次重试当成一般死锁证明，持久性还由该封闭状态的源码条件支持。

复现命令（仓库根目录，单 CPU；C++ binary 不入 Git）：

```bash
python3 docs/dtc_l1/review_packs/DTC_MODERN_LAYOUT_PROPOSAL_V1/check_layout.py
g++ -std=c++17 -O0 -Wall -Wextra -I /workspace/worktrees/gpgpu-sim-iscas2027-dtc-service-closure-174-v1/src/gpgpu-sim docs/dtc_l1/review_packs/DTC_MODERN_LAYOUT_PROPOSAL_V1/shrink_pool_oracle.cc -o /workspace/builds/dtc-modern-layout-174-v1/shrink_pool_oracle
/workspace/builds/dtc-modern-layout-174-v1/shrink_pool_oracle
```

这些 PASS 不覆盖 SRAM 时序/面积、RTL 可实现性、完整 simulator 路径、数值语义、现代 ISA 准入或性能。没有把复用审计的算术通过升级成现代 DTC 准入；Hotspot 地址语义和 SM89 准入仍为独立门槛。下一步的具体决定留在 [NEXT_DECISION.md](NEXT_DECISION.md)。
