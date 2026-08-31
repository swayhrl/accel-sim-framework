#!/usr/bin/env python3
"""CSV-only temporal-reuse-distance redraw for the v6 nonzero blocker roster."""
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
V2=HERE.parents[0]/'PAPER_FIGURES_DRAFT_v2'/'plot_scripts'/'redraw_paper_figures.py'
spec=importlib.util.spec_from_file_location('paper_figures_v2',V2)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.ROOT=HERE;m.OUT=HERE/'figures';m.TABLES=HERE/'plotting_tables'
m.ORDER=['dwt2d','convolutionSeparable','spmv','scan','FWT_7_21','cfd_097k','btree']
m.GROUPS=[(0,4,'Low Temporal Reuse'),(4,7,'Reuse Rich')]
m.OUT.mkdir(parents=True,exist_ok=True);m.TABLES.mkdir(exist_ok=True)
A,B=m.read('FIG1V2_PANEL_A.csv'),m.read('FIG1V2_PANEL_B.csv')
rows=[r for w in m.ORDER for r in B if r['workload']==w]
m.write('FIG1_L2_TEMPORAL_REUSE_DISTANCE_NONZERO_PAPER_DRAFT.csv',rows)
m.temporal_distance(A,B)
(m.OUT/'FIG1_L2_TEMPORAL_REUSE_DISTANCE_PAPER_DRAFT.png').rename(m.OUT/'FIG1_L2_TEMPORAL_REUSE_DISTANCE_NONZERO_PAPER_DRAFT.png')
(m.OUT/'FIG1_L2_TEMPORAL_REUSE_DISTANCE_PAPER_DRAFT.svg').rename(m.OUT/'FIG1_L2_TEMPORAL_REUSE_DISTANCE_NONZERO_PAPER_DRAFT.svg')
