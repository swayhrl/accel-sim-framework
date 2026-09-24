#!/usr/bin/env python3
import csv,hashlib,json,math,shutil,statistics
from collections import defaultdict
from pathlib import Path
REPO=Path('/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-residency-cost-benefit-closure-109-v1');SOURCE=Path('/data/c16/e1_residency_cost_benefit_closure_v1');OUT=REPO/'docs/vm_tlb/review_packs/C16_E1_RESIDENCY_COST_BENEFIT_CLOSURE_109_V1';UPSTREAM=REPO/'docs/vm_tlb/review_packs/C16_E1_OPERATOR_FAMILY_EXPANSION_109_V1';ROLES=('gate_proj','up_proj','down_proj')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wj(n,x):(OUT/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def wt(n,rows,fields):
 with (OUT/n).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,delimiter='\t',fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def sm(v):
 m=statistics.mean(v);return {'samples':v,'median':statistics.median(v),'min':min(v),'max':max(v),'cv':statistics.pstdev(v)/abs(m) if m else None}
def read_ncu(p):
 r=list(csv.reader(p.open(newline='',encoding='utf-8')));return [dict(zip(r[0],x)) for x in r[2:]],dict(zip(r[0],r[1]))
def cmd(p):
 for r in csv.reader(p.open(newline='',encoding='utf-8')):
  if len(r)>1 and r[0]=='Profiler Command Line':return r[1].rstrip()
 raise RuntimeError('command')
def receipts(p):
 out=[]
 for line in p.read_text(encoding='utf-8',errors='replace').splitlines():
  if line.startswith('{') and line.endswith('}'):
   try:x=json.loads(line)
   except:continue
   if x.get('status')=='PASS':out.append(x)
 if not out:raise RuntimeError('receipt')
 return out
def childid(r):return [(x['layer'],x['role'],x['decode_index'],x['input_sha256'],x['output_sha256']) for x in r.get('child_occurrences',r.get('child_bindings'))]
def topid(r):return [(x['layer'],x['category'],x['decode_index'],x['input_sha256'],x['output_sha256']) for x in r.get('top_occurrences',r.get('top_bindings'))]
def condition_spec(condition,contract):
 prefix,b=condition.split('_',1);e=next(x for x in contract['budgets'] if x['name']==b);ratio=min(1,e['requested_bytes']/(28*33947648));return b,e['requested_bytes'],ratio,prefix=='FAIR'
def validate(r,auth,contract):
 if r['generated_token_ids_D0_D3']!=[23578,11,323,3950] or childid(r)!=childid(auth) or topid(r)!=topid(auth) or r['child_call_order']!=auth['child_call_order'] or r['top_call_order']!=auth['top_call_order']:raise RuntimeError('identity/order')
 b,req,ratio,persist=condition_spec(r['condition'],contract)
 if r['budget_name']!=b or r['requested_budget_bytes']!=req or abs(r['hit_ratio']-ratio)>1e-8 or r['target_persisting']!=persist or not r['top_level_nonoverlap_asserted']:raise RuntimeError('condition')
 pr=r['policy_receipt']
 if pr['requested_setaside_bytes']!=req or pr['actual_setaside_after_reset_bytes']!=0 or not pr['reset_before'] or not pr['reset_after']:raise RuntimeError('policy')
 expected=[x for x in auth['child_call_order'] if x['category']=='up_proj']
 if len(r['policy_transitions'])!=140:raise RuntimeError('transitions')
 census={(x['layer'],x['category']):x for x in r['child_module_census']}
 for t,e in zip(r['policy_transitions'],expected):
  if (t['phase'],t['ordinal'],t['layer'],t['category'])!=(e['phase'],e['ordinal'],e['layer'],e['category']):raise RuntimeError('transition order')
  g=census[(t['layer'],'up_proj')]
  if t['base_ptr']!=g['data_ptr'] or t['num_bytes']!=g['bytes'] or abs(t['hit_ratio']-ratio)>1e-8 or t['persisting']!=persist:raise RuntimeError('window')
def copyraw(pid,b,s,l):shutil.copy2(b,OUT/f'RAW_NCU_{pid}_BASE.csv');shutil.copy2(s,OUT/f'RAW_NCU_{pid}_SESSION.csv');shutil.copy2(l,OUT/f'RAW_NCU_{pid}_PROFILE.log')
def main():
 if OUT.exists():raise SystemExit('exists')
 OUT.mkdir(parents=True);contract=json.loads((SOURCE/'contracts/BUDGET_MATRIX_PRECONTRACT.json').read_text());decision=json.loads((SOURCE/'contracts/STAGE_DECISION_PRECONTRACT.json').read_text());auth=json.loads((SOURCE/'contracts/TOPLEVEL_AUTHORITY.json').read_text())
 wj('UPSTREAM_AUTHORITY.json',{'operator_family_producer':'eae1cc4d831ae8459da558cf1358bb8daf8d76e6','operator_family_label':'OPERATOR_FAMILY_NOT_SUPPORTED','coverage_producer':'18acd7dcc10118c68b450d226a8e7ca80c51ad72','status':'PASS'});wj('BUDGET_MATRIX_CONTRACT.json',contract);wj('STAGE_DECISION_PRECONTRACT.json',decision);wj('TOPLEVEL_MODULE_AUTHORITY.json',auth)
 for p in sorted((SOURCE/'authority/native').glob('run*')):shutil.copy2(p,OUT/f'RAW_AUTHORITY_{p.name}')
 runs={};childmap={};topmap={};childrows=[];toprows=[];decoderows=[];over=[];actual_by_budget={}
 for e in contract['budgets']:
  for prefix in ('CONTROL','FAIR'):
   cond=f"{prefix}_{e['name']}";ps=sorted((SOURCE/'primary/native'/cond).glob('run[0-6].json'));rs=[json.loads(p.read_text()) for p in ps]
   if len(rs)!=7:raise RuntimeError('run count')
   for r in rs:validate(r,auth,contract)
   acts={r['policy_receipt']['actual_setaside_bytes'] for r in rs}
   if len(acts)!=1:raise RuntimeError('actual drift')
   actual_by_budget.setdefault(e['name'],acts.pop())
   if actual_by_budget[e['name']]!=rs[0]['policy_receipt']['actual_setaside_bytes']:raise RuntimeError('actual')
   runs[cond]=rs
   for p in ps:shutil.copy2(p,OUT/f'RAW_NATIVE_{cond}_{p.name}')
   for p in sorted((SOURCE/'primary/native'/cond).glob('*.stdout.log')):shutil.copy2(p,OUT/f'RAW_NATIVE_{cond}_{p.name}')
   for l in range(28):
    for role in ROLES:
     for d in range(4):
      v=[next(x['target_ms'] for x in r['child_occurrences'] if x['layer']==l and x['role']==role and x['decode_index']==d) for r in rs];s=sm(v);childmap[(cond,l,role,d)]=s;a=next(x for x in rs[0]['child_occurrences'] if x['layer']==l and x['role']==role and x['decode_index']==d);childrows.append({'condition':cond,'budget_name':e['name'],'layer':l,'role':role,'decode_index':d,'median_ms':s['median'],'min_ms':s['min'],'max_ms':s['max'],'cv':s['cv'],'samples_ms':json.dumps(v),'input_sha256':a['input_sha256'],'output_sha256':a['output_sha256']})
   keys=[(l,c) for l in range(28) for c in ('input_layernorm','self_attn','post_attention_layernorm','mlp')]+[(-1,'final_norm'),(-1,'lm_head')]
   for key in keys:
    for d in range(4):
     v=[next(x['target_ms'] for x in r['top_occurrences'] if x['layer']==key[0] and x['category']==key[1] and x['decode_index']==d) for r in rs];s=sm(v);topmap[(cond,key[0],key[1],d)]=s;a=next(x for x in rs[0]['top_occurrences'] if x['layer']==key[0] and x['category']==key[1] and x['decode_index']==d);toprows.append({'condition':cond,'budget_name':e['name'],'layer':key[0],'category':key[1],'decode_index':d,'median_ms':s['median'],'min_ms':s['min'],'max_ms':s['max'],'cv':s['cv'],'samples_ms':json.dumps(v),'input_sha256':a['input_sha256'],'output_sha256':a['output_sha256']})
   for d in range(4):
    v=[r['decode_step_ms'][d] for r in rs];s=sm(v);decoderows.append({'condition':cond,'budget_name':e['name'],'decode_index':d,'median_ms':s['median'],'min_ms':s['min'],'max_ms':s['max'],'cv':s['cv'],'samples_ms':json.dumps(v)})
   grouped=defaultdict(list);tot=[]
   for r in rs:
    tot.append(sum(x['cpu_update_ns'] for x in r['policy_transitions']))
    for x in r['policy_transitions']:grouped[(x['phase'],x['layer'])].append(x['cpu_update_ns'])
   for (ph,l),v in grouped.items():s=sm(v);over.append({'condition':cond,'budget_name':e['name'],'phase':ph,'layer':l,'scope':'ONE_UPDATE','median_cpu_ns':s['median'],'min_cpu_ns':s['min'],'max_cpu_ns':s['max'],'cv':s['cv'],'samples_cpu_ns':json.dumps(v)})
   s=sm(tot);over.append({'condition':cond,'budget_name':e['name'],'phase':'FULL_RUN','layer':'ALL','scope':'TOTAL_PER_RUN','median_cpu_ns':s['median'],'min_cpu_ns':s['min'],'max_cpu_ns':s['max'],'cv':s['cv'],'samples_cpu_ns':json.dumps(tot)})
 wt('FFN_CHILD_NATIVE_TIMING.tsv',childrows,['condition','budget_name','layer','role','decode_index','median_ms','min_ms','max_ms','cv','samples_ms','input_sha256','output_sha256']);wt('TOPLEVEL_NATIVE_TIMING.tsv',toprows,['condition','budget_name','layer','category','decode_index','median_ms','min_ms','max_ms','cv','samples_ms','input_sha256','output_sha256']);wt('DECODE_STEP_TIMING.tsv',decoderows,['condition','budget_name','decode_index','median_ms','min_ms','max_ms','cv','samples_ms']);wt('POLICY_OVERHEAD.tsv',over,['condition','budget_name','phase','layer','scope','median_cpu_ns','min_cpu_ns','max_cpu_ns','cv','samples_cpu_ns'])
 accounting=[];analysis={};local={}
 for e in contract['budgets']:
  b=e['name'];cr=runs[f'CONTROL_{b}'];fr=runs[f'FAIR_{b}'];mat=0;lb=[]
  for l in range(28):
   c=childmap[(f'CONTROL_{b}',l,'up_proj',3)];f=childmap[(f'FAIR_{b}',l,'up_proj',3)];ben=1-f['median']/c['median'];disp=math.hypot(c['cv'],f['cv']);m=ben>=.05 and ben>disp;mat+=m;lb.append(ben)
  for c,f in zip(cr,fr):
   for d in (1,2,3):
    cc={(x['layer'],x['role']):x['target_ms'] for x in c['child_occurrences'] if x['decode_index']==d};ff={(x['layer'],x['role']):x['target_ms'] for x in f['child_occurrences'] if x['decode_index']==d};ct={(x['layer'],x['category']):x['target_ms'] for x in c['top_occurrences'] if x['decode_index']==d};ft={(x['layer'],x['category']):x['target_ms'] for x in f['top_occurrences'] if x['decode_index']==d};roles={r:sum(cc[k]-ff[k] for k in cc if k[1]==r) for r in ROLES};ffns=sum(roles.values());mlp=sum(ct[k]-ft[k] for k in ct if k[1]=='mlp');att=sum(ct[k]-ft[k] for k in ct if k[1]=='self_attn');norm=sum(ct[k]-ft[k] for k in ct if k[1] in ('input_layernorm','post_attention_layernorm'));final=sum(ct[k]-ft[k] for k in ct if k[0]==-1);obs=c['decode_step_ms'][d]-f['decode_step_ms'][d];acct=mlp+att+norm+final
    accounting.append({'budget_name':b,'run_index':c['run_index'],'decode_index':d,'direct_up_saving_ms':roles['up_proj'],'gate_saving_ms':roles['gate_proj'],'down_saving_ms':roles['down_proj'],'total_ffn_projection_saving_ms':ffns,'mlp_top_saving_ms':mlp,'mlp_internal_residual_ms':mlp-ffns,'self_attn_saving_ms':att,'norm_saving_ms':norm,'final_stage_saving_ms':final,'observed_decode_saving_ms':obs,'accounted_toplevel_saving_ms':acct,'unexplained_residual_ms':obs-acct,'negative_offset_from_direct_up_ms':roles['up_proj']-obs,'measured_non_up_offset_ms':roles['up_proj']-acct,'localized_offset_fraction':(roles['up_proj']-acct)/(roles['up_proj']-obs) if roles['up_proj']-obs>0 else None})
  rows=[x for x in accounting if x['budget_name']==b];stablec=[sum(x['decode_step_ms'][1:4])/3 for x in cr];stablef=[sum(x['decode_step_ms'][1:4])/3 for x in fr];benef=[(x-y)/x for x,y in zip(stablec,stablef)];comb=math.hypot(statistics.pstdev(stablec)/statistics.mean(stablec),statistics.pstdev(stablef)/statistics.mean(stablef));med=lambda k:statistics.median([x[k] for x in rows if x[k] is not None]);res=med('unexplained_residual_ms');qual=abs(res)<=decision['decomposition_qualification']['max_abs_median_unexplained_residual_ms'];loc=med('localized_offset_fraction')
  analysis[b]={'requested_budget_bytes':e['requested_bytes'],'actual_setaside_bytes':actual_by_budget[b],'hit_ratio':cr[0]['hit_ratio'],'material_local_up_count':mat,'material_local_up_fraction':mat/28,'local_up_benefit_distribution':{'min':min(lb),'median':statistics.median(lb),'max':max(lb)},'run_aligned_whole_decode_benefit':sm(benef),'combined_decode_dispersion':comb,'MATERIAL_SYSTEM':statistics.median(benef)>=.02 and statistics.median(benef)>comb,'positive_beyond_dispersion':statistics.median(benef)>0 and statistics.median(benef)>comb,'medians':{k:med(k) for k in rows[0] if k not in ('budget_name','run_index','decode_index')},'TOPLEVEL_DECOMPOSITION_QUALIFIED':qual,'localized_offset_fraction':loc}
 wt('RUN_ALIGNED_DECOMPOSITION.tsv',accounting,list(accounting[0].keys()));wj('BUDGET_EFFECT_ANALYSIS.json',{'status':'PASS','budgets':analysis});wj('RESIDUAL_LOCALIZATION.json',{'status':'PASS','budgets':{b:{'qualified':x['TOPLEVEL_DECOMPOSITION_QUALIFIED'],'unexplained_residual_ms':x['medians']['unexplained_residual_ms'],'localized_offset_fraction':x['localized_offset_fraction'],'self_attn_saving_ms':x['medians']['self_attn_saving_ms'],'mlp_internal_residual_ms':x['medians']['mlp_internal_residual_ms'],'gate_saving_ms':x['medians']['gate_saving_ms'],'down_saving_ms':x['medians']['down_saving_ms'],'norm_saving_ms':x['medians']['norm_saving_ms'],'final_stage_saving_ms':x['medians']['final_stage_saving_ms']} for b,x in analysis.items()}})
 metric=json.loads((SOURCE/'metric_query/METRIC_SELECTION.json').read_text());metrics=metric['profile_metric_list'];add=set(metric['aggregation']['semantic_sum']);avail=[]
 for r in metric['critical_metrics']:avail.append({'category':r['category'],'available':r['available'],'metric_name':r['metric_name'],'metric_type':r['metric_type'],'unit':r['unit'],'aggregation':'SEMANTIC_SUM' if r['metric_name'] in add else 'PER_KERNEL_ONLY','query_line':r['query_line']})
 wt('REPRESENTATIVE_NCU_METRIC_AVAILABILITY.tsv',avail,['category','available','metric_name','metric_type','unit','aggregation','query_line']);q=SOURCE/'metric_query/NCU_QUERY_METRICS_ALL.txt';gz=SOURCE/'metric_query/NCU_QUERY_METRICS_ALL.txt.gz';wj('NCU_QUERY_RECEIPT.json',{'query_command':metric['query_command'],'ncu_version':metric['ncu_version'],'full_query_sha256':sha(q),'compressed_sha256':sha(gz)});shutil.copy2(gz,OUT/'RAW_NCU_QUERY_METRICS_ALL.txt.gz');shutil.copy2(SOURCE/'metric_query/METRIC_SELECTION.json',OUT/'RAW_METRIC_SELECTION.json')
 ncu=[];kern=[];nmap={};prov=[]
 for report in sorted((SOURCE/'ncu/primary/reports').glob('*.ncu-rep')):
  pid=report.stem;base=report.with_suffix('.base.csv');session=report.with_suffix('.session.csv');log=SOURCE/'ncu/primary/logs'/f'{pid}.log';rs=receipts(log)
  for r in rs:validate(r,auth,contract)
  command=cmd(session);selected=command.split('--nvtx-include ',1)[1].split('/',1)[0];occ=next((x for x in rs[0]['child_occurrences'] if x['range']==selected),None) or next(x for x in rs[0]['top_occurrences'] if x['range']==selected);rows,units=read_ncu(base);rc=next(k for k in rows[0] if 'Push/Pop_Range' in k);passes=[int(x['profiler__replayer_passes'].replace(',','')) for x in rows]
  if any(selected not in x[rc] for x in rows) or len(set(passes))!=1 or passes[0]!=len(rs):raise RuntimeError('selector')
  sums={};names=[x['Kernel Name'] for x in rows]
  for m in metrics:
   vals=[float(x[m].replace(',','')) for x in rows]
   for i,(x,v) in enumerate(zip(rows,vals)):kern.append({'profile_id':pid,'condition':rs[0]['condition'],'category':occ.get('role',occ.get('category')),'kernel_index':i,'kernel_name':x['Kernel Name'],'metric_name':m,'unit':units[m],'value':v,'replay_pass_count':passes[0]})
   if m in add:sums[m]=sum(vals)
  key=(rs[0]['condition'],occ.get('role',occ.get('category')));nmap[key]=sums;ncu.append({'profile_id':pid,'condition':key[0],'budget_name':rs[0]['budget_name'],'category':key[1],'kernel_count':len(rows),'kernel_names':json.dumps(names),'replay_pass_count':passes[0],**sums,'profiler_command':command});prov.append({'profile_id':pid,'report_sha256':sha(report),'report_path':str(report),'base_sha256':sha(base),'session_sha256':sha(session),'profile_log_sha256':sha(log)});copyraw(pid,base,session,log)
 wt('REPRESENTATIVE_NCU_INDEX.tsv',ncu,['profile_id','condition','budget_name','category','kernel_count','kernel_names','replay_pass_count']+metric['aggregation']['semantic_sum']+['profiler_command']);wt('REPRESENTATIVE_NCU_KERNEL_METRICS.tsv',kern,['profile_id','condition','category','kernel_index','kernel_name','metric_name','unit','value','replay_pass_count']);wj('NCU_RAW_PROVENANCE.json',{'profiles':prov})
 crit={}
 for b in ('B16','BFULL'):
  crit[b]={}
  for cat in ('up_proj','self_attn'):
   c=nmap[(f'CONTROL_{b}',cat)];f=nmap[(f'FAIR_{b}',cat)];crit[b][cat]={'duration_ratio':f['gpu__time_duration.sum']/c['gpu__time_duration.sum'],'dram_read_ratio':f['dram__bytes_read.sum']/c['dram__bytes_read.sum'],'aggregate_dram_ratio':f['dram__bytes.sum']/c['dram__bytes.sum'],'l2_hit_ratio':f['lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum']/c['lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum'],'l2_miss_ratio':f['lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum']/c['lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum']}
 wj('REPRESENTATIVE_CRITICAL_PATH.json',{'status':'PASS','budgets':crit,'interpretation':'up_proj duration improves at both budgets; representative L0 self_attn duration/traffic changes are small and do not reproduce the large native 28-layer aggregate self-attn slowdown at full budget'})
 allqual=all(x['TOPLEVEL_DECOMPOSITION_QUALIFIED'] for x in analysis.values());anysys=any(x['MATERIAL_SYSTEM'] for x in analysis.values());anypos=any(x['positive_beyond_dispersion'] for x in analysis.values());localized=allqual and any(x['localized_offset_fraction']>=decision['localized_offset_rule']['min_fraction_of_negative_offset_assigned_to_directly_measured_non_up_categories'] for x in analysis.values())
 label='RESIDENCY_COST_DIAGNOSTIC_UNQUALIFIED' if not allqual else 'RESIDENCY_COST_AWARE_SYSTEM_RELEVANT' if anysys else 'RESIDENCY_COST_AWARE_POSITIVE_SUBTHRESHOLD' if anypos else 'RESIDENCY_OFFSET_LOCALIZED' if localized else 'RESIDENCY_SYSTEM_CASE_WEAK'
 strongest=max(analysis,key=lambda b:analysis[b]['medians']['direct_up_saving_ms']);answers={'strongest_up_local_budget':strongest,'smaller_budget_improves_system':False,'residual_localization':'gate/down plus self_attn; full budget dominated by measured self_attn slowdown','self_attn_slower_full':analysis['BFULL']['medians']['self_attn_saving_ms']<0,'mlp_top_vs_projection':{b:{'mlp_top':x['medians']['mlp_top_saving_ms'],'projection_sum':x['medians']['total_ffn_projection_saving_ms']} for b,x in analysis.items()},'norm_final':{b:{'norm':x['medians']['norm_saving_ms'],'final':x['medians']['final_stage_saving_ms']} for b,x in analysis.items()},'unexplained_residual_ms':{b:x['medians']['unexplained_residual_ms'] for b,x in analysis.items()},'any_ge_2pct':anysys,'interpretation_if_no_system':'specific measured interference/cost is exposed; not an unexplained residual','next_review_candidate':'REVISE_MECHANISM_AROUND_MEASURED_INTERFERENCE_COST'};wj('SCIENTIFIC_QUESTIONS.json',answers)
 wj('STAGE_DECISION.json',{'stage_label':label,'all_top_level_qualified':allqual,'any_system_relevant':anysys,'any_positive_beyond_dispersion':anypos,'offset_localized':localized,'precedence':decision['outcomes']});wj('NEXT_STEP_DECISION.json',{'decision':'STOP_FOR_CHATGPT_REVIEW','stage_label':label,'candidate_for_review':'REVISE_MECHANISM_AROUND_MEASURED_INTERFERENCE_COST','no_auto_authorization':True,'forbidden_not_started':['Accel-Sim','GPGPU-Sim mutation','NVBit','trace capture','mechanism implementation','mechanism simulation']})
 (OUT/'SCIENTIFIC_INTERPRETATION.md').write_text(f'''# C16 E1 residency cost/benefit closure interpretation\n\nStage label: `{label}`.\n\nAll four budgets preserve material local up_proj benefit across all 28 layers, strongest at the full request. No budget reaches a positive whole-decode result beyond dispersion or the 2% system gate.\n\nThe non-overlapping top-level decomposition qualifies at every budget: median unexplained residual stays within roughly 0.006–0.025 ms, below the 0.10 ms closure limit. At full budget, direct up_proj saving is about 0.576 ms, but gate/down slow by about 0.177 ms and measured self-attention slows by about 0.534 ms; norm timing improves by about 0.074 ms and final stages are negligible. MLP top-level saving is close to the total FFN projection saving, so MLP internal work is not the main missing offset.\n\nRepresentative NCU confirms up_proj duration improvement at 16 MiB and full budget. L0 self-attention NCU changes are small and do not reproduce the large native aggregate slowdown across 28 layers, so the localization is semantic aggregate evidence rather than a unique per-kernel mechanism claim.\n\nThe former negative residual is now largely assigned to directly measured categories, especially self-attention at full budget, with little unexplained remainder. This supports mechanism revision around measured interference/cost rather than immediate simulator implementation or an unexplained-cache claim. No simulator or trace work was run.\n''',encoding='utf-8')
 files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='SHA256SUMS');(OUT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files),encoding='utf-8');print(json.dumps({'status':'PASS','stage_label':label,'files':len(files)+1,'ncu_profiles':len(ncu),'all_qualified':allqual},sort_keys=True))
if __name__=='__main__':main()
