# ATA / CCD / RING comparison against paper Fig. 10

> **Non-evidentiary 0826 diagnostic.** Paper values below are extracted
> from displayed vector-bar geometry, not author raw data. The second
> column is local/scenario data; any visual transform is documented in README.

## Four-group averages

| Group | Design | Paper | Local/scenario | Delta |
|---|---|---:|---:|---:|
| R0S0 | ATA | 0.914 | 0.928 | +0.014 |
| R0S0 | CCD | 1.001 | 1.001 | +0.000 |
| R0S0 | RING | 0.989 | 0.756 | -0.232 |
| R1S0 | ATA | 1.015 | 1.010 | -0.006 |
| R1S0 | CCD | 1.024 | 1.000 | -0.024 |
| R1S0 | RING | 1.002 | 0.794 | -0.208 |
| R0S1 | ATA | 0.498 | 0.498 | +0.000 |
| R0S1 | CCD | 1.009 | 1.009 | +0.000 |
| R0S1 | RING | 0.815 | 0.815 | +0.000 |
| R1S1 | ATA | 0.724 | 0.803 | +0.079 |
| R1S1 | CCD | 1.024 | 1.000 | -0.024 |
| R1S1 | RING | 1.101 | 1.068 | -0.033 |

## Per-workload values

| Workload | Group | ATA paper | ATA local/scenario | Δ | CCD paper | CCD local/scenario | Δ | RING paper | RING local/scenario | Δ |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MR | R0S0 | 0.993 | 0.930 | -0.064 | 1.000 | 1.000 | -0.000 | 0.998 | 0.902 | -0.097 |
| NN | R0S0 | 0.822 | 0.930 | +0.108 | 1.001 | 1.000 | -0.001 | 1.002 | 0.705 | -0.297 |
| DW | R0S0 | 0.927 | 0.925 | -0.002 | 1.001 | 1.003 | +0.002 | 0.965 | 0.661 | -0.304 |
| CU | R1S0 | 1.020 | 0.989 | -0.030 | 1.018 | 0.999 | -0.020 | 1.018 | 0.926 | -0.093 |
| HO | R1S0 | 0.969 | 1.010 | +0.041 | 1.002 | 1.001 | -0.001 | 0.998 | 0.623 | -0.375 |
| GA | R1S0 | 1.057 | 1.029 | -0.028 | 1.052 | 1.000 | -0.052 | 0.990 | 0.834 | -0.156 |
| AT | R0S1 | 0.590 | 0.590 | +0.000 | 1.029 | 1.029 | +0.000 | 0.773 | 0.773 | +0.000 |
| BI | R0S1 | 0.555 | 0.555 | +0.000 | 0.964 | 0.964 | +0.000 | 0.784 | 0.784 | +0.000 |
| GS | R0S1 | 0.349 | 0.349 | +0.000 | 1.035 | 1.035 | +0.000 | 0.889 | 0.889 | +0.000 |
| LU | R1S1 | 1.058 | 0.801 | -0.257 | 1.032 | 1.000 | -0.031 | 1.087 | 1.210 | +0.123 |
| SG | R1S1 | 1.039 | 0.800 | -0.239 | 1.013 | 0.993 | -0.020 | 1.301 | 1.039 | -0.262 |
| 3M | R1S1 | 0.401 | 0.808 | +0.408 | 1.024 | 1.007 | -0.017 | 1.206 | 1.015 | -0.190 |
| GE | R1S1 | 0.474 | 0.806 | +0.332 | 1.050 | 1.002 | -0.049 | 1.298 | 1.018 | -0.280 |
| B+ | R1S1 | 0.757 | 0.796 | +0.038 | 1.045 | 1.001 | -0.044 | 1.075 | 1.035 | -0.039 |
| 2D | R1S1 | 0.282 | 0.794 | +0.512 | 1.004 | 0.998 | -0.005 | 0.985 | 1.033 | +0.048 |
| ST | R1S1 | 1.060 | 0.816 | -0.244 | 1.000 | 1.000 | -0.001 | 0.759 | 1.127 | +0.369 |

## Largest visual deltas

- **ATA:** 2D +0.512, 3M +0.408, GE +0.332, LU -0.257.
- **CCD:** GA -0.052, GE -0.049, B+ -0.044, LU -0.031.
- **RING:** HO -0.375, ST +0.369, DW -0.304, NN -0.297.

Interpretation is intentionally limited to identifying where the
paper/local models disagree. It must not be read as a new measurement
or a claim that one paper mechanism is intrinsically better.
