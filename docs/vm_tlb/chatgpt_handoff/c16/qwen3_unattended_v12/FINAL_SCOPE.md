# C16 Qwen3-8B Unattended V12 — Final Scope

Status: `FINAL_AUTHORITY_BOUND`. Files containing `DRAFT` are historical preparation only and are not executable authority.

Authorities:
- node109 framework: `d7f5ad2c06831193113401b688711be80058cd00`
- V12 result: `79d3899a1279210c008e0caff2950958e7f06dba`
- decision: `C16_QWEN3_AUTHORIZATION_174NEW_V12_PASS`
- authorization SHA256: `b6c2b5551271de3a9edc270df9218ce48fd1492dc73819c160e4f438f1abf7b9`
- V2 validation SHA256: `1f62abb9b6ffa4f93901c51eb2160a4fea6c0c7117402a943ee77732b7bd26e9`
- detailed scientific policy: coordination HEAD `59ccffbe260b20086bc4b68205393db696dd0e0b`

The V12 result proves readiness and 42/42 canonical V2 validation. The coordination authority supplies detailed scenario, target-selection and STOP policy. Use the conservative intersection.

Model: `Qwen/Qwen3-8B` @ `b968826d9c46dd6066d109eabc6255188de91218`, BF16.

Validated V2 root: `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/prospective_inputs/C16_PROSPECTIVE_COMMON_INPUT_V2`.
Required first baseline: `qwen3-8b__S2_TEXT.json` (`S2_TEXT_B1_T2048_D32`).
Conditional extension: `qwen3-8b__S3_TEXT.json` (`S3_TEXT_B1_T8192_D16`).

Before any Qwen3 GPU work, read the exact validated S2 payload and materialize its canonical token-sequence SHA256 and serialized payload SHA256 into campaign `AUTHORITY_BINDING.json`.

Execution policy: exact semantic layer streaming/replay is the safe baseline. Native full-resident mode is optional only when exact BF16 feasibility is independently proven and explicitly recorded. Lack of full residency is not a blocker.

Target policy: prefer one losslessly bound decode MLP linear anchor; allow at most one materially distinct attention/KV target. Never infer semantic identity from launch order.

A required S2 failure in authority, exact state, replay equivalence, signature, fresh path audit, formal capture or serial ACK is BLOCKED. Scoped PASS may cover only optional second-target/S3/optional fields after required S2 closure.
