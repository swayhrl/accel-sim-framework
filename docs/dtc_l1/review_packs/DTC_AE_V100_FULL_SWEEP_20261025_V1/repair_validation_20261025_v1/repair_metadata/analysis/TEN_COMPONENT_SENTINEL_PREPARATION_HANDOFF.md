# Ten repair component sentinel candidates

Prepared only, with zero simulator starts or authority changes. Candidate
manifest is `control/SENTINEL_CASES_CANDIDATE_V1.json` (10 cases). Integrate
these into the separately approved 23-point repair scope, never original288.

Policy: original Framework `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`,
section7 lines188–201: lines194–198 require five-mode VecAdd; line199 requires
one mixed Store/Atomic/bypass sentinel when non-load paths are touched. These
cases use five modes for both inputs as authorized correctness regression.

Input1 is the complete original EP_VECTORADD_S genuine164 trace, 4,000,000
elements: one kernel,15,625CTAs,56,000,000 thread-instructions. All103.5MB
members were freshly read and SHA-checked against the existing native receipt.
There is no subset or modification of the original trace.

Input2 is a NEW AUTHORED engineering trace-format component fixture, NOT an
NVBit capture, NOT the recovered original M4 application/trace, and NOT a
formal workload. OneCTA/32threads/9warp instructions/288thread-instructions
exercise two cacheable loads, one explicit bypass load, one store, one
returning ATOMG and one zero-destination RED. Both atomic operations access
one address across32lanes, testing unmerged per-lane responses. Numerical
application values remain UNPROVEN. Authorship, exact bytes and source
contracts are bound in the manifest and full-body input bindings.

Five exact config vectors retain original DM's platform/cache geometry,
service capacities and270 options except selector mode0/1/2/3/4 and
finite_service enabled only for whole-line IO/OO. No parameter is tuned to
performance. LEGACY has no DTC counters; its real source returns before
printing them. BASE/IO/OO/SECTOR use exact per-mode source counter names,
drain-zero/equality and mixed-path activity contracts. Every run must be a
fresh cold process with checkpoint/resume0; retained valid Ref0 cachelines
need not be zero at terminal.

All10 use32MiB operational result caps. The bound references closed original
6M vectorAdd PASS cases whose maximum result footprint was2,533,403bytes;
the new full4M is smaller, the mixed fixture tiny, diagnostics disabled.
This is operational margin, not a guarantee; cap enforcement is fail-closed.

Actual frozen Framework parser CPU verification passed all9 authored mixed
records and the first complete legacy-format original VecAdd warp. The
original whole4M body was independently completely audited and SHA-checked.
All opcodes exist in the frozen Volta map. These tests construct no GPU
simulator, launch no kernel and call no GPU cycle function.

The main repair runner owns final source/binary/runtime substitution,
scope23 freezing/publication, epoch2 registration and all model starts.
These candidates do not authorize a performance aggregate or promote any
failed historical attempt. All original and new input assets are SOURCE_KEEP.
