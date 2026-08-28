# C2P-Cache figure index

This is the curated, reviewer-facing figure tree for the C2P-Cache work.
It intentionally separates editable paper-figure redraws from measured local
results.  Campaign directories under `hw_run/` retain their raw, re-runnable
outputs and are not a publication-asset directory.

## Layout

| Directory | Contents | Primary source / provenance |
|---|---|---|
| `paper-redraw/` | Editable redraws of the reference paper's Fig. 1, 4(a--d), 5, 6, and 9; each current redraw has `.drawio`, `.svg`, `.pdf`, and `.png`.  `c2p_paper_fig5_layout_simplified.*` is a separate, intentionally simplified Fig. 5 variant and does not replace the paper redraw. | The editable `.drawio` is authoritative; PDF/SVG/PNG are synchronized exports. |
| `paper-redraw/archive/` | Superseded but retained export variants. | Not for citation or new edits. |
| `mechanism-schematics/` | Original explanatory diagrams for the local C2P design and its proposed extensions. | Editable `.drawio` source and synchronized PDF/SVG/PNG exports. |
| `local-results/paper16-local-rs64/` | Local 64KiB-L1 paper16 results: Fig. 3 and Fig. 10--14 in vector and preview formats. | Audited `paper16_cases.csv` / `paper16_modes.csv` from the C2P experiment branch. |
| `tables/` | Local Table 1--3 LaTeX sources plus compiled PDFs. | `.tex` is authoritative. |
| `0826/fig3-paper-inferred16/` | Non-evidentiary diagnostic: publisher-vector Fig. 3 with eight inferred extension-suite points removed. | Rebuild script, source-vector export, and explicit inference map; not a formal result or paper figure. |
| `0826/fig10-paper-rs-rebucket16/` | Non-evidentiary diagnostic: existing local Fig. 10 values rebucketed by the paper's R/S labels. | Rebuild script, SVG-derived local values, paper-vector comparison, and explicit limitations; not a formal result or paper figure. |
| `0826/fig10-paper-rs-rebucket16-r1s1-mismatch-plus10/` | Non-evidentiary what-if: +10% C2P IPC applied only to paper-R1S1/local-mismatch workloads. | Sensitivity-only reuse of the parent rebucketing script; not new simulation data, a formal result, or a paper figure. |

## Local-result provenance

- `fig3_local_rs64_*` is rendered by the C2P experiment branch's
  `scripts/plot_c2p_paper_fig3.py` from the final campaign's
  `paper16_cases.csv`.  Its `fig3_local_rs64_points.csv` records every plotted
  point, rather than making the scatter depend on a hand-copied table.
- `fig10_*` through `fig14_*` are the final paper16 exports.  Their metric and
  style contract is retained as `figure_style_audit.md` in the same directory.
- The local 64KiB classification is `R = oracle_peer_hits / eligible_L1_misses`
  at 200-cycle L2 and `S = IPC(L2=50) / IPC(L2=200)`; the Fig. 3 guide lines
  use `R=0.30` and `S=1.10`.

## Editing and release rule

1. Edit a source (`.drawio`, `.tex`, or plotting script/data), never a PNG or
   PDF directly.
2. Re-export all published formats after an edit.
3. Keep raw campaign output in its own run directory; copy only a reviewed,
   named release into this tree.
4. Add a new result family below `local-results/<campaign-name>/`; do not add
   loose files at this directory's root.
