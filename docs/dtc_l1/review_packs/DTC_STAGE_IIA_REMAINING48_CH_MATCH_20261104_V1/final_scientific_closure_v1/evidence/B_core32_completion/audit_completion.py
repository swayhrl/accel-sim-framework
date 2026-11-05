import collections, csv, datetime, gzip, hashlib, json, subprocess
from pathlib import Path

A = Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1')
F = Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1')
O = A/'agents/B_remaining48_completion_audit_20261105_v1'
C = 'b665d5ea77b5ae022a86cd03c6c464f5b11cb15e'
REL = 'docs/dtc_l1/review_packs/DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1/'
checks=[]; pins=[]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
 p=Path(p);pins.append({'path':str(p),'sha256':sha(p)});return json.loads(p.read_bytes())
def check(name,ok,detail=None):
 checks.append({'check':name,'pass':bool(ok),'detail':detail})
 if not ok: raise AssertionError((name,detail))
def put(name,x): (O/name).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def verify_mf(p):
 d=load(p)
 for r in d['files']:
  q=p.parent/r['path'];check('manifest_member',sha(q)==r['sha256'],str(q))
 return d
def rows(prefix,base):
 for p in sorted((base/'public/details').glob(prefix+'.*.gz')):
  with gzip.open(p,'rt') as f:
   for l in f: yield json.loads(l)
def git(*args):
 return subprocess.check_output(['git','-c','safe.directory='+str(A/'execution-worktree'),'-C',str(A/'execution-worktree'),*args])

O.mkdir(exist_ok=False)
provider=load(A/'agents/B_runtime_analysis_v1/snapshot_runner_v1/PUBLICATION_PROVIDER.json')
check('final_provider_48',provider['summary']['accepted_CH']==48 and provider['summary']['registered_consumed']==48 and provider['summary']['registered_remaining']==0)
check('provider_qualified',provider['source_qualified'] is True and provider['all_registered48_terminal_verified'] is True)
corepath=next(Path(r['path'])for r in provider['files']if 'CORE32_RESULTS.json.gz' in r['name'])
for r in provider['files']:check('provider_member',sha(r['path'])==r['sha256'],r['path'])
verify_mf(Path(provider['manifest']['path']))
with gzip.open(corepath,'rt')as f:core=json.load(f)
programs=core['all_programs'];check('core32',len(programs)==32 and len({r['input_digest']for r in programs})==32)
source_n=0;source_roles=collections.Counter();aliases=[]
for r in programs:
 check('six_accepted',len(r['six_source_cells'])==6 and all(s['accepted']for s in r['six_source_cells'].values()),r['program'])
 for k,s in r['six_source_cells'].items():
  check('source_RESULT_SHA',sha(s['source_RESULT_path'])==s['source_RESULT_sha256'],(r['program'],k))
  source_n+=1;source_roles[s['source_role']]+=1
  if s.get('legal_prior_P0_alias'):aliases.append({'program':r['program'],'cell':k,'alias':s['legal_prior_P0_alias']})
check('192_sources',source_n==192);check('six_aliases',len(aliases)==6)
B=next((A/'agents/B_final24_consumption_preparation_v1/updates').iterdir())
verify_mf(B/'MANIFEST.json');summary=load(B/'public/PROGRAM_SUMMARY.json');receipt=load(B/'public/SOURCE_AND_COMPLETION_RECEIPT.json')
check('final24_receipt',receipt['parsed_accepted_source_n']==144 and receipt['parsed_kernel_records']==43524 and not receipt['live_raw_consumed'])
new24={r['input_digest']:r for r in summary['programs']};check('24_inputs',len(new24)==24)
metadata={(r['input_digest'],r['cell'],r['profile']):r for r in rows('source_metadata',B)}
counts=collections.Counter();cycles=collections.Counter();ords=collections.defaultdict(set);nulls=collections.Counter()
for r in rows('kernels',B):
 k=(r['input_digest'],r['actual_design'],r['actual_profile']);counts[k]+=1;cycles[k]+=r['cycles'];ords[k].add(r['ordinal'])
 for field,value in r['print_interval_additive'].items():
  if value is None:nulls[field]+=1
