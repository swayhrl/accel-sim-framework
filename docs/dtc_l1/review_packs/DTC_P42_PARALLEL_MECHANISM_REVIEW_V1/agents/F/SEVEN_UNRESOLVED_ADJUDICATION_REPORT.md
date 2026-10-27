# 七项输入身份与完整性只读收敛报告（Agent F）

结论：V1 仍为 **35 项冻结、7 项 UNRESOLVED**，本轮没有新增冻结。21 份当前 kernelslist.g 的 SHA 全部与 V1 相符。四项可形成基于 Rodinia 3.1 发布 `run` 命令的 V2 条件建议；CFD、streamcluster 存在标准应用范围矛盾；kmeans 的输入内容和收敛范围仍缺证据。

本报告不读取 cycles、加速比、模拟耗时或修复性能，也不按 PASS 选择。没有新模拟、捕获、trace 主体扫描或运行中任务改动。英文 v0.23、原 35 项及 ATAX 前缀排除证据保持不变。

| 程序 | V2 条件候选 | 本轮明确的范围判断 | 尚缺的关键证据 |
|---|---|---|---|
| backprop | 3.1 / 65536 | 单次训练的两个 kernel 与源码一致 | 42-suite source-version precedence not approved/frozen；Capture executable/build/tracer linkage；Generated input content or capture-time generator/runtime binding; source seed alone is insufficient |
| cfd | 无 | 5 个 kernel 缺 time_step，标准应为 14003 个 | Capture-time source/binary identity and truncation/ROI configuration；Raw mesh contents, exact nel and capture-linked SHA；Full time-step/iteration capture or approved bounded-region contract; neither is granted by current authorization |
| kmeans | 3.1 / kdd_cup（暂不可冻结） | invert + 两次迭代；不能由数量判定收敛/截断 | Actual dataset bytes/SHA and row/feature parser result；Capture stdout final iterated-N/convergence result plus tracer scope；Source-version precedence and capture binary/source/build binding |
| nn | 3.1 / filelist_4 -r 5 -lat 30 -lng 90 | 读入全部记录后一次 GPU 距离计算，top-N 在 CPU | filelist bytes plus ordered constituent data files and capture-linked SHAs；Capture executable/build/tracer identity including emulation macro state；Explicit V2 version-policy adoption; historical terminal-scope receipts are not full-app certification |
| nw | 3.1 / 2048 10 | 255 次波前 launch 与源码公式一致 | Capture executable/compiler/tracer linkage；Generated sequence content binding to generator and C-library behavior；Explicit V2 version policy; whole-app numerical correctness remains separate |
| pathfinder | 3.1 / 100000 100 20 | 5 次金字塔 launch 与源码公式一致 | Capture executable/compiler/tracer binding；Capture-time generated wall contents or exact generator/runtime binding；Explicit V2 source-version precedence |
| streamcluster | 无；10/20/256 仅命令候选 | 5 次 launch 少于一次标准搜索 sweep 的 32/179 次 | Capture binary/source/compile flags and tracer kernel-window rules；Capture completion/host convergence log and complete launch range；Generated coordinate content/runtime binding; explicit parameter-policy decision |

这里的 V2 候选是审阅建议，**不是已批准的版本优先级，也不是完整应用/数值正确性的认证**。仅“新版参数更大”不足以构成选择理由；建议依据是可核验的发布 run 命令、源码 parser 与捕获范围。

## 最重要的新增发现

1. **streamcluster 也有范围阻断。** 已与固定上游 commit 核对一致的 `streamcluster_cuda_cpu.cpp` 中，`ITER=3`；每个实际进入的 pFL sweep 固定调用 `floor(3*kmax*ln(kmax))` 次 pgain。每次 pgain 无条件发一个 `kernel_compute_cost`。kmax=6/20 时分别为 32/179 次，现有两份只有 5 次。必须先找出 capture 二进制、ROI/窗口限制或提前退出证据。不能称为完整 streamcluster。

2. **CFD 的缺口被再次锁定，不能靠本地源码差异解释。** 本地与上游的差异集中在 CUDA 错误检查包装，二者仍保持 2000 次外迭代、每次三阶段 RK。标准完整 launch 数为 `3+2000×(1+3+3)=14003`；当前 5 个 kernel 连第一次 time_step 都没有。193K 对应的 `193536` 仅是 padded nelr，真实 nel 和 mesh SHA 未与捕获绑定。

3. **kmeans 同名数据集不是一维大小序列。** 按源码矩阵/成员/中心复制布局条件推导：

