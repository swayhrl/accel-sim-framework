---
name: paper-experiment-audit
description: Evidence-grounded reading of original architecture/AI-system papers by individual experiment group, workload, control variables, hardware and evidence tier; useful for AI-ARCH P01/P13 literature work and AWMA nearest-neighbor checks. Do not use to invent unreported settings or start benchmarks.
---

# Paper experiment group audit

## Scope

Use this on a specific source paper or a bounded paper set when extracting workload choices, comparing scientific baselines, screening architectural opportunities, or designing a minimal experiment. Prefer official paper/conference/arXiv original PDFs or author repositories (pin versions), not second-hand abstracts. Only report parts directly verified; call the rest `未核实`. `未披露` means *not disclosed in the examined version/sections*, not that no version anywhere contains it.

Do **not** treat a paper's entire model list as if every figure used those models. Do not turn an author estimate, kernel microbenchmark, local replay or simulator forecast into an end-to-end native result. Do not infer the authors' motivation from our own choice rationale.

## Procedure

1. **Register original source/version**: title, authors, venue/year or preprint version, URL, PDF/repository revision, sections/figures/tables and reading depth (full text, section checked, abstract only).
2. **Split by actual experiment group** (one row per logically distinct question/measurement). Extract purpose; models vs synthetic/custom configs/checkpoints; weights/shape/precision; input generation and exact length; phase; software backend; platform; variables varied; controls held fixed; baseline strength; measured metric and statistical unit.
3. **Classify evidence**: actual on-GPU native model execution, standalone kernel native, functional/architectural simulator, trace/replay, analytic estimate or projection, accuracy/quality test, source-only, hypothetical. Multiple tiers within one paper stay in separate rows.
4. **Author vs inference**: separately record authors' explicit reason for selecting workload/setup and our methodological interpretation. Mark contradictions, confounds, unreported fields and limitations; don't repair missing data with typical values.
5. **Compare nearest work**: distinguish the exact capability already provided by a strong software baseline, the paper's causal claim and what remains unknown. Evidence from another GPU generation cannot be silently treated as Ada/RTX4080 native.
6. **Convert to research questions** only if asked: propose up to 2-3 falsifiable hypotheses with baseline, diagnostic intervention/oracle, expected observables, controls, negative/STOP condition and *untouched independent validation*. Map available 109/174/164 assets **after** defining questions; a model being downloaded is not a reason to assign it an experiment. Discovery probes must be separately authorized; hardware mechanisms require strong baseline plus meaningful remaining constraint.

## Coordination limits

AI-ARCH covers training and inference, LLM and non-LLM, single/multi-GPU and CPU–GPU. P01/P13 currently ask how GPU bottlenecks change with execution scale/resources. NanoFlow and MPK are *reading leads*, not sources of local native claims. AWMA and C16 frozen outcomes are comparison anchors, not automatically reusable input identities or permissions. Do not modify the AI-ARCH atlas, any experiment or holdout without explicit instruction.

## Output

Follow [references/EXPERIMENT_GROUP_TEMPLATE.md](references/EXPERIMENT_GROUP_TEMPLATE.md); prefer an auditable Markdown table with one row per experiment group and source position. In Chinese, summarize the author's question, setup, measured vs modeled conclusion, where comparison is confounded, and our proposed next *design* action. Label `作者明确说明`, `我们的归纳`, `未披露`, and `未核实` separately.
