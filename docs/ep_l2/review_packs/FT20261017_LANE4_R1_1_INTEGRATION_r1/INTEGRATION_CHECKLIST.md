# Lane1 future R1.1 integration checklist

This is a review/integration contract, not build or run authorization.
Review_r14 d962f847cbf7ba6d525bbb23964fee392bd8a69f retains the original
scientific scope. Core candidate8ff56eb0804a027f1e253e629dd2915b02bc03b5
is unchanged and uncompiled. No official R1.1 source or binary is assigned here.

## Inputs and ordering

1. Lane1 first freezes official R0.1 and its producer evidence; Lane5's first
   B16/U_WB16 pairs do not wait for this work. Lane1 owns future R1.1 integration.
2. Record the actual future R1.1 Core/Framework commits. It must already have
   the ideal reference/response APIs and the repaired clean/quiescent native
   host-prefill path. **The minimal sync patch is not a patch for bare c948**,
   which does not contain the ideal reference header. Do not merge old lane
   branches or reapply the obsolete duplicate-getter deletion.
3. Review base tree5e03cbadd8ab598717bab7d56bc230560b61b8b5 is c948 plus
   existing ideals, repaired fixture extraction and the native Tag-offset fix.
   It is a reproducible private-index tree, not an official release commit.
   Frozen tool prepare_ft_lane4_r7_static.py at705cd7b30d825cd1d9887e48427475a126d9bc83
   reconstructs it from published inputs. PATCH_IDENTITIES records exact
   pre/post SHA256 and Git blobs; the full-index patches provide review context.
4. Check future source preimages. If the native Tag touch still lacks memcpy
   offset, review CORE_TAG_TIMESTAMP.patch separately. If already correct,
   retain it; never add the offset to the bank arbiter or response timestamp.
5. Apply CORE_HOST_PREFILL_SYNC_MINIMAL.patch, then
   CORE_HOST_PREFILL_REGRESSIONS.patch in an isolated candidate. Their combined
   replay on the exact review base yields Core8ff56eb0's full tree
   1949be28284e3d9d1674ee21211eb5885e75a128. Different official preimages require
   a reviewed adaptation/new revision, not an assumption of production equivalence.

| File | Required integration | Preserve/check |
|---|---|---|
| src/gpgpu-sim/ep-l2-ideal-reference.h | host_prefill(line, byte mask) | Selected versions0 and old known values erased; unselected versions/data, other lines, response copies and next_version_ retained |
| src/gpgpu-sim/l2cache.cc | Hook after successful ft_try_force_tag_access and before existing offset increment | Existing full drain, dirty/pinned/generation/index/mask rejection occurs first; hook only for I_READ_HIT; full-width line address |
| tests/ep_l2/test_ideal_host_prefill_reference.cc | New reference regression | Sector granularity, snapshot copy, monotonic later producer, repeated/cold prefill, high addresses |
| tests/ep_l2/test_ideal_host_prefill_partition.cc | New real-partition regression | GPU store, dirty refusal, actual WB/lower drain, later legal prefill, held response and untouched sector |
| tests/ep_l2/ideal_host_prefill_b16.config | Directed test input | Static B16/WBUF16, all unrelated features OFF, real ROP delay/response backpressure; not application geometry |
| util/ep_l2/test_ft_lane4_production.py | Framework qualification entry6ecb02ab496f5df2db40401fe9da18cfb68235d6 | Verified central registry loader before metadata/claim; link manifest checked before lease; --include-host-prefill adds the two new cases to affected regressions |

No source semantic change was needed in this r14 continuation. The one engineering
fix is in the Framework directed-test entry: its former direct registry import
did not check CLIENT_CONTRACT. It now uses the existing hash-verified loader;
two targeted Python failure-path tests passed without a lease/compiler.

## Semantic review findings

- **Selected sector:** all bytes of an accepted native32B sector become unknown
  version0 symbols. This is not numeric zero data. Replacing the selected old
  producer is intended host-write semantics; preserving old producer state
  applies to unselected bytes/sectors and prior response snapshots.
- **Producer order:** next_version_ is not reset. A later GPU write still gets
  a newer version; a host prefill does not erase unrelated historical producers.
- **Held response:** l2_char_no_resource_leak checks the real response queue,
  requester tracker and ideal response/arrival/known-write maps. A held response
  rejects host prefill before the hook. Response vectors are value copies.
- **Dirty refusal:** native dirty/pending/invalid-mask rejection returns before
  reference mutation or offset increment. No free WB or dirty discard is added.
- **Clocks:** physical service is gpu_sim_cycle+gpu_tot_sim_cycle; Tag age is
  physical cycle+memcpy offset. Ideal bank request and reply keep physical time.
- **Scope:** later clean/quiescent prefill remains legal after GPU producers and
  a real WB/drain. No initial-only restriction, whole-memory reset, new oracle,
  budget increase, trace change or current performance claim is introduced.

## Current test state and future sign-off

Both new C++ cases are **NOT_COMPILED_NOT_RUN**, with no observed old-red/new-green
execution. File/config hashes and required assertions are in R1_1_QUALIFICATION.json.
The expected counterexample is a GPU-produced A sector, real dirty eviction and
drain, then accepted host prefill of A: the old reference kept producer bytes,
while native Payload became version0. The fixed source synchronizes them.

Future exact build/test receipts must bind source commits, library/link-input
hashes, compiler command/assertions enabled, executable/config hashes, output
hashes and normal completion. Lane5 independently qualifies physical_bank_clock,
memcpy_payload_identity, affected ordinary gates and each requested ideal mode.
Tag-offset0/nonzero and actual per-bank <=1op/physical-cycle evidence must come
from production gates, not this static review. Only then can same-binary B16 and
the original18 cells use current V2 authorization and unchanged shared admission.
