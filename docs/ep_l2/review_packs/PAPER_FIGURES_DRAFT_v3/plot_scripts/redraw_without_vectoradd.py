#!/usr/bin/env python3
"""Paper-figure v3: CSV-only redraw excluding vectorAdd_4M."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
V2 = HERE.parents[0] / "PAPER_FIGURES_DRAFT_v2" / "plot_scripts" / "redraw_paper_figures.py"
spec = importlib.util.spec_from_file_location("paper_figures_v2", V2)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

module.ROOT = HERE
module.OUT = HERE / "figures"
module.TABLES = HERE / "plotting_tables"
module.ORDER = [name for name in module.ORDER if name != "vectorAdd_4M"]
module.GROUPS = [(0, 1, "Streaming / Spatial"), (1, 8, "Low Temporal Reuse"), (8, 12, "Reuse Rich")]
module.main()
