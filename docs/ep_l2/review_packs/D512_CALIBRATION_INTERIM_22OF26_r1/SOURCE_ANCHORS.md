# Source and configuration anchors

| Item | Immutable identity |
|---|---|
| D512 Core | `878f80869ce212e779df20b6421e4dc7f987825d` |
| D512 Framework | `aae62b66685f15437cecf0193934f628e6fac6ae` |
| D512 runtime composite SHA-256 | `a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416` |
| D512 Legacy overlay SHA-256 | `44d3d3ddcc96b5bee76749ad36540d24c09637b2bf2ddd28e1748be94ec45e15` |
| D512 Banked overlay SHA-256 | `492269014ee869f9023cc7ec4fb3ac8dd7da04bf96d34e2e55ffb74d040007b3` |
| Base config SHA-256 | `8ccad878b6abfec8254ecd6c7e0efee2714908dc3a04f611ff8787000e277bd3` |
| Trace-config SHA-256 | `19dd14b3a4b6c1a1cb2833bd091f0dbd485ad79336ef7d4b0c9db1f7c46f504e` |
| Formal D256 Core / Framework | `ece1a3a77c5628763e0a4605bfd1c639ee6a1495` / `f08d2ce857972fad73c4e1ab7162ba94c6336507` |

All 22 audited rows use exactly one D512 source/config tuple, the frozen
roster trace corresponding to their workload, 850 MHz, descriptor capacity
512, Line MSHR 128, per-address cap 32, WAD 128, and frozen BASE L1. The
authorized experimental delta is descriptor capacity only (256 to 512).
