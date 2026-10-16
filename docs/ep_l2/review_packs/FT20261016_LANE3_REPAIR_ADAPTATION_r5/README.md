# Lane 3 r5 — repair-candidate source adaptation, not a qualified release

Authority: review_r3 `a41bfb55934303a4d4a342762f74a16d137d0316`. The newer Lane 5 withdrawal supersedes old R0/R1 application acceptance. All old raw logs, CSVs, binaries, r1–r4 packs and the five whole-commandlist oracle inputs remain unchanged.

Core source `b90e5e861a934503f35c56688e7007da6bb3dcc0`; Framework tooling source `90b4e464892a344d4bb2c8652963f02db18bfdb6`. This branch merges the exact Lane 5 repair candidate `832d986b03dc3c940eb99a1ae6845dd07297f4ed` with r4 and adapts RO. **It is not Lane 1's official R0.1 parent or release.** Latest bounded Lane 1 publication `3840f9585b710a5abea8201c14fa05cdea930aa7` still records official integration in progress under resource hold; no repaired official Core SHA has been published.

The adaptation preserves Tag timestamps while using physical GPU cycles for shared bank/WB/WAD service. RO packet timestamps use physical time, RO fill/read bridges reject a nonphysical clock, and host prefill is rejected after the certified whole-commandlist epoch has ever begun. Warmup checks actual Tag selection, payload owner/generation, bank class and sector readiness using existing metadata. Attached Tag lookup, detached independent completion, shared D512, separate OFF defaults and oracle scope are retained.

Executed: 16 bounded static source checks, four exact-parent patch-application checks, five Python configuration-receipt tests. **No C++ compile or new runtime test was executed.** New nonzero-offset/C8/C16/four-mode fixtures are staged with NOT_RUN status. No new binary, application config, application trace execution or run key exists for r5. Old r4 local fixture PASS is not upgraded to r5 or repaired-application qualification.

Disk remains below 48GiB. Audit under the central registry lock inventoried only Lane 3's own nonactive object cache: about 1.25GiB, insufficient alone to recover the floor plus build headroom. No deletion, migration, build lease or simulation was attempted. Frozen results and unrelated active projects were untouched. Lane 1/Lane 5 retain repair/build/independent-validation priority.

Read SOURCE_AND_GATES.json, CONFLICT_AUDIT.md, TEST_PLAN.md and METADATA_DELTA.md. Once an official R0.1 SHA exists, recheck/rebase this adapter against that exact parent; do not treat the provisional repair candidate as an accepted baseline.