| 捕获参数 | npoints（条件推导） | nfeatures（条件推导） | 原始输入内容 SHA |
|---|---:|---:|---|
| _o__i___data_819200_txt | 819200 | 34 | 未绑定 |
| _o__i___data_kdd_cup | 494020 | 34 | 未绑定 |
| _i_data_400_txt__g_data_400_result_txt__o | 400 | 34 | 未绑定 |
| _o__i___data_28k_4x_features_txt | 28672 | 138 | 未绑定 |

这些维度由真实 commandlist 复制字节数和已读源码公式交叉约束；由于 capture 二进制尚未绑定，它们不是数据内容认证。`28k_4x_features` 的条件推导是 28672×138，不能直接按名字解释为任意其他输入的四倍。三个 3.1 输入都捕获两次 kmeansPoint：可能是两次收敛，也可能受捕获窗口影响，必须用已有 convergence/capture 日志判定。

4. **NN 的 filelist_4 名字不构成同数据证据。** 3.1 HtoD 坐标缓存 342112 字节，在两个 float 的 LatLong 布局下对应 42764 条记录；2.0-ft 使用四批 735000 字节字符记录。3.1 的 `-r 5` 是 CPU top-N 返回数量，不传给 GPU euclid。历史 DTC_LEGACY_NN 三个 cohort 有精确 provenance 指针，但其 terminal-scope 状态不能冒充 42-suite 的整应用认证。

5. **2.0-ft 和 3.1 不能当重复 capture 直接合并。** 2.0-ft 上游 README 明确其目的是缩小规模的功能回归，且版本内同参数的 format0/format3 捕获 SHA 不同。NW 还存在 kernel 参数签名差异。旧捕获全部保留；不根据哪个更快、成功或省时来选择。

## 七项逐项证据与建议

### backprop

状态：`UNRESOLVED_V1_UNCHANGED`；范围：`SOURCE_SCOPE_CONSISTENT_NOT_CAPTURE_CERTIFIED`。

- Both versions train one network once; hidden/output sizes are 16/1 and the initialization seed is 7.
- 3.1 packaged run specifies 65536. Its two captured kernels and HtoD sizes 262148 and 4456516 bytes agree with (65536+1)*4 and (65536+1)*17*4.
- 2.0-ft is explicitly a modified functional-regression collection; its 4096 input is not an alias of the 3.1 65536 input. Two 4096 captures have different trace-format identities and member SHAs.

建议：Prefer the 3.1 release run command over small 2.0-ft regression variants, if this outcome-independent suite policy is adopted explicitly for V2.

仍缺：42-suite source-version precedence not approved/frozen；Capture executable/build/tracer linkage；Generated input content or capture-time generator/runtime binding; source seed alone is insufficient。

源码位置：
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/backprop/facetrain.c:14–52`，SHA256 `5a1c324735b4eb7ff08d6b488134a8e66b5aaddcd4168623803ccbb96c8dd293`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/backprop/backprop_cuda.cu:80–84`，SHA256 `1bd966c36f6277d8d0246a5411e734e69e96050532303e40c5253e06b76d6383`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/backprop/backprop_cuda.cu:118–128`，SHA256 `1bd966c36f6277d8d0246a5411e734e69e96050532303e40c5253e06b76d6383`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/backprop/backprop.c:132–136`，SHA256 `3528b0256e55650908f4ff77fbdfa1e2bcbdb69237e5d343426652aa341ff70e`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/backprop/imagenet.c:8–23`，SHA256 `c3b48529cb45eaff4136a54ba5b01c29dcedf9c2de8c79c2813b34ef8a174323`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/backprop/run:1–2`，SHA256 `bf76b243af20efe1f18c9088ad3f7e49552a503ae3cb4b8e222abcabc3f51fc8`。

