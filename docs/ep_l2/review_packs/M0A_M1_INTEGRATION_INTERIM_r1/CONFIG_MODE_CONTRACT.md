# Configuration and mode contract

Both modes use accepted D512 resources, 850 MHz, static payload policy, and one source/binary family.

| Mode | `m0a_stats` | Functional vector |
| --- | ---: | --- |
| `BASE_M1_STATIC` | 0 | unified=0, ro=0, tvd=0, adaptive=0 |
| `M0A_ON_M1_STATIC` | 1 | unified=0, ro=0, tvd=0, adaptive=0 |

The only runtime overlay delta is `-gpgpu_ep_l2_m0a_stats 0 -> 1`. Every manifest records semantic base `EP_L2_D512_CALIBRATED`, Core/Framework SHA, composite config digest, trace, result root, explicit mode, M0a switch, feature vector, maturity, and promotion dependencies.
