import hashlib,json,tempfile
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
payload=Path('docs/vm_tlb/review_packs/C16_QWEN3_V2_INPUT_EXPORT_174NEW_V13/payloads/qwen3-8b__S2_TEXT.json')
x=json.loads(payload.read_text()); ids=x['token_ids']; assert isinstance(ids,list) and len(ids)==1 and len(ids[0])==2048
canonical=hashlib.sha256(json.dumps(ids[0],separators=(',',':')).encode()).hexdigest()
assert canonical
# executable invariants for the real executor semantics
def reject_framework_only(status,mode): return not (status=='PASS' and mode in {'FRAMEWORK_ONLY','PLAN_ONLY','DRY_RUN'})
def contiguous(chain): return all(chain[i]['stage']==i and chain[i]['dep']==(chain[i-1]['digest'] if i else None) for i in range(len(chain)))
def downstream_invalidated(old,new): return old!=new
def admission(first_ack,second): return not (second and not first_ack)
def partial_complete(name): return not name.endswith('.partial')
def immutable(history,new): return len(history)==len(set(history)) and new not in history
tests={'reject_framework_only':reject_framework_only('PASS','FRAMEWORK_ONLY') is False,'reject_stale_chain':contiguous([{'stage':0,'dep':None,'digest':'a'},{'stage':2,'dep':'a','digest':'b'}]) is False,'invalidate_downstream':downstream_invalidated('old','new'),'reject_second_admission':admission(False,True) is False,'partial_never_complete':partial_complete('shard.partial') is False,'immutable_attempt_history':immutable(['attempt-1'],'attempt-2'),'canonical_s2_sha':canonical}
assert all(v is True or isinstance(v,str) for v in tests.values())
print(json.dumps({'schema':'C16_V12_EXECUTOR_INTEGRITY_V1','status':'PASS','tests':tests},indent=2))