候选输入身份：
- `5fa6f81161d230f55179618027a07e9060d87511e79943049494e2768d2788ad`；bundle `ec5bf83f2598dc909dd20fa64139728ccd82d5630a01a37a11ac22fce4804398`；`/root/workspace/assets/traces/bundles/ec5bf83f2598dc909dd20fa64139728ccd82d5630a01a37a11ac22fce4804398/tree/kernelslist.g`；commandlist SHA `dba1ae62526e8e6f962e332e7a0da0a1b92a1efd3fa6709c7086146137662b05`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。
- `66a2ff40b5b4f8daee8b489afd05afbcd68725361ea49d50e2e29dfefea76ece`；bundle `40de4750eeba2d3299b98a45d0a746f5cac98930c3be10f9b80b1aace0559f6e`；`/root/workspace/assets/traces/bundles/40de4750eeba2d3299b98a45d0a746f5cac98930c3be10f9b80b1aace0559f6e/tree/kernelslist.g`；commandlist SHA `5fbb64c25b3a0f1d4a41f85cf90ea7861b844af1f79121f728bf70f1a7a5057a`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。
- `6dad43cf98e6624064e55e543a0fc20ebdcb9c7378a34ccae0fee2890e91c39f`；bundle `904bd860131f179217000c03276ede3ad03f7cf869b568c611e521bb2ab3514e`；`/root/workspace/assets/traces/bundles/904bd860131f179217000c03276ede3ad03f7cf869b568c611e521bb2ab3514e/tree/kernelslist.g`；commandlist SHA `0c8d1a7c40dd9b7dcc8c0306a7aee0fec0b963dad4d5279bc6bb10ce1176fbd6`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。

### cfd

状态：`UNRESOLVED_V1_UNCHANGED`；范围：`STANDARD_FULL_APPLICATION_SCOPE_CONTRADICTION`。

- Pinned and deployed euler3d retain iterations=2000 and RK=3. Three initialization launches plus 2000*(one step-factor + three flux + three time-step)=14003 GPU launches are expected.
- All three available candidates contain only three initialize + one step-factor + one flux kernel; no time-step occurs. Even a complete first iteration would require 10 kernels.
- The local source differs from pinned b059fdae only by CUDA error-check wrapper removal; this does not explain five captured kernels.
- 193K grid1008*192 describes padded nelr=193536, not exact mesh nel. A historical 097K E1 reference input SHA exists, but is not bound to the capture contents.

建议：Do not promote any five-kernel candidate as a full CFD application. Recover capture executable and documented ROI/early-stop evidence first. An explicit partial-region suite would be a different scientific contract.

仍缺：Capture-time source/binary identity and truncation/ROI configuration；Raw mesh contents, exact nel and capture-linked SHA；Full time-step/iteration capture or approved bounded-region contract; neither is granted by current authorization。

