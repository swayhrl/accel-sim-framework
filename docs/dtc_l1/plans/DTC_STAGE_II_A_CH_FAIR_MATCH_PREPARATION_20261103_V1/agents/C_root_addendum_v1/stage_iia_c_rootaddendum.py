from pathlib import Path
import json,hashlib,collections
BASE=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_preparation_20261103_v1');P=BASE/'plan-worktree/docs/dtc_l1/plans/DTC_STAGE_II_A_CH_FAIR_MATCH_PREPARATION_20261103_V1';C=BASE/'agents/C';OUT=BASE/'agents/C_root_addendum_v1';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest();files=['README.md','STATISTICS_AND_HARDWARE_BOUNDARIES.md','RESOURCE_AND_BATCH_PLAN.md','WORKLOAD_CONTROL_AND_OBSERVATIONS.md','NEXT_EXECUTION_GOAL_PENDING_APPROVAL.md','SIX_CELL_PAIRING_PLAN.json','CANDIDATE_RELEASE_STATE.json'];pins=[{'path':n,'bytes':len((P/n).read_bytes()),'sha256':sha((P/n).read_bytes())} for n in files]
audit=json.loads((C/'INDEPENDENT_SET_AUDIT.json').read_text());expected={x['program']:x['input_digest'] for x in audit['candidates']};exp={(x['program'],x['profile']):x for x in audit['candidates']};A=json.loads((P/'agents/A/FIRST_BATCH.json').read_text());first=set(A['candidate_ids']);pair=json.loads((P/'SIX_CELL_PAIRING_PLAN.json').read_text());release=json.loads((P/'CANDIDATE_RELEASE_STATE.json').read_text());checks=[]
def ck(n,b,d=None):checks.append({'check':n,'PASS':bool(b),'detail':d})
cm=json.loads((C/'MANIFEST.json').read_text());ck('Original C14 frozen files unchanged',sha((C/'MANIFEST.json').read_bytes())=='360e040678f8f06aec0ad34c687dc4f144cf9ab1c62ce8764cdc033ceb6a00ae' and all(sha((C/x['path']).read_bytes())==x['sha256'] for x in cm['files']))
ck('Root copies of A B C all manifest-owned bytes match',all(all(sha((P/'agents'/agent/x['path']).read_bytes())==x['sha256'] for x in json.loads((P/'agents'/agent/'MANIFEST.json').read_text())['files']) for agent in ['A','B','C']))
ck('Six-cell plan exact frozen35 identities',{r['program']:r['input_digest'] for r in pair['rows']}==expected)
orig=[];new=[];config=[]
for r in pair['rows']:
 n=r['program'];e=exp[(n,'F128')]['original_status']|exp[(n,'F256')]['original_status']
 for k in ['CH_P0','DH_P0','DH_F128','DH_F256']:
  x=r['cells'][k];y=e[k.replace('_','-')];orig.append(x['cycles']==y['cycles'] and x['cohort']==y['cohort'] and x.get('source_sha256')==y['RESULT_sha256'] and x['accepted']==y['valid'])
 for f in ['F128','F256']:
  x=r['cells']['CH_'+f];new.append(x['cycles'] is None and x['status']=='PLANNED_NOT_REGISTERED_NOT_AUTHORIZED_NOT_MEASURED')
  for a in x['config_files']:
   pp=P/a['path'];base=x.get('config_files_base',pair.get('config_files_base',''))
   if not pp.exists() and base:pp=P/base/a['path']
   config.append({'program':n,'profile':f,'path':str(pp),'PASS':pp.exists() and sha(pp.read_bytes())==a['sha256']})
ck('Original140 six-cell values preserve status and source identity',len(orig)==140 and all(orig))
ck('New CH70 cycles null not accepted',len(new)==70 and all(new) and pair['CH_variant_measurements_available']==0 and not pair['IR_R2_EP_PQ_PS_performance_used'])
ck('Root embedded config locators resolve and hashes match',len(config)==280 and all(x['PASS'] for x in config),{'verified':len(config),'bad':[x for x in config if not x['PASS']][:5]})
cs=release['candidates'];cc=collections.Counter(x['category'] for x in cs);ck('70 release candidates64/2/4 no grant start request UUID',len(cs)==70 and cc=={'CORE':64,'SUPPLEMENT':2,'DEFERRED':4} and release['planned']==70 and release['grants']==release['starts']==0 and all(x['UUID'] is None and x['scientific_request'] is None and not x['actual_execution_authorized'] and x['registration_state']=='NOT_REGISTERED' and x['measured_cycles'] is None for x in cs))
ck('First16 membership equals frozen A first batch; remaining48 not released',{x['candidate_id'] for x in cs if x['first_batch']}==first and len(first)==16 and len([x for x in cs if x['category']=='CORE' and not x['first_batch']])==48)
ck('All release categories exact independent original adjudication',all(x['category']=={'CORE_FOURWAY':'CORE','SUPPLEMENTAL':'SUPPLEMENT','DEFERRED':'DEFERRED'}[exp[(x['program'],x['profile'])]['classification']] for x in cs))
# Prose review is recorded separately; string checks only guard presence, not proof of scientific causation.
stat=(P/'STATISTICS_AND_HARDWARE_BOUNDARIES.md').read_text();nextg=(P/'NEXT_EXECUTION_GOAL_PENDING_APPROVAL.md').read_text();res=(P/'RESOURCE_AND_BATCH_PLAN.md').read_text();control=(P/'WORKLOAD_CONTROL_AND_OBSERVATIONS.md').read_text()
ck('No execution authorizations hidden in proposal release state','尚未获执行授权' in nextg and '不启动本Goal' in nextg and '计划文件本身不构成grant' in nextg)
ck('Resource estimate not guaranteed full-run bound',all(x in res for x in ['不是硬上限或未来实测','不能保证','不把失败峰值当完整成功上界','必须重新测','压力暂停新准入']))
ck('Evidence-source caveats and per-kernel missingness preserved',all(x in control for x in ['捕获源码/ELF尚未认证','不换输入','43条有计数器','WHOLE_TRACE_ONLY','不能单独证明']))
ck('V2 uniform candidate must retain frozen35 coverage', '统一候选最终仍须覆盖原冻结35' in stat and '不能临时缩成受益程序' in stat)
(OUT/'ROOT_INTEGRATION_REVIEW.json').write_text(json.dumps({'schema':'DTC_STAGE_IIA_C_ROOT_INTEGRATION_REVIEW_ADDENDUM_V1','reviewed_root':str(P),'planning_status':'PASS' if all(x['PASS'] for x in checks) else 'HOLD','execution_status':'NOT_AUTHORIZED','checks':checks,'all_checks_PASS':all(x['PASS'] for x in checks),'root_file_SHA_receipts':pins,'pending_links_excluded_from_defects':['CPU_INTEGRATION_QUALIFICATION.json','NO_EXECUTION_INTEGRITY.json','MANIFEST.json','PUBLICATION_READBACK.json'],'semantic_review_note':'Root addressed both review clarifications before final readback: explicit V2 frozen35 requirement and config_files_base=agents/A. No source or old AgentC files modified.'},indent=2)+'\n');print(json.dumps([{'check':x['check'],'PASS':x['PASS']} for x in checks],indent=2))

