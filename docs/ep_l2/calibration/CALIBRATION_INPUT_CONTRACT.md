# Lane-D calibration input contract

Every D512 or L1 result root consumed by Lane D must have a separately
published JSON contract using schema `EP_L2_CALIBRATION_CONTRACT_V2`. The
analyzer receives its path as the fifth colon-separated component of `--cell`.
The formal D256 reference is
`docs/ep_l2/calibration/contracts/D256_BASE.json`.

Required fields are `semantic_base_id`, formal `base_core_sha` and
`base_framework_sha`, candidate Core/Framework SHAs, `equivalence_gate`
(`id`, `status=PASS`, and evidence path), `allowed_source_delta_class`, an
effective key/value configuration map, and `allowed_config_fields`. Every
contract must additionally bind `runtime_config_composite_sha256` to the
actual run's audit digest and provide `config_delta_gate` with `status: PASS`
and an evidence path. The analyzer rejects a run before analysis when its
actual digest differs from the contract, or when this gate is incomplete.

Lane D permits exactly these effective-config differences:

| Cell | Allowed fields |
| --- | --- |
| D512_BASE | `descriptor_pool_size` |
| D256_META_HR | `l1_mshr_entries`, `l1_merge_cap`, `l1_missq_entries` |
| D256_BANK_HR | `l1_bank_count` |
| D512_META_HR | D512 plus META-HR fields |
| D512_BANK_HR | D512 plus BANK-HR field |

Any extra, missing, or undeclared changed field is rejected. A changed SHA
without a PASS equivalence gate, or one based on a different formal SHA pair,
is also rejected. This contract authorizes comparison only; it does not
promote a calibration cell to the formal baseline.
