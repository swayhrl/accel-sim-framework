#!/usr/bin/env python3
"""Static M5.0BT regression: all checker aliases and controller invariants."""
import subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
poly=ROOT/'util/dtc_l1/verify_m5_polybench_output.py'
aliases={'bicg':'bicg','atax':'atax','gemv':'gemv','mvt':'mvt','syrk':'syrk','gesu':'gesu','syr2k':'syr2k','2mm':'2mm','2dconv':'conv2d'}
with tempfile.TemporaryDirectory() as t:
 p=Path(t)/'valid.log'
 for internal,checker in aliases.items():
  p.write_text('Number of misses: 0\n' if checker=='gemv' else 'Non-Matching CPU-GPU Outputs Beyond Error Threshold of 0.05 Percent: 0\n')
  subprocess.run([sys.executable,str(poly),checker,str(p)],check=True,stdout=subprocess.PIPE,text=True)
text=(ROOT/'util/dtc_l1/m5_trace_capture_controller.py').read_text()
assert 'DYNAMIC_KERNEL_RANGE",None' in text and 'RETRY_READY' in text and 'CAPTURE_RESULT_MANIFEST.tsv' in text
assert 'DYNAMIC_KERNEL_RANGE' in text and 'NVBit archive lacks required' in text
print('PASS M5.0BT checker aliases=9; Error Threshold accepted; resumable controller contract present')
