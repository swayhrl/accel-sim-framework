# Lane AC OPT-COLLECT pipeline V1

2026-10-18, original `huangrulin-174`, root. **IMPLEMENTED_DEFAULT_OFF;
PASS_CPU_REAL_LDST_PIPELINE_SCOPE_ONLY; READY_FOR_INDEPENDENT_LANE_AG_REVIEW.**
Full GPU/ISA/value/coherence integration is PARTIAL/UNTESTED. No independent AG
acceptance, application performance, native or hardware/PPA PASS is asserted.
Full/canary/native-workload/GPU starts and old-lock acquisitions are all **0**.

## Released identity and concrete behavior

Core: **83aca449135703c176cfab29ae43e1245d00a557**, branch
`hrl/iscas2027-dtc-lane-ac-collect-pipeline-core-174-v1`.
Input X2 Core e32afdcf44be3374ff36d22568ed01a075459b6f was fetched exactly;
its direct parent is c0a5e2c31e407c57e3a4af3ce529c921e8059a05. AC started
from that e32 HEAD, not another Lane's new work.
Framework review branch: `hrl/iscas2027-dtc-lane-ac-collect-pipeline-174-v1`,
started at631eb6418f6e7f1f548afd33351cbc0d98d27145. Executed qualification-tool
source is ab1930efc4135f0d6a4fcc4b81f48303bc4b87a4; later documentation/publication
SHAs are recorded separately. No Framework trace executable was built or run.

Independent OPT_BOOL `-gpgpu_dtc_l1_collect_wb_pipeline` defaults0. ON is
fail-closed outside PAPER_OO+finiteV1+ordinary L1D. One collecting owner and one
waiting-WB slot can overlap; original4x32B collection and1-retire absolute-cycle
quotas remain. Old WB arbitration/RFU denial and original sidecar priority stay.
Data collection uses original ready_cycle and collect(); WB still requires
cycle>collect_done_cycle. A denied WB keeps its result/Refs and retries later.
A finished collector behind a full result slot backpressures all new collectors.

All instruction/PIB/reference descriptors, physical identities/generations,
waiter/inflight/return owners and completion ledgers retain their original
lifetimes. Collection and bank transfer release no Ref. Original retirement
releases only after successful WB. Full admission and same-warp PROXY_FENCE
blocking remain. Noncacheable observations do not repeat architectural effects.
K1 sources, linearization, ordinary pending commit, atomic zero-added simulated
cycle assumption and normal cumulative export contract remain byte unchanged.
No Tag/physical/PIB capacity, frequency/clock, lower cap, trace or finite port is
retuned. AA5/X2/other Lane source, raw, worktrees, locks and original evidence
were not modified, and no historical result is relabeled.

## Explicit cost

Two raw-sector data banks are modeled and charged, each bounded by the original
physical-pool byte bound. At640 lines: **80KiB/bank,160KiB additional data per SM,
10MiB for64SM**, separate from the original80KiB physical cache pool. At most
one instruction owns each bank. Bank roles swap without bulk copying; no extra
collection port or data capacity is hidden in128 PIB entries. A warp/instruction
holds at most80KiB raw collected bytes per bank under this conservative bound;
4/8/16-sector fixtures require128/256/512B per instruction. Compact warp-output
packing, physical byte routing/ports, SRAM macros, area/frequency and full values
are unproven. This is not an equal-area or zero-cost hardware optimization.
See PIPELINE_RESOURCE_CONTRACT.md and RESOURCE_MODEL.json.

## Qualification

