#!/usr/bin/env python3
"""Portable offline EPET component decoder and display CLI; never model acceptance.
render requires independently supplied ordered kernel UID/name catalog.
synthetic-cpu is an explicit separate engineering mode, never an application.
"""
from __future__ import annotations
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,importlib.util,json,os,pathlib,stat
P=pathlib.Path;HERE=P(__file__).resolve().parent
PINS={'epet_decoder.py':'f20c6795bf770c41a19928f972d6f1eb7f948cf988f07136a61b1cbd502e5e8f','event_timeline_views.py':'1c38835957bad229a0e2ff98bbc998ce934e0cd4a72456d480fa293042673872','ep-l2-event-timeline-contract.json':'e5b078dc5a544c9ae5ba0d3415b017be92f2961b36e8a7ad2a219098388f8bfa','ep-l2-event-timeline.h':'43abce5b30c3628e9ee7232f2f98c5a1c1bd471537f05139869be82df098f978'}
GEOMETRY={'slices':64,'sets':32,'ways':8}
class Rejected(ValueError):pass
def need(ok,msg):
 if not ok:raise Rejected(msg)
def sha(path):
 h=hashlib.sha256()
 with P(path).open('rb')as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()
def safe_path(value):
 original=P(value);need('..'not in original.parts,'parent traversal is not accepted; use a direct path')
 p=P(os.path.abspath(str(original)))
 for item in [*reversed(p.parents),p]:
  try:st=item.lstat()
  except FileNotFoundError:continue
  need(not stat.S_ISLNK(st.st_mode),'symlink rejected: '+str(item))
 return p
def regular(value):
 p=safe_path(value);need(p.is_file()and stat.S_ISREG(p.stat().st_mode),'regular input file required: '+str(p));return p
def load(name):
 p=regular(HERE/name);need(sha(p)==PINS[name],'bundled implementation SHA drift: '+name)
 sp=importlib.util.spec_from_file_location('_portable_'+name.replace('.','_'),p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def catalog(path):
 p=regular(path);need(p.stat().st_size<=1<<20,'catalog <=1MiB');value=json.loads(p.read_bytes());need(type(value)is list and 1<=len(value)<=64,'explicit ordered catalog list of1..64 kernels');seen=set()
 for row in value:
  need(type(row)is dict and set(row)=={'uid','name'}and type(row['uid'])is int and 0<=row['uid']<(1<<64)-1 and row['uid']not in seen,'unique uint64 UID and exact uid/name keys')
  need(type(row['name'])is str and 0<len(row['name'].encode('utf8'))<=255,'complete bounded UTF8 kernel name');seen.add(row['uid'])
 return p,value
def exclusive_json(path,value):
 data=(json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf8')
 with P(path).open('xb')as f:f.write(data)
def run(raw,out_root,*,contract=None,header=None,kernel_catalog=None,synthetic_cpu=False):
 """Read raw once via pinned decoder, then display retained events only.
 Source/input/native/scientific authority is deliberately external and ungranted.
 """
 need(type(synthetic_cpu)is bool,'explicit mode')
 raw=regular(raw);contract=regular(contract or HERE/'ep-l2-event-timeline-contract.json');header=regular(header or HERE/'ep-l2-event-timeline.h')
 need(sha(contract)==PINS['ep-l2-event-timeline-contract.json']and sha(header)==PINS['ep-l2-event-timeline.h'],'exact78f4 contract/header identity required')
 expected=None;catpath=None
 if kernel_catalog is not None:catpath,expected=catalog(kernel_catalog)
 need(synthetic_cpu or expected is not None,'render requires --kernel-catalog; never infer its independent expectation from the same wire')
 output=safe_path(out_root);need(not os.path.lexists(output),'outputroot must be fresh; no overwrite or merge');need(output.parent.is_dir(),'outputroot parent must already exist')
 need(not raw.is_relative_to(output)and not output.is_relative_to(raw),'input/output disjoint')
 decoder=load('epet_decoder.py');converter=load('event_timeline_views.py')
 verified=decoder.decode(raw,contract,PINS['ep-l2-event-timeline-contract.json'],expected_geometry=GEOMETRY,synthetic=synthetic_cpu,header_path=header,header_sha256=PINS['ep-l2-event-timeline.h'],expected_kernel_catalog=expected)
 # No output is created on decode/catalog rejection. Reserve a unique root once.
 output.mkdir(mode=0o700);safe_path(output);view=output/'views';need(not os.path.lexists(view),'fresh views directory')
 verified_path=output/'VERIFIED_EPET_COMPONENT.json';exclusive_json(verified_path,verified)
 # Exact original converter bytes; only its output confinement root is rebound.
 converter.ROOT=output;rendered=converter.render(verified_path,contract,view)
 report={'status':'OFFLINE_EP_ET_COMPONENT_AND_VIEWS_ONLY_NOT_APPLICATION_ACCEPTED','mode':'SYNTHETIC_CPU_ENGINEERING'if synthetic_cpu else'APPLICATION_WIRE_COMPONENT_ONLY','synthetic_fixture':synthetic_cpu,'raw':{'path':str(raw),'sha256':verified['raw_sha256']},'contract':{'path':str(contract),'sha256':PINS['ep-l2-event-timeline-contract.json']},'header':{'path':str(header),'sha256':PINS['ep-l2-event-timeline.h']},'expected_geometry':GEOMETRY,'kernel_catalog':None if catpath is None else{'path':str(catpath),'sha256':sha(catpath)},'modules':{name:{'path':str(HERE/name),'sha256':digest}for name,digest in PINS.items()if name.endswith('.py')},'wrapper':{'path':str(P(__file__).resolve()),'sha256':sha(__file__)},'verified_component':{'path':str(verified_path),'sha256':sha(verified_path)},'views_manifest':{'path':str(view/'VIEW_MANIFEST.json'),'sha256':sha(view/'VIEW_MANIFEST.json')},'retained_unique_events':rendered['events'],'display_coordinate':'global recorded ordinal; synthetic display steps, never physical seconds/ns/ps','retained_unknowns_and_generation_namespaces_preserved':True,'event_capture_coverage':'BOUNDED_SELECTED_WINDOWS_ONLY','source_binary_or_input_identity_qualified':False,'scientific_acceptance_granted':False,'model_executed':False,'actor_imported':False}
 exclusive_json(output/'OFFLINE_VIEW_PACKAGE_RECEIPT.json',report);return report

def main():
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='operation',required=True)
 for name in ['render','synthetic-cpu']:
  a=sub.add_parser(name);a.add_argument('--raw',required=True);a.add_argument('--out-root',required=True);a.add_argument('--contract');a.add_argument('--header');a.add_argument('--kernel-catalog',required=name=='render')
 args=p.parse_args()
 try:r=run(args.raw,args.out_root,contract=args.contract,header=args.header,kernel_catalog=args.kernel_catalog,synthetic_cpu=args.operation=='synthetic-cpu');print(json.dumps({'status':r['status'],'mode':r['mode'],'events':r['retained_unique_events'],'receipt':str(P(args.out_root)/'OFFLINE_VIEW_PACKAGE_RECEIPT.json')}))
 except(ValueError,KeyError,TypeError,OSError)as e:print(json.dumps({'status':'OFFLINE_VIEW_REJECTED','reason':str(e)}),file=sys.stderr);return 2
 return 0
if __name__=='__main__':raise SystemExit(main())
