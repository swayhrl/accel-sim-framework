# DTC_LANE_V2_VALUE_VISIBILITY_SCOPE_174

2026-10-18，Asia/Shanghai。**只读值语义范围与CPU见证已交付；生产load读值正确性仍UNPROVEN。K2为future-only，未实施、未授权启动。** 本Goal不重复启动或修改V1、不改Core、不跑模拟器/性能、不重扫trace body。

独立 Framework 分支 `hrl/iscas2027-dtc-lane-v2-value-scope-174-v1`，worktree `/workspace/worktrees/accel-sim-iscas2027-dtc-lane-v2-value-scope-174-v1`。从V1 HEAD `26abd496417d9392245052e54fbd9ba27c6ffd96`建立，只新增本V2目录。执行位置原174主机 `huangrulin-174`，root账户/原容器。

已fetch/read-back冻结Core `6fba0136f8465b59fe5858a950fa39efb265f654`、V1、Y V1 `b673d046b38f61159b5db67a477d58d1afa4662f`。初读X Framework `0c8fcb571977303f3e87ecb0cac6cf7bd25d3cfc`为旧STOP；发布前远端更新，已补fetch/read-back `49fb5d1b62b6f2387abc2d568bc8ae7543dc0df4`，报告绑定X Core `c0a5e2c31e407c57e3a4af3ce529c921e8059a05`，状态为OO default-off已实现、本地CPU通过、Lane Y独立验证pending。Y V1仍绑定旧Core `f8b34dd7…`，不外推到新Core；旧STOP只作历史，不重开用户入口选择。X trace-build仍单列`0c8fcb…`，所审5份Framework路由文件与冻结build18/最终review逐字节核同，不据此推binary同一。[SOURCE_SHA256.tsv](SOURCE_SHA256.tsv)绑定30份输入源码/发布证据。

用户K1裁决保持：原LDST invalidate **source请求E** 撤查询映射并保护旧physical/generation/PIB/Ref/return。ordinary pending-commit **C**、真实kernel-done **D**、无E写后读分别建模记录。V2不给E新增数据发布含义，不把C/D换作E。

新增值层结论：普通SASS路由、byte mask、pending/Ref与返回generation能支持结构和时序谓词；它们不能给出W的payload、V(W,domain)或L的合法read-from。尤其store sidecar退出、WB本地ACK、PROXY_FENCE、kernel完成均不能当通用publish。trace格式虽有可选寄存器值字段，普通load/store consumer没有据此完成通用值传播与逐load比较；本轮不检查实际trace字段覆盖率，归W。

CPU检查：25个独立合成序列，**8 PASS_SYNTHETIC_CONDITIONAL、13预期REJECT、4 UNPROVEN**；25个错误期望负控均退出1。冻结/X header分别编译运行2次，仅证明无E同identity命中、外部byte版本可不同，以及X OO选中E时old pending identity可保留至final Ref；7/9由fixture注入。**production value tests=0；完整模拟器=0；performance=0；trace body reads=0；K2 implementation=false。** 这些检查不替代K1全范围独立验收。

|交付文件|范围|
|---|---|
|[VALUE_VISIBILITY_SCOPE.md](VALUE_VISIBILITY_SCOPE.md)|四概念、发布快照、条件化值规格、可证明/缺证据域、STOP边界|
|[LITMUS_AND_EXPECTED_OUTCOMES.tsv](LITMUS_AND_EXPECTED_OUTCOMES.tsv)|25个按实际route整理的场景、显式字节期望、负例和未定谓词|
|[SOURCE_ROUTING_CROSSWALK.md](SOURCE_ROUTING_CROSSWALK.md)|17类实际可达source事件、源码行号、已有身份与缺少的payload/visibility接口|
|[K2_FUTURE_ONLY.md](K2_FUTURE_ONLY.md)|候选D2支持域、最小值/顺序/生命周期规格及授权后验收门槛；没有实现机制|
|[CPU_VALUE_WITNESSES.json](CPU_VALUE_WITNESSES.json)|实际合成观察、预期拒绝、负控退出码和两版header桥接结果|
|[INPUT_PUBLICATION_READBACK.json](INPUT_PUBLICATION_READBACK.json)|固定V/Y/X远端回读、X历史与新发布快照、冻结Core fetch身份|
|[SOURCE_SHA256.tsv](SOURCE_SHA256.tsv)、[SHA256SUMS](SHA256SUMS)|输入commit/blob/SHA与本包逐文件SHA；SHA256SUMS不包含自身|

复核：在本worktree运行 `python3 -E docs/dtc_l1/review_packs/DTC_LANE_V2_VALUE_SCOPE_V1/scripts/run_cpu_scope.py`。脚本只读固定Git对象，临时编译header桥接，运行合成byte/read-from checker；仅写本V2的SOURCE_SHA256/CPU结果。正常退出0表示观察到预期的有条件PASS/REJECT/UNPROVEN；不代表ISA正确性。`sha256sum -c SHA256SUMS`在本包目录验证发布文件；若重跑改变结果，必须审查并重建manifest，不能沿用旧hash。

**STOP-VALUE / STOP-ISA / STOP-K2**按缺口交付，不借结构守恒声称load值正确，不启动新机制。Git提交/push/fetch-back逐blob核对并保持clean，最终外部回执写 `/workspace/dtc-lane-v2-value-scope-174-v1/FINAL_FETCH_BACK.json`，绑定最终HEAD/tree而不自引用。本包不写V1、X/Y/W或其它Lane的工作目录/状态，也不重启任何历史Goal。