源码位置：
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/cfd/euler3d.cu:17–27`，SHA256 `b5015e61e413dbf711a1e928505d5591f21639644a156dfe31f2e126ce788079`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/cfd/euler3d.cu:499–507`，SHA256 `b5015e61e413dbf711a1e928505d5591f21639644a156dfe31f2e126ce788079`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/cfd/euler3d.cu:555–566`，SHA256 `b5015e61e413dbf711a1e928505d5591f21639644a156dfe31f2e126ce788079`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/cfd/euler3d.cu:580–596`，SHA256 `b5015e61e413dbf711a1e928505d5591f21639644a156dfe31f2e126ce788079`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/cfd/run:1–10`，SHA256 `073fca9db81e8b6bb7c1ab2b56488c0650af2b7e0c6719c54542d89e3461c8b5`。

候选输入身份：
- `45cba351972ddf30016bd9bd4859e3ebb531eb53ecae5276e836b59fddc1b088`；bundle `78d6597c05617de71d2d95e3646163fa5c4a2cf3e83ad0b2528d7c3658caf9da`；`/root/workspace/assets/traces/bundles/78d6597c05617de71d2d95e3646163fa5c4a2cf3e83ad0b2528d7c3658caf9da/tree/kernelslist.g`；commandlist SHA `ce71e70525c6299a6be1bae3790b0eeb0417e1f4608cbd10e706c0a14fdd6b46`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。
- `85700545918390d7a5cb33340f2043b13bf86a86d6141de238916cc60eb941cd`；bundle `b1078876afe93f28615201619796b9f79ba617a44271c365c516dabbbc59c3b4`；`/root/workspace/assets/traces/bundles/b1078876afe93f28615201619796b9f79ba617a44271c365c516dabbbc59c3b4/tree/kernelslist.g`；commandlist SHA `ce71e70525c6299a6be1bae3790b0eeb0417e1f4608cbd10e706c0a14fdd6b46`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。
- `f9edab43938e7bf465a95ddec5eb3934582df86b287ea546432620d7b24829ad`；bundle `88c1fa43e191a5903de74e466aed03ec020a4ff338e3ea47988ac367c3caf5ef`；`/root/workspace/assets/traces/bundles/88c1fa43e191a5903de74e466aed03ec020a4ff338e3ea47988ac367c3caf5ef/tree/kernelslist.g`；commandlist SHA `ce71e70525c6299a6be1bae3790b0eeb0417e1f4608cbd10e706c0a14fdd6b46`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。

### kmeans

状态：`UNRESOLVED_V1_UNCHANGED`；范围：`DATA_DEPENDENT_CONVERGENCE_NOT_CERTIFIED`。

- The 3.1 packaged run uses kdd_cup; source defaults are kmin=kmax=5, threshold=0.001 and one outer run.
- All three 3.1 captures contain invert_mapping plus two kmeansPoint launches. This can be a two-iteration convergence, but neither a fixed two-iteration application nor truncation is proven from kernel count.
- Source-layout conditional dimensions from independent HtoD matrix/membership/center sizes are 819200x34, 494020x34 (kdd_cup), 28672x138 (28k_4x_features), and 400x34 (2.0-ft). These are not certified raw dataset identities.
- The existing official 400 capture data symlink is broken on 174-new. A result file is not the original input data.

建议：kdd_cup is the source-packaged run candidate; do not freeze until dataset and convergence/capture-completeness evidence close.

仍缺：Actual dataset bytes/SHA and row/feature parser result；Capture stdout final iterated-N/convergence result plus tracer scope；Source-version precedence and capture binary/source/build binding。

源码位置：
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/kmeans/kmeans.c:108–123`，SHA256 `3544ffbe528072518729e41b7241ceb4a699919a8bbeda7ae5f0bcc176e45646`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/kmeans/kmeans.c:190–220`，SHA256 `3544ffbe528072518729e41b7241ceb4a699919a8bbeda7ae5f0bcc176e45646`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/kmeans/kmeans_clustering.c:133–171`，SHA256 `4ebdf3a00bc41ebfc340113da816e3aa74dd85a56145df8b4826c0d796660381`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/kmeans/kmeans_cuda.cu:47–80`，SHA256 `1c15cfeda08c5823c9fc50fa1abfcec34e2023f21a25ac3a9fee6f51e2e020c0`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/kmeans/kmeans_cuda.cu:152–156`，SHA256 `1c15cfeda08c5823c9fc50fa1abfcec34e2023f21a25ac3a9fee6f51e2e020c0`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/kmeans/kmeans_cuda.cu:228–245`，SHA256 `1c15cfeda08c5823c9fc50fa1abfcec34e2023f21a25ac3a9fee6f51e2e020c0`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/kmeans/run:1–2`，SHA256 `acb8afec40f122dfc56685e27a44c38d5bd9384568f7faf337ffec44d3e1e0d9`。

候选输入身份：
- `1213f9ab49665a65b429c79e0511047e92524e5f9bf53cc706ab222af22634aa`；bundle `431ab220196ca6e43a41312060ae62801d7c45202d21b65df9a70902e712c070`；`/root/workspace/assets/traces/bundles/431ab220196ca6e43a41312060ae62801d7c45202d21b65df9a70902e712c070/tree/kernelslist.g`；commandlist SHA `7817f1fdac1aaff86b270b82d301999050ed8247f67f0a1f2637b03d51f48c59`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。
- `2315d0e612ee7cd4ee6e711e2a673e85d7490bec9a8767ec67bde3ddafff970a`；bundle `98f208255003482005dc87f9462bead5f13c94402e0c88c57b15f6bb542bbd12`；`/root/workspace/assets/traces/bundles/98f208255003482005dc87f9462bead5f13c94402e0c88c57b15f6bb542bbd12/tree/kernelslist.g`；commandlist SHA `313a57cb311e5ab4e38837844a10db3428ef68f84cea6f6750c64a343fc72dc5`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。
- `bd8f42c4d21e28ce7d2f6f458bae67720d5237ef8418b8581796d33e2c9d76e1`；bundle `f23950fed2246d97e43b80287872a473834abc632694ea5d6175e35b5334363a`；`/root/workspace/assets/traces/bundles/f23950fed2246d97e43b80287872a473834abc632694ea5d6175e35b5334363a/tree/kernelslist.g`；commandlist SHA `96ea17a1edb6f3c10a45ca36833cf1ecc0da085e0df0711748ecb505df18086e`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。
- `c7efba60561811c0652e5bb9331fc1f4c8265ef8a54b75ddc746319292817e76`；bundle `6adc60f1099f9c8936fbc6f0fcd2941bbcce9a245686fb0e9f1574cc615b7d07`；`/root/workspace/assets/traces/bundles/6adc60f1099f9c8936fbc6f0fcd2941bbcce9a245686fb0e9f1574cc615b7d07/tree/kernelslist.g`；commandlist SHA `c2d4d2544f725153fe4b3d9e0f66bc62da065ddb5b41bc3a4505e2c15a38cd1d`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。

