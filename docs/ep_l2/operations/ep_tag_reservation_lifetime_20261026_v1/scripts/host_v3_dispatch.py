#!/usr/bin/env python3
"""Exact finite EP lifetime native leaf. Import alone never launches or mutates."""
import sys
sys.dont_write_bytecode=True
import hashlib,importlib.util,json,os,pathlib
ROOT=pathlib.Path('/root/data/ep_tag_reservation_lifetime_20261026_v1')
CASES={'EP_NATIVE_VECTOR_TAG_LIFETIME_ON_20261026_V2'}
OPERATIONS={'prepare','inspect','status','qualify','register','run-native','accept'}
def need(x,why):
 if not x:raise RuntimeError(why)
def scope(args):
 need(len(args)==5 and args[3:]==['--project','EP_L2'],'exact native argv/project required; no extra arguments')
 namespace,operation,case=args[:3]
 need(case in CASES,'exact lifetime case required')
 need((namespace=='experiment' and operation in OPERATIONS) or (namespace=='result' and operation=='archive'),'unsupported exact lifetime native operation')
 return operation,case
def main(args):
 operation,case=scope(args)
 specpath=ROOT/'cases'/case/'control/FROZEN_SPEC.json'
 need(specpath.is_file(),'exact frozen case specification not materialized')
 s=json.loads(specpath.read_bytes());path=ROOT/'tools_v3/finite_native_runtime.py'
 need(s.get('runtime_module_path')==str(path) and s.get('runtime_module_sha256') and path.is_file(),'final exact native runtime not qualified')
 need(hashlib.sha256(path.read_bytes()).hexdigest()==s['runtime_module_sha256'],'native runtime SHA drift')
 modspec=importlib.util.spec_from_file_location('ep_tag_lifetime_exact_runtime',path);module=importlib.util.module_from_spec(modspec);sys.modules[modspec.name]=module;modspec.loader.exec_module(module)
 os.environ['EP_TAG_LIFETIME_NATIVE_ENTRY']='1'
 return module.dispatch(operation,case)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:]),sort_keys=True,indent=2))
 except Exception as error:print(json.dumps({'status':'HOLD','reason':type(error).__name__+': '+str(error),'automatic_retry':False}),file=sys.stderr);sys.exit(2)
