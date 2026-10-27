"""One finite metadata snapshot; append only. No active raw/trace/control access."""
import pathlib,json,hashlib,datetime
R=pathlib.Path('/root/data/dtc_hash_downstream18_20261027_v1')
A=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_p42_parallel_mechanism_review_v1/agents/E')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
prior_manifest=json.loads((A/'DELIVERY_MANIFEST.json').read_text())
prior_hashes={x['name']:sha(A/x['name']) for x in prior_manifest['files']}
prior_hashes['DELIVERY_MANIFEST.json']=sha(A/'DELIVERY_MANIFEST.json')
# This script runs on 164/174 Linux. Preservation hashes below apply to
# that original copy; Windows may retain a separately hashed CRLF manifest.
# Never infer identity of the manifest itself from its listed file identities.
prior=json.loads((A/'PQ_PS_INDEPENDENT_REVIEW.json').read_text());old=json.loads((A/'ACCEPTED_CELL_EVIDENCE.json').read_text());oldcoh={x['cohort'] for x in old}
sp=R/'analysis/AUTO_SUMMARY.json';buf=sp.read_bytes();summary=json.loads(buf);cutoff=datetime.datetime.now(datetime.timezone.utc).isoformat();sources=[{'path':str(sp),'sha256':hashlib.sha256(buf).hexdigest(),'observed_UTC':cutoff}]
def load(p):
 p=pathlib.Path(p);b=p.read_bytes();sources.append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)});return json.loads(b)
checks=[]
def ck(n,b):
 checks.append({'check':n,'pass':bool(b)})
 if not b:raise AssertionError(n)
