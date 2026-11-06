# Forward correction: R1 equality is seven programs, not eight

Original frozen manifest: `6ac899ecf8fec1b9b7559a14399c028e173b68b9c1b547d809f4e237fedfea41`. Its116 members remain byte-identical.

The sentence `BothR1 combinations have identical accepted cycles onall8.` in A_HEADROOM_OVERVIEW.md:31 is incorrect. It overgeneralizes from seven equal-cycle inputs. The original32 record JSON/Markdown and both numerical matrices already preserve the correct scan values; they need no data replacement.

Use this forward paragraph in the canonical report:

The physical768 and1024 single-factor candidates have identical accepted cycles on their seven common accepted inputs; scan has no accepted single-factor value. The two R1 combinations have identical accepted cycles on seven programs, while scan uses6,680,780 cycles forPHYS768+OO-PIB192 and6,651,571 forPHYS1024+OO-PIB192, a decrease of29,209 cycles (about0.4372%) under the larger-physical combination. This is measured within the combination contract, not an isolated physical-only scan result or a theoretical saturation bound. No scan multiplicative J is available because its V1 single-factor terms are unaccepted.

|Program|PHYS768+PIB192 cycles|PHYS1024+PIB192 cycles|1024 minus768|
|---|---:|---:|---:|
|2DCONV|470776|470776|0|
|GEMM|814235|814235|0|
|MVT|30609855|30609855|0|
|BICG|30892841|30892841|0|
|ATAX|30602022|30602022|0|
|convolutionSeparable|818340|818340|0|
|scan|6680780|6651571|-29209|
|vectorAdd|217305|217305|0|

All16 actual accepted RESULT SHA/cycles and kernel sums, original record JSON, program Markdown and both matrix formats were checked (99 checksPASS). Text search finds the incorrect sentence only in the original overview, and no equivalent claim in record JSON/program reports. CORRECTION.json pins all16 actual sources. No original file, simulation, Core, controller, registry, Goal or Git state was changed.
