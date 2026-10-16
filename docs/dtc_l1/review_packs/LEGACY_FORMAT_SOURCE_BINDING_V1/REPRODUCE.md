# 有界CPU-only复核步骤

本说明复核本轮来源证据，不重新执行Hotspot V2、65成员格式遍历或629成员body auditor。使用新的独立输出目录；所有操作只读原输入，没有模拟器或GPU命令。

1. 用 `git show 5248a5ed482156450a3baa2799f26ebae02e1d93:<原授权路径>` 核两份授权快照SHA。原授权路径、完整文件SHA及远端祖先检查见AUTHORIZATION_READ_RECEIPT.json。
2. 源码资产可由ARCHIVE_ASSET_RECEIPT.json中的外层tar绝对offset/bytes直接seek读取并验证SHA，不需解压大trace子包。LUD源码还可以从本地历史GPU-app-collection clone取出：

```bash
git -C /tmp/accelsim-gpu-app-collection-seed show 40e0052cebd3f98006190ed09e78f4981ef1a41b:src/cuda/rodinia/3.1/cuda/lud/cuda/lud_kernel.cu
```

需要的LUD源码SHA为 `fe3d0a5f06c82947f54cbf6fd9a75342b61263808a1587ead929fc3f8763fdc0`。本地已验证副本在 `/workspace/dtc-hotspot-format-174-v1/source-binding-v1/assets/2cee2235be76-lud_kernel.cu`。

3. 已有独立archive Git对象库可直接复核，不必再次复制pack：

```bash
git --git-dir=/workspace/dtc-hotspot-format-174-v1/source-binding-v1/archive-git show 9cdd82aae3f95eaba78a9b01cfb5880f8f4f93ee:util/tracer_nvbit/tracer_tool/tracer_tool.cu
```

该blob的Git SHA是 `d8028fee05e288aa1d76ec6833d647a5b908691c`，SHA256是 `61955513bd801178565851fceebef89a489e118df40c4861c34b7366716b7e31`；version3、打印P、编码E的源码位置由PRODUCER_SOURCE_LOCATIONS.tsv绑定。若对象库不再存在，ARCHIVE_GIT_PACK_HEADERS.json及ARCHIVED_GIT_SOURCE_PROOF.json给出pack/index和9个loose objects在外层tar内的偏移/尺寸；只在私有bare repo恢复这些对象，不改现有Framework仓库。没有必要复核所有Git对象或读取完整40GB归档的payload。

4. 复用原风险index，稀疏复核Btree与LUD global证据：

```bash
python3 util/dtc_l1/legacy_format_binding_evidence_v1.py --prior-receipt docs/dtc_l1/review_packs/LEGACY_FORMAT_SCIENTIFIC_RISKS_V1/RISK_DETAIL_RECEIPT.json --inventory docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/r0/PAYLOAD_MEMBERS.tsv --lud-source /workspace/dtc-hotspot-format-174-v1/source-binding-v1/assets/2cee2235be76-lud_kernel.cu --output-dir /workspace/dtc-hotspot-format-174-v1/reproduce-binding-index-proof
```

输出目录必须不存在。要求index的104476行及压缩/解压SHA、6000条Btree full32、5792条合同条件差异、19840条LUD global源码模型匹配（11904 load、7936 store）、40个首次标签和19800条后续检查全部一致。该工具不读取其他原trace记录、不执行规范化，也不把模型PASS转为SOURCE_BINDING_PASS。首样本PC标签拟合与未绑定宏/编译物的模型假设在receipt中明示。

5. Btree现成候选可用cuobjdump11.8 `--dump-sass` 读取三个独立输出资产；它不是执行ELF。PRECOMPILED_CANDIDATES.json提供45MB validation.tgz的外层offset/size/SHA及3个内部ELF成员名/SHA，BTREE_PRECOMPILED_COMPARISON.json提供SASS SHA与sm70/function/PC过滤后的原始行。必须限定sm70 `findRangeK`，不要误用sm75同PC的不同指令。原观测为PC1c40/LDG.E.SYS，候选为PC1c40/BRA，故拒绝适用。

复核应产生相同证据与UNRESOLVED结论；它不是新输入准入流程，不能启动Lane A实验、改写原terminal PASS或释放HOLD。
