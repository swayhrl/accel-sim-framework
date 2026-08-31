#!/usr/bin/env python3
"""CSV-only redraw with ASCII-safe, non-overlapping distance semantics."""
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
V9=HERE.parents[0]/'PAPER_FIGURES_DRAFT_v9'/'plot_scripts'/'plot_temporal_distance_merged.py'
spec=importlib.util.spec_from_file_location('paper_figures_v9',V9)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.ROOT=HERE
m.CATS=[('1-256',['<=8','9-16','17-32','33-64','65-128','129-256'],'#1f5a85'),('257-512',['257-512'],'#eadba6'),('513-2048',['513-1024','1025-2048'],'#ea944e'),('>=2049',['2049-4096','>4096'],'#9f3d28')]
m.main()
(HERE/'figures'/'FIG1_L2_TEMPORAL_REUSE_DISTANCE_MERGED_PAPER_DRAFT.png').rename(HERE/'figures'/'FIG1_L2_TEMPORAL_REUSE_DISTANCE_SEMANTIC_LABELS_PAPER_DRAFT.png')
(HERE/'figures'/'FIG1_L2_TEMPORAL_REUSE_DISTANCE_MERGED_PAPER_DRAFT.svg').rename(HERE/'figures'/'FIG1_L2_TEMPORAL_REUSE_DISTANCE_SEMANTIC_LABELS_PAPER_DRAFT.svg')
(HERE/'plotting_tables'/'FIG1_L2_TEMPORAL_REUSE_DISTANCE_MERGED_PAPER_DRAFT.csv').rename(HERE/'plotting_tables'/'FIG1_L2_TEMPORAL_REUSE_DISTANCE_SEMANTIC_LABELS_PAPER_DRAFT.csv')
