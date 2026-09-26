# Native B1 diagnostic preregistration

Recorded after all four B0 qualification results and before any Native B1
result.

## Selection

- L1: 1,053,975 L1 launches, 1,052,216 hits (99.83%), 1,759 misses,
  MSHR/PWQ full zero.
- M1: 131,916 L1 launches, 131,584 hits (99.75%), 332 misses,
  MSHR/PWQ full zero.
- L2: 4,609 L1 launches, 4,321 hits (93.75%), 288 misses,
  MSHR/PWQ full zero.
- M2: only four L1 launches and two PTWs; remains B0-only
  `LOW_TRANSLATION_DEMAND_CONTROL`.

Therefore L1/M1/L2 follow Case H and receive exactly the already accepted B1-
equivalent 0/80 path diagnostic. No miss/walker or capacity diagnostic is
preregistered.

## Frozen comparison

- baseline: each target's B0 `WARP_VPN_DEDUP_REFERENCE` at 10/80;
- diagnostic: same binary, grouping, trace, mapping, ports and resources with
  the conservative VIPT-like timing equivalence at 0/80;
- no B2, zero-all, parameter sweep, MPW/LATPC emulation, or mechanism code.

## Decision

A positive cycle reduction greater than 1% is `MATERIAL_PATH_SENSITIVITY`, a
project threshold inherited from the accepted post-classic diagnostic. Raw
responses are reported regardless of sign.

It becomes `ACCESS_PATH_MODEL_SENSITIVE_ONLY` when B1 explains the response and
no distinct miss-side resource remains material. A new problem requires a
finite residual that survives B1 and is differentiated from closest work.

Maximum Native diagnostic replays committed here: three of the allowed six.
