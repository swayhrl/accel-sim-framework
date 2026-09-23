# C16 E1 fixed-budget protected-coverage scaling interpretation

Stage label: `COVERAGE_SCALING_POSITIVE_BUT_SUBTHRESHOLD`.

Seven-run census measures stable decode shares of roughly 14.76% gate_proj, 16.84% up_proj, 15.78% down_proj, and 47.39% for all 84 FFN projections. The primary up_proj-only scaling therefore covers a measured 16.8% opportunity at N28.

All N28 selected layers retain material local D3 benefit, but median per-layer benefit dilutes from about 47.5% at N1 to about 25% at broad coverage. Run-aligned N28 whole-decode benefit is about 0.89%, positive beyond dispersion but below the registered 2% system-relevance gate. Realization of summed local savings declines as N grows. N14A and N14B produce closely matched shares, local benefit fractions, decode benefits, and realization ratios, so the curve is not an artifact of one favorable half.

The conditional FULLHINT control fires. FULLHINT_N28 changes the FAIR_N28 benefit by only about 0.08 percentage points, below the 0.5-point NCU trigger; the 1/N hint is not the main limiter in this bounded test. Critical-path NCU retains GEMM duration/stall benefit at N28 even as L2 hit/miss and DRAM-read ratios approach unity.

The evidence supports a positive but subthreshold system effect for full up_proj coverage. Because gate/down expand measured FFN projection opportunity from 16.8% to roughly 47.4%, broader operator-family coverage is the leading review candidate before simulator implementation; this producer does not authorize that next step. No simulator, NVBit capture, full trace, or mechanism implementation was run.
