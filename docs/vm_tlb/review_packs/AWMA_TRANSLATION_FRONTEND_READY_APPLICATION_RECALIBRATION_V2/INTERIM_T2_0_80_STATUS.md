# INTERIM — V2 T2 0/80 Receipt

Status: `INTERIM / NOT_FINAL / T2_0_80_ONLY`

This checkpoint records one completed speculative matrix point under the active
`AWMA_TRANSLATION_FRONTEND_READY_APPLICATION_RECALIBRATION_V2` Goal. It does
not classify V2, promote a baseline, or replace the required final review pack.
Five matrix points remain live at this checkpoint.

## Authority

- Execution branch: `hrl/awma-174-translation-frontend-ready-application-v2`
- V1 authority: `ad6f38878bc1e7c268b17e65fdb3793a3899a84d`
- Coordination authority: `hrl/awma-mainline-reset-crossview-v2 @ 4caa249e30c1341a38c850d20636b6909a2b0696`
- Candidate binary SHA256: `f9f7afef8cf4186527b1fda13a05dc7d060006dc6a945fb27ad7573986fa29c7`
- V2 source checkpoint SHA256: `f1b8abb52d5a49f4277989bbc28196e819c8f04a8c307f5d17988b7e0bf491ae`

## T2 V2 0/80 result

- Runner root: `/tmp/awma_v2/.awma_runtime/v2/runs/T2_V2_0_80_SPEC_RETRY1`
- Runner index SHA256: `2a458d31a945cf11ce465b563582e6ab29292ae692bd3d2acd74bf4e8b5c2c4a`
- Effective config SHA256: `fe43d71c273f656781ce0abf7942b2f6ddbdbc2cb744fa8c85c297af91da8f4e`
- Raw run log SHA256: `43ddee8c66fb21bad8ba6fdd0ddaf95d89791c7f8e933530089b5126054977cd`
- Terminal cycles: `71,743`
- `gpu_sim_insn`: `43,357,696`
- `gpu_tot_issued_cta`: `1,216`
- Coverage: admissions=`483,061`; translated=`483,061`; untranslated=`0`; unobserved=`0`; unique=`411,008`; translated_unique=`411,008`.
- READY accounting: prelaunch ready=`411,008`; prelaunch applied=`411,008`; head applied=`0`; duplicate attempts=`0`; ready-unapplied observations=`0`.
- Quiescence: translation MSHR active=`0`; PWQ occupancy=`0`; walkers active=`0`.
- Segment F0: lifecycle `INACTIVE`; functional lookup/accept/hit/miss counters all `0`.

This is a valid terminal candidate receipt pending final cross-point and source
contract audit.

## Runner-path correction

The first T2 speculative invocation had an invalid derived runner index ending
with literal `n`, yielding a non-existent `.xzn` payload and `Unsupported file
type`. Its log is retained as a path-only failure. `RETRY1` uses a one-filename
plus LF index and is the only T2 0/80 receipt above.

## Remaining live points

`T0 10/80`, `T0 0/80`, `T1 10/80`, `T1 0/80`, and `T2 10/80` remain running.
No final V2 classification or matrix conclusion is authorized at this point.