### nn

状态：`UNRESOLVED_V1_UNCHANGED`；范围：`SOURCE_SCOPE_CONSISTENT_NOT_CAPTURE_CERTIFIED`。

- 3.1 packaged run matches filelist_4 -r 5 -lat 30 -lng 90 and emits one euclid GPU kernel after reading all records; -r selects the CPU-side top-N result count, not an euclid GPU argument.
- The 342112-byte HtoD coordinate buffer implies 42764 LatLong records under the 3.1 two-float layout. The 2.0-ft candidates instead use four 735000-byte character-record batches. Same filelist_4 spelling is not proof of the same files or records.
- 3.1 has a DTC_LEGACY_NN pointer to three historical cohorts under commit b2d6121e169dd0605d3e3c51cd010e7e77effd49. Their recorded status is checked terminal scope only until comparison complete, not approval of whole-app input identity for the 42-suite.
- Deployed nn_cuda.cu additionally has an emulation-only memory-size branch absent at pinned b059fdae; GPU kernel and host read/launch scope match in the inspected diff, but exact capture compile flags remain unknown.

建议：3.1 packaged run plus historical named reference provides the strongest provenance candidate, subject to dataset and source-version-policy closure.

仍缺：filelist bytes plus ordered constituent data files and capture-linked SHAs；Capture executable/build/tracer identity including emulation macro state；Explicit V2 version-policy adoption; historical terminal-scope receipts are not full-app certification。

源码位置：
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/nn/nn_cuda.cu:20–30`，SHA256 `f14cbe11c06073b37c61628ac9901db0f4aa00d866ba338d303113631d5dc103`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/nn/nn_cuda.cu:143–162`，SHA256 `f14cbe11c06073b37c61628ac9901db0f4aa00d866ba338d303113631d5dc103`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/nn/nn_cuda.cu:176–223`，SHA256 `f14cbe11c06073b37c61628ac9901db0f4aa00d866ba338d303113631d5dc103`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/nn/run:1–2`，SHA256 `b62906da469c51033305e3842ea521edd09da587dee57ea31b90e2f2b2f215ad`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/2.0-ft/nn/nn_cuda.cu:13–32`，SHA256 `146a6bbc0661b1f424de5aed693fd0279ecd539ace85cb02ecb4fa1ecc0f6fc1`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/2.0-ft/nn/nn_cuda.cu:147–208`，SHA256 `146a6bbc0661b1f424de5aed693fd0279ecd539ace85cb02ecb4fa1ecc0f6fc1`。

候选输入身份：
- `7530ee6952c967c574b81bbf6b2abe768d937e414eda9fe902711fd743972d8c`；bundle `ac131cadb7d95e3214041a0dde73a56a6c26c6beed51fa14cf204ace620a479d`；`/root/workspace/assets/traces/bundles/ac131cadb7d95e3214041a0dde73a56a6c26c6beed51fa14cf204ace620a479d/tree/kernelslist.g`；commandlist SHA `6fdec3a4a4aaf5970d9986a03ee5d2826907e683b3f169e8574c0ccf9537fb24`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。
- `8df9ee2d901953e7f4fee2732082bcfd80298003754feb6535340a9e621227cc`；bundle `f667b73231611a4692e3ad66628414a3db0763ad91e35e6fc0818bae15d0272c`；`/root/workspace/assets/traces/bundles/f667b73231611a4692e3ad66628414a3db0763ad91e35e6fc0818bae15d0272c/tree/kernelslist.g`；commandlist SHA `6b5e83e43dc74ae1b23312e1772d19a774b6c7397740c1bc1e0f572db77f8664`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。
- `fff1afd00c2eb305a08f67233cb21718f780bcddac2a81649087a270cf80bfbb`；bundle `574ca39f96bc0f20a14baf7fa55a4b6329402f579f2418fabd7c3ab94fad9310`；`/root/workspace/assets/traces/bundles/574ca39f96bc0f20a14baf7fa55a4b6329402f579f2418fabd7c3ab94fad9310/tree/kernelslist.g`；commandlist SHA `361295bf468986cf0b805a33ccc1ec9ca74d496fced32575e73d2c142743fb32`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。

### nw

