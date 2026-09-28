# Next 174-new independent consumer contract

- RUN_ID: `C16R_olmoe-routing-provenance-multiround-v1_20260928T092536Z_c91846a955f5`
- Pipeline durable RUN_ID: `C16R_olmoe-1b-7b-0125-instruct_routing-provenance-multiround_prefill2048-decode64_passive-hooks_all-layers_20260928T092536Z_c91846a955f5`
- producer scientific commit: `35bc117a961ad55114f9d75752beb29f6acadc59`
- source manifest SHA256: `07ce90441cecfc29d2669c306084913e8b704234cd4e065c403a01fc4487ac9b`
- four input identities: `P_TEXT`, `P_CODE`, `P_STRUCTURED`, `P_PROSE` exactly as bound in `INPUT_FREEZE_INDEX.tsv`
- six sessions: `T0_NOHOOK_A`, `T1_NOHOOK_B`, `T2_TEXT_ALLLAYER`, `C1_CODE_ALLLAYER`, `S1_STRUCTURED_ALLLAYER`, `P1_PROSE_ALLLAYER`
- expected session rows: 6; expected routing rows: 4096 = 4 sessions x 64 steps x 16 layers
- recompute lags 1..32; seed 20260928; 1000 whole-step-set permutations per session/layer/lag
- recompute prompt periodicity, V34 Layer1 comparison, token/routing association and cross-layer concordance directly from durable raw
- do not use producer TSV/JSON summaries as calculation authority
- do not automatically start the consumer from Lane 7
