"""Main-only source proposal. Not started by its author.

The reviewed old publisher is privately adapted, never edited. Existing common
PUBLOCK, explicit Main enable, reciprocal worktree validation, narrow staging,
remote SHA/fetch/manifest readback and no-overwrite leaves remain unchanged.
"""
from pathlib import Path
import hashlib,json,types
PUBLISHER_PATH='/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1/agents/L1_background_publication_v1/watch_publish_oracle_results.py'
PUBLISHER_SHA256='a6da7d0e0904daaa41593058836f3ad640ea23b6c5057b3c74e232e6ea38a5ef'
def source_module(name='unified_publisher_proposal'):
 p=Path(PUBLISHER_PATH);data=p.read_bytes()
 if hashlib.sha256(data).hexdigest()!=PUBLISHER_SHA256:raise ValueError('OLD_PUBLISHER_PIN_DRIFT')
 text=data.decode()
 if text.count("control/publication_v1/BACKGROUND_INDEX")!=1:raise ValueError('INDEX_ANCHOR_CHANGED')
 text=text.replace('control/publication_v1/BACKGROUND_INDEX','control/publication_v1/CLEAN_UNIFIED_BACKGROUND_INDEX')
 # Only commit gets a longer metadata/FS allowance. All other Git calls
 # retain the original60 seconds, and all original transaction/readback gates remain.
 timeout_anchor='capture_output=True,check=False,timeout=60)'
 if text.count(timeout_anchor)!=1:raise ValueError('GIT_TIMEOUT_ANCHOR_CHANGED')
 text=text.replace(timeout_anchor,"capture_output=True,check=False,timeout=(300 if args and args[0]=='commit' else 60))")
 m=types.ModuleType(name);m.__file__=__file__
 exec(compile(text,str(p)+'#private_explicit_index','exec'),m.__dict__)
 old=m.publication_view
 def state_view(report,matrix):
  view=old(report,matrix)
  rows=sorted(({'plan_id':r['plan_id'],'status':r.get('status'),'classification':r.get('classification'),
   'raw_status':r.get('raw_status'),'result_sha256':r.get('result_sha256'),'uuid':r.get('uuid'),
   'cycles':r.get('cycles'),'pair_status':r.get('pair_status'),'validation_error':r.get('validation_error')}
   for r in report['rows']),key=lambda r:r['plan_id'])
  state_sha=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  # The existing lifecycle's fingerprint slot is explicitly a publication
  # trigger; retain the actual S closed-result digest under its exact label.
  view['scientific_closed_result_fingerprint_sha256']=view['closed_fingerprint_sha256']
  view['closed_fingerprint_sha256']=state_sha
  view['publication_change_fingerprint_sha256']=state_sha
  view['fingerprint_contract']='Legacy publisher lifecycle slot closed_fingerprint_sha256 is the publication-state trigger; scientific_closed_result_fingerprint_sha256 retains S result digest.'
  return view
 m.publication_view=state_view
 return m
if __name__=='__main__':source_module().main()
