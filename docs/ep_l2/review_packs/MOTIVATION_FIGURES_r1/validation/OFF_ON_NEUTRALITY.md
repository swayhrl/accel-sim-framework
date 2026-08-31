# Final frozen-provenance OFF/ON neutrality

The raw-run comparison command was:

```text
rg '^(EPL2B0V1|EPL2M0AV1|EPL2DRAMV1|L2_char_resource_leak_free)' raw.log | sha256sum
```

The equality digest includes B0, M0a, L1 embedded in B0, DRAM, and terminal
real-resource invariant records. All three pairs have exact matching final
cycles/instructions and matching digest.

| Workload | cycles OFF/ON | instructions OFF/ON | OFF hash = ON hash | Result |
|---|---:|---:|---|---|
| vectorAdd_4M | 73,873 / 73,873 | 56,000,000 / 56,000,000 | `d477d58e9b2432361acfdf018d17572b896bcfe6b0289c3b5f9f436a756a2a24` | PASS |
| convolutionSeparable | 292,211 / 292,211 | 714,547,200 / 714,547,200 | `684f83073a3ecb78ee0d49219f30febaf64c788b5ac1df5fe98b95db79714531` | PASS |
| sad | 110,653 / 110,653 | 157,583,646 / 157,583,646 | `574b26f25f62036a082efa1d10e896eb066fa1e71548ee6ab7351bd86ac0ee59` | PASS |
