#!/usr/bin/env python3
"""No-GPU integration tests for controller redirection, bundle and storage rules."""
import importlib.util, json, tempfile
from pathlib import Path
spec=importlib.util.spec_from_file_location("c",Path(__file__).with_name("m5_trace_capture_controller.py"));c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
with tempfile.TemporaryDirectory() as x:
 o=Path(x); log=o/'log'; c.run(['sh','-c','echo checker-pass'],stdout=log.open('w')); assert log.read_text().strip()=='checker-pass'
 p=o/'bundles/bicg/traces';p.mkdir(parents=True);(p/'kernel-1.trace').write_text('x');(p/'kernel-1.traceg').write_text('y');(p/'kernelslist').write_text('kernel-1.trace\n');(p/'kernelslist.g').write_text('kernel-1.traceg\n');(p/'stats.csv').write_text('kernel id,kernel mangled name,grid_dimX,block_dimX\nkernel-1.trace,_Zx,1,32\n')
 inv,raw,grp=c.inventory(p); assert len(inv)==len(raw)==len(grp)==1
 b=p.parent;(b/'CAPTURE_RESULT.json').write_text(json.dumps({'trace_bundle_id':'id'}));(b/'SHA256SUMS').write_text('')
 # write sums over all prior files, then validate/immutable archive and transfer.
 fs=[z for z in b.rglob('*') if z.is_file() and z.name!='SHA256SUMS'];(b/'SHA256SUMS').write_text(''.join(f'{c.sha(z)}  {z.relative_to(b)}\n' for z in fs));assert c.valid_bundle(b); arc,meta=c.archive_bundle(b); dst=o/'copy.tar.gz';dst.write_bytes(arc.read_bytes());assert c.verify_transfer(arc,dst)['status']=='PASS'
 try:c.verify_transfer(arc,o/'missing')
 except FileNotFoundError:pass
 else:raise AssertionError('bad transfer accepted')
 (o/'STORAGE_BUDGET.tsv').write_text('pilot\traw_bytes\tgrouped_bytes\tarchive_bytes\tprojected_10_raw_bytes\tfree_bytes\nBICG\t1\t1\t1\t10\t999999999999\n');assert c.storage_gate(o)['status']=='PASS'
print('PASS controller offline redirects/inventory/immutability/archive/transfer/storage gate')