freeze=load(R/'control/FREEZE_MANIFEST.json');frozen={v['path']:v['sha256'] for v in freeze['files']};added=[]
for coh,state in sorted(summary['states'].items()):
 if state!='PASS_DOWNSTREAM18_STRICT_ARCHIVE_NATIVE_RESTORE' or coh in oldcoh:continue
 specpath=R/'control'/(coh+'_SPEC.json');s=load(specpath);rrpath=R/'analysis'/(coh+'.RESULT.json');r=load(rrpath);p=r['proof'];dp=R/'control/qualification_ledger'/(coh+'.DONE.json');d=load(dp);out=R/'DTC/run/results'/r['uuid'];ex=load(out/'NATIVE_EXIT.json')
 ck(coh+'_frozen_spec',sha(specpath)==frozen[str(specpath)])
 ck(coh+'_natural_success',d==ex and d['stop_reason'] is None and d['launcher_wait_returncode']==0 and d['native_simulator_observed'] and d['uuid']==r['uuid'])
 ck(coh+'_strict_acceptance',r['state']==state and p['performance_accepted'] and p['performance_scope']=='NEW_DOWNSTREAM18_ONLY' and r['new_contract_only'] and not r['original_or_repair_results_replaced'])
 ck(coh+'_identity',p['input_digest']==s['input_digest'] and p['core_commit']==s['core_commit']==prior['core_commit'] and p['framework_commit']==s['framework_commit']==prior['framework_commit'] and p['binary_sha256']==s['binary_sha256']==prior['binary_sha256'])
 ck(coh+'_effective_options',p['effective_options']==s['expected_options'])
 for c in s['configs']:ck(coh+'_'+pathlib.Path(c['path']).name,sha(c['path'])==c['sha256'])
 ck(coh+'_input_binding',sha(s['input_binding_path'])==s['input_binding_sha256'])
 ck(coh+'_population',p['instructions']==s['expected']['instructions'] and p['CTA']==s['expected']['CTA'] and p['kernel_count']==s['expected']['kernels']==2 and sum(x['cycles'] for x in p['kernels'])==p['cycles']==r['cycles'])
 ck(coh+'_archive_restore',r['archive']['receipt']['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET' and r['archive']['receipt']['source_disposition']=='SOURCE_KEEP')
 ck(coh+'_raw_identity',d['raw_sha256']==p['raw_gzip_sha256'] and d['raw_uncompressed_sha256']==p['raw_uncompressed_sha256'])
 added.append({'program':s['program'],'cell':s['cell'],'profile':s['downstream_profile'],'cohort':coh,'uuid':r['uuid'],'input_digest':s['input_digest'],'cycles':r['cycles'],'kernels':p['kernels'],'metrics':p['metrics'],'traffic':p['traffic'],'latency_counters':p['latency_counters'],'core_commit':p['core_commit'],'framework_commit':p['framework_commit'],'binary_sha256':p['binary_sha256'],'library_sha256':prior['core_library_sha256'],'raw_path':str(out/'raw.log.gz'),'raw_gzip_sha256':p['raw_gzip_sha256'],'raw_uncompressed_sha256':p['raw_uncompressed_sha256'],'result_path':str(rrpath),'result_sha256':sha(rrpath),'DONE_path':str(dp),'DONE_sha256':sha(dp),'spec_path':str(specpath),'spec_sha256':sha(specpath),'configs':s['configs'],'archive':r['archive'],'numerical_correctness':p['full_application_numerical_values'],'scope':'NEW_DOWNSTREAM18_ONLY'})
idx={(v['program'],v['cell'],v['profile']):v for v in old+added};within=[];changes=[];relative=[]
for pg in ['ATAX','MVT','BICG']:
 for prof in ['P0','PQ','PS']:
  ch=idx.get((pg,'CH',prof));dh=idx.get((pg,'DH',prof))
  if ch and dh:
   ck(f'{pg}_{prof}_paired_kernels',[(x['ordinal'],x['kernel'],x['active_instructions'],x['cumulative_CTA']) for x in ch['kernels']]==[(x['ordinal'],x['kernel'],x['active_instructions'],x['cumulative_CTA']) for x in dh['kernels']])
   within.append({'program':pg,'profile':prof,'CH_over_DH':ch['cycles']/dh['cycles'],'CH_cycles':ch['cycles'],'DH_cycles':dh['cycles'],'cohorts':[ch['cohort'],dh['cohort']],'kernel_CH_over_DH':[{'ordinal':a['ordinal'],'kernel':a['kernel'],'CH_cycles':a['cycles'],'DH_cycles':b['cycles'],'ratio':a['cycles']/b['cycles']} for a,b in zip(ch['kernels'],dh['kernels'])]})
 for prof in ['PQ','PS']:
  for cell in ['CH','DH']:
   a=idx.get((pg,cell,'P0'));b=idx.get((pg,cell,prof));changes.append({'program':pg,'cell':cell,'profile':prof,'status':'ACCEPTED' if a and b else 'PENDING','speedup':a['cycles']/b['cycles'] if a and b else None})
  req=[(pg,'CH','P0'),(pg,'DH','P0'),(pg,'CH',prof),(pg,'DH',prof)];missing=[list(k) for k in req if k not in idx];row={'program':pg,'profile':prof,'status':'PENDING' if missing else 'ACCEPTED','K':None,'missing':missing}
  if not missing:
   ch0,dh0,chp,dhp=[idx[k]['cycles'] for k in req];row['K']=(dh0/dhp)/(ch0/chp)
  relative.append(row)
for name,h in prior_hashes.items():ck('prior_byte_preserved_'+name,sha(A/name)==h)
d={'schema':'DTC_E_LATEST_ACCEPTED_ADDENDUM_V1','observed_UTC':cutoff,'prior_cutoff_UTC':prior['observed_UTC'],'accepted_cells':len(idx),'pending_cells':18-len(idx),'new_accepted_cells':added,'within_profile_CH_over_DH':within,'matched_P0_speedups':changes,'relative_recovery_factors':relative,'source_inventory':sources,'status_snapshot':summary,'prior_files_sha256_164_original':prior_hashes,'prior_file_hash_scope':'164_ORIGINAL_COPY_ONLY; do not apply manifest-self hash to a separately created Windows copy','tests':checks,'active_raw_reads':0,'trace_reads':0,'new_model_starts':0,'controller_or_goal_or_lease_changes':0,'scope_caveats':['Whole declared frozen trace; no newly certified full-application numerical correctness.','No historical original-build P0 substitution.','No final-cycle prediction or waiting for additional models.','Original V1 files retain their own location-specific original hashes.']}
md=['# Latest accepted-cell addendum — Agent E','',f'One finite metadata snapshot: **{cutoff}**. V1 cutoff remains **{prior["observed_UTC"]}**. Latest strictly accepted count **{len(idx)}/18**; **{18-len(idx)} pending**. Prior V1 bytes are preserved.','', '## Newly closed and qualified','', '| Input | Cell | Profile | Cycles |','|---|---|---|---:|']
for a in added:md.append(f'| {a["program"]} | {a["cell"]} | {a["profile"]} | {a["cycles"]:,} |')
md+=['', 'Each added cell passed independent natural DONE/NATIVE_EXIT success matching, strict acceptance, input/config/source/binary/population qualification, archive verification and native restore receipt checks. No active raw file was read.','', '## Complete within-profile CH/DH pairs','', '| Input | Profile | CH cycles | DH cycles | CH/DH |','|---|---|---:|---:|---:|']
for x in within:md.append(f'| {x["program"]} | {x["profile"]} | {x["CH_cycles"]:,} | {x["DH_cycles"]:,} | {x["CH_over_DH"]:.9f} |')
md+=['', '**All relative recovery factors K_PQ/K_PS remain PENDING** while the required DH P0 baselines are missing. A CHPS/DHPS pair establishes a comparison within PS only; it does not show how much PS changed DTC relative to its own P0. No pending result is predicted or filled from the old original build.','', 'The additions retain input SHA, cohort, UUID, strict result/DONE hashes, raw paths/hashes, config hashes, archive/native-restore receipt and full accepted metrics in `LATEST_ACCEPTED_ADDENDUM.json`. These results remain confined to the new downstream18 contract and do not newly prove full-application numerical correctness.','',f'{len(checks)} assertions passed; prior files retain their original164 SHA256. A separately serialized Windows manifest must be verified against its own original exact hash. No new simulation, trace read, running controller/lease/Goal intervention, or historical-file rewrite occurred.','']
outputs={'LATEST_ACCEPTED_ADDENDUM.json':json.dumps(d,indent=2,ensure_ascii=False)+'\n','LATEST_ACCEPTED_ADDENDUM.md':'\n'.join(md),'LATEST_ACCEPTED_VALIDATION.json':json.dumps({'observed_UTC':cutoff,'passed':len(checks),'tests':checks},indent=2)+'\n'}
for n,text in outputs.items():
 ck('append_only_'+n,not (A/n).exists());(A/n).write_text(text,encoding='utf8')
files=[{'name':n,'sha256':sha(A/n),'bytes':(A/n).stat().st_size} for n in outputs]
man={'schema':'DTC_E_APPEND_ONLY_MANIFEST_SUPPLEMENT_V1','observed_UTC':cutoff,'prior_delivery_manifest_sha256':prior_hashes['DELIVERY_MANIFEST.json'],'files':files,'prior_files_unchanged':True}
assert not (A/'LATEST_MANIFEST_SUPPLEMENT.json').exists();(A/'LATEST_MANIFEST_SUPPLEMENT.json').write_text(json.dumps(man,indent=2)+'\n')
print(json.dumps({'accepted':len(idx),'pending':18-len(idx),'cutoff':cutoff,'new':[{'program':v['program'],'cell':v['cell'],'profile':v['profile'],'cycles':v['cycles']} for v in added],'within':within,'passed':len(checks),'files':files},indent=2))
