import importlib.util,pathlib,json,math,copy,ast
D=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('pure_combo_reader',D/'consumer.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
checks=[]
def ck(n,v):assert v,n;checks.append({'name':n,'PASS':True})
ck('no_combo_prediction',c.metrics(None,100,120,90,80)['S_combo']is None and c.metrics(None,100,120,90,80)['J']is None)
ck('known_singles_stay_known_without_prediction',c.metrics(None,100,120,90,80)['S_physical']==100/90)
ck('missing_PIB_J_null',c.metrics(75,100,120,90,None)['J']is None)
ck('missing_phys_J_null',c.metrics(75,100,120,None,80)['J']is None)
x=c.metrics(75,100,120,90,80);ck('real_term_formula',x['S_combo']==100/75 and x['R_combo']==120/75 and x['J']==90*80/(100*75))
ck('J_not_absolute_DTC_win',c.metrics(105,100,90,130,130)['J']>1 and c.metrics(105,100,90,130,130)['R_combo']<1)
rows=[]
for v in ['PHYS768_OOPIB192_TAG64x8','PHYS1024_OOPIB192_TAG64x8']:
 for i in range(8):
  accepted=i<(7 if v.startswith('PHYS768')else 6);cycles=80+i if accepted else None;pc=90 if i<5 else None;bc=85 if i<5 else None;r=dict(program='CPU_FIXTURE_'+str(i),suite='CPU_FIXTURE_SUITE',input_digest=str(i),variant=v,accepted=accepted,status='ACCEPTED_STRICT_ARCHIVE_RESTORE'if accepted else'AWAIT_CLOSED_RESULT',cycles=cycles,baseline_DH_cycles=100,baseline_CH_cycles=110,V1_physical={'cycles':pc},V1_PIB={'cycles':bc});r.update(c.metrics(cycles,100,110,pc,bc));rows.append(r)
s=c.summarize(rows);ck('16cells_not16programs',s['planned_combo_cells']==16 and s['fixed_program_inputs']==8);ck('common_combo_intersection_6',s['common_combo_accepted_inputs']['n']==6);ck('common_J_intersection_5',s['common_J_complete_terms_inputs']['n']==5);ck('partial_not_uniform_full',all(x['not_full8_until_all_accepted']for x in s['profiles'].values()));ck('GM_common_same_membership',all(v['S_combo']['n']==6 for v in s['common_combo_accepted_inputs']['profiles'].values()));ck('GM_J_common_same_membership',all(v['J']['n']==5 for v in s['common_J_complete_terms_inputs']['profiles'].values()));ck('pending_not_zero_performance',all(r['S_combo']is None and r['J']is None for r in rows if not r['accepted']))
# Exact arithmetic signs do not depend on float tolerance.
r=copy.deepcopy(rows[0]);r['cycles']=100;r['S_combo']=1.0;r['I']=1.0;ck('exact_cycle_zero',c.metric_stats([r],'S_combo')['zero_exact_arithmetic']==1)
r['cycles']=101;r['S_combo']=100/101;ck('negative_preserved',c.metric_stats([r],'S_combo')['negative_exact']==1)
# A legally archived negative may naturally exit0 after strict rejection.
c.cr.validate_exit_policy({'stop_reason':None,'launcher_wait_returncode':0},False);ck('natural0_strict_negative_allowed',True)
for a,tag in [({'stop_reason':'CPU_FIXTURE_STOP','launcher_wait_returncode':0},'stop'),({'stop_reason':None,'launcher_wait_returncode':1},'rc')]:
 try:c.cr.validate_exit_policy(a,True);ok=False
 except Exception:ok=True
 ck('accepted_reject_'+tag,ok)
# Extracted qualification function ASTs are identical to already independently reviewed V2 reader.
old=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1/agents/B_perf_results_consumer_v2/snapshot.py');a=ast.parse(old.read_text());b=ast.parse((D/'closed_reader.py').read_text())
for name in ['baselines','strict_literals','validate_exit_policy','qualify_closed']:
 aa=next(n for n in a.body if isinstance(n,ast.FunctionDef)and n.name==name);bb=next(n for n in b.body if isinstance(n,ast.FunctionDef)and n.name==name);ck('qualification_exact_reviewed_AST_'+name,ast.dump(aa,include_attributes=False)==ast.dump(bb,include_attributes=False))
# Canonical dispatch-spec serialization is unchanged from the original qualifier.
ck('canonical_spec_json_newline',c.cr.js({'x':1})==(json.dumps({'x':1},sort_keys=True,indent=2)+'\n').encode())
m,cs,a,base,refs=c.matrix()
for inp in a['inputs']:
 program=inp['population']['program'];dh=base[program,'DH'];ch=base[program,'CH'];v=c.read(dh['canonical_RESULT']['path']);kr=c.closed_kernel_rows({'cycles':dh['cycles'],'kernels':v['proof']['kernels']},dh,ch);ck('actual_closed_P0_kernel_schema_'+program,len(kr)==dh['expected']['kernels']and all(x['within_DH_cycle_delta']==0 for x in kr))
(D/'CPU_QUALIFICATION.json').write_text(json.dumps({'schema':'CPU_ONLY_COMBO_READER_FIXTURES_V1','all_pass':True,'count':len(checks),'checks':checks,'fixture_scope':'Pure arithmetic/missingness/common-set/signs/negative exit policy and exact reviewed reader AST, plus all8 actual closedP0 kernel-schema metadata checks. Synthetic cycles are CPU_FIXTURE_ONLY, never scientific model results. Actual grant/archive/new16 runtime qualification not claimed by these fixtures.','fixture_math_summary':s,'new_models':0,'native_writes':0,'no_V1_service_called':True},indent=2)+'\n');print('PASS',len(checks))
