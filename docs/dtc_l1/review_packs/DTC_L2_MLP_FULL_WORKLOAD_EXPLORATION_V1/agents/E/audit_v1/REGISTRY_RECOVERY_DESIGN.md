# Read-only audit: registry extension recovery gap

The frozen `l2_registry.extend()` has an ordinary engineering recovery gap. CPU
fault injection against the actual source reproduces it: the authority callback
commits 35 new grants, then writing `MATRIX_CURRENT.json` fails. The proposal ID is
not recorded in history. Retrying the same proposal reaches `assert c not in
q['admitted_specs']`, even though every existing grant is the correct unconsumed
identity. The synthetic fixture creates 35 admitted-but-unlisted identities. It
does not update production authority or start a model.

Current order is specs/configs → authority → matrix revision journal → current
matrix → search history. Thus a failure before the revision journal is written is
also possible. A failure after current matrix but before search history is less
severe: existing cohorts are skipped on retry and history is completed. A failure
between authority and current matrix needs explicit reconciliation.

## Proposed additive wrapper, for coordinator review only

Keep every frozen tool unchanged. A qualified wrapper in the sole existing owner
should retain the original `extend()` and use an additional, independently pinned
transaction module. It must never create a competing dispatcher.

1. Acquire an extension-specific owner lock in the same sole dispatcher. Reload
   the current matrix/history/authority under the normal registry read checks.
   Normalize parameters using the frozen generator; verify proposal ID, exact
   frozen 35-input set, CH/DH design, and existing P0 references.
2. Before calling the original extension, write and fsync an immutable PREPARED
   journal with proposal bytes/hash, canonical profile/parameters, intended
   cohorts, base matrix hash/revision, expected config/spec hashes where available,
   source/build contract hashes and prior relevant request grant/accounting hash.
3. If extension returns, independently verify source/spec/config identity,
   current matrix, input linkages, budget and remaining count, then append a
   COMMITTED receipt. Preserve the PREPARED journal permanently.
4. If extension raises, record an ERROR receipt and reconcile before another
   proposal or model admission. Match existing authority grants to the exact
   intended cohort and actual spec SHA. Verify config bytes, normalized parameter
   vector, input digest/scope, trace path, Core/FW/binaries, design, and all270
   resolved expected options. A same-name parameter or SHA mismatch is a hold.
5. For already granted exact identities, append only missing matrix rows and
   input/history links. **Do not add budget again, regrant, reset consumed IDs,
   touch old requests, rewrite actual results, or restart a consumed model.** If
   the authority already lists a consumed identity, preserve its UUID and natural
   receipt and reconcile the matrix link rather than launch it again.
6. If the authority grant is absent, resume only the ungranted intended cells
   through a new qualified registration operation, using the original legitimate
   request. The exact finite delta equals genuinely missing new identities.
7. Preserve each matrix revision journal and atomic replacement order. Fsync
   relevant parent directories. Commit search-history proposal ID exactly once
   after matrix consistency is verified.

For a pre-wrapper gap with no PREPARED record, recovery can reconstruct intended
rows from the request's `authorized_extensions` entry, exact admitted specs/input
linkages and the frozen P0 row. This requires the same full identity checks and
an explicit recovered-transaction receipt; prefix matching alone is insufficient.

## Minimum new CPU qualifications

Use actual frozen generator/spec/schema and isolated filesystem/authority mocks.
Inject errors before/after authority, before/after revision journal, before/after
matrix replacement and before/after history replacement. Include partial batches,
duplicate retries, a consumed grant, concurrent stale snapshots, and mismatched
profile/input/config/spec SHA. Assert exactly one grant and unchanged spent UUIDs,
budget increase only for genuinely absent grants, unchanged other requests, no
model execution, and terminal reconstruction of every intended matrix row.

## Audit fixture correction

The first audit attempt incorrectly equated the generator's explicit-text option
dictionary with all270 resolved options and stopped on an assertion. Explicit
configuration text contains139 keys; the canonical spec additionally preserves
registered defaults and the trace option for a total270. A quoted multiline DRAM
timing value also cannot be fully parsed by the generator's line-local helper.
The corrected cross-module check verifies all270 canonical expected keys are
preserved, all268 non-target values are identical, only the two authorized target
keys can differ, and all fixed config bytes/options remain unchanged. This was a
fixture correction and does not indicate a changed model contract.
