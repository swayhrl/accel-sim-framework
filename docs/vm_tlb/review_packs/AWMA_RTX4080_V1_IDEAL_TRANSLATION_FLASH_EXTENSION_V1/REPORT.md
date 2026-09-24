# AWMA RTX4080/V1 ideal-translation Flash extension V1

Status: `PASS / COMPLETE`.

The frozen ideal-control implementation from
`hrl/awma-rtx4080-v1-ideal-translation-control-v3@5e59fbcf7e5217e91d40e5ff2e38dfd3f48a97f8`
was reused without semantic, source, platform, or parameter changes. Only the two
authorized Flash targets were run.

| target | family | C_10_80 | C_0_80 | C_ideal | S_L1 | S_ALL |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DECODE_FLASH_PRIMARY_1_STEP16 | splitkv | 73923 | 74723 | 70450 | -0.010822072 | 0.046981318 |
| DECODE_FLASH_PRIMARY_2_STEP16 | splitkv-combine | 10480 | 10312 | 8835 | 0.016030534 | 0.156965649 |

`S_L1=(C_10_80-C_0_80)/C_10_80` and
`S_ALL=(C_10_80-C_ideal)/C_10_80`.

`S_ALL` is the causal response to this specific ideal-translation intervention.
It is not a translation runtime fraction. `S_ALL-S_L1` is not a PTW fraction.
No monotonicity requirement against 0/80 or 10/80 was applied.

Both runs matched accepted instructions, CTA, and UID coverage; had zero
untranslated/unobserved accesses and duplicate attempts; were terminal and
quiescent; and had zero modeled lookup/MSHR/PWQ/walker/PTW/PWC/PTE activity.
