# FAST64.1 OO Lower-Cap Telemetry Resolution

Status: **RESOLVED — NEW CORE IDENTITY REQUIRED FOR FORMAL OO CAP EVIDENCE**

Resolution ID: `FAST64-1-TELE-001`.

## Trigger and source proof

FAST64.1 requires a direct zero observation for
`DTC_L1_lower_cap_full_events` in the BICG IO/OO 8192-versus-high-cap
qualification. The frozen Core authority
`15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9` reported that field for
`PAPER_BASE` and `PAPER_IO`, but its `PAPER_OO` terminal reporter omitted it.
The same omission existed in `MODERN_OO_SECTOR`.

This is a generic evidence/reporting omission, not a DTC request, arbitration,
queue, timing, or retirement-semantic defect. The existing counter is updated
in the common global lower-credit path; only its terminal `fprintf` was
missing in the two OO reporter branches.

## Minimal source-correct repair

Core branch `hrl/decoupled-l1-m5-v0` now records:

- Core commit: `bbcbb5e7565417102087bc80b14c349b4e568c05`
- Commit: `fix(dtc): report lower cap stalls for OO modes`
- Changed path: `src/gpgpu-sim/shader.cc`
- Change: four lines total, adding the existing
  `dtc_l1_lower_cap_full_events()` value to `PAPER_OO` and
  `MODERN_OO_SECTOR` terminal output only.

No mechanism configuration, request lifecycle, scheduling, clock advance,
queue capacity, assertion, or cache behavior changed. The Core commit was
pushed before any result is classified under its new identity.

## Equivalence regression

The isolated Release runtime built after the Core commit is:

| item | value |
| --- | --- |
| runtime path | `/tmp/dtc-fast64-telemetry-build-sEWez4/accel-sim.out` |
| runtime SHA-256 | `6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041` |
| Core identity | `bbcbb5e7565417102087bc80b14c349b4e568c05` |
| Framework source identity | `c02ea2259e4bc6ee0ee026734aa60e561ea79724` |
| payload | frozen NN C2P canonical trace, list SHA `6b5e83e43dc74ae1b23312e1772d19a774b6c7397740c1bc1e0f572db77f8664` |

New-Core NN Base/IO/OO all naturally terminated, passed the strict row
validator, consumed the exact frozen trace member, and have compact evidence
under `generated/telemetry_regression/`.

Compared with the original FAST64 NN smoke identity:

| mode | original cycle / instruction | new-Core cycle / instruction | permitted difference |
| --- | --- | --- | --- |
| Base | 6,985 / 1,284,872 | 6,985 / 1,284,872 | none |
| IO | 6,095 / 1,284,872 | 6,095 / 1,284,872 | none |
| OO | 6,105 / 1,284,872 | 6,105 / 1,284,872 | new `DTC_L1_lower_cap_full_events = 0` only |

All pre-existing parser-visible DTC/cache/traffic fields are exact across the
old and new runs. This establishes telemetry-only equivalence for the new Core
identity; it does not turn the old outputs into proof of the previously
unreported OO counter.

## Invalidation / preservation map

The following live pre-repair FAST64.1 rows use old runtime SHA
`75f37ef8deb36fdcba4ae2615ad9c0b229998f3527ef1a52a14b56a29ca3fc8d` and
Core `15cfa76e…`:

- BICG Base / IO@8192 / OO@8192 / IO@1048576 / OO@1048576;
- GESUMMV IO@8192 / IO@1048576.

They remain preserved in `/workspace/fast64-runs/` and are not killed,
overwritten, relabelled as failures, or deleted. They are classified
`PRE_REPAIR_TELEMETRY_INCOMPLETE_ANCHOR`: useful behavioural/progress anchors,
but not accepted formal OO cap evidence because the necessary OO cap-full
counter is absent. After their natural terminal states are recorded, the
affected qualification rows must be rerun with Core `bbcbb5e…` and the new
runtime. No still-live row may be duplicated.

## Next action

Allow all existing jobs to finish naturally. Then validate/archive their
compact anchor evidence and dispatch the affected FAST64.1 qualification rows
under the new Core identity. FAST64.1 remains ACTIVE; this document is not a
stage PASS artifact.