check('144_metadata',len(metadata)==144);check('43524_details',sum(counts.values())==43524)
for k,r in metadata.items():
 check('kernel_count_cycles_ordinals',counts[k]==r['kernel_count'] and cycles[k]==r['cycles'] and ords[k]==set(range(1,r['kernel_count']+1)),k)
 check('single_stream_scope',r['kernel_scope']=='SINGLE_STREAM_ZERO_CUMULATIVE',k)
 check('metadata_result_match',any(s['source_RESULT_sha256']==r['RESULT_sha256']for s in new24[k[0]]['six_source_cells'].values()),k)
phase_n=sum(1 for _ in rows('phase_summaries',B));cycle_n=sum(1 for _ in rows('six_cell_kernel_cycles',B));check('7254_sixcell_kernels',cycle_n==7254)
idx=load(B/'public/CORE32_MECHANISM_EVIDENCE_INDEX.json');first8=idx['first8_reviewed_evidence']['first8']
for p in first8:
 for m in p['reviewed_package_manifests']:
  check('first8_manifest_pin',sha(m['path'])==m['sha256'],m['path']);verify_mf(Path(m['path']))
conv=F/'agents/A_convseparable_three_profiles_v1/MANIFEST.json';verify_mf(conv)
first8_names={r['program']for r in first8};check('32_disjoint_mechanism_coverage',len(first8_names)==8 and first8_names.isdisjoint(r['program']for r in new24.values()) and first8_names|{r['program']for r in new24.values()}=={r['program']for r in programs})
cat=load(A/'agents/B_closed_samples_analysis_v1/CONSUMED_COUNTER_CATALOG.json')
Cdir=next((A/'agents/C_final48_independent_audits_v1').iterdir());review=load(Cdir/'REVIEW.json');check('C_final48_PASS',review['status']=='PASS_ALL48_INDEPENDENT_LIFECYCLE_AND_REVIEWED_INTEGER_STATISTICS' and review['accepted']==48)
mathdir=A/'root_independent_cycle_statistics_v1'/B.name;verify_mf(mathdir/'MANIFEST.json')
with gzip.open(mathdir/'AUDIT.json.gz','rt')as f:math=json.load(f)
check('Root_final_math',math['status']=='PASS' and math['accepted_slots_rechecked']==192 and math['new48_raw_cycle_endpoints_rechecked']==48 and math['final_full32'])
gitfiles=git('ls-tree','-r','--name-only',C,REL).decode().splitlines();readme=git('show',C+':'+REL+'README.md').decode()
publication=load(A/'publication_service_v1/LATEST_PUBLICATION.json')
check('b665_not_final_closure',publication['commit']==C and publication['final_scientific_closure'] is False)
gaps=[
 {'id':'publish_final24','state':'LOCAL_COMPLETE_NOT_IN_b665','source':str(B/'MANIFEST.json'),'sha256':sha(B/'MANIFEST.json'),'minimum_action':'Export MANIFEST and exactly declared public members; do not rerun consumer or include private staging.'},
 {'id':'publish_final_C48_and_Root_math','state':'LOCAL_PASS_NOT_IN_b665','source':str(Cdir/'REVIEW.json'),'sha256':sha(Cdir/'REVIEW.json'),'minimum_action':'Publish C final full48 review and independent Root full32 audit with original source pins.'},
 {'id':'final_scientific_narrative','state':'MISSING_FROM_b665','source':REL+'README.md','minimum_action':'Add forward final32 report and final GES/counter interpretation; preserve dated partial reports.'},
 {'id':'final_figure_approval_and_promotion','state':'RENDERED_UNPROMOTED','source':str(A/'agents/A_figures_v1/snapshots'/B.name),'minimum_action':'Root visually inspect existing common32 final PNGs; record approval and publish exact final figure manifest/provider.'},
 {'id':'full32_direction_and_next_stage_boundary','state':'EARLIER_PLAN_CONDITIONAL','source':str(A/'root_next_stage_recommendations_v1/RECOMMENDATIONS_PENDING_APPROVAL.md'),'minimum_action':'Use final matched32 evidence in forward recommendations; no implicit authority for subsequent simulations.'},
 {'id':'first8_conv_index','state':'INDEX_UNDERSPECIFIED','source':str(conv),'sha256':sha(conv),'minimum_action':'Append this already-existing six-source Rows/Columns report to forward first8 index; old index points only to counter catalog.'},
 {'id':'GEMM_2D_F256_mechanism','state':'EXPLICIT_SCOPED_GAP_NOT_PERFORMANCE_GAP','minimum_action':'Keep first8 F128-only counter scope explicit; all-six accepted performance remains complete. Optional closed-only F256 counter supplement only if claiming six-profile mechanism coverage.'},
 {'id':'Root_final_signoff_and_goal_transition','state':'ROOT_ONLY','minimum_action':'After final export/readback, independent review and visual/narrative approval, record requirement-by-requirement closure and complete old Goal; no model action.'}
]
check('final24_not_in_b665',not any(x.endswith('/PROGRAM_SUMMARY.json')for x in gitfiles))
csvrows=[]
for r in programs:
 x={'program':r['program'],'suite':r['suite'],'input_digest':r['input_digest'],'mechanism_group':'NEW24_FULL_SIXCELL_DETAIL'if r['input_digest']in new24 else'FIRST8_REUSED_SCOPED','accepted_cells':6}
 for k,s in r['six_source_cells'].items():x[k]=s['cycles']
 if r['input_digest']in new24:x['kernels_per_cell']=new24[r['input_digest']]['mechanism_kernel_counts']['CH_P0']
 else:x['kernels_per_cell']='REUSED_AUTHORITY'
 for p in ['F128','F256']:
  for m,v in r['metrics_by_profile'][p].items():x[p+'_'+m]=v
 csvrows.append(x)