| Check | Final result |
| --- | --- |
| Fresh independent release/Core identity | clean83aca449, O3 assertions ON, CUDA11.8; fresh e32 baseline; build concurrency<=2, no old product reuse |
| Original7 Core CTests |7/7 passed unchanged |
| New bounded-resource CTest |passed; both full80KiB banks,6 deliberate assert negatives including stale generation |
| Real production-LDST CPU processes |80:75 positive,5 expected unsupported ON rejections |
| Same-ready4/8/16-sector pairs |first WB unchanged; second WB one component cycle earlier with legal WB/collect overlap; not workload performance |
| Multicycle/denied/arbitration/fence/partial/waiter/generation/K1/sidecar |bounded production issue/admission/cycle/RFU/ledger paths pass; three LDST microsteps cannot replenish quotas |
| Strict OFF equivalence |17 byte-identical typed-state triples and51 normal-print boundaries; sole excluded line is host wall-time rate |
| Normal64-SM cumulative export |complete unique population, no-sample sentinel, last whole snapshot;16 malformed/truncated/private/OFF export negatives rejected |
| Exact source allowlist |seven paths; removing ON pieces recovers entire original shader/header/parser/build wiring; all other tracked files unchanged |
| Identity before/after |1297 per-file baseline/new/tool SHA bindings; source manifests stable; actual maps for75 positive processes,5 abort maps explicitly unavailable |

The new library SHA256 is
`2d69d5a5442cd32e3a6d5b2abd3e171703f4f22189a07a2a366073ed3a88924b`;
the CPU probe SHA256 is
`50a6f7b9a2b092bf7a24aafd1cc4946ad5e03df72e28dc9991471cc157a4b075`.
All positive CPU processes bind their actual loaded library and executable.
The actual library ELF also contains cycle()->writeback()->pipeline_collect()
and the normal GPU/DTC printer symbols. Raw logs/builds/binaries remain only
under the independent AC paths; review JSON binds their SHA/build IDs/link flags.

Source-defined finite traffic/credit/Ref/shadow/physical/PIB and completion counts
conserve at every checked edge and final drain. New telemetry has explicit sample
units, port/retire histograms, first/last/sentinel, eligible/idle, overlap, occupancy,
backpressure and RFU-denial fields. It is ON-only, normally exported, cumulative,
and never summed across snapshots. Additional host output is no GPU-cycle or
hardware-area evidence.

## Limits and engineering receipts

The fixture uses controlled admission alignment, a CPU lower-packet link and a
controlled WB owner in the arbitration case; it invokes real production LDST
cycle, RFU bank reservations, completion ledger and normal gpu_print_stat().
It never launches a kernel, GPU cycle, trace replay or simulation thread. It
cannot prove full lower hierarchy or loaded values. This is materially stronger
than a reference scheduler but remains a bounded component proof.

Two ordinary fixture issues were resolved without production-scope expansion:
initial1-channel IPOLY incompatibility was corrected to32 channels/2subpartitions;
strict public comparison exposed unchanged baseline dram_t::n_ref being
uninitialized. Both CPU fixtures explicitly set that unused/no-DRAM-cycle input
to0. Production DRAM is untouched; full-run refresh initialization is unproven.
Prior failed and superseded logs remain, including the first OFF comparison;
none is substituted for final83aca449 evidence. The original sidecar priority
was retained during implementation review, and the final generation test places
the old request in actual inflight/credit ownership before K1 mapping loss.

All new tests and equivalence claims are scoped in TEST_MATRIX.md and
K0_EQUIVALENCE.md. No old performance row is reused for ON. Other-mode OFF checks
cover initialization only. Full native/ISA/coherence, physical hardware timing,
compact buffering and independent AG acceptance remain external gates; they are
not invented PASS labels or permission to start simulators.

## Delivery and Lane AG handoff

README, SOURCE_DELTA.{md,json,patch}, PIPELINE_RESOURCE_CONTRACT, TEST_MATRIX,
K0_EQUIVALENCE, RUNNER_AND_STATS_INTERFACE, RESOURCE_MODEL, CONFIG_AND_PARSER,
CPU_TEST_RECEIPTS, CTEST, BINARY_IDENTITY, SOURCE_SHA256.tsv and SHA256SUMS form the
review pack. PUBLICATION_RECEIPT records source/payload push/fetch-back. The final
receipt commit and clean-tree verification are bound externally, avoiding a
self-referential SHA.

**Lane AG: pin immutable Core83aca449135703c176cfab29ae43e1245d00a557.**
LANE_AG_HANDOFF.md supplies the published handoff, exact switch/resource contract
and remaining validation boundaries. No private-mailbox delivery or AG acceptance
is claimed. This Goal closes with implementation/CPU qualification/publication;
it starts no subsequent simulation campaign.
