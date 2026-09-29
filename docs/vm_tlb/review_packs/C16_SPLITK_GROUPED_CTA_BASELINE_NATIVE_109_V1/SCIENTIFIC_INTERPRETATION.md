# Scientific interpretation

Decision: `GROUPED_MAPPING_SOLVES_MOST_SPLIT1_REUSE_PROBLEM`.

The experiment used one patched binary and a branch-free runtime mapping select.
ROW and GROUP_M16 preserved the grid, block, split/reduction behavior, scratch,
data layout, K-loop, dequantization, MMA, and address-set union.  Exhaustive
static enumeration proved complete, non-overlapping coverage of all 6144 output
tiles per split plane.  Dynamic outputs were bitwise identical by mapping.

ROW calibration passed.  Median deviations from accepted historical points were
0.67%, 1.78%, 1.53%, and 1.73% for K3072/split8, K3072/split1,
K4096/split8, and K4096/split1.  None reached the 5% materiality threshold.

For split1, GROUP_M16 produced the preregistered recovery:

| K | ROW hit | GROUP hit | hit gain | DRAM GROUP/ROW | time GROUP/ROW |
|---:|---:|---:|---:|---:|---:|
| 3072 | 63.56% | 95.95% | 32.39 pp | 0.145x | 0.724x |
| 4096 | 63.26% | 95.95% | 32.69 pp | 0.135x | 0.669x |

Miss sectors fell from 21,838,604 to 2,451,456 at K3072 and from
29,515,740 to 3,268,608 at K4096.  GROUP_M16 therefore restored almost the
entire high-hit regime and materially improved split1 timing.

Split8 was already saturated: grouped mapping changed hit by only 0.069 pp and
0.047 pp, DRAM remained approximately 1.00x, and timing improved only 1.4% and
2.6%.  Under the same GROUP_M16 mapping, split1 and split8 had essentially the
same GEMM hit rate, while split1 used only 40.3%/45.5% as much GEMM DRAM and was
38.73%/30.90% faster at K3072/K4096.  Thus no residual split8 advantage remains
at these frozen points; its earlier advantage primarily compensated for ROW
mapping locality loss plus paid reduction/output costs.

This is a classic strong software baseline, not a new mechanism.  The evidence
is limited to this AutoAWQ kernel family and synthetic GPT-3 proxy.  It does not
prove that logical block-ID adjacency is physical issue order, recommend one
GROUP_M for every W4 kernel, or represent a complete GPT-3 model.
