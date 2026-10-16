# Source comparison and support differences

Evidence labels: VERIFIED_CODE for pinned source, VERIFIED_RUN for host-only probes/offline disassembly, UNKNOWN where the trace does not carry the needed state. A previous platform qualification is not transferred to DTC.

## Anchors and existing assets

| Artifact | Immutable source | Observed behavior | Reusable scope / unresolved boundary |
|---|---|---|---|
| DTC frozen frontend | Framework18a68dcccd795f1b6cda75504e9450d00c9cee02 | trace_driven.cc:199?216 recognizes80/86/90 and older versions, not89; unsupported calls exit(0) | Actual parser and classifier inspection; unsupported is rejection, regardless of process exit |
| AWMA cross-calibration |6f9c1df1a03bd9d26130b80be1c31f5957074630 | explicit environment gate admits89 to Ampere_OpcodeMap | Recorded opt-in prototype, not an Ada ISA/timing proof |
| AWMA Ada-named candidate |aeec5b9a69865012b16ac0a6627143e29f1fee06 | defines ADA_RTX_BINART_VERSION89; removes environment gate; same Ampere_OpcodeMap | Config/source artifact only; adding a symbolic name does not change categories, register conversion or memory semantics |
| C16 namespace integration |2fa207fbc37a48f12641d810319b03ba1cf4e381 | literal89 maps to Ampere_OpcodeMap; full4515-kernel audit covers65 roots and154 spellings; three address-integration canaries | Address propagation/observation and audit methods reusable; pack explicitly excludes full Ada timing fidelity |
| Local source inventory |194 worktrees /5 distinct trace_driven.cc byte variants | All representative files match recorded Git sources; SM89 variants above remain aliases | Bounded existing-asset search; no separate Ada semantic table found in inspected variants, not a claim about every external implementation |
| RTX4080 platform config |AWMA candidate's SM89_RTX4080_AWMA_V1 trace.config | int2/2,SP2/1,DP64/64,SFU21/8,tensor32/32; branch4/4,uniform4/1 | Inherited declared model parameters. Config name/native4080 operation do not establish calibration for this SpMV |
| Native SpMV |producer890fb0be; consumer e3dbe3db | source/binary/input/trace SHA closed, actual cubin89; canonical canary failed before instructions | Native measurements valid; small36-CTA/warm0-DRAM scope unchanged; no direct simulated benefit |

SOURCE_ARTIFACTS.json records exact source blobs, SHA256, lines and local representative heads. FROZEN_CPU_SOURCE_IDENTITIES.json records every compiled parser/header input. No adapter code was cherry-picked. A whole older C16 file would also remove unrelated frozen frontend functionality; no wholesale transplant is proposed.

## Instruction names versus semantic support

NVIDIA's [archived CUDA Binary Utilities13.1 instruction reference](https://docs.nvidia.com/cuda/archive/13.1.0/cuda-binary-utilities/index.html#nvidia-ampere-gpu-and-ada-instruction-set) groups Ampere/Ada mnemonic families and distinguishes vector, uniform, predicate and constant operands. This supports terminology and root membership, not cycle equality, an89?86 dispatcher, or full modifier/dependency correctness. The [Ada compatibility guide12.8](https://docs.nvidia.com/cuda/archive/12.8.1/ada-compatibility-guide/index.html) makes cubin compatibility directional:86 can run on89, whereas89 is not supported on86. No new tool was installed to read these documents.

All23 SpMV spellings are retained separately. Full spelling overlap with the previous C16 audit is22/23; FFMA.FTZ was absent there. Even full spelling overlap does not show data width, paired outputs, constant addresses, predicates, barriers or latency are modeled correctly. OPCODE_COVERAGE.tsv separates observed fields, frozen enum/category, unresolved interpretation and timing-source role.

## What the immutable dynamic trace determines

The PC order, active masks, kernel/CTA/warp scope and global load/store lane addresses are already captured. No arithmetic result, branch target or predicate truth needs to be re-executed to rediscover the observed path. Signed immediates are parsed as the frozen uint64_t bit pattern (e.g.?3?2^64?3); this is recorded storage behavior, not a trace edit.

The simulator still interprets register readiness, instruction category/issue resources, operand/memory width, memory space/cache path, completion, and barrier/reconvergence service. Trace-driven PC/mask consumption does not make these costs or dependencies free. Frozen get_pdom_stack_top_info treats control hazards as already resolved and get_active_mask reads recorded masks; BRA/BSSY/BSYNC are assigned specialized branch-unit service. These are model contracts to review, not reconstructed native barrier state. No CTA BAR instruction occurs in this input; BSSY/BSYNC are convergence operations and are not mislabeled CTA barriers.

## Concrete information gaps beyond dispatcher89

1. **Paired constant-load destination.** Original SASS PCs0x310 and0x320 write LDC.64 to R16/R2; offline nvdisasm marks both consecutive GPRs written. Immutable records declare just R16/R2. PCs0x360/0x410 later read R17/R3. The frozen frontend copies recorded destinations unchanged (`outcount=reg_dsts_num`) and has no LDC.64 expansion;64 actual dynamic instances exhibit this missing producer edge. The diagnostic does not modify or synthesize a destination. Later Core repair cannot be assumed from this frontend evidence.
2. **Constant data/address path.** All LDC/LDC.64/ULDC.64 records have memory-width0 and no memory-address object. The frozen decoder's OP_LDC case forces data_size4 for both LDC and LDC.64, despite the static64-bit form. Thus byte width and address traffic are not established by successful parsing. The original producer ignores constant operands; constant-address reconstruction is outside this task.
3. **Uniform/predicate operands.** ULDC.64 UR4/UR5 and ISETP predicate destinations appear in original disassembly but are omitted from producer records. The frozen register converter only maps regular REG to num+1; other typed operands become0. CPU synthetic typed probes confirm that behavior. Dynamic masks fix which lanes execute; they do not restore predicate/uniform scoreboard edges.
4. **Wide address arithmetic.** IMAD.WIDE outputs and LDG.E/STG.E64-bit address bases are captured as base GPRs; constant address terms and uniform descriptor dependencies are not fully explicit. Recorded lane addresses are adequate to identify observed requests, while complete producer/consumer readiness remains a separate contract.
5. **Timing and modifiers.** Existing root category selection and config latencies are available source facts. They do not validate the resource treatment of .WIDE/.MOV.U32/.IADD/.FTZ/.LUT or Ada service timing. CPU classification/grammar checks supply no cycle calibration. No timing table is imported into mainline.

These gaps do not invalidate producer-native numerics or the consumer's format audit. They prevent treating a tiny dispatcher patch as complete scientific admission. No original12 cohort or other project's acceptance is reopened; this is a new SpMV support feasibility finding.
