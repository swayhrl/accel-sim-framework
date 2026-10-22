# C SGEMM positive whole-epoch RO candidate r1

**POSITIVE_MODEL_CERTIFICATE_CANDIDATE; PREPARED_NOT_E_QUALIFIED_NOT_ADOPTED.**
Assigned preparation `C-SGEMM-POSITIVE-RO-CERTIFICATION-r1` in batch
`EPL2_RO_POSITIVE_QUALIFICATION_PREPARATION_20261022_r1` is DONE. The exact complete
SGEMM frozen trace has positive read-only coverage under the unchanged closed-world,
whole-commandlist, canonical-VA, 128B-line model. This is no application/native,
numeric, Tag-detach or runtime-qualification PASS.

## Measured complete input and coverage

One complete body open read **2,216,170,035 bytes** and computed exact SHA
`1b0739908e3aef52cedea68962172ccac55f0c2d4c651623cb8fb0655475db06` during
original parser/classification. The original parser closed all **51,847,488**
instruction records. The full 92-byte commandlist matches
`0a0d21711ff3f3de1604fc0a243d5be2df5155147bb09bc4533bd017b62f5913`:
two initial HtoD operations and the original single kernel. No host command is
removed, added, reordered or inferred. There are no post-initialization HtoD
updates in this exact list. Full composite identity remains
`694ce08c82354963d0a24f45b13020c9a98d21e60b511166812d6176b4f486cb`.
The active-lane instruction total1,658,916,864 is reused from the saved complete
D/E proof by this newly matched full body SHA, not freshly recomputed.

| Offline line-model quantity | Actual result |
| --- | ---: |
| Unique / read-containing global128B lines | 98,272 / 98,272 |
| Certified RO lines | 64,480 |
| SAME_LINE_STORE excluded read-containing lines | 33,792 |
| All global read lane-line references | 76,505,088 |
| Certified RO read lane-line references | 75,423,744 |
| Excluded SAME_LINE_STORE read references | 1,081,344 |
| Global write lane-line references | 1,081,344 |
| Global atomic lane-line references | 0 |
| Unresolved opcodes / host-update exclusions | 0 / 0 |
| Positive compressed ranges | 2 |

The candidate covers 65.613807% of read-containing
lines and 98.586572% of global read lane-line
references. References count every lane and each128B line touched by its width;
they are neither unique transactions nor observed L2 requests. The two exact
ranges are in `oracle/certified_ranges.csv`; `RO_COVERAGE.json` binds all hashes,
denominators, exclusions, assumptions and source/tool identities.

## One pass, original semantics, actual resources

Known published C input assets and the existing E offline inventory had only the
SGEMM empty fallback, so no matching positive proof could be reused. FWT, previous
fallback/native controls, applications and old figures were not rerun.

The unchanged original `ro_oracle.py` SHA
`763cbcdf633c07ace9102d5796743a0a2485c9a66860c1577c01d6ecd9af9225`
supplied `stream_kernel`, `instruction`, `memory_kind`, full line classification,
SQLite and artifact generation. Its ordinary entry performs extra before/after
body hashing, incompatible with this batch's one-pass bound. The owned
`single_pass_oracle.py` changes only I/O binding: the old pre-hash request returns
the declared frozen expectation, explicitly not a measured digest; raw bytes
feeding the original parser are simultaneously hashed. Full EOF, length, stat
identity, instruction closure and measured expected SHA must succeed before the
post-hash request or manifest completion. No original classifier or production
source is edited. The exact published execution producer is
`a658740e293919d7578cc55c9c2b5a39cef3bc9f`.

Three new tiny **Python-only** adapter controls passed: positive classification,
post-initialization partial-line host exclusion and wrong-hash refusal without
manifest completion. These are not C++/native tests. Final artifact validation
passed 24 checks, including SQLite integrity, reason/denominator closure,
all artifact SHAs and ranges matching exactly all eligible database rows. It
never reopens the trace and never invokes the original full-rehash verifier.

The existing original E `Coordinator.reserve_work` admitted lease
`2a58692e00e24aeb8c1c8cfdb56d4a63`: roleC, administrative test resource class,
**actual offline Python only**, 1CPU,256MiB address-space/reserved memory,
16MiB SQLite cache and256MiB monitored allocated-growth cap. The frozen5GiB floor
and2GiB stop margin remained enforced. No second registry/controller, lease
exception, Goal restart or dependency watcher was created. The finite resource
guard ended with its own child and the lease is **RELEASED**.

Measured worker time **328.775s**, peak worker RSS
**29,360,128B**; retained raw artifacts are
**6,933,927 logical bytes / 7,036,928
allocated bytes**. `RUN_RECEIPT.json` and `ARTIFACTS_RAW_IDENTITY.json` retain
actual output/accounting identities. Raw SQLite and tiny controls remain under
`/workspace/ep_l2_ms20261019_e_results/C_SGEMM_RO_POSITIVE_20261022_r1`; SQLite/trace bodies are not copied to Git. Only small
certificate/coverage/receipt metadata is published here; those additional copy
bytes remain generated artifacts and are reported separately in final readback.
Actual application starts remain **50**, originalT0/10GiB-new/24GiB-total policy
and historical results unchanged. This offline329s is not simulation cost.

## Qualification and claim boundaries

`QUALIFICATION_CONTRACT.json` is the precise future-use contract. No external or
hidden CPU/DMA/device writer, no hidden VA alias/MMIO, canonical global VA,
complete visible traced agents and drained initialization/writeback remain
explicit **model assumptions**, not universal physical proofs. Every same-line
GPU store/atomic and any later host update is excluded across the entire epoch;
unknown memory agents poison positive certification. Later uncovered
clean/quiescent prefill remains allowed through actual native ownership/version/
drain guards; no initial-only rule or host-update waiver is introduced.

The old accepted SGEMM empty-fallback S/F pair remains exactly as accepted. Its
historical report of unassessed opportunity is retained; this new proof adds
model-scope opportunity evidence, not a retrospective runtime upgrade. FWT's
existing whole-epoch SAME_LINE_STORE zero remains distinct and unchanged. R35's
FAIL, later full-joint UNRUN fixtures, original Conv proof, old HOLD/INCOMPLETE
and withdrawn results are preserved.

A2 receives exact candidate hashes for one static main61 schema/domain/native
applicability binding, using d010/9dd/main61 and original finite1168/P1 W/V/T/M
policy. E2 independently decides positive-certificate input/profile/source/
manifest/ranges/current CLIENT_CONTRACT qualification and adoption. Previous
empty-fallback Q cannot substitute. D can immediately use these actual
coverage/exclusion results; C does not wait for all lanes.

Positive coverage is not a miss, RO admission, independent pending request,
Tag replacement, successful detach, MSHR relief or critical-cycle reduction.
No reuse_seen reset, sibling protection removal, capacity reduction, early
completion or input rewrite is allowed to manufacture activation. Full S/F
changes several mechanisms and does not isolate T or M. E must separately prove
old-S invariance and comparison-rule reuse if proposing one new certified F;
otherwise only an explicitly needed fresh pair may be proposed. Neither route,
any native/build, nor an application start is authorized by this packet.
Old about7.85GiB runtime RSS and29–31min walltime are cost priors, not a safe
positive-RO envelope; E must forecast current resources, collector/metadata/
certificate reserve and cumulative generation. No backup scan or run occurred.
