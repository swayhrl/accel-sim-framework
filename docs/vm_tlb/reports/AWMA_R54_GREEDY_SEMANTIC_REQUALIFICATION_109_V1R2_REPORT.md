# AWMA R54 V1R2 on node109

The Hub backend passed a separately frozen temperature=0 greedy contract across all three prefixes: S0, 2048 and 4096. Each fallback/Hub pair generated the same 64 token IDs, with identical stop behavior, finite logits and valid cache progression. Top2 ordering differed at 7 of 192 diagnostic steps. V1 and V1R1 negative results remain valid for their own contracts.

The real `DynamicCache` has 18 GDN layers and 6 full-attention layers. An exact recurrent checkpoint contains 19,759,104 bytes of GDN conv/recurrent state plus metadata. Full-attention KV remains a separate resident prefix cache. The 512-token restore canary, M0/P0, P0/P1/P2 snapshot hashes, A/B restore continuations and holdout semantic gates all passed.

Discovery medians: P0 156.947 ms; P1-D512 178.667 ms (+13.84%); P2-D512 167.278 ms (+6.58%); P2-D2048 159.409 ms (+1.57%). D512 P2 exceeded the frozen 5% and 3× jitter gates. Holdout P0 78.018 ms and P2-D512 82.941 ms (+6.31%) reproduced the residual.

Timed copy GPU work was 1.27 ms against 10.33 ms discovery overhead and 0.670 ms against 4.923 ms holdout overhead. Measured host snapshot scheduling was 6.52 and 3.213 ms respectively. The discrepancy is not localized to a GPU snapshot engine. Restore was 0.11–0.12 ms above live suffix, 0.073–0.080% of avoided prefix recompute. Measured-component N=1/2/4 amortization is in `AMORTIZATION_RESULTS.tsv`; it does not assert a real service hit distribution.

Final state: `R54_HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED_V1`. NCU was not admitted because no GPU-local snapshot kernel or qualifying GPU-local residual remained. Source/closest-work and R55 source-only audits inherit the accepted V1 files.

One timing harness repair preallocated chunk inputs before the CUDA start event; the first discovery attempt is retained under `full_r54/raw/production_attempt0_input_constructed_after_start`. Holdout density was pre-registered as D512 before holdout and stayed D512 under the corrected discovery numbers. Exact token-4096 checkpoint payload hashes match across the repair, so restore evidence remains attached to the corrected production checkpoint identity.
