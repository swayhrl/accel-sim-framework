import csv,hashlib,json,shutil,subprocess
from collections import Counter
from pathlib import Path
wt=Path('/home/huangrulin/workspace/worktrees/accel-sim-deepseek-v27');b=Path('/data/c16/deepseek_v27');s2=Path('/data/c16/deepseek_v26');p=wt/'docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_S3_MIXED_QK_109_V27'
if p.exists():raise SystemExit('pack exists')
def sha(x):
 h=hashlib.sha256()
 with Path(x).open('rb') as f:
  for z in iter(lambda:f.read(1048576),b''):h.update(z)
 return h.hexdigest()
def cp(a,c):c.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a,c)
p.mkdir();(p/'evidence').mkdir();(p/'formal').mkdir();(p/'ncu').mkdir()
for n in ['QK_REPLAY.json','QK_SIGNATURE.json','QK_static.tsv','QK_static.log','QK_FORMAL_AUDIT.json','qk_incontext_r1.nsys-rep','qk_replay.nsys-rep']:cp(b/n,p/'evidence'/n)
for n in ['PERSISTENT_MLA_LIFETIME.json','EXACT_STATE_CHAIN.json']:cp(b/'state'/n,p/'evidence'/n)
cp(b/'QK_ncu.ncu-rep',p/'ncu/QK_ncu.ncu-rep');cp(b/'QK_ncu.log',p/'ncu/QK_ncu.log')
with (p/'UPSTREAM_AUTHORITY.tsv').open('w',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows([['authority','value'],['V26_HEAD','afa5b3898ba33ad03f507e20b5312ef28f601c11'],['S2_RUN','C16R_deepseek-v2-lite_s2-text_decode_nvbit-warp-mref-shard_v26-qk-mixed_20260917T130000Z_c26c26c26c26'],['S2_evidence_class','MIXED_PERSISTENT_CACHE_CONSUMER']])
s3state=json.loads((b/'state/PERSISTENT_MLA_LIFETIME.json').read_text());cp(b/'authority/deepseek-v2-lite__S3_TEXT.json',p/'evidence/deepseek-v2-lite__S3_TEXT.json');(p/'S3_INPUT_AUTHORITY.json').write_text(json.dumps({'source':'C16_PROSPECTIVE_COMMON_INPUT_V1 deepseek S3','payload_sha256':'66fa598b03432cbd67f7fc7d469abe647f33ece260e59d0892d7714836c2a96e','token_count':8192,'canonical_token_matrix_sha256':'4580ba74b652dd74f0127c66324258a079798ad1eae449464697c4167c14ad22','no_retokenization':True},indent=2,sort_keys=True)+'\n');(p/'S3_STATE_AND_CACHE_RECEIPT.json').write_text(json.dumps(s3state,indent=2,sort_keys=True)+'\n')
sig=json.loads((b/'QK_SIGNATURE.json').read_text());rep=json.loads((b/'QK_REPLAY.json').read_text());(p/'S3_QK_TARGET_QUALIFICATION.json').write_text(json.dumps({'target':'layer0.self_attn.QK_matmul','evidence_class':'MIXED_PERSISTENT_CACHE_CONSUMER','replay':rep,'signature':sig,'persistent_positions':8192,'current_positions':1},indent=2,sort_keys=True)+'\n')
rows=list(csv.DictReader((b/'QK_static.tsv').open(),delimiter='\t'));(p/'S3_STATIC_PATH_AUDIT.json').write_text(json.dumps({'relation_to_v26':'DIFFERENT_FUNCTION_NOT_DIRECTLY_COMPARABLE','s3_static_map_sha256':sha(b/'QK_static.tsv'),'direct_global_mrefs':sum(x['memory_space']=='GLOBAL' and x['has_mref']=='1' for x in rows),'ldgsts':sum(x['memory_space']=='GLOBAL_TO_SHARED' for x in rows),'generic_mrefs':sum(x['memory_space']=='GENERIC' and x['has_mref']=='1' for x in rows),'source_address_method':'SASS-derived register pairs'},indent=2,sort_keys=True)+'\n')
s2a=json.loads((s2/'QK_FORMAL_AUDIT.json').read_text());s3a=json.loads((b/'QK_FORMAL_AUDIT.json').read_text())
def sums(a):
 c=Counter()
 for r in a['shards']:
  c.update(r.get('membership',{}))
 return dict(c)
s2m,s3m=sums(s2a),sums(s3a)
ratio=lambda x,y:None if not x else y/x
scale={'relation':'DIFFERENT_FUNCTION_NOT_DIRECTLY_COMPARABLE','S2':{'context':2048,'cache_after_length':2049,'audit':s2a,'membership':s2m},'S3':{'context':8192,'cache_after_length':8193,'audit':s3a,'membership':s3m},'ratios':{'context_length':4.0,'cache_after_length':8193/2049,'total_events':ratio(s2a['active_lane_events'],s3a['active_lane_events']),'persistent_prefix_events':ratio(s2m.get('PERSISTENT_KEY_PREFIX',0),s3m.get('PERSISTENT_KEY_PREFIX',0)),'current_append_events':ratio(s2m.get('CURRENT_KEY_APPEND',0),s3m.get('CURRENT_KEY_APPEND',0)),'query_current_events':ratio(s2m.get('QUERY_CURRENT_TOKEN',0),s3m.get('QUERY_CURRENT_TOKEN',0))},'aggregate_unique_rule':'SUM_OF_PER_SHARD_UNIQUES_ONLY; no cross-shard VA union'}
(p/'S2_VS_S3_MIXED_QK_SCALING.json').write_text(json.dumps(scale,indent=2,sort_keys=True)+'\n')
run='C16R_deepseek-v2-lite_s3-text_decode_nvbit-warp-mref-shard_v27-qk-mixed_20260917T140000Z_d27d27d27d27';ready=Path('/data/c16/capture/ready')/run
for n in ['RUN_MANIFEST.json','LOCAL_CLOSE_RECEIPT.json','WARP_SHARD_MANIFEST.json','QUICKCHECK.json']:cp(ready/n,p/'formal'/n)
remote='hrl174new:/root/share/mnt164/huangrulin/c16_ai_workload'
for src,n in [(f'{remote}/receipts/{run}/VERIFICATION.json','VERIFICATION.json'),(f'{remote}/receipts/{run}/ADMISSION.json','ADMISSION.json'),(f'{remote}/reports/transfer_acks/{run}.TRANSFER_ACK.json','ACK.json')]:subprocess.run(['scp',src,str(p/'formal'/n)],check=True)
(p/'S3_FORMAL_SUMMARY.json').write_text(json.dumps(s3a,indent=2,sort_keys=True)+'\n');(p/'S3_ADMISSION_ACK.json').write_text((p/'formal/ACK.json').read_text());(p/'NCU_TYPED_EVIDENCE.json').write_text(json.dumps({'S2':'V26 raw report preserved upstream','S3':'ncu/QK_ncu.ncu-rep','warning':'cache-control none; no normalized byte or cache/TLB causal claim'},indent=2,sort_keys=True)+'\n')
(p/'SCIENTIFIC_INTERPRETATION.md').write_text(f'''# S2 to S3 typed mixed-QK scaling\n\nThe exact semantic role and evidence class remain `MIXED_PERSISTENT_CACHE_CONSUMER`. S3 kernel implementation differs from S2, so static sets are not directly comparable. Measured total active-lane event ratio is {scale['ratios']['total_events']}; persistent-prefix ratio {scale['ratios']['persistent_prefix_events']}; current-append ratio {scale['ratios']['current_append_events']}; query-current ratio {scale['ratios']['query_current_events']}. These are typed target measurements only, not whole-model or cache/TLB causal conclusions.\n''')
(p/'NEXT_STEP_AUTHORIZATION.json').write_text(json.dumps({'decision':'DEEPSEEK_MLA_S2_S3_MIXED_QK_SCALING_CLOSED_FOR_C16_STRATIFICATION','s3_executed_in_v27':True,'further_operator_execution_authorized':False},indent=2,sort_keys=True)+'\n');(p/'FINAL_DECISION.json').write_text(json.dumps({'decision':'C16_DEEPSEEK_V2_LITE_S3_MIXED_QK_109_V27_PASS','s3_run_id':run,'ack':'PASS','evidence_class':'MIXED_PERSISTENT_CACHE_CONSUMER'},indent=2,sort_keys=True)+'\n');(p/'OPEN_ISSUES.md').write_text('# Open issues\n\nS2 and S3 use different QK kernel implementations; compare typed endpoint measurements, not static instruction identities or absolute VA.\n')
items=[]
for f in sorted(p.rglob('*')):
 if f.is_file() and f.name!='SHA256SUMS':items.append(f'{sha(f)}  {f.relative_to(p).as_posix()}')
(p/'SHA256SUMS').write_text('\n'.join(items)+'\n');print(p)