状态：`UNRESOLVED_V1_UNCHANGED`；范围：`SOURCE_SCOPE_CONSISTENT_NOT_CAPTURE_CERTIFIED`。

- 3.1 packaged run specifies 2048 10. Source generates equal-length sequences using seed7 and accepts a single dimension and penalty; the README usage is stale and should not override the parser.
- With BLOCK_SIZE=16 the two wavefront loops emit 2*(2048/16)-1=255 launches, exactly the captured count. The 2.0-ft 128 case correspondingly emits15 launches.
- 2.0-ft kernel signatures include an additional output matrix pointer, so matching application name is not identical kernel implementation. Its two captures differ in format/body SHAs.

建议：Use 3.1 packaged run command if the V2 source-version policy is adopted. This is not a performance-based size choice.

仍缺：Capture executable/compiler/tracer linkage；Generated sequence content binding to generator and C-library behavior；Explicit V2 version policy; whole-app numerical correctness remains separate。

源码位置：
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/nw/needle.cu:83–109`，SHA256 `6152a04e5cd37a0c3f78efdc5cb4d8269bd10694840c23cb9b8345ac525962ee`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/nw/needle.cu:147–165`，SHA256 `6152a04e5cd37a0c3f78efdc5cb4d8269bd10694840c23cb9b8345ac525962ee`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/nw/needle.h:1–20`，SHA256 `38ffaf31b59432e204dff8b22e10ada572c18eae27abfd0a82ea3f08b178b180`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/nw/run:1–2`，SHA256 `6dc271b38f8453cb83bf4c301635e184bf8ad12e55dae7c268e1add6a30b6d34`。

候选输入身份：
- `2982f1db6fe849710e62f66ae7c4cdf45f0143a403df440e66110bf40dc1344d`；bundle `18f1dd467edc0ac092a0d81f567cba0a997191d96dd28cc1af9a770d1855855c`；`/root/workspace/assets/traces/bundles/18f1dd467edc0ac092a0d81f567cba0a997191d96dd28cc1af9a770d1855855c/tree/kernelslist.g`；commandlist SHA `c26635d0ada3b828fb330c48b1a2dcae599fc739f8eb90ecc639e3df4b039672`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。
- `cf569ed4fa54b5f11746ce6c0c44e43807ac9d0164e21e4900b5bdb61377e8c7`；bundle `09ef98199caae61f5db044fcdfe6687a2d07efd91299e33b9eafe17f439aae79`；`/root/workspace/assets/traces/bundles/09ef98199caae61f5db044fcdfe6687a2d07efd91299e33b9eafe17f439aae79/tree/kernelslist.g`；commandlist SHA `213b4d922272ba7ae3dbf78eebd5066a2da0a2bc556aeeb8ef9bee2b9a809bfe`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。
- `ec1461f2c83fe1bd4d0ca8aefecc4874db6f1c8621ae8b5365003666842c717f`；bundle `74047d288da44737d1b7733b9f6a4e4a3076e7ad63108b165705fb899e9b6cb4`；`/root/workspace/assets/traces/bundles/74047d288da44737d1b7733b9f6a4e4a3076e7ad63108b165705fb899e9b6cb4/tree/kernelslist.g`；commandlist SHA `05e27a956b7d6ff3dc1b7be8ea09d1c7031bc158f20b4c5c451fdf7a4f5bff0a`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。

### pathfinder

状态：`UNRESOLVED_V1_UNCHANGED`；范围：`SOURCE_SCOPE_CONSISTENT_NOT_CAPTURE_CERTIFIED`。

- Parser binds argv1=cols, argv2=rows and argv3=pyramid_height; the packaged run is 100000 100 20 > result.txt. The output redirection is not a fourth application argument.
- Source seed is9. Source loop ceil((rows-1)/height) predicts5 launches for 100000x100,height20 and4 for1000x20,height5, agreeing with the trace commandlists.
- The two same-argument 2.0-ft captures differ in trace-format identity and member SHAs; no duplicate elimination by program name or outcome is justified.

建议：Use the 3.1 packaged run if the V2 source-version policy is adopted; retain output redirection as shell semantics.

仍缺：Capture executable/compiler/tracer binding；Capture-time generated wall contents or exact generator/runtime binding；Explicit V2 source-version precedence。

