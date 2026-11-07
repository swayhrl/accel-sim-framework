CLEAN lifecycle V2 private production candidate

This engineering scope has zero scientific/model launches. Main remains the
only formal integration, scientific budget, Native and Git publication owner.
Existing bf4/Source78/Core862 and all prior C deliverables remain immutable.

The candidate connects timed tokens to ordinary CLEAN +1/net0, dirty
install plus existing packet-UID binding, lower enqueue/completion, clean and
dirty promotion, read begin/response/cancel, pre-Native rollback and indexed
terminal cleanup. Six registered producer heads share K=1 primary/K=2 compare
row service and one count commit lane. Pending completion ownership cannot be
released before its paid token and real packet/credit retirement.

Supported command profile is initialization memcpy only followed by kernels,
across-kernel retention, then clocked terminal cleanup after all commandlist
kernels retire. Unsupported post-kernel memcpy is rejected before launch.
Per-kernel flush and unclocked timed flush are rejected. This is not generic
Host/NI/RO/full-configuration qualification.

Timing differs explicitly from old Python transaction contract: registered
ingress1 + READ1 + COMMIT1 = minimum3 L2 ticks per isolated operation.
K2 does not claim arbitrary merged nonzero count updates; the single count
lane revalidates serially and can return COUNTER_BUSY. Net0 is charged.
Canceled READs are not refunded. All128 cleanup rows, including EMPTY,
consume the fabric: actual production CPU terminal test requires384ticks.

The indexed 128-row selector is conservative correctness/cost evidence:
minimum384 L2ticks for full scan plus mutation. It is NOT a performance
optimization, not a new application result, and not a revival of the stopped
128-cycle LRU science direction. Physical CDC and PPA remain UNKNOWN.

New finite tests only; old12 directed/3185 combinations and earlier C suites
are reused as historical evidence and not rerun. New Python V2 finite event
schedule is compared with actual current production header traces.

build_v1/Core212087 preserves a newly found negative: delayed promotion WB
still in L2 missqueue had no request_tracker entry, allowing busy=false
before metadata READ completed. Successor Core40a815 makes timed busy include
actual FT/metadata ownership. A pressure-test negative was fixture sequencing
(the write made the intended victim MRU); successor fixture restores it to
actual LRU before testing bank pressure. Neither original log is erased.

Current acceptance files, final Source5, banner and build/test receipts are
listed by the final manifest. Production CPU PASS is bounded engineering,
not complete-application acceptance, silicon correctness or performance/PPA.

Final engineering result: Core40a815 / Frameworkd5bf173 full consistent build
PASS; production lifecycle18/18 PASS; new PythonV2/production16 snapshots
MATCH; finite header negative3 PASS. Both actual ELF .rodata banners match.
Production supported-profile boundary and costs are in
PRODUCTION_BOUNDARY_AND_ACCEPTANCE_V2.json and RESOURCE_AND_TIMING_CONTRACT_V2.json.
SOURCE5_V2.json pins all8 static libraries and both application/fixture ELFs.
No application ELF was executed. Only CPU fixture ELFs were executed.
Counter/ingress logical-bit estimates exclude physical encoding; host sizeof
is reported separately and is not a PPA estimate.
