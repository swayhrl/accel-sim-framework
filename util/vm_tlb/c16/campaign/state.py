"""Fail-closed, resumable C16 campaign state primitives."""
import hashlib,json,os,time
from pathlib import Path
STAGES=['ASSET_AUTHORITY','ENVIRONMENT_PREFLIGHT','INPUT_AUTHORITY','NATIVE_SMOKE','KERNEL_CENSUS','SEMANTIC_TARGET_SELECTION','SELECTIVE_STATE_CAPTURE','REPLAY_EQUIVALENCE','IN_CONTEXT_SIGNATURE_GATE','FRESH_STATIC_PATH_AUDIT','FORMAL_CAPTURE','FORMAL_ADMISSION_ACK','NCU_PROFILE','REVIEW_PACK_CLOSE']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def receipt(campaign,stage,status,inputs,outputs,next_stage,argv=None,deps=None):
 if stage not in STAGES or status not in {'PASS','BLOCKED','SKIPPED','FAIL'}:raise ValueError('invalid transition')
 return {'schema':'C16_CAMPAIGN_STAGE_RECEIPT_V1','campaign_id':campaign['campaign_id'],'model':campaign['model'],'scenario':campaign.get('scenario'),'phase':campaign.get('phase'),'stage':stage,'status':status,'inputs':inputs,'outputs':outputs,'argv':argv or [],'dependencies':deps or [],'timestamp_metadata_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'next_stage':next_stage}
def write_new(path,obj):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.partial');tmp.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n');os.replace(tmp,p)
def last_valid(root):
 out=[]
 for p in Path(root).glob('*.json'):
  try:o=json.loads(p.read_text())
  except:continue
  if o.get('schema')=='C16_CAMPAIGN_STAGE_RECEIPT_V1' and o.get('status')=='PASS':out.append((STAGES.index(o['stage']),p,o))
 return max(out) if out else None
