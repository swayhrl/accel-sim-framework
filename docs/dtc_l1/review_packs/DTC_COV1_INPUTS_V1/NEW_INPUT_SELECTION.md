# Fixed bounded new-input selection

Status: PREPARED_NOT_TESTED. Selection fixed in source/access publication `2cba9b193b091db8dd4550c4c3120b1d82d57ec6`, before new candidate or new-input performance. No N simulation results were read. Each class considered no more than three assets. No all-disk search, body scan or producer task was launched.

## N1: more SM concurrency

The old primary BICG has only 16 CTAs per kernel. Candidate 1, the already captured source-backed M5 BICG4096-square, also has 16 per kernel and fails the256-CTA target. Candidate 2, the same pinned source with NX=4096, NY=65281, is selected as an uncaptured native recipe: ceil(65281/256)=256 for kernel1, ceil(4096/256)=16 for kernel2. This is the smallest enlarged NY at unchanged NX and native256-thread block yielding256 CTAs, and deliberately retains the second kernel's low parallelism. It is not256 CTAs in every kernel. Matrix A occupies1,069,563,904 bytes; maximum signed32 element index267,390,975 remains safe. No CTA replication or address relocation. No third candidate needed; ATAX fallback not selected.

Freeze `sgrauerg/polybenchGpu@5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c`, `CUDA/BICG/bicg.{cu,cuh}`. The original header tests macro N before dataset definitions; use `-DN=1 -DNX=4096 -DNY=65281`, retaining FP32, algorithm, init, two kernels and block256×1. Native command is the binary without arguments; require exactly one source comparison with zero mismatches at its0.5% threshold and retain full s/q output reference. Existing canonical4096 capture is a separate lineage, not an enlarged payload. State BLOCKED_CAPTURE. A compatible authorized SM70 capture node and actual environment/producer/resource plan are still required; no109 task or node connection is assumed.

## N2: exceed L2 residency of a real reused operand

Candidate 1, pinned PolyBench/GPU GEMM default512 cube, has only1MiB B and fails20MiB. Candidate 2, same naive FP32 source2290 cube, is fixed provisionally: B is4×2290²=20,976,400 bytes, exceeding2×10MiB=20,971,520;2289 square is20,958,084 bytes and fails. This is the smallest square integer size satisfying the chosen single reused-B criterion. A/B/C total bytes are not used as the residency proof. B is read repeatedly across output rows in the source; actual DRAM traffic may remain small and must be retained without a size search. No third candidate is needed.

Freeze the same PolyBench commit, `CUDA/GEMM/gemm.{cu,cuh}`, `-DN=1 -DNI=2290 -DNJ=2290 -DNK=2290`; square shape avoids transposed grid extents in this historical wrapper. Block32×8, expected grid72×287=20,664 CTAs, edge predication intact, one full kernel. Retain source CPU comparison0.05%, all output C and actual compiled SASS. However, original main GEMM's source/build is unbound in accepted A/T evidence. This is BLOCKED_SOURCE_BINDING_AND_CAPTURE until the coordinator can demonstrate unchanged algorithm/precision/access implementation relative to the intended old source; it cannot silently substitute a wrapper or Tensor-Core implementation. No fake scale result follows from the fixed recipe.

## N3: irregular source-backed indexed reads

Candidate 1, already captured SM70/V100 Parboil medium bcsstk18 JDS SpMV, is selected under the plan's gather alternative: the actual kernel issues `x_vec[d_index[j]]`. It is explicitly JDS indexed gather, not CSR. Source and input identities,50 original kernel invocations, reference output and archive are documented in entry commit46df826's `M5_0BT_SPMV_CAPTURE_CLOSEOUT.md`; local metadata confirms374 CTAs per invocation. Candidate 2,109 SM89 Parboil1138_bus, is rejected by existing NOT_ADMITTED ISA qualification; no alias or revival. A third input is unnecessary.

Use exact existing capture bundle `d8790ea7279aa79345650ffaafc61835187d8b1e6c4b10a6e6e2cc24891db270`; archive SHA `5d7d92ca08d6a3c2b8f5e4b7085428dcaa1ec5bdae330816132113eefb3f0852`; matrix SHA `abbe1909f57d6fc17fc800446bac326bd0c5343305cf193b3aa1bc8f40c82ec9`, vector SHA `d155de2b9615cae3c2bb8b60a9e82a7d26be7e80de772a5f1c0cb830d2e49061`, output SHA `69314cf6c1796cf8e0f93fe143e1dd5a96685ec6eaead46eeaf03f6c00c4c4f1`. No seed is applicable to these immutable file inputs. Source wrapper de9cf4293f418877aa9cdb6a2395338ca06674a6 and Parboil4e0fc54866546efa44fe93af57c9cef62f6c8eb9; CUDA11.8 sm70 -O2 shared cudart, NVBit1.8. Input command `spmv -i bcsstk18.mtx,vector.bin -o result.bin` is historical recipe, not executed here. Preserve all50 captured launches, HtoD and initialization; do not relabel a prefix as the app.

State CAPTURE_EXISTS_WAIT_AG4_TERMINAL_AUTHORITY_FOR_CURRENT_REPLAY_QUALIFICATION. Existing M5 replay evidence uses different scientific source/options and is not a new production comparison. Current decoder and full member/instruction/CTA access qualification remain unexecuted; no startup or budget is charged. Local metadata is an access pointer, not a fresh payload SHA check.

## Native producer and CPU window

After terminal authority and role registration, use one bounded two-hour COV1 CPU window for metadata/format qualification and reference checks. Reuse A's complete body audit; if an additional body scan is essential, one coordinator-owned stream per fixed input writes a shared address/type index with unknown alias preserved. No repeated hash of unchanged huge payload. Fix actual tools, executable identities, options, original initial state and producer resources before any input capture or simulator family. No N point can run before F, SEM1 support scope, executable preregistration, full-input qualification and coordinator budget admission are published.

Bounded inventory accounting: the separately inspected `gpgpu-workloads@de9cf4293f418877aa9cdb6a2395338ca06674a6` tiny wrapper GEMM64 cube is N2's third source candidate and is rejected for insufficient single-B footprint and unbound wrapper/source equivalence. ATAX was inspected only as N1's third fallback source; it is not selected because the preferred rectangular BICG recipe meets the stated at-least-one-kernel target without changing its native block. No additional candidate search remains pending.

Post-terminal execution update: only the tiny independent BICG/GEMM/sparse
reference examples and expected invalid-index rejection ran once, under
coordinator role d9750bd8fc4a3d4ee2bb620f03c44eb7a4a2277d;4/4 PASS. The fixed
full source/native recipes above remain unexecuted, N1/N2 captures absent and
N3 full-input/decoder qualification pending the unchanged10GiB heavy-input
resource gate. No selected source, dimension, matrix, seed or scope changed.
