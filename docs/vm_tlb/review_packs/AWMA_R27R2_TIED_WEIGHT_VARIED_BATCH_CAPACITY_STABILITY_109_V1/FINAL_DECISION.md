# Final decision

`R27R2_NUMERIC_OR_STATE_NOT_QUALIFIED`

The exact parquet and immutable token bank qualified: 36,718 rows, 2,435,023 tokens, fixed first 540,672 IDs, and 4,224/4,224 distinct windows. At B1, both C1 and S2 differ from B0 in the required complete total gradient on all four bank steps. The first mismatch is C1 step 1 (`max_abs=0.09375`, `mean_abs≈1.80e-7`); C1's FP32 first moment also reaches `max_abs≈0.01464` at step 4. Fixed `rtol=atol=1e-2` was not changed. Fresh checkpoint load and C1↔S2 policy switch pass, but cannot override the B0 qualification failure. No implementation freeze, capacity search, Gate D, allocator diagnostic, or formal timing was run.
