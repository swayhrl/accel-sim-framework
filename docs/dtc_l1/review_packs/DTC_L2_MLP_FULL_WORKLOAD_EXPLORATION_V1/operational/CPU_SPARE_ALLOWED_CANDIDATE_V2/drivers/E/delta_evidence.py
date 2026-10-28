"""Write only independent delta evidence; never alter qualified source/QA."""
import pathlib,hashlib,difflib,json
P=pathlib.Path;H=P(__file__).resolve().parent;D=H/'final_delta_v1';D.mkdir(exist_ok=True)
def digest(b):return hashlib.sha256(b).hexdigest()
owner=(H/'cpu_owner.py').read_bytes();extra=(H/'cpu_extra_strict.py').read_bytes()
assert digest(owner)=='4945156fe11db69f75a6f1dc39e08a0f5c7b28ef43244525f570bebbf33cf080'
assert digest(extra)=='5339e64ffd580e40c93cde4ab0ef9e1cfa92a91045d078a55a93ede37484a5de'
old=owner.decode()
for line in ["  eligible=[c for c in eligible if not(R/'control/qualification_ledger'/(c+'.INTENT.json')).exists()]\n",
 " static_old=copy.deepcopy(old);static_new=copy.deepcopy(new_cfg)\n",
 " static_old.pop('allowed_cohorts');static_new.pop('allowed_cohorts')\n",
 " assert static_old==static_new,'Scope append cannot change approval, lineage, policy, source or validation contract'\n"]:
 assert old.count(line)==1;old=old.replace(line,'')
old_owner=old.encode();assert digest(old_owner)=='fdd608eac11eca3fbffa3a118cf249455a92cb615a0bfba95cd59bd8b2bd178f'
matches=[]
for newline in ['\n','\r\n']:
 for tail in range(6):
  b=(extra.decode().rstrip().replace('\n',newline)+newline*tail).encode()
  if digest(b)=='932d6c0160e7e05289e3bafc79845d5aebcc11cf4676eb103206c794f706fcae':matches.append(b)
if not matches:
 snapshot=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/A/cpu_spare_memory_v2/CPU2_SCOPE_ki8t84t6/out/CPU_SPARE_MEMORY_ADMISSION_SNAPSHOT.json')
 previous=json.loads(snapshot.read_bytes())['source_snapshots']['extra_strict']
 preserved=previous['utf8'].encode();assert digest(preserved)==previous['sha256']=='932d6c0160e7e05289e3bafc79845d5aebcc11cf4676eb103206c794f706fcae'
 matches=[preserved]
assert len(matches)==1,'Cannot establish exact old extra preimage'
old_extra=matches[0]
(D/'cpu_owner.fdd608ea.py').write_bytes(old_owner);(D/'cpu_extra_strict.932d6c01.py').write_bytes(old_extra)
diff=''.join(difflib.unified_diff(old_owner.decode().splitlines(True),owner.decode().splitlines(True),fromfile='fdd608ea',tofile='4945156f'))
(D/'OWNER_EXACT_DIFF.patch').write_text(diff)
proofs=[]
for name in('OWNER_CPU_QUALIFICATION.json','EXTRA_CPU_QUALIFICATION.json'):
 b=(H/name).read_bytes();v=json.loads(b);assert v['status']=='PASS'
 vals=json.dumps(v);assert digest(owner)in vals and digest(extra)in vals
 proofs.append(dict(path=str(H/name),sha256=digest(b),count=v['count'],status=v['status']))
out=dict(status='EXACT_PREIMAGE_AND_FINAL_QA_IDENTITIES_VERIFIED',current_owner_sha256=digest(owner),current_extra_sha256=digest(extra),
 previous_owner_sha256=digest(old_owner),previous_extra_sha256=digest(old_extra),
 owner_logic_delta='4 added lines: exclude existing INTENT from frame witness; require scope append to preserve every config field except allowed_cohorts',
 extra_logic_changed=False,extra_difference='EOL normalization and trailing blank-line removal only',
 extra_normalized_text_equal=old_extra.decode().replace('\r\n','\n').rstrip()==extra.decode().rstrip(),
 proof_identities=proofs,source_or_QA_modified_by_this_script=False,production_changes=0,models_started=0,new_grants=0)
(D/'DELTA_AND_QA.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
