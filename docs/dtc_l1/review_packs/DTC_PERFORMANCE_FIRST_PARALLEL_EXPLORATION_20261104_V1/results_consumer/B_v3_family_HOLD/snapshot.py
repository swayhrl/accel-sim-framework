"""V3 pure reporting overlay on immutable V2 reader; no service/authority/model actions."""
from pathlib import Path
import json,hashlib,importlib.util,sys,argparse,datetime,csv,uuid,copy
import family_hold_overlay as h
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
js=lambda v:(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def base_reader():
 b=json.loads((D/'FIXED_HOLD_BINDING.json').read_bytes());V=Path(b['V2_directory']);h.require(sha(V/'MANIFEST.json')==b['V2_manifest_sha256']and sha(V/'snapshot.py')==b['V2_source_sha256'],'IMMUTABLE_V2_CHANGED');mf=json.loads((V/'MANIFEST.json').read_bytes())
 for x in mf['files']:h.require(sha(V/x['path'])==x['sha256'],'V2_MEMBER_CHANGED:'+x['path'])
 for key in ['A_runtime_manifest','approved_ops']:h.require(sha(b[key]['path'])==b[key]['sha256'],'HOLD_SCHEMA_SOURCE_CHANGED:'+key)
 sys.path.insert(0,str(V));s=importlib.util.spec_from_file_location('private_immutable_perf_reader_v2',V/'snapshot.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m,b

def collect():
 base,b=base_reader();captured={};original=base.runtime_context
 def observe(*args,**kwargs):
  ctx=original(*args,**kwargs);captured[args[1]]=ctx;return ctx
 # Private imported module only; frozenV2 source and existing reportservice are untouched.
 base.runtime_context=observe
 try:snapshot=base.collect()
 finally:base.runtime_context=original
 fixed,_,_=base.fixed_inputs();out=h.overlay(snapshot,captured,b['approved_ops']['sha256'],base.summarize,fixed);out['report_overlay_source']={'V2_manifest_sha256':b['V2_manifest_sha256'],'A_runtime_manifest':b['A_runtime_manifest'],'approved_ops':b['approved_ops'],'snapshot_source_sha256':sha(__file__),'family_overlay_source_sha256':sha(D/'family_hold_overlay.py')};out['observed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path);a=ap.parse_args();out=a.output_dir.resolve()if a.output_dir else D/'snapshots'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')+'_'+uuid.uuid4().hex[:8]);h.require(out.resolve().is_relative_to(D.resolve())and out.resolve().is_relative_to((D/'snapshots').resolve()),'OWN_REPORT_OUTPUT_ONLY');h.require(not out.exists(),'NO_REPORT_OVERWRITE');s=collect();out.mkdir(parents=True,exist_ok=False)
 for name,value in [('SNAPSHOT.json',s),('SUMMARY.json',s['summary']),('FAMILY_HOLD_REPORT.json',s['admission_hold_overlay'])]:(out/name).write_bytes(js(value))
 fields=['program','suite','input_digest','variant','route','status','accepted','cycles','S_DH','Rnew','Rold','I','cohort']
 with(out/'RESULTS.csv').open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r.get(k)for k in fields}for r in s['rows'])
 (out/'README.md').write_text('Fixed8 x4nonTag plus16CPU TagHOLD. Actualaccepted/archivednegative/unstartedfamilyHOLD/pending distinct. Explicittyped actualq.admission_holds only: noUUID/noacceptedcycles/no refund; globalq.state or speedup does not implyHOLD. All32candidateoutcomes accounted mayincludeverifiedunusedHOLD; all32closedscience requiresactualclosedRESULT for everypoint. Missingcounter!=0; tolerantzero labeled. V2fullstrict/archive/restoration proof reusedunchanged. No model/controller/registry/Git action.\n')
 files=[{'name':p.name,'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(out.iterdir())if p.is_file()];h.require(all(x['bytes']<8*1024**2 for x in files),'REPORT_OVERSIZE');(out/'MANIFEST.json').write_bytes(js({'schema':'DTC_PERF_STRUCTURE48_SNAPSHOT_MANIFEST_V3','observed_utc':s['observed_utc'],'files':files,'new_models':0,'native_writes':0,'report_source_sha256':sha(__file__)}));provider={'schema':'DTC_PERF_STRUCTURE48_READONLY_PUBLICATION_PROVIDER_V3','observed_utc':s['observed_utc'],'snapshot':str(out),'manifest':{'path':str(out/'MANIFEST.json'),'sha256':sha(out/'MANIFEST.json')},'files':files,'summary':s['summary'],'report_only':True,'baseline_source_qualified':s['source_baselines_qualified'],'all_existing_closed_results_qualified':s['summary']['verification_HOLD_points']==0,'admission_hold_metadata_qualified':not s['admission_hold_overlay']['issues'],'all32_nonTag_closed_verified':s['summary']['all32_nonTag_closed_verified'],'all32_candidates_accounted_verified':s['summary']['all32_candidates_accounted_verified'],'new_models':0,'native_writes':0};tmp=D/('PUBLICATION_PROVIDER.'+uuid.uuid4().hex+'.tmp');tmp.write_bytes(js(provider));tmp.replace(D/'PUBLICATION_PROVIDER.json');print(json.dumps({'status':'READONLY_V3_SNAPSHOT_COMPLETE','manifest':provider['manifest'],'status_counts':s['summary']['status_counts'],'unused_family_HOLD':s['summary']['unstarted_family_HOLD_points']}))
if __name__=='__main__':main()
