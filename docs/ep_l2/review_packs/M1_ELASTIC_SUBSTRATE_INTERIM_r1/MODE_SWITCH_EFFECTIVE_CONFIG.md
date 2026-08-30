# Mode-switch effective configuration

Recorded runs use the accepted calibrated D512 research baseline and retain M1 infrastructure-only behavior.

| Property | Effective value |
| --- | --- |
| Descriptor pool | `512` |
| Frequency | `850 MHz` |
| Payload policy | `static` / `0` |
| Unified Payload Pool | off |
| RO pending-state | off |
| WAD-backed TVD | off |
| Adaptive/headroom behavior | off |
| Production bypass traffic | absent |
| Resident mapping | tag `i` → payload ID `i` |
| Bank class | payload ID modulo 4 |

The parser/configuration gate rejects any non-static payload policy or enabled functional mechanism bit before simulation. Directed test fixture: `tests/ep_l2/m1_unsupported_feature.config`.

Configuration digest for all recorded rows: `a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416`.
