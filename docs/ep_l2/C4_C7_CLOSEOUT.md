# EP-L2 C4–C7 closeout

Status: directed checks passed; workload characterization deliberately not run.

| Stage | Delivered invariant |
|---|---|
| C4 WAD | Dirty victim reserves one of 128 address descriptors before tag replacement; same-address lower reads wait; release is only through `memory_partition_unit::set_done(L2_WRBK_ACC)`. |
| C5 Legacy | Metadata-only 1024 resident + 128 bypass payload ownership/generation model and separate 1R1W operation admission. No 128-B byte array is created. |
| C6 Banked | Fixed static roles remain 1024+128; global ID maps by `%4` to four banks and one operation/bank/cycle is enforced with retry on collision. |
| C7 Stats | Separate `EPL2B0V1` application/kernel-snapshot output contains target MSHR, descriptor, WAD, payload and lower-queue state; `L2CHARV1` remains unchanged. |

The B0 overlays are [B0-Legacy](../../tests/ep_l2/b0_legacy_850.config) and
[B0-Banked](../../tests/ep_l2/b0_banked_850.config). Both retain static roles:
no Unified borrowing, RO no-MSHR, replaceable RO pending, TVD functionality or
graphics borrowing is implemented.

## Directed evidence

All passed against the Core CMake build:

* C3/C3b descriptor and production-path lifecycle regressions;
* C4 real WAD saturation, no-pre-mutation blocking, same-address wait and
  `set_done()` drain;
* C5 Legacy 1024/128 ownership plus 1R1W admission;
* C6 four-bank collision/retry and static-role bounds;
* C7 independent schema check.

Stop point: no workload campaign or 850-MHz versus 1-GHz characterization has
been run. That is the next separately authorized phase.
