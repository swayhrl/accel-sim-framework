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
assert 'class WorkloadSpec' in text and 'valid BICG bundle/archive and storage admission receipt required' in text
assert 'git(p,"ls-files","-s")' in text
assert 'kernel_invocation_manifest_sha' in text and 'kernel_geometry_manifest_sha' in text
assert '"spmv_wrapper"' in text and '"parboil"' in text and '"matrix_sha256"' in text
tsv=(ROOT/'docs/dtc_l1/m5/trace/PAPER10_TRACE_CAPTURE_MANIFEST.tsv').read_text().splitlines()
hdr=tsv[0].split('\t'); col=hdr.index('trace_capture_build_contract')
assert all('sm_52' not in x.split('\t')[col] for x in tsv[2:] if x)
handoff=(ROOT/'docs/dtc_l1/m5/AUTODL_V100_CAPTURE_HOST_HANDOFF.md').read_text()
assert '--workloads bicg --pilot-only' in handoff and '--spmv-wrapper' not in handoff.split('## Exact BICG pilot command',1)[1].split('The expected',1)[0]
orchestrator=(ROOT/'util/dtc_l1/m5_autodl_capture_orchestrator.sh').read_text()
assert 'M5_CONTROL_CHECKOUT_PREPARED' in orchestrator and 'TRACER_PIN_CHECKOUT_PREPARED' in orchestrator and 'rsync -a --partial --append-verify' in orchestrator
print('PASS M5.0BT checker aliases=9; workload-spec/TSV/AutoDL contract present')
