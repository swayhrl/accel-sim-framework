# Corrected Conventional Sector-L2 Resource Model

```text
SM / ICNT
   ↓
ROP fixed-latency queue
   ↓
ICNT→L2 FIFO (in order, one head examined per L2 cycle)
   ↓
non-mutating tag/MSHR admission preview
   ├── HIT          → data port → L2→ICNT response FIFO
   ├── MSHR MERGE   → merge target only
   └── NEW MISS     → eager line/sector reservation → MSHR
                              ├── demand lower read
                              └── dirty victim writeback, when selected
                                         ↓
                             shared Miss/Lower-request queue
                                         ↓
                                  L2→DRAM FIFO → MC / HBM
                                         ↓
                              DRAM→L2 FIFO → fill port
                                         ↓
                              MSHR response-ready state
                                         ↓
                                 L2→ICNT response FIFO
```

## Explicitly modeled resources

- tag/set/way reservation and configured replacement policy;
- MSHR entries and merge targets;
- shared cache miss/lower-request queue (not a dedicated WBQ);
- data and fill ports, separately;
- four memory-subpartition FIFOs;
- DRAM arbitration credits and scheduler admission;
- L2 response FIFO and ROP fixed-latency queue.

## Request-specific admission

| Action | New MSHR | New shared queue entries | Data port | Immediate RespQ |
|---|---:|---:|---:|---:|
| Read hit | 0 | 0 | yes | yes |
| Read MSHR merge | 0 | 0 | no | no |
| New clean read miss | 1 | 1 | no | no |
| New dirty-victim read miss | 1 | 2 | yes | no |
| Lazy write hit | 0 | 0 | yes | yes* |
| Lazy write miss, clean victim | 0 | 0 | no | yes* |
| Lazy write miss, dirty victim | 0 | 1 | yes | yes* |

`*` An `L1_WRBK_ACC` consumed locally does not require an upper response
slot.

## Do not overclaim

This is not a measurement of physical NVIDIA internal SRAM-bank counts,
tag-bank organization, hardware MSHR implementation, real WBQ capacity,
response virtual channels or slice pipeline width.  IPOLY remains the primary
set mapping; later mapping sensitivity must be reported separately.
