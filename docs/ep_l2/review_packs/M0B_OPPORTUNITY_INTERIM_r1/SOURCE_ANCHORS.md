# Source Anchors

| Item | Exact value |
|---|---|
| promoted integrated Core parent | `1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e` |
| promoted integrated Framework runtime parent | `d61ffd23c926a25fa463a3e6e955c885b45f0f8a` |
| M0b Core candidate used by ON | `9907b7e617ea0ee6580fb8156e985838720f08fa` |
| M0b Framework candidate used by ON | `8a0299cab19a658d34b7a2dc0b6d91e8373c121b` |
| branch | `hrl/ep-l2-m0b-opportunity-v0` |
| semantic base | `EP_L2_D512_CALIBRATED`, 850 MHz, banked D512 |

ON effective ordered config inputs and SHA-256:

| Input | SHA-256 |
|---|---|
| Core QV100 base | `8ccad878b6abfec8254ecd6c7e0efee2714908dc3a04f611ff8787000e277bd3` |
| Framework trace config | `19dd14b3a4b6c1a1cb2833bd091f0dbd485ad79336ef7d4b0c9db1f7c46f504e` |
| D512 banked overlay | `492269014ee869f9023cc7ec4fb3ac8dd7da04bf96d34e2e55ffb74d040007b3` |
| ON overlay | `92ce6ea52e0d642c36e08a5c5ac4c44f935456c73600c529f7d4d2944356ab6b` |

Both modes set `-gpgpu_ep_l2_m0a_stats 1`; the only authorized OFF delta is
`-gpgpu_ep_l2_m0b_stats 1 -> 0`.  Its overlay SHA-256 is
`5e1ee872b86bde44f1d061a22fb197eaac79056a2240a5b2ba29899743810b39`.
