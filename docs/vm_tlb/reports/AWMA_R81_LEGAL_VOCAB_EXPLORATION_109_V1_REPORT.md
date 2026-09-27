# AWMA R81 legal vocabulary exploration on node109

**Result:** `R81_SOFTWARE_OPPORTUNITY_NO_ARCH_CLAIM`. The fixed 12-request authored fixture produced 207 grammar timesteps. C0/C1/H0 each had a median legal union of 147,068 / 151,936 rows (96.8% of the model head); broad free-text states occupied 63/78, 63/72 and 47/57 timesteps. Exact legal masks, current hidden states, prompt token IDs, matcher histories, model/head weights and selected IDs are bound in the raw authority. All arms were semantically exact on all 12 requests, all JSON outputs were valid and none truncated at 128.

| C0 shared | 78 | 63 | 611.0 | 633.1 | +3.62% |
| C1 heterogeneous | 72 | 63 | 555.7 | 561.2 | +0.98% |
| H0 holdout | 57 | 47 | 445.4 | 442.1 | -0.73% |

The direct-index A3 prototype reduced head-region time 45–53% on the pre-registered sparse stratum, including independent H0 content. Broad states cost 6.7–27.5% more than A0. Therefore there was no stable complete-generation improvement. A2 indexed-union was slower because the union was usually near full vocabulary; NSYS's separate C1 canary recorded substantially more host-to-device index/mask traffic for A2. These profiler sums are not the formal latency metric. CPU grammar compile cost is separately reported.

The exact C0 paired repeat resolved a high-variance first run without changing inputs or code; both runs remain indexed. Kestrel already performs indexed weight selection, FlashSampling establishes tiled fused selection, XGrammar supplies the legal masks, and FlashRec documents restricted SID-range projection. `SOURCE_CAPABILITY_MAP.md` records their specific scope and the limits of R81's ports. The only concrete next direction is a separate software support-aware dispatch study; this Goal stops before any architecture claim.
