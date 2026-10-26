#!/usr/bin/env python3
"""Restore EP evidence from this closed bundle without the original runtime/controller."""
import argparse,hashlib,importlib.util,json,os,pathlib,subprocess
P=pathlib.Path
def need(ok,why):
 if not ok:raise RuntimeError(why)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=argparse.ArgumentParser();a.add_argument('--destination',required=True);a.add_argument('--minimum-free-bytes',type=int,required=True);args=a.parse_args()
bundle=P(__file__).resolve().parent;target=P(args.destination).resolve()
binding=json.loads((bundle/'RESTORE_TOOL_MANIFEST.json').read_text())
for name,h in binding['tool_sha256'].items():need(digest(bundle/name)==h,'tool SHA mismatch '+name)
s=importlib.util.spec_from_file_location('bundle_restore_primitives',bundle/'full_result_bundle.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
m=json.loads((bundle/'SOURCE_MANIFEST.json').read_text());v=f.import_v9((bundle/'v9_transaction.py').read_bytes())
raw=sum(r['size'] for r in m['entries'] if r['type']=='file')
need(args.minimum_free_bytes>=5*2**30+raw+16*2**20,'fresh external resource lower bound required')
need(os.uname().nodename=='huangrulin-sshfs-174','independent native174-new Target required')
def gate():
 fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(target.parent)],text=True))['filesystems'][0]
 need(fs['fstype']=='ext4','Target must be local ext4')
 st=os.statvfs(target.parent);need(st.f_bavail*st.f_frsize>=args.minimum_free_bytes,'resource lower bound HOLD')
gate();f.verify_archive(bundle,m)
proof=f.check_native(target,m) if target.exists() else f.restore(bundle,m,target,v,gate=gate)
print(json.dumps({'status':'INDEPENDENT_BUNDLE_TO_NATIVE_TARGET_RESTORE_PASS','source_bundle':str(bundle),'target':str(target),'manifest_txid':m['txid'],'tool_manifest_sha256':digest(bundle/'RESTORE_TOOL_MANIFEST.json'),'rows':proof,'runtime_or_controller_imported':False}))
