# AG8R1 current release: explicit user I/O amendment

Status: revised source/qualification frozen for fresh admission; **0 actual simulator starts, 0 accepted AD, F=null**. Historical old IO refusal is preserved, not backapproved.

C1 completed once: 8 wall/source checks, 4 exception-scope cases, no simulator. On the latest explicit instruction “I/O不重要，不要因为I/O停下”, host+cgroup IO PSI are warnings for both new AD points at admission and runtime, including persistence/1800s episode. The old foreground wait was terminated and reaped before source changes; it never produced an executable release or consumed a start. Its inactive proposals remain sealed; two new inactive proposals route the unchanged two-start budget and are executable only after fresh amended R2. No failed simulation is retried.

Focused amendment CPU validation passed 15 cases in ~6s, including synthetic sustained99% IO through21590s, preserved21600 deadline, disk/OOM/memory/swap/no-retirement/identity/cadence stops. These are synthetic policy tests, not performance results. Original four C1-qualified subjects, Core/Framework simulator, producer, inputs,270 options and four-point selection remain unchanged. New Python policy is explicit opt-in, isolated from original production ResourcePolicy. Shared-I/O harmlessness/fairness is not empirically proven or claimed.

Fresh admission still requires two samples >=10s apart, current BA/root authority, >32GiB host/cgroup memory headroom, memory PSI, no new OOM, disk >5GiB after2GiB expected writes, exact device and identity. Run limits retain21600s,2GiB output,30s freshness,600s no retirement; default single simulator, AD_Gaussian conditional on full AD_GEMM strict acceptance. No extra canary/retry/BASE/AE or BA32 expenditure.

Next: exact GitHub readback, fresh admission, then conditional two-point execution. Results are pending; no partial-cycle performance claims.
