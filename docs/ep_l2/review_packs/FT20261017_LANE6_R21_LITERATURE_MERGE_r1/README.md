# Lane6 EN-v6 r21 — R20 literature merged into the accepted H0 manuscript

Open `EP_L2_EN_v6_r21.pdf`; editable source is `EP_L2_EN_v6_r21.tex`. This is a new revision of the existing Lane6 EN-v6/r19 paper, not a replacement of frozen packs. Four technical pages plus one reference-only page; unchanged IEEEtran fonts/margins; real H0 Fig2/Fig3 unchanged. The fourteen-entry verified R20 BibTeX library is preserved byte-for-byte; twelve keys are actually cited through IEEEtran BibTeX. The generated `.bbl` is included for rebuilding.

`CITATION_SOURCE_MAP.md` maps each cited proposition to sources and limits. `MERGE_REVIEW.md` records substantive edits and remaining scientific gaps. `SOURCE_MANIFEST.json`, `upstream_r20/`, final compiler logs, extracted pages, previews and layout audit identify inputs and validation. `FIGURE_PROVENANCE.json` links numerical figures to the original five native intakes; no numerical evidence is regenerated from prose or literature.

Build in a new scratch directory using `python3 build_paper.py --output-dir /tmp/ep-l2-r21-check`. A standard TeX install needs IEEEtran class/BST, newtx fonts, TikZ, booktabs/tabularx, cite, hyperref, microtype and BibTeX. On this host cached dependencies were supplied by `--tex-deps /tmp/ep-l2-lane6-r5-texdeps`. No third-party papers/fonts/BST are bundled.

The short literature task is complete. H0 five pairs and +0.160% geometric-mean speed-ratio gain remain the empirical result. There are no new D4/Q4 paper results in this pack. `NEXT_RESULT_INTAKE.md` preserves the existing event-driven native intake; no watcher or experiment is launched. New accepted pairs are a future data dependency, not a failure or blocker for this manuscript revision.