源码位置：
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/pathfinder/pathfinder.cu:19–65`，SHA256 `c37fccc0b23cb385ad03a3f5cb242df3d6b433ea5e5a8c48f4a620bb04fbb0a6`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/pathfinder/pathfinder.cu:188–204`，SHA256 `c37fccc0b23cb385ad03a3f5cb242df3d6b433ea5e5a8c48f4a620bb04fbb0a6`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/pathfinder/run:1–2`，SHA256 `66c7c740102940c2ed376b30fed351a41709ff1c379cc97b379cb4587f4bb777`。

候选输入身份：
- `030e87a45e9c6dae2c164392ab7dbbf9ea8511802f04258628b5d0830ebd5e67`；bundle `47dd66b3aeb256c6623a03b6b2c7892d2f48af507ddc2bebead7b7ac8ca4d86d`；`/root/workspace/assets/traces/bundles/47dd66b3aeb256c6623a03b6b2c7892d2f48af507ddc2bebead7b7ac8ca4d86d/tree/kernelslist.g`；commandlist SHA `219367024ddaa7d8ce6853e8f802f6d44debec3c63e3708a638d280db2c273bc`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。
- `6811f98b1edd34f6ea0496797625a38322fc6125f92e94572555366aaa7418d8`；bundle `d51caaa5915b36e02da65db92d34833dcede91cd0998a41b7b565be34d36af82`；`/root/workspace/assets/traces/bundles/d51caaa5915b36e02da65db92d34833dcede91cd0998a41b7b565be34d36af82/tree/kernelslist.g`；commandlist SHA `c00c2b6c1b306b501bc7e862743e27c9942beab6caeac022da3466b9d586f2c6`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。
- `ccdd1b98bff6187e23c60ac1b37e6358cd83539010530d6c13dfe7595bb0a228`；bundle `dd2b687e905f3f0f90ed47a356c5a1e57710032e2e2f3f5a7a4ac58f8e7f7364`；`/root/workspace/assets/traces/bundles/dd2b687e905f3f0f90ed47a356c5a1e57710032e2e2f3f5a7a4ac58f8e7f7364/tree/kernelslist.g`；commandlist SHA `22daac544948ce42c7bd9e5287b3a48effb3f148a0389feb447b277c9ff84f3c`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。

### streamcluster

状态：`UNRESOLVED_V1_UNCHANGED`；范围：`STANDARD_FULL_APPLICATION_SCOPE_CONTRADICTION`。

- 3.1 packaged run is 10 20 256 65536 65536 1000 none output.txt 1. For positive n, source generates coordinates with SimStream seeded by srand48(1); none is not an external dataset filename in this case.
- The 3/6/16 candidate adds an extra output.txt argument. The inspected 3.1 parser accepts argc>=10 and reads only argv1..9, so the trailing argument is ignored under this source; it does not restore a goldfile check.
- The CPU pFL path uses ITER=3 and emits floor(3*kmax*ln(kmax)) pgain calls in every entered sweep; each pgain unconditionally launches one kernel_compute_cost. This is32 calls for kmax6 or179 calls for kmax20. Five captured kernels cannot be a complete sweep under the inspected standard source.
- Both candidates have exactly five complete kernels. Their missing HtoD entries also cannot certify host initialization. Capture binary/ROI or early termination must explain this before whole-application use.

建议：The 10/20/256 tuple matches the packaged command, but do not freeze a five-kernel capture as complete streamcluster. Resolve the source/capture scope mismatch before a V2 identity decision.

仍缺：Capture binary/source/compile flags and tracer kernel-window rules；Capture completion/host convergence log and complete launch range；Generated coordinate content/runtime binding; explicit parameter-policy decision。

源码位置：
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/streamcluster/streamcluster_cuda_cpu.cpp:20–23`，SHA256 `3e8a435af2552220fe143e2d8ad9c7efdad2c1a3927e08c3e79253e198631030`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/streamcluster/streamcluster_cuda_cpu.cpp:329–348`，SHA256 `3e8a435af2552220fe143e2d8ad9c7efdad2c1a3927e08c3e79253e198631030`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/streamcluster/streamcluster_cuda_cpu.cpp:565–585`，SHA256 `3e8a435af2552220fe143e2d8ad9c7efdad2c1a3927e08c3e79253e198631030`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/streamcluster/streamcluster_cuda_cpu.cpp:887–903`，SHA256 `3e8a435af2552220fe143e2d8ad9c7efdad2c1a3927e08c3e79253e198631030`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/streamcluster/streamcluster_cuda.cu:132–174`，SHA256 `a2eff9aaa34e08ae48d2f6d3fd37683f90c14834af53b53831688a6f806c835c`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/streamcluster/streamcluster_cuda.cu:239–257`，SHA256 `a2eff9aaa34e08ae48d2f6d3fd37683f90c14834af53b53831688a6f806c835c`。
- `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/streamcluster/run:1–2`，SHA256 `2d14bba219a40bb21c883222be02d0548d56c2c81a10bb28d869276df6469dae`。

候选输入身份：
- `322bdf9f1830fad4464c03da9c2367fa7c1b74ffbc72098673bec76529c7bc7e`；bundle `752bee55fbc52e3eab9ac97482d0d58f8d3ddbaa4cd41169c61deb81f13c5ed9`；`/root/workspace/assets/traces/bundles/752bee55fbc52e3eab9ac97482d0d58f8d3ddbaa4cd41169c61deb81f13c5ed9/tree/kernelslist.g`；commandlist SHA `ce71e70525c6299a6be1bae3790b0eeb0417e1f4608cbd10e706c0a14fdd6b46`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。
- `f7d6397ed7ffa266724e124e76e896015cd71a9936a43e787d815c3c8420f348`；bundle `86ff95b9eb7f8d0924e19abfb7ab21bf417a669bc360ad10efa4b47b14d4b3d3`；`/root/workspace/assets/traces/bundles/86ff95b9eb7f8d0924e19abfb7ab21bf417a669bc360ad10efa4b47b14d4b3d3/tree/kernelslist.g`；commandlist SHA `ce71e70525c6299a6be1bae3790b0eeb0417e1f4608cbd10e706c0a14fdd6b46`。完整 capture run.sh 原文/SHA、成员 SHA、kernel 范围见 `INPUT_IDENTITY_CATALOG.json` 对应 input_digest。

## 来源核验与未解决边界

- 基准审阅 commit：`71584878be0c80375f9d25bcd80e171b7bf4478d`，目录 `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/`。
- 当前164冻结文件 `/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_paper42_hash_review_20261027_v1/analysis/REPRESENTATIVE_FREEZE.json` 的 SHA256 仍为 `a4157b56b48d8d8df048b9f64e62d54b091e80176d7a05169ef9c64b0c06da9d`；local副本一致。
- 固定上游源码：`accel-sim/gpu-app-collection@b059fdae25c2aabf737486aada743fca114469ce`；18份文件独立读取，16份与部署字节相同；另外2份为 CFD 的错误检查包装修改和 NN 的 emulation-only 内存分支。逐文件 URL、SHA、diff 见 `UPSTREAM_SOURCE_VERIFICATION.json`。
- 112份小源码/命令文件约765KB；无仓库 Git 元数据，不能把部署目录整体冒充一个已验证 commit。已读具体文件均保留路径、SHA与内容；未比较的文件不宣称等价。
- `get_data.sh` 指向的数据目录在本机指定位置不存在，5个官方2.0-ft capture目录的 data symlink均为历史服务器绝对路径且当前失效。这只是有界路径核查，不宣称数据在所有服务器上不存在；也没有下载、重构或重新采集输入。
- 历史 M5 E1 表记载 097K candidate mesh SHA `43534e58454ba8baf95253e14d3b07150b9960577e922a954d6e51142a27abfa`，但其 executable/PTX/完整 capture 仍未绑定，故不用于绕过 CFD 范围阻断。
- 每份 trace 的已声明 grid/warp 完整性与应用全部 host 迭代完整性是不同层次。已有 accepted、负例、修复、HOLD 身份均不作替换；本报告没有重新计算性能。

## 后续最小动作

1. 只读恢复 CFD、streamcluster 的捕获二进制/源码/启动环境与 kernel 窗口参数，首先解释为何恰为5个kernel。
2. 只读定位已有 kmeans/NN 原始数据及 manifest、收敛与捕获退出日志，按输入SHA和有序文件清单绑定，不用文件名替代内容。
3. 审阅 V2 的“Rodinia3.1发布run优先于2.0-ft功能回归”统一身份规则；若采纳，backprop/NW/pathfinder/NN已有命令与范围依据。CFD、streamcluster仍不得因此晋升。
4. 只有现有证据无法闭合时，另行提出 `NEW_SCIENTIFIC_EXECUTION_APPROVAL_REQUIRED` 的捕获完整性验证合同；本轮不执行。

分析代码 `build_identity_report.py` 只消费已有身份/源码/commandlist证据，不加载 PERFORMANCE.json、cycles、模拟耗时或strict结果来选择代表。
