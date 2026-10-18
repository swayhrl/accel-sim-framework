"""Audit exact existing evidence; never execute/re-execute RTL or EDA tools."""
from pathlib import Path
import json,hashlib,gzip,argparse,re,datetime,subprocess
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--candidate',choices=('R3A','R3B_FINAL','ALL'),default='ALL');a=p.parse_args();assert not a.out.exists();book=Path('/workspace/ep_l2_rtl_r3_metadata_cost');art=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_R3_METADATA_AND_COST_OPT_lane2');candidates=json.loads((book/'SOURCE_CANDIDATES.json').read_text());audit=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def decoded(p):
 p=Path(p)
 if p.exists():return p.read_bytes()
 return gzip.decompress(p.with_name(p.name+'.gz').read_bytes())
def binary(row,default=None):
 path=Path(row.get('exact_binary_archive',row.get('archive',default)));assert path.is_file()
 with gzip.open(path,'rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['binary_sha256']
 return {'archive':str(path),'archive_sha256':sha(path),'decoded_binary_sha256':row['binary_sha256']}
LEGACY_REFERENCE='rtl/ep_l2/rtl/ep_l2_slice_top.sv'
LEGACY_REFERENCE_SHA=hashlib.sha256(subprocess.check_output(['git','show','1b011c6a51900462db9ae169d33bca742999abdb:'+LEGACY_REFERENCE],cwd=candidates['R3B_FINAL']['worktree'])).hexdigest()
def source(data,expected):
 assert {p:data[p] for p in expected}==expected,('canonical hardware identity differs',data,expected)
 extras=set(data)-set(expected);assert extras<=set([LEGACY_REFERENCE]),('unknown extra RTL source',extras)
 for p in extras:assert data[p]==sha(wt/p)==LEGACY_REFERENCE_SHA,'legacy uninstantiated reference differs'

def entry(candidate,kind,path,details):
 audit.append({'candidate':candidate,'gate':kind,'receipt':str(path),'receipt_sha256':sha(path),'status':'VERIFIED_EXISTING_ACTUAL_EVIDENCE_PASS','details':details});print(candidate,kind,'verified',flush=True)
for label,key,base,boundary,ctrl,overlap in [('R3A','R3A',art/'R3A_QUAL',art/'R3A_BOUNDARY_RETRY_r3',art/'R3A_CONTROLLER_CONTROL_CUT',art/'R3A_CONCURRENCY'),('R3B_FINAL','R3B_FINAL',art/'R3B_FINAL_QUAL_RESUME_r2',art/'R3B_FINAL_QUAL_RESUME_r2/unified-last-physical',art/'R3B_FINAL_CONTROLLER_CONTROL_CUT_v2',art/'R3B_FINAL_QUAL/concurrency')]:
 if a.candidate!='ALL' and label!=a.candidate:continue
 cand=candidates[key];expected=cand['five_RTL_files'];wt=Path(cand['worktree']);assert {p:sha(wt/p) for p in expected}==expected;fixture_sha=sha(wt/'rtl/ep_l2/tb/ep_l2_slice_tb.sv')
 for kind,d,expected_pairs in [('base',base/'functional',{(0,32),(1,32),(2,32),(0,3)}),('highest_physical',boundary,{(1,32)})]:
  receipt=d/'FUNCTIONAL_RECEIPT.json';rows=load(receipt);assert {(r['mode'],r['GEN_W']) for r in rows}==expected_pairs and len(rows)==len(expected_pairs);details=[]
  for row in rows:
   assert row['returncode']==0 and row['full_synthesizable_top'] is True and row['stimulus_sha256']==fixture_sha;source(row['RTL_sha256'],expected)
   boundary_flag=row.get('unified_last_physical_only',row['qualification_scope'].startswith('Unified full1024Tags/highestPID1167'));assert boundary_flag==(kind=='highest_physical')
   name='UNIFIED_LAST_PHYSICAL' if kind=='highest_physical' else 'GENERATION_EXHAUSTION' if row['GEN_W']==3 else {0:'B16',1:'UNIFIED',2:'S64'}[row['mode']]
   log=Path(row.get('run_log',str(d/(name+'-run.log'))));text=decoded(log).decode()
   if kind=='highest_physical':assert 'UNIFIED_LAST_PHYSICAL_BOUNDARY physicalID1167 row291 bank3 localWB36 other-bank-free108 same-request-credit-resume byte-WB37 PASS cycles3379' in text
   elif row['GEN_W']==3:assert 'CASE generation exhaustion, no wrap PASS mode0 G3' in text
   else:assert re.search(r'RTL_RESULT mode='+str(row['mode'])+r' tags=1024 physical=1168 wb_peak=\d+ WAD=128 gen=32 .* PASS',text)
   details.append({'mode':row['mode'],'GEN_W':row['GEN_W'],'run_log_sha256':hashlib.sha256(decoded(log)).hexdigest(),**binary(row)})
  entry(label,kind,receipt,details)
 receipt=base/'lane3-bytes/LANE3_BYTE_RECEIPT.json';r=load(receipt);source(r['RTL_sha256'],expected);assert r['stimulus_sha256']=='297e1d9547e9cae1ae998ef4eff6361acd1a6f85d737d1390b58032ea868a921' and r['reference_sha256']=='7000ec4892560dfcdc00e81b90a631a7446c552a7b6cb83db8e0e7de250a7a90';assert r['generated_fixture_sha256']==sha(receipt.parent/'lane3_actual_tb.sv');assert {x['mode'] for x in r['rows']}=={'B16','S64','UNIFIED'} and len(r['rows'])==3
 details=[]
 for row in r['rows']:
  assert row['status']=='ACTUAL_RTL_BYTE_COMPARISON_PASS' and row['comparisons']==13 and row['full_line_final_comparisons']==10;details.append({'mode':row['mode'],**binary(row,receipt.parent/(row['mode']+'.vvp.gz'))})
 entry(label,'Lane3_actual_10vector_bytes',receipt,details)
 for kind,d,filename,marker in [('concurrent_GEN',overlap,'CONCURRENT_GEN_RECEIPT.json','R3_ACTUAL_GEN_CONCURRENCY_FULL_CAPACITY')]+[('owner_stress',art/('R3B_FINAL_QUAL/owner-stress' if label=='R3B_FINAL' else 'R3A_OWNER_SAMEBANK_DIRECTED_r1'),'OWNER_STRESS_RECEIPT.json','R3_ACTUAL_OWNER_STRESS')]:
  receipt=d/filename;r=load(receipt);source(r['source_RTL_sha256'],expected);assert {x['mode'] for x in r['rows']}=={'B16','S64','UNIFIED'} and len(r['rows'])==3;fixture=d/('concurrent_tb.sv' if kind=='concurrent_GEN' else 'owner_stress_tb.sv');assert r['fixture_sha256']==sha(fixture);details=[]
  for row in r['rows']:
   assert row['status'].endswith('_PASS');log=Path(row.get('run_log',str(d/(row['mode']+'-run.log'))));text=decoded(log).decode();assert marker in text and 'PASS' in text;details.append({'mode':row['mode'],**binary(row)})
  entry(label,kind,receipt,details)
 receipt=ctrl/'CONTROLLER_EQ_RECEIPT.json';r=load(receipt);assert {x['mode'] for x in r['rows']}=={0,1,2} and all(x['depth']==4 and x['status']=='BOUNDED_ACTUAL_CONTROLLER_EQ_PASS' for x in r['rows']);assert r['captured_RTL_sha256']=={Path(p).name:v for p,v in expected.items() if p.endswith(('ep_l2_slice_ctrl.sv','ep_l2_metadata_word.sv'))}
 for mode in (0,1,2):assert 'SUCCESS!' in decoded(ctrl/f'proof-{mode}.log').decode()
 entry(label,'controller_small32payload_4cycle_control_cut_NOT_UNBOUNDED',receipt,r['scope'])
# Common actual word induction / all-index two-port miter; no rerun.
receipt=art/'R3A/proofs/R3_PORT_WORD_EQ_RECEIPT.json';r=load(receipt);assert r['R3_metadata_sha256']==candidates['R3A']['five_RTL_files']['rtl/ep_l2/rtl/ep_l2_metadata_word.sv'];assert r['status']=='ACTUAL_R2_R3_WORD_INDUCTION_AND_EXHAUSTIVE_TWO_GEN_PORTS_PASS';assert all(x['status']=='ACTUAL_SOURCE_SAT_PASS' for x in r['rows']);entry('COMMON','GEN3_GEN32_word_port_SAT',receipt,{'scope':r['scope'],'premises':r['environment'],'whole_controller_equivalence':r['whole_controller_equivalence']})
if a.candidate in ('ALL','R3B_FINAL'):
 receipt=art/'R3B_OWNER_PROOF_PREP_v2/OWNER_INVARIANT_EQ_RECEIPT.json';r=load(receipt);assert r['status'].endswith('_PASS') and r['actual_metadata_source_sha256']==candidates['R3B_FINAL']['five_RTL_files']['rtl/ep_l2/rtl/ep_l2_metadata_word.sv'];entry('R3B_FINAL','conditional_legal_event_owner_invariant_NOT_GLOBAL_REACHABILITY',receipt,r)
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps({'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'ALL_REQUIRED_FINITE_FUNCTIONAL_GATES_VERIFIED_FOR_SELECTED_SOURCES','selected_candidates':['R3A','R3B_FINAL'] if a.candidate=='ALL' else [a.candidate],'scope':'actual configured RTL finite regression and explicit scoped symbolic proofs only; no global/unbounded proof, wholeGPU/app performance or timing closure inferred','uninstantiated_legacy_reference_checked_separately':{'path':LEGACY_REFERENCE,'sha256':LEGACY_REFERENCE_SHA},'entries':audit},indent=2)+'\n')