with (O/'CORE32_PROGRAM_COVERAGE.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=sorted(set().union(*(x.keys()for x in csvrows))));w.writeheader();w.writerows(csvrows)
put('AUDIT.json',{'schema':'DTC_REMAINING48_EXISTING_COMPLETION_EVIDENCE_AUDIT_V1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit_examined':C,'scope':'Existing closed derived evidence; no lifecycle reexecution/raw model scan; no Goal state mutation','source_roles':dict(source_roles),'new48_accepted':48,'core32_cells':192,'new24_sources':144,'new24_kernel_rows':43524,'new24_unique_kernel_positions':cycle_n,'phase_summary_rows':phase_n,'counter_missing_interval_counts_preserved':dict(nulls),'first8_index':first8,'conv_forward_authority':{'path':str(conv),'sha256':sha(conv)},'C48_status':review['status'],'Root_math_status':math['status'],'gaps':gaps,'checks':checks,'scientific_model_starts':0,'native_writes':0})
put('SOURCE_PINS.json',pins)
put('FULL32_STATISTICS.json',core['all_core32'])
put('SIX_P0_ALIAS_IDENTITIES.json',aliases)
put('FINAL24_COUNTER_AND_CAPTURE_BOUNDARIES.json',summary['phase_and_counter_boundaries'])
put('COUNTER_CATALOG_REFERENCE.json',{'source':str(A/'agents/B_closed_samples_analysis_v1/CONSUMED_COUNTER_CATALOG.json'),'sha256':sha(A/'agents/B_closed_samples_analysis_v1/CONSUMED_COUNTER_CATALOG.json'),'MRQ_item':next(x for x in cat['items']if x['field']=='latency_counters.avg_mrq_latency'),'no_first8_stream_scope_promotion':'All144 final24 metadata independently explicitly SINGLE_STREAM_ZERO_CUMULATIVE; counter/source semantics still retain declared scope.'})
put('PUBLICATION_GAPS.json',gaps)
print(json.dumps({'output':str(O),'checks_passed':len(checks),'core32':32,'new24kernelrecords':43524,'gaps':len(gaps)}))
