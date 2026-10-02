# AWMA R24 tied-weight gradient lifetime native validation V1

Stage: `AWMA_R24_TIED_WEIGHT_GRADIENT_LIFETIME_NATIVE_109_V1`

Final decision:
`R24_TILED_DELAYED_UPDATE_NET_RESPONSE_PRESENT`

## 1. Tied storage and input authority

The exact `Qwen/Qwen2.5-0.5B-Instruct` revision
`7ae557604adf67be50417f59c2c2f167def9a775` and model SHA256
`fdf756fa...288fb7fe` were used. Runtime checks proved that
`model.embed_tokens.weight` and `lm_head.weight` have the same data pointer and
untyped-storage pointer. The single BF16 tied matrix is `[151936,896]`; it is the
only trainable parameter.

The exact `ACCEPTED_R101_TRAIN_DISCOVERY_256` token file was used. Its SHA256,
255-position `input_ids` hash, and shifted 255-position labels hash all match the
frozen contract. No alternate input, prefix, model, sequence length, batch, or
vocabulary was used.

CCE is the isolated `3de376c...` source with the accepted first-store patch.
Patched `cce_backward.py` and `tl_utils.py` hashes match the prior authority;
autotune stayed off and all fixed block meta matched.

## 2. What the three arms execute

- `B0_STRONG`: CCE produces dH and a full classifier dW before backbone
  backward. That dW remains live while the normal dense input-embedding
  contribution is produced, then both are merged and consumed by AdamW.
- `S1_LATE_FULL`: CCE produces dH only, the full backbone produces the normal
  dense lookup gradient, and only then CCE produces one full classifier dW.
  AdamW still consumes a complete VxH gradient.
- `S2_LATE_TILED`: dH propagates through a compact embedding backward that emits
  113 unique lookup rows. Classifier dW is generated in 17 fixed 9,344-row
  tiles, merged with matching compact rows, and immediately consumed by the
  same AdamW tile function. Formal S2 never forms a full VxH gradient or shadow.

All arms share one frozen explicit AdamW contract and restore the same
post-bootstrap W/m/v/step/RNG state outside timing.

## 3. Numerical qualification

All 21 required comparisons passed at the frozen `rtol=atol=1e-2`:

- loss and final-hidden dH;
- complete tied-weight gradient;
- updated W;
- FP32 first and second AdamW moments;
- exact step counter;
- next-forward loss.

The largest total-gradient absolute difference for S1 and S2 was `0.0078125`;
cosines were `0.99998395` and `0.99998528`. First mismatch is `NONE`; all values
were finite.

## 4. Dense-gradient existence and lifetime

| Arm | Full VxH gradient in formal path | First full-gradient point | Median lifetime |
|---|---|---|---:|
| B0 | Yes | classifier dW before backbone backward | 20.098 ms |
| S1 | Yes | dense lookup dW after backbone backward | 16.307 ms |
| S2 | No | never | n/a |

S1 shortens measured full-gradient lifetime by 3.791 ms (18.86%) but still
materializes two full-size contribution/total buffers at peak.

## 5. Measured memory response

Primary allocator result is target-region peak allocated memory:

| Arm | Target peak allocated | Target peak delta | Whole-microstep peak allocated |
|---|---:|---:|---:|
| B0 | 4,535,017,472 B | 818,510,336 B | 4,535,017,472 B |
| S1 | 4,558,633,984 B | 842,126,848 B | 4,558,633,984 B |
| S2 | 3,724,405,760 B | 7,898,624 B | 3,724,405,760 B |

S2 lowers measured target peak allocated memory by 810,611,712 bytes
(773.06 MiB, 17.87%) versus B0 and by 834,228,224 bytes (795.58 MiB, 18.30%)
versus S1. Its actual persistent compact lookup representation is 113 rows and
203,400 bytes. The fixed FP32 tile buffer is 33,488,896 bytes; its BF16 consumer
tile is 16,744,448 bytes. Allocator bytes are not labeled as DRAM traffic.

## 6. TARGET_REGION Native timing

All S2 costs are included: compact lookup construction, 17 late classifier
tiles, compact merge, and 17 tilewise AdamW updates.

| Group | B0 median (ms) | S1 median (ms) | S2 median (ms) | S2 vs B0 | S2 vs S1 |
|---|---:|---:|---:|---:|---:|
| G0 | 27.3681 | 28.7289 | 27.5323 | 0.60% slower, stable | 4.17% faster, stable |
| G1 | 25.8754 | 27.0835 | 25.6253 | 0.97% faster, stable | 5.38% faster, stable |
| G2 | 25.8671 | 27.0735 | 25.6030 | 1.02% faster, stable | 5.43% faster, stable |

Across all 15 samples, medians are B0 `25.8755 ms`, S1 `27.0948 ms`, and S2
`25.6354 ms`. S2 is mixed but not consistently worse versus B0 and is stable
faster than S1 in all three groups. It does not meet the capacity-time-tradeoff
condition, which requires stable regression in at least two groups.

Complete-microstep group medians are neutral/mildly favorable versus B0
(-0.05%, +0.73%, +0.81% improvement) and favor S2 over S1 by 3.06--3.73%.
These are microstep results, not training-throughput claims.

## 7. Is S1 sufficient?

No. S1 does shorten lifetime, but it increases target time by 4.66--4.97% in
all three stable groups, slightly raises measured peak memory, and retains full
gradient materialization. S2 provides the causal capacity benefit and is faster
than S1 in every group despite including all tiling costs.

## 8. Scope and next step

This is one real-token, one-model, B1/T255 target-family microstep with only tied
W trainable. It does not establish convergence, full-model training speedup,
multi-shape generality, or a hardware residual. The result justifies considering
a production-quality software integration and separately authorized broader
workload validation; it does not justify hardware/PPA or automatic continuation.

Allocator/direct accounting closes the causal question, so NSYS was skipped.
