# 109-DTC-L1 首次历史资产只读接手

接手固定基线：`768aa1142cd07ee0829a0808abb0b2ff7847e7c1`。109 观察：`2026-11-09T13:11:09.817847+00:00` 至 `2026-11-09T13:12:33.237949+00:00` UTC，`PC` / `huangrulin` / `/home/huangrulin`。本窗口负责 109 历史 native/profile/capture 资产和来源维护；唯一 Main 为“DTC-L1交接-1”。

## 实际范围和结果

固定调查包 manifest 的 11/11 成员 bytes、SHA256、Git blob 均吻合；规定的 Main 接受、producer、consumer、SM89 与指定归档回执已按固定提交读取。仅经既有 SSH 入口在两处 DTC worktree、两处专属 root 及明确共享依赖上做一次只读核验。两处 root 分别有 586、48 个文件；扫描未触及上限，未跟随 symlink 跨出 root。`findmnt -T` 对两个 root 均指向 109 本地 `/` ext4 `/dev/nvme0n1p2`。未检查 GPU 锁、活动控制面或 174/164 现场。

| 历史入口 | 今日观察 | 身份与未提交状态 |
|---|---|---|
| `/home/huangrulin/workspace/worktrees/accel-sim-dtc-native-coverage-109-v1` | PRESENT_METADATA_ONLY | HEAD `890fb0be7e681a60419c49ca0a7aa85731d8c164`，历史分支，`git status --porcelain` 含 untracked 检查为空 |
| `/data/c16/dtc_native_coverage_109_v1` | PRESENT_METADATA_ONLY | 586 文件、79 目录；native 指定成员 285/285 路径和大小相符 |
| `/home/huangrulin/workspace/worktrees/accel-sim-dtc-sm89-admission-109-v1` | PRESENT_METADATA_ONLY | HEAD `d58e75ce32845a281692f19aeb4057b4c9822a3f`，历史分支，`git status --porcelain` 含 untracked 检查为空 |
| `/data/c16/dtc_sm89_admission_feasibility_109_v1` | PRESENT_METADATA_ONLY | 48 文件、4 目录；CPU 指定成员 45/45 路径和大小相符 |

映射逐成员见 `METADATA_MEMBER_MAP.json`。全部 330 个索引成员为 **METADATA_MATCH**，无旧路径缺失或大小不符；没有读取、重 hash、解压任何 payload。109 当前 `PAYLOAD_FILES.json` 与固定 native 索引的小文件 SHA 同为 `8b6f25483a78af6b8b13571b2656793e48e04acaa1593e6809e63f0ebe51bf5e`；CPU `RAW_LOG_INDEX.json` 同为 `6cfc9205bd197e362f76c8ccabf82b752e404f60ead0ce43be839a59db83d7d7`。`PAYLOAD_FILES.json` 是索引，不是第 286 个 payload；174 首次误算与后续更正仍按固定 consumer 回执保留。

## 归档范围与额外文件

native 历史指定 285 成员包在 2026-10-16 的 164 目的端逐成员 SHA 验收 PASS。109 本地同名归档今日可见，大小 85,512,354B；164 上的 `/root/share/mnt164/...` 是 174-new/root namespace，本轮未跨跳，状态 **REFERENCED_NOT_RECHECKED**。当前本地归档仅大小吻合，不能宣称与164内容相同或今日 SHA PASS。2026-11-04 **整树 TARGET_UNVERIFIED** 仍有效；两种范围不能相减计算未归档字节或据此清理。

native 另有 301 个未列入指定 285 成员的文件：INDEX_OR_RECEIPT 5, LAYERNORM_MATERIALIZED_INPUT 2, LOCAL_ARCHIVE_OR_GIT_CLOSEOUT 2, PARBOIL_GIT_METADATA_OR_OBJECT 99, PARBOIL_UPSTREAM_SOURCE_OR_INPUT 182, SPMV_BUILD_SOURCE_OR_OUTPUT 11。其中 Parboil 本地 `.git` 对象/元数据、上游源码/输入和 SpMV 构建物、LayerNorm materialized 输入，均需保留原身份；另有本地归档、索引和回执。`METADATA_MEMBER_MAP.json` 逐路径列出，不把“额外”解释为可删或可再生。未找到覆盖这些额外文件的整树 true164 成员映射/恢复回执。

CPU 小归档在 109 今日可见，大小 576,292B；历史 45 成员仅有本地 archive/逐成员验收。root 另有 3 个非索引文件（INDEX_OR_RECEIPT 2, LOCAL_ARCHIVE_OR_GIT_CLOSEOUT 1）。本轮专属 root 中未发现后续 true164 持久化回执，状态保持 **UNKNOWN_NO_EVIDENCE_IN_INSPECTED_SCOPE**。

## 科学和共享依赖边界

SpMV small1138_bus 的 4 个 producer capture 目录、LayerNorm1024 的 6 个 capture 目录及失败尝试目录均今日可见；只查目录/文件元数据。producer 格式 PASS 与历史 native 有效不改变 174 的 SpMV `unsupported binary version: 89` / NOT_ADMITTED 或后续 109 CPU `NO_GO_FOR_DROP_IN_SM89_ADMISSION / HOLD`。LayerNorm 的实际 cubin86、跳过 `CALL.REL.NOINC` 仍 NOT_ADMITTED；8192 敏感性输入仍仅 native/profile、未 capture。109 RTX4080 谱系不能补作 SM70 CORE32 的统一 producer。

共享 `/data/c16/env/c16-py310`、历史 AWMA tracer `.so`、`/usr/local/cuda-12.8/bin/nvdisasm` 今日可见，只核 metadata，未激活或运行。当前 PyTorch/NCU/driver 版本未执行再验证；历史版本与新环境资格不混称。早期 M5 V100/medium SpMV 是外部 producer，不归属 109 small 输入。

## 未决项与停止

1. native 指定包的 164 今日可见性及本地归档与该目的端的当前字节同一性未核；若未来需要，须有明确跨节点/完整性任务。
2. native 整树额外 301 文件缺完整 true164 成员映射与恢复证明；当前不具备清理依据。
3. CPU 小归档是否存在已验证持久化副本，在本次专属 root 与固定回执中仍未知。
4. 今日共享工具版本与任何未来 SM89/LayerNorm 准入仍须另立科学合同；既有 HOLD 保持。

本轮新 native、profile、capture、模拟、request、预算、GPU 锁和历史来源修改均为 0。完成文档回传后 `STOP_PENDING_EXPLICIT_TASK`。
