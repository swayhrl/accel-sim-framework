# EN-v2 absorption and reference/format audit

Upstream: `swayhrl/accel-sim-framework`, `hrl/ep-l2-iscas2027-english-editorial-v1`, exact `2d7091bf54f4aa77aca5f44e3005166dce8f7ae7`. Three original source/audit files are preserved byte-for-byte under `upstream_editorial/`; SHA-256 and byte sizes are in SOURCE_MANIFEST. No merge or overwrite of that branch or Lane6 r1–r4.

Retained: full English structure, architecture/lifetime TikZ, matched configuration table, explicit Fig.2–4 reservations, ten on-topic references, bounded novelty claims, oracle scope and retraction qualification. EN-v3 changes only draft labels/PDF subject, extracts the current result-status sentence into a guarded input file, and explicitly charges generation/owner comparisons, free-slot selection and oldest-ready arbitration. No result numbers added. Source diff is recorded in validation/EDITORIAL_DIFF.patch.

Current Lane6 independently checked the official [ISCAS author instructions](https://epapers2.org/iscas2027/ESR/authorinfo1.php) and [samples](https://epapers2.org/iscas2027/ESR/samples.php), 2026-10-17: four technical pages plus an optional reference-only fifth, Letter or A4, embedded fonts, no Type3, PDF under 5 MB, IEEEtran conference. Actual local EN-v3 compile, rather than editorial PDF assertions, establishes the page/font/overflow facts in LAYOUT_VALIDATION.json. Author information remains pending. Not submission-ready.

The upstream audit reports partial full-text inspection for nine references and publisher metadata only for Jouppi1990; that statement belongs to the editorial producer. Lane6 does not claim to have opened the user's Library PDFs. Independent checks this turn:

| Source | Directly checked support | Limit |
|---|---|---|
| [V-Way author PDF](https://hps.ece.utexas.edu/pub/qureshi_isca05.pdf) | Tag/data indirection and differing tag/data capacity, §2–3 | No external performance adopted |
| [Gebhart NVIDIA PDF](https://research.nvidia.com/sites/default/files/pubs/2012-12_Unifying-Primary-Cache/Gebhart_MICRO_2012.pdf) | SM registers/cache/scratchpad unification, kernel configuration, evaluated write-through cache, §4 | Different scope from dirty L2 writeback |
| [MiCache author source](https://github.com/CGCL-codes/MiCache) | README's shared cache/MSHR storage and named cache/MSHR/subentry components | Paper response-conversion detail remains attributed to the preserved editorial full-text audit; publisher fetch unavailable |
| DL-MSHR | Bibliography and precise write-miss-data scope carried from editorial audit | No new claim of independently reading full text; publisher/author PDF retrieval did not yield readable full text in this check |
| Other six references | Exact bibliography and rationale retained from editorial audit | No new independent full-text claim |

MiCache is a close storage-sharing precedent; FPGA platform alone does not exclude it. DL-MSHR cannot be called metadata-only. EP-L2 does not claim the first tag/data indirection, GPU unification, or transient cache storage. Its proposed distinction is dirty resident-to-WB data ownership with fixed resident tags, pool and bank budgets. This is a scoped related-work argument, not an exhaustive novelty proof. No CACTI/McPAT/GPUWattch citation substitutes for actual PPA.
