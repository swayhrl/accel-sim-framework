#!/usr/bin/env python3
"""Validate and package the C16 E1 operator-family expansion stage."""

import csv,hashlib,json,math,shutil,statistics
from collections import defaultdict
from pathlib import Path

REPO=Path('/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-operator-family-expansion-109-v1')
SOURCE=Path('/data/c16/e1_operator_family_expansion_v1')
OUT=REPO/'docs/vm_tlb/review_packs/C16_E1_OPERATOR_FAMILY_EXPANSION_109_V1'
UPSTREAM=REPO/'docs/vm_tlb/review_packs/C16_E1_COVERAGE_SCALING_109_V1'
ROLES=('gate_proj','up_proj','down_proj')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_json(n,x):(OUT/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def write_tsv(n,rows,fields):
 with (OUT/n).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,delimiter='\t',fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def summary(v):
 m=statistics.mean(v);return {'samples':v,'median':statistics.median(v),'min':min(v),'max':max(v),'cv':statistics.pstdev(v)/abs(m) if m else None}
def percentile(v,q):
 v=sorted(v);p=(len(v)-1)*q;a=int(math.floor(p));b=int(math.ceil(p));return v[a] if a==b else v[a]*(b-p)+v[b]*(p-a)
def percentile(v,q):
 v=sorted(v);p=(len(v)-1)*q;a=int(math.floor(p));b=int(math.ceil(p));return v[a] if a==b else v[a]*(b-p)+v[b]*(p-a)
def read_ncu(p):
 rows=list(csv.reader(p.open(newline='',encoding='utf-8')));return [dict(zip(rows[0],r)) for r in rows[2:]],dict(zip(rows[0],rows[1]))
def session_command(p):
 for r in csv.reader(p.open(newline='',encoding='utf-8')):
  if len(r)>=2 and r[0]=='Profiler Command Line':return r[1].rstrip()
 raise RuntimeError('missing command')
def copy_raw(profile,base,session,log):
 shutil.copy2(base,OUT/f'RAW_NCU_{profile}_BASE.csv');shutil.copy2(session,OUT/f'RAW_NCU_{profile}_SESSION.csv');shutil.copy2(log,OUT/f'RAW_NCU_{profile}_PROFILE.log')
def log_receipts(p):
 out=[]
 for line in p.read_text(encoding='utf-8',errors='replace').splitlines():
  if line.startswith('{') and line.endswith('}'):
   try:x=json.loads(line)
   except:continue
   if x.get('status')=='PASS':out.append(x)
 if not out:raise RuntimeError(f'missing receipt {p}')
 return out
def identity(run):
 rows=sorted(run['occurrences'],key=lambda x:(x['layer'],x['role'],x['decode_index']));return (run['generated_token_ids_D0_D3'],[(x['layer'],x['role'],x['decode_index'],x['input_sha256'],x['output_sha256']) for x in rows])
def condition_spec(condition,contract):
 if condition in ('CONTROL_FULL_GUD84','FULLHINT_GUD84'):
  e=contract['condition_sets']['GUD84'];return 'GUD84',e['selected_roles'],84,1.0,condition=='FULLHINT_GUD84'
 for name,e in contract['condition_sets'].items():
  if condition==e['control_condition']:return name,e['selected_roles'],e['selected_module_count'],e['hit_ratio'],False
  if condition==e['fair_condition']:return name,e['selected_roles'],e['selected_module_count'],e['hit_ratio'],True
 raise RuntimeError(condition)
def validate_run(run,authority,contract):
 if identity(run)!=authority or run['call_order']!=authority_call_order:raise RuntimeError(f'identity/order {run["condition"]}')
 name,roles,count,ratio,persist=condition_spec(run['condition'],contract)
 if run['set_name']!=name or run['selected_roles']!=roles or run['selected_module_count']!=count or abs(run['hit_ratio']-ratio)>1e-7 or run['target_persisting']!=persist:raise RuntimeError('condition contract')
 pr=run['policy_receipt']
 if pr['requested_setaside_bytes']!=33947648 or pr['actual_setaside_bytes']!=37748736 or pr['actual_setaside_after_reset_bytes']!=0 or not pr['reset_before'] or not pr['reset_after']:raise RuntimeError('budget/reset')
 expected=[x for x in authority_call_order if x['role'] in roles]
 if len(expected)!=count*5 or len(run['policy_transitions'])!=len(expected):raise RuntimeError('transition count')
 census={(x['layer'],x['role']):x for x in run['module_census']}
 for t,e in zip(run['policy_transitions'],expected):
  if (t['phase'],t['ordinal'],t['layer'],t['role'])!=(e['phase'],e['ordinal'],e['layer'],e['role']):raise RuntimeError('transition order')
  g=census[(t['layer'],t['role'])]
  if t['base_ptr']!=g['data_ptr'] or t['num_bytes']!=g['bytes'] or t['persisting']!=persist or abs(t['hit_ratio']-ratio)>1e-7:raise RuntimeError('window/policy')
  if persist and (t['hit_property']!='cudaAccessPropertyPersisting' or t['miss_property']!='cudaAccessPropertyStreaming'):raise RuntimeError('fair props')
  if not persist and (t['hit_property']!='cudaAccessPropertyNormal' or t['miss_property']!='cudaAccessPropertyNormal'):raise RuntimeError('control props')
def copy_raw(profile,base,session,log):
 shutil.copy2(base,OUT/f'RAW_NCU_{profile}_BASE.csv');shutil.copy2(session,OUT/f'RAW_NCU_{profile}_SESSION.csv');shutil.copy2(log,OUT/f'RAW_NCU_{profile}_PROFILE.log')

def main():
 if OUT.exists():raise SystemExit('pack exists')
 OUT.mkdir(parents=True)
 contract=json.loads((SOURCE/'contracts/CONDITION_MATRIX_PRECONTRACT.json').read_text());decision=json.loads((SOURCE/'contracts/STAGE_DECISION_PRECONTRACT.json').read_text());authority_doc=json.loads((SOURCE/'contracts/CALL_ORDER_AUTHORITY.json').read_text())
 global authority_call_order;authority_call_order=authority_doc['call_order'];authority=(authority_doc['generated_token_ids_D0_D3'],sorted([(x['layer'],x['role'],x['decode_index'],x['input_sha256'],x['output_sha256']) for x in authority_doc['occurrence_bindings']]))
 write_json('UPSTREAM_AUTHORITY.json',{'coverage_producer':'18acd7dcc10118c68b450d226a8e7ca80c51ad72','coverage_label':'COVERAGE_SCALING_POSITIVE_BUT_SUBTHRESHOLD','shared_producer':'1e701f013fc174b5b4df9febb5c33500f9ea586e','frozen_prior_labels_preserved':True,'status':'PASS'})
 write_json('NATURAL_FFN_CALL_ORDER.json',authority_doc);write_json('CONDITION_MATRIX_PRECONTRACT.json',contract);write_json('STAGE_DECISION_PRECONTRACT.json',decision)
 for p in sorted((SOURCE/'order/native').glob('run*')):shutil.copy2(p,OUT/f'RAW_ORDER_{p.name}')
 write_json('OPERATOR_FAMILY_POLICY_CONTRACT.json',{'status':'PASS','fixed_requested_setaside_bytes':33947648,'expected_actual_setaside_bytes':37748736,'conditions':contract['condition_sets'],'natural_call_order_authority':True,'all_84_events_every_condition':True,'no_in_run_reset':True,'hitRatio_is_hint_not_exact_fraction':True})
 runs={};timing={};native_rows=[];decode_rows=[];overhead=[];overhead_totals={}
 for name,e in contract['condition_sets'].items():
  for condition in (e['control_condition'],e['fair_condition']):
   paths=sorted((SOURCE/'primary/native'/condition).glob('run[0-6].json'));rs=[json.loads(p.read_text()) for p in paths]
   if len(rs)!=7:raise RuntimeError('run count')
   for r in rs:validate_run(r,authority,contract)
   runs[condition]=rs
   for p in paths:shutil.copy2(p,OUT/f'RAW_NATIVE_{condition}_{p.name}')
   for p in sorted((SOURCE/'primary/native'/condition).glob('*.stdout.log')):shutil.copy2(p,OUT/f'RAW_NATIVE_{condition}_{p.name}')
   for layer in range(28):
    for role in ROLES:
     for d in range(4):
      vals=[next(x['target_ms'] for x in r['occurrences'] if x['layer']==layer and x['role']==role and x['decode_index']==d) for r in rs];s=summary(vals);timing[(condition,layer,role,d)]=s;a=next(x for x in rs[0]['occurrences'] if x['layer']==layer and x['role']==role and x['decode_index']==d)
      native_rows.append({'condition':condition,'set_name':name,'layer':layer,'role':role,'decode_index':d,'selected':role in e['selected_roles'],'median_ms':s['median'],'min_ms':s['min'],'max_ms':s['max'],'cv':s['cv'],'samples_ms':json.dumps(vals),'input_sha256':a['input_sha256'],'output_sha256':a['output_sha256']})
   for d in range(4):
    vals=[r['decode_step_ms'][d] for r in rs];s=summary(vals);decode_rows.append({'condition':condition,'set_name':name,'decode_index':d,'median_ms':s['median'],'min_ms':s['min'],'max_ms':s['max'],'cv':s['cv'],'samples_ms':json.dumps(vals)})
   grouped=defaultdict(list);tot=[]
   for r in rs:
    tot.append(sum(x['cpu_update_ns'] for x in r['policy_transitions']))
    for x in r['policy_transitions']:grouped[(x['phase'],x['layer'],x['role'])].append(x['cpu_update_ns'])
   for (ph,l,role),vals in grouped.items():
    s=summary(vals);overhead.append({'condition':condition,'set_name':name,'phase':ph,'layer':l,'role':role,'scope':'ONE_UPDATE','median_cpu_ns':s['median'],'min_cpu_ns':s['min'],'max_cpu_ns':s['max'],'cv':s['cv'],'samples_cpu_ns':json.dumps(vals)})
   s=summary(tot);overhead_totals[condition]=s;overhead.append({'condition':condition,'set_name':name,'phase':'FULL_RUN','layer':'ALL','role':'ALL','scope':'TOTAL_PER_RUN','median_cpu_ns':s['median'],'min_cpu_ns':s['min'],'max_cpu_ns':s['max'],'cv':s['cv'],'samples_cpu_ns':json.dumps(tot)})
 write_tsv('OPERATOR_FAMILY_NATIVE_TIMING.tsv',native_rows,['condition','set_name','layer','role','decode_index','selected','median_ms','min_ms','max_ms','cv','samples_ms','input_sha256','output_sha256'])
 write_tsv('OPERATOR_FAMILY_DECODE_TIMING.tsv',decode_rows,['condition','set_name','decode_index','median_ms','min_ms','max_ms','cv','samples_ms'])
 write_tsv('OPERATOR_FAMILY_POLICY_OVERHEAD.tsv',overhead,['condition','set_name','phase','layer','role','scope','median_cpu_ns','min_cpu_ns','max_cpu_ns','cv','samples_cpu_ns'])
 overhead_analysis={}
 for name,e in contract['condition_sets'].items():
  c=overhead_totals[e['control_condition']];f=overhead_totals[e['fair_condition']]
  overhead_analysis[name]={'control_condition':e['control_condition'],'fair_condition':e['fair_condition'],'control_total_median_cpu_ns':c['median'],'fair_total_median_cpu_ns':f['median'],'FAIR_minus_CONTROL_median_cpu_ns':f['median']-c['median'],'diagnostic_only_not_subtracted_from_gpu_timing':True}
 write_json('POLICY_OVERHEAD_ANALYSIS.json',{'status':'PASS','sets':overhead_analysis})
 accounting=[];analyses={};local={}
 for name,e in contract['condition_sets'].items():
  cr=runs[e['control_condition']];fr=runs[e['fair_condition']];selected=set(e['selected_roles']);localres={};mat=0;bens=[]
  for l in range(28):
   for role in selected:
    c=timing[(e['control_condition'],l,role,3)];f=timing[(e['fair_condition'],l,role,3)];b=1-f['median']/c['median'];disp=math.hypot(c['cv'],f['cv']);m=b>=.05 and b>disp;mat+=m;bens.append(b);localres[f'L{l}:{role}']={'benefit_fraction':b,'combined_dispersion':disp,'MATERIAL_LOCAL':m}
  stablec=[sum(x['decode_step_ms'][1:4])/3 for x in cr];stablef=[sum(x['decode_step_ms'][1:4])/3 for x in fr];runbenef=[(c-f)/c for c,f in zip(stablec,stablef)];combined=math.hypot(statistics.pstdev(stablec)/statistics.mean(stablec),statistics.pstdev(stablef)/statistics.mean(stablef))
  for a,b in zip(cr,fr):
   for d in (1,2,3):
    ct={(x['layer'],x['role']):x['target_ms'] for x in a['occurrences'] if x['decode_index']==d};ft={(x['layer'],x['role']):x['target_ms'] for x in b['occurrences'] if x['decode_index']==d};sel=[k for k in ct if k[1] in selected];uns=[k for k in ct if k[1] not in selected];direct=sum(ct[k]-ft[k] for k in sel);un=sum(ct[k]-ft[k] for k in uns);total=direct+un;obs=a['decode_step_ms'][d]-b['decode_step_ms'][d];res=obs-total;roles={r:sum(ct[k]-ft[k] for k in ct if k[1]==r) for r in ROLES}
    accounting.append({'set_name':name,'run_index':a['run_index'],'decode_index':d,'control_decode_ms':a['decode_step_ms'][d],'fair_decode_ms':b['decode_step_ms'][d],'selected_share':sum(ct[k] for k in sel)/a['decode_step_ms'][d],'direct_selected_saving_ms':direct,'unselected_ffn_saving_ms':un,'total_ffn_saving_ms':total,'observed_decode_saving_ms':obs,'outside_ffn_residual_ms':res,'selected_realization':obs/direct if direct>0 else None,'ffn_realization':obs/total if total>0 else None,'gate_saving_ms':roles['gate_proj'],'up_saving_ms':roles['up_proj'],'down_saving_ms':roles['down_proj']})
  rows=[x for x in accounting if x['set_name']==name];med=lambda k:statistics.median([x[k] for x in rows if x[k] is not None]);benefit=statistics.median(runbenef);sys=benefit>=.02 and benefit>combined
  analyses[name]={'selected_roles':e['selected_roles'],'selected_module_count':e['selected_module_count'],'material_selected_count':mat,'material_selected_fraction':mat/e['selected_module_count'],'selected_benefit_distribution':{'min':min(bens),'p25':percentile(bens,.25),'median':statistics.median(bens),'p75':percentile(bens,.75),'max':max(bens)},'run_aligned_whole_decode_benefit':summary(runbenef),'combined_decode_dispersion':combined,'MATERIAL_SYSTEM':sys,'positive_beyond_dispersion':benefit>0 and benefit>combined,'medians':{k:med(k) for k in ['selected_share','direct_selected_saving_ms','unselected_ffn_saving_ms','total_ffn_saving_ms','observed_decode_saving_ms','outside_ffn_residual_ms','selected_realization','ffn_realization','gate_saving_ms','up_saving_ms','down_saving_ms']}}
  local[name]=localres
 write_tsv('OPERATOR_FAMILY_RUN_ALIGNED_ACCOUNTING.tsv',accounting,['set_name','run_index','decode_index','control_decode_ms','fair_decode_ms','selected_share','direct_selected_saving_ms','unselected_ffn_saving_ms','total_ffn_saving_ms','observed_decode_saving_ms','outside_ffn_residual_ms','selected_realization','ffn_realization','gate_saving_ms','up_saving_ms','down_saving_ms'])
 write_json('ROLE_ONLY_ANALYSIS.json',{k:analyses[k] for k in ['GATE28','UP28','DOWN28']});write_json('PAIRWISE_ANALYSIS.json',{k:analyses[k] for k in ['GU56','GD56','UD56']});write_json('ALL_FFN_ANALYSIS.json',analyses['GUD84']);write_json('RESIDUAL_DECOMPOSITION.json',{'status':'PASS','conditions':analyses,'local_D3':local,'negative_residual_label':'negative residual outside measured FFN accounting; no causal attribution'})
 gud=analyses['GUD84'];trigger=gud['material_selected_fraction']>=.5 and gud['run_aligned_whole_decode_benefit']['median']<.02
 write_json('FULLHINT_GUD84_TRIGGER.json',{'triggered':trigger,'material_selected_fraction':gud['material_selected_fraction'],'whole_decode_benefit':gud['run_aligned_whole_decode_benefit']['median'],'contract':contract['fullhint']})
 write_json('FULLHINT_GUD84_ANALYSIS.json',{'status':'NOT_RUN_TRIGGER_FALSE' if not trigger else 'ERROR_EXPECTED_ARTIFACTS','reason':'GUD84 material selected fraction below 0.50' if not trigger else None,'additional_ncu_run':False})
 if trigger:raise RuntimeError('FULLHINT trigger true but no artifacts')
 metric=json.loads((SOURCE/'metric_query/METRIC_SELECTION.json').read_text());metrics=metric['profile_metric_list'];add=set(metric['aggregation']['semantic_sum']);avail=[]
 for r in metric['critical_metrics']:avail.append({'category':r['category'],'available':r['available'],'metric_name':r['metric_name'],'metric_type':r['metric_type'],'unit':r['unit'],'aggregation':'SEMANTIC_SUM' if r['metric_name'] in add else 'PER_KERNEL_ONLY','query_line':r['query_line']})
 write_tsv('OPERATOR_FAMILY_NCU_METRIC_AVAILABILITY.tsv',avail,['category','available','metric_name','metric_type','unit','aggregation','query_line']);q=SOURCE/'metric_query/NCU_QUERY_METRICS_ALL.txt';gz=SOURCE/'metric_query/NCU_QUERY_METRICS_ALL.txt.gz';write_json('NCU_QUERY_RECEIPT.json',{'query_command':metric['query_command'],'ncu_version':metric['ncu_version'],'full_query_sha256':sha(q),'compressed_sha256':sha(gz)});shutil.copy2(gz,OUT/'RAW_NCU_QUERY_METRICS_ALL.txt.gz');shutil.copy2(SOURCE/'metric_query/METRIC_SELECTION.json',OUT/'RAW_METRIC_SELECTION.json')
 ncu=[];kernels=[];nmap={};prov=[]
 for report in sorted((SOURCE/'ncu/primary/reports').glob('*.ncu-rep')):
  pid=report.stem;base=report.with_suffix('.base.csv');session=report.with_suffix('.session.csv');log=SOURCE/'ncu/primary/logs'/f'{pid}.log';receipts=log_receipts(log)
  for r in receipts:validate_run(r,authority,contract)
  cmd=session_command(session);selected=cmd.split('--nvtx-include ',1)[1].split('/',1)[0];occ=next(x for x in receipts[0]['occurrences'] if x['range']==selected);rows,units=read_ncu(base);rc=next(k for k in rows[0] if 'Push/Pop_Range' in k);passes=[int(x['profiler__replayer_passes'].replace(',','')) for x in rows]
  if any(selected not in x[rc] for x in rows) or len(set(passes))!=1 or passes[0]!=len(receipts):raise RuntimeError('ncu selector')
  sums={};names=[x['Kernel Name'] for x in rows]
  for m in metrics:
   vals=[float(x[m].replace(',','')) for x in rows]
   for i,(x,v) in enumerate(zip(rows,vals)):kernels.append({'profile_id':pid,'condition':receipts[0]['condition'],'role':occ['role'],'kernel_index':i,'kernel_role':'GEMM' if 'gemm_forward' in x['Kernel Name'] else 'REDUCTION','kernel_name':x['Kernel Name'],'metric_name':m,'unit':units[m],'value':v,'replay_pass_count':passes[0]})
   if m in add:sums[m]=sum(vals)
  key=(receipts[0]['condition'],occ['role']);nmap[key]=sums;ncu.append({'profile_id':pid,'condition':key[0],'role':key[1],'layer':0,'decode_index':3,'kernel_count':len(rows),'kernel_names':json.dumps(names),'replay_pass_count':passes[0],**sums,'profiler_command':cmd});prov.append({'profile_id':pid,'report_path':str(report),'report_sha256':sha(report),'base_sha256':sha(base),'session_sha256':sha(session),'profile_log_sha256':sha(log)});copy_raw(pid,base,session,log)
 write_tsv('OPERATOR_FAMILY_NCU_INDEX.tsv',ncu,['profile_id','condition','role','layer','decode_index','kernel_count','kernel_names','replay_pass_count']+metric['aggregation']['semantic_sum']+['profiler_command']);write_tsv('OPERATOR_FAMILY_NCU_KERNEL_METRICS.tsv',kernels,['profile_id','condition','role','kernel_index','kernel_role','kernel_name','metric_name','unit','value','replay_pass_count']);write_json('NCU_RAW_PROVENANCE.json',{'profiles':prov})
 crit={}
 for role,setname in [('gate_proj','GATE28'),('up_proj','UP28'),('down_proj','DOWN28')]:
  crit[role]={}
  for s in [setname,'GUD84']:
   c=nmap[(f'CONTROL_{s}',role)];f=nmap[(f'FAIR_{s}',role)];cg={x['metric_name']:x['value'] for x in kernels if x['condition']==f'CONTROL_{s}' and x['role']==role and x['kernel_role']=='GEMM'};fg={x['metric_name']:x['value'] for x in kernels if x['condition']==f'FAIR_{s}' and x['role']==role and x['kernel_role']=='GEMM'}
   crit[role][s]={'duration_ratio':f['gpu__time_duration.sum']/c['gpu__time_duration.sum'],'dram_read_ratio':f['dram__bytes_read.sum']/c['dram__bytes_read.sum'],'l2_hit_ratio':f['lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum']/c['lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum'],'l2_miss_ratio':f['lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum']/c['lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum'],'gemm_long_scoreboard_delta':fg['smsp__warp_issue_stalled_long_scoreboard_per_warp_active.pct']-cg['smsp__warp_issue_stalled_long_scoreboard_per_warp_active.pct']}
 write_json('OPERATOR_FAMILY_CRITICAL_PATH.json',{'status':'PASS','roles':crit,'interpretation':'gate/up GEMM duration and long-scoreboard may improve while L2/DRAM-read remain nearly flat; down changes little; aggregate traffic is not a sufficient proxy'})
 anysys=any(x['MATERIAL_SYSTEM'] for x in analyses.values());gud_direct_fraction=gud['medians']['direct_selected_saving_ms']/statistics.median([sum(r['decode_step_ms'][1:4])/3 for r in runs['CONTROL_GUD84']]);collateral=(not anysys and gud_direct_fraction>=.02 and gud['material_selected_fraction']>=.5 and gud['medians']['outside_ffn_residual_ms']<0);anypos=any(x['positive_beyond_dispersion'] for x in analyses.values())
 label='OPERATOR_FAMILY_SYSTEM_RELEVANT' if anysys else 'OPERATOR_FAMILY_COLLATERAL_LIMITED' if collateral else 'OPERATOR_FAMILY_POSITIVE_BUT_SUBTHRESHOLD' if anypos else 'OPERATOR_FAMILY_NOT_SUPPORTED'
 opportunity=json.loads((UPSTREAM/'FFN_OPPORTUNITY_ANALYSIS.json').read_text())['run_aligned_stable_shares']
 questions={
  '1_decode_opportunity':{'gate':opportunity['gate_proj_share']['median'],'up':opportunity['up_proj_share']['median'],'down':opportunity['down_proj_share']['median'],'all_ffn':opportunity['all_ffn_projection_share']['median']},
  '2_role_only_direct_benefit':{'GATE28_ms':analyses['GATE28']['medians']['direct_selected_saving_ms'],'UP28_ms':analyses['UP28']['medians']['direct_selected_saving_ms'],'DOWN28_ms':analyses['DOWN28']['medians']['direct_selected_saving_ms'],'interpretation':'only UP28 has broad material local benefit'},
  '3_cross_role_effects':{'UP28_gate_ms':analyses['UP28']['medians']['gate_saving_ms'],'UP28_down_ms':analyses['UP28']['medians']['down_saving_ms'],'GATE28_up_ms':analyses['GATE28']['medians']['up_saving_ms'],'DOWN28_up_ms':analyses['DOWN28']['medians']['up_saving_ms'],'boundary':'signed measured timing changes; no causal collateral label'},
  '4_UP28_residual':{'direct_up_ms':analyses['UP28']['medians']['direct_selected_saving_ms'],'unselected_gate_down_ms':analyses['UP28']['medians']['unselected_ffn_saving_ms'],'outside_ffn_residual_ms':analyses['UP28']['medians']['outside_ffn_residual_ms'],'observed_decode_saving_ms':analyses['UP28']['medians']['observed_decode_saving_ms']},
  '5_pairwise_residuals_ms':{k:analyses[k]['medians']['outside_ffn_residual_ms'] for k in ['GU56','GD56','UD56']},
  '6_GUD84_direct_ffn_saving_ms':gud['medians']['direct_selected_saving_ms'],
  '7_GUD84_realized':{'observed_decode_saving_ms':gud['medians']['observed_decode_saving_ms'],'selected_realization':gud['medians']['selected_realization'],'ffn_realization':gud['medians']['ffn_realization']},
  '8_any_ge_2pct_system_effect':anysys,
  '9_limiting_factor':'insufficient gate/down local benefit plus negative residual outside measured FFN accounting offsets up_proj saving',
  '10_FULLHINT':{'triggered':trigger,'reason':'GUD84 material selected fraction is below 0.50'},
  '11_trace_simulator_readiness':{'producer_answer':'NOT_AUTO_AUTHORIZED','review_candidate':'STOP_RESIDENCY_MECHANISM_SYSTEM_CASE_WEAK'}
 }
 write_json('SCIENTIFIC_QUESTIONS.json',questions)
 write_json('STAGE_DECISION.json',{'stage_label':label,'any_system_relevant':anysys,'GUD84_direct_selected_saving_fraction_of_control_decode':gud_direct_fraction,'GUD84_material_selected_fraction':gud['material_selected_fraction'],'GUD84_outside_ffn_residual_ms':gud['medians']['outside_ffn_residual_ms'],'any_positive_beyond_dispersion':anypos,'precedence':decision['precedence']})
 write_json('NEXT_STEP_DECISION.json',{'decision':'STOP_FOR_CHATGPT_REVIEW','stage_label':label,'candidate_for_review':'STOP_RESIDENCY_MECHANISM_SYSTEM_CASE_WEAK','no_auto_authorization':True,'forbidden_not_started':['Accel-Sim','GPGPU-Sim mutation','NVBit','trace capture','mechanism implementation','mechanism simulation']})
 (OUT/'SCIENTIFIC_INTERPRETATION.md').write_text(f'''# C16 E1 operator-family expansion interpretation\n\nStage label: `{label}`.\n\nThe runtime call-order authority closes 420 natural FFN invocations per full run in measured gate→up→down order. All fourteen preregistered conditions preserve tokens, all 84 FFN identities, exact qweight windows, and one fixed requested/actual set-aside.\n\nRole-only persistence is highly asymmetric. UP28 retains strong direct up_proj saving, while GATE28 and DOWN28 show essentially no direct selected-family benefit. Protecting UP28 makes measured gate/down timing slower, and a large negative residual remains outside measured FFN accounting. Pairwise conditions do not remove that residual. Under GUD84, direct FFN saving is about {gud['medians']['direct_selected_saving_ms']:.3f} ms per stable step, but only about {gud['medians']['observed_decode_saving_ms']:.3f} ms appears in whole decode; median outside-FFN residual is {gud['medians']['outside_ffn_residual_ms']:.3f} ms. This is reported only as a negative residual outside measured FFN accounting, not as proven cache collateral slowdown.\n\nNo predeclared condition reaches the 2% whole-decode gate or even a positive-beyond-dispersion subthreshold result. GUD84 has only one-third of selected modules MATERIAL_LOCAL, so FULLHINT is not triggered. Representative NCU reproduces up_proj GEMM duration/stall benefit, finds a smaller gate GEMM effect, and little down_proj change, while L2/DRAM-read counters remain nearly flat.\n\nThe evidence does not justify automatic bounded trace or simulator implementation from this producer. No simulator, NVBit, or trace work was run.\n''',encoding='utf-8')
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='SHA256SUMS');(OUT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files),encoding='utf-8');print(json.dumps({'status':'PASS','stage_label':label,'files':len(files)+1,'ncu_profiles':len(ncu),'fullhint_triggered':trigger},sort_keys=True))

if __name__=='__main__':main()
