# ATA / CCD / RING comparison against paper Fig. 10

> **Non-evidentiary 0826 diagnostic.** Paper values below are extracted
> from displayed vector-bar geometry, not author raw data. Local values are
> the existing local-16 measurements rebucketed by paper R/S labels.

## Four-group averages

| Group | Design | Paper | Local | Delta |
|---|---|---:|---:|---:|
| R0S0 | ATA | 0.914 | 0.998 | +0.084 |
| R0S0 | CCD | 1.001 | 1.001 | +0.000 |
| R0S0 | RING | 0.989 | 0.756 | -0.232 |
| R1S0 | ATA | 1.015 | 1.000 | -0.016 |
| R1S0 | CCD | 1.024 | 1.000 | -0.024 |
| R1S0 | RING | 1.002 | 0.794 | -0.208 |
| R0S1 | ATA | 0.498 | 0.962 | +0.464 |
| R0S1 | CCD | 1.009 | 1.016 | +0.007 |
| R0S1 | RING | 0.815 | 0.851 | +0.036 |
| R1S1 | ATA | 0.724 | 1.004 | +0.279 |
| R1S1 | CCD | 1.024 | 1.000 | -0.024 |
| R1S1 | RING | 1.101 | 0.657 | -0.445 |

## Per-workload values

| Workload | Group | ATA paper | ATA local | Δ | CCD paper | CCD local | Δ | RING paper | RING local | Δ |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MR | R0S0 | 0.993 | 1.000 | +0.006 | 1.000 | 1.000 | -0.000 | 0.998 | 0.902 | -0.097 |
| NN | R0S0 | 0.822 | 1.000 | +0.178 | 1.001 | 1.000 | -0.001 | 1.002 | 0.705 | -0.297 |
| DW | R0S0 | 0.927 | 0.994 | +0.068 | 1.001 | 1.003 | +0.002 | 0.965 | 0.661 | -0.304 |
| CU | R1S0 | 1.020 | 0.999 | -0.020 | 1.018 | 0.999 | -0.020 | 1.018 | 0.926 | -0.093 |
| HO | R1S0 | 0.969 | 1.000 | +0.031 | 1.002 | 1.001 | -0.001 | 0.998 | 0.623 | -0.375 |
| GA | R1S0 | 1.057 | 0.999 | -0.058 | 1.052 | 1.000 | -0.052 | 0.990 | 0.834 | -0.156 |
| AT | R0S1 | 0.590 | 0.969 | +0.379 | 1.029 | 1.017 | -0.012 | 0.773 | 0.833 | +0.060 |
| BI | R0S1 | 0.555 | 0.969 | +0.414 | 0.964 | 1.046 | +0.081 | 0.784 | 0.819 | +0.035 |
| GS | R0S1 | 0.349 | 0.949 | +0.599 | 1.035 | 0.987 | -0.048 | 0.889 | 0.903 | +0.013 |
| LU | R1S1 | 1.058 | 1.001 | -0.057 | 1.032 | 1.000 | -0.031 | 1.087 | 0.744 | -0.343 |
| SG | R1S1 | 1.039 | 1.000 | -0.039 | 1.013 | 0.993 | -0.020 | 1.301 | 0.638 | -0.662 |
| 3M | R1S1 | 0.401 | 1.011 | +0.610 | 1.024 | 1.007 | -0.017 | 1.206 | 0.624 | -0.581 |
| GE | R1S1 | 0.474 | 1.008 | +0.534 | 1.050 | 1.002 | -0.049 | 1.298 | 0.626 | -0.672 |
| B+ | R1S1 | 0.757 | 0.995 | +0.237 | 1.045 | 1.001 | -0.044 | 1.075 | 0.636 | -0.438 |
| 2D | R1S1 | 0.282 | 0.993 | +0.711 | 1.004 | 0.998 | -0.005 | 0.985 | 0.635 | -0.350 |
| ST | R1S1 | 1.060 | 1.020 | -0.040 | 1.000 | 1.000 | -0.001 | 0.759 | 0.693 | -0.066 |

## Largest visual deltas

- **ATA:** 2D +0.711, 3M +0.610, GS +0.599, GE +0.534.
- **CCD:** BI +0.081, GA -0.052, GE -0.049, GS -0.048.
- **RING:** GE -0.672, SG -0.662, 3M -0.581, B+ -0.438.

Interpretation is intentionally limited to identifying where the
paper/local models disagree. It must not be read as a new measurement
or a claim that one paper mechanism is intrinsically better.
