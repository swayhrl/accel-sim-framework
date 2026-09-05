#!/usr/bin/env python3
"""No-GPU regression for M5.0BT immutability, resume and spec contracts."""
import importlib.util,json,tempfile
from pathlib import Path
spec=importlib.util.spec_from_file_location("c",Path(__file__).with_name("m5_trace_capture_controller.py"));c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
def sums(b):
 (b/"SHA256SUMS").write_text("".join(f"{c.sha(p)}  {p.relative_to(b)}\n" for p in sorted(x for x in b.rglob("*") if x.is_file() and x.name!="SHA256SUMS")))
def bundle(root,w="bicg"):
 b=root/"bundles"/w;t=b/"traces";t.mkdir(parents=True)
 for n,v in {"application.stdout":"ok","tracer.stderr":"","correctness.log":"PASS","postprocess.stdout":"PASS"}.items():(b/n).write_text(v)
 (t/"kernel-1.trace").write_text("raw");(t/"kernel-1.traceg").write_text("grouped");(t/"kernelslist").write_text("kernel-1.trace\n");(t/"kernelslist.g").write_text("kernel-1.traceg\n");(t/"stats.csv").write_text("kernel id,kernel mangled name,grid_dimX,grid_dimY,grid_dimZ,block_dimX,block_dimY,block_dimZ\n0,_Zx,1,1,1,32,1,1\n")
 inv,geo,_,_=c.inventory(t);(b/"kernel_invocation_manifest.json").write_text(json.dumps(inv));(b/"kernel_geometry_manifest.json").write_text(json.dumps(geo));(b/"CAPTURE_RESULT.json").write_text(json.dumps({"trace_bundle_id":"id-"+w,"kernel_invocation_count":1}));sums(b);return b
with tempfile.TemporaryDirectory() as x:
 o=Path(x);b=bundle(o);assert c.valid_bundle(b)
 # D: all checksum hazards fail closed.
 bad=o/"bad";bad.mkdir()
 for name,content in {"empty":"","malformed":"x","absolute":"0"*64+"  /etc/passwd\n","escape":"0"*64+"  ../x\n","duplicate":"0"*64+"  x\n"+"0"*64+"  x\n"}.items():
  q=bad/name;q.mkdir();(q/"CAPTURE_RESULT.json").write_text("{}");(q/"SHA256SUMS").write_text(content);assert not c.valid_bundle(q),name
 (b/"SHA256SUMS").write_text((b/"SHA256SUMS").read_text().replace("application.stdout","missing"));assert not c.valid_bundle(b);sums(b)
 (b/"SHA256SUMS").write_text((b/"SHA256SUMS").read_text().replace("a","b",1));assert not c.valid_bundle(b);sums(b)
 # E: valid bundle with no archive performs archive only; no capture mutation.
 before=c.sha(b/"CAPTURE_RESULT.json");assert not c.valid_archive(o,"bicg");arc=c.archive(o,b);assert c.valid_archive(o,"bicg") and c.sha(b/"CAPTURE_RESULT.json")==before
 # G: an archive failure leaves the scientifically valid bundle non-final.
 failing=bundle(o,"atax");oldrun=c.run;c.run=lambda *a,**k: (_ for _ in ()).throw(RuntimeError("injected archive failure"))
 try:c.archive(o,failing)
 except RuntimeError:pass
 else:raise AssertionError("injected archive failure accepted")
 finally:c.run=oldrun
 assert c.valid_bundle(failing) and not c.valid_archive(o,"atax") and not c.receipt(o,"atax").exists()
 # F: valid archive with no receipt transfers only.
 assert not c.receipt(o,"bicg").exists();dst=o/"copy/bicg.tar.zst";c.transfer(o,"bicg",dst);assert c.receipt(o,"bicg").is_file() and c.sha(arc)==c.sha(dst)
 # H: global rows are deterministic and only archive-backed.
 c.global_manifest(o);first=(o/"CAPTURE_RESULT_MANIFEST.tsv").read_text();c.global_manifest(o);assert first==(o/"CAPTURE_RESULT_MANIFEST.tsv").read_text() and len(first.splitlines())==2
 # C: a single non-BICG request cannot evade admission.
 try:c.gate(o)
 except RuntimeError:pass
 else:raise AssertionError("non-BICG gate accepted absent receipt")
 a,_=c.paths(o,"bicg");(o/"STORAGE_ADMISSION.json").write_text(json.dumps({"bicg_trace_bundle_id":"id-bicg","bicg_archive_sha256":c.sha(a),"raw_bytes":1,"grouped_bytes":1,"archive_bytes":1,"working_headroom_bytes":1,"safety_factor":1,"projected_bytes":4,"free_bytes":999999,"data_volume":str(o),"admission":"PASS"}));assert c.gate(o)["status"]=="PASS"
 # L: ordered correspondence rejects reordering.
 t=b/"traces";(t/"kernelslist.g").write_text("kernel-2.traceg\n")
 try:c.inventory(t)
 except RuntimeError:pass
 else:raise AssertionError("reordered replay list accepted")
 # A/B: a BICG selection has no SpMV dependency and only pins requested roots.
 m=o/"manifest.tsv";old=c.MANIFEST;c.MANIFEST=m
 poly=o/"poly";(poly/"CUDA/BICG").mkdir(parents=True);(poly/"CUDA/BICG/bicg.cu").write_text("x")
 m.write_text("thesis_id\tsource_sha256\nbicg\t"+c.sha(poly/"CUDA/BICG/bicg.cu")+"\n")
 tracer=o/"tracer";tracer.mkdir();nv=o/"nvbit.tar";nv.write_text("x")
 class A: pass
 z=A();z.workloads="bicg";z.pilot_only=True;z.polybench_src=poly;z.tracer_framework_src=tracer;z.nvbit_archive=nv;z.spmv_wrapper=None;z.parboil_src=None;z.spmv_input_dir=None;z.spmv_reference=None
 oldgit,oldtree=c.git,c.tree;c.git=lambda p,*q: ("" if q[0]=="status" else c.PIN if p==tracer else c.POLY_PIN if p==poly else "");c.tree=lambda p:"tree";assert c.sources(z,c.specs(z))["polybench"]["tree"]=="tree";c.git,c.tree,c.MANIFEST=oldgit,oldtree,old
print("PASS M5.0BT controller: fail-closed sums, archive/transfer resume, storage gate, ordered replay, BICG-only spec")
