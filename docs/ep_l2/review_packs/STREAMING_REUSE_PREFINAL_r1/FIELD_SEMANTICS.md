# EPL2SRV1 field contract

Each demand request is classified from the batch prestate, using the 32-B sector identity within its 128-B line.

| Class | Meaning |
| --- | --- |
| `cold_new_line_sector` | First observed sector in a never-before observed line. |
| `spatial_new_sector` | First observed sector in an already observed line; this is spatial continuation. |
| `temporal_sector_reuse` | Exact same 32-B sector observed again. |

Closure invariant is `cold + spatial + temporal = total demand sector references`; the parser rejects violations. Reuse distance applies only to temporal-sector events. `one_touch_sector_fraction` is calculated over unique sector identities, not lines. `excluded_writeback_requests` is reported separately and excluded from all classes.

