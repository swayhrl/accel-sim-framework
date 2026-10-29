"""Focused final delta QA. Synthetic shape fixtures are never scientific output."""
import copy,gzip,hashlib,json,pathlib,tempfile,time,sys,resource
sys.dont_write_bytecode=True
import analysis_extensions as x
import background_analysis as b
import readable_report as md
import ready_emitter as e
D=pathlib.Path(__file__).parent;checks=[]
def check(n,fn):fn();checks.append({'name':n,'status':'PASS'})
def reject(fn):
 try:fn()
 except (ValueError,KeyError,AssertionError,FileNotFoundError):return
 raise AssertionError('expected fail-closed HOLD')
cfg=e.read(D/'CONFIG.cpu_policy_actual_F3.json');p=x.policy(cfg,qualification_only=True);R=pathlib.Path(cfg['root']);q=e.read(cfg['registry_path'])['registered_future_requests'][cfg['request']];cert_paths=sorted((R/'analysis').glob('*.NEGATIVE_ARCHIVE_CLOSURE_CERTIFICATE.json'));actual=[]
def read_negative(cp,pol=p):
 closure=e.read(cp);c=closure['cohort'];return x.negative_terminal(c,e.read(R/'analysis'/(c+'.RESULT.json')),R,q,pol)
def actual_negatives():
 for cp in cert_paths:
  z=read_negative(cp);assert z['terminal'] is True and z['accepted'] is False and z['cycles'] is None;actual.append({'cohort':e.read(cp)['cohort'],'RESULT_sha256':z['RESULT_sha256'],'uuid':z['same_uuid'],'terminal':True,'accepted':False,'cycles':None})
 assert len(actual)>=2
check('actual_F3_same_UUID_negative_certificates_readonly_terminal_not_accepted',actual_negatives)
def wrapper():
 z=copy.deepcopy(p);z['installations'][0]['put_callback_chain']['wrapper']['sha256']='wrong';reject(lambda:read_negative(cert_paths[0],z))
check('wrong_IO_wrapper_chain_rejected',wrapper)
def target():
 z=copy.deepcopy(p);z['installations'][0]['put_callback_chain']['original_target']['qualname']='other';reject(lambda:read_negative(cert_paths[0],z))
check('wrong_original_put_target_rejected',target)
def unknown():
 z=copy.deepcopy(p);z['installations'][0]['collector']['sha256']='f'*64;reject(lambda:read_negative(cert_paths[0],z))
check('unknown_collector_installation_rejected',unknown)
def multi():
 z=copy.deepcopy(p);future=copy.deepcopy(z['installations'][0]);future['collector']['sha256']='f'*64;z['installations'].append(future);assert read_negative(cert_paths[0],z)['terminal']
 z['installations'].append(copy.deepcopy(z['installations'][0]));reject(lambda:read_negative(cert_paths[0],z))
check('exact_multi_installation_selection_retains_history_and_rejects_ambiguity',multi)
def historical_pin():
 z=copy.deepcopy(p);z['installations'][0]['exact_certificate_sha256'][e.read(cert_paths[0])['cohort']]='wrong';reject(lambda:read_negative(cert_paths[0],z))
check('historical_F3_certificate_exact_SHA_allowlist_enforced',historical_pin)
def absent():reject(lambda:read_negative(cert_paths[0],None));reject(lambda:x.policy(cfg))
check('missing_or_CPU_only_policy_never_production_authority',absent)
start=time.monotonic();config=e.read(D/'CONFIG.formal_with_historical.candidate.json');config['output_root']=tempfile.mkdtemp(prefix='CPU_ACTUAL_FORMAL_V3_',dir=D);config['ready_authorization_path']=str(D/'QA_NO_AUTH.json');config['negative_terminal_policy']=None;cp=D/'CONFIG.cpu_formal.json';e.atomic(cp,config);sys.addaudithook(b.audit);w=b.Worker(config,cp);w.tick();pointer=e.read(w.out/'LATEST.json');mp=pathlib.Path(pointer['manifest_path']);report=e.read(mp.parent/'REPORT.json');manifest=e.read(mp);markdown=(mp.parent/'RESULTS.md').read_bytes();payload=sum(pathlib.Path(z['path']).stat().st_size for z in manifest['publication_files']);assert payload<=1048576

def renderer():
 text=markdown.decode();body=text.split('<!-- FIXED35_TABLE_START -->\n',1)[1].split('<!-- FIXED35_TABLE_END -->',1)[0];rows=body.strip().splitlines()[2:];assert len(rows)==35
 source=report['derived35'];tab={z.split('|')[3].strip():[v.strip() for v in z.split('|')[4:-1]] for z in rows};assert len(tab)==35
 for digest in source['summary']['programs']:
  expected=[]
  for cell,profile in md.SLOTS:
   row=next(r for r in source['rows'] if r['key']['input_digest']==digest and r['key']['cell']==cell and r['key']['profile']==profile);value=tab[digest[:16]][len(expected)]
   if row['selected']:assert str(row['selected']['cycles']) in value
   else:assert value.startswith('MISSING ')
   if row['original']['raw_state']=='FAIL_L2MLP_ARCHIVED_NO_RETRY':assert 'O:NEG' in value
   expected.append(value)
 assert 'O:NEG_TYPED' in text and '37842f4191c6a0f293a01d22834c28794c3e23a477b1d657976d01bdb055c9e7' in text
 assert len(markdown)<40*1024 and 'Historical downstream18: own P0 = 1' in text and 'Matched inputs across both views' in text and md.render(report)==markdown
check('renderer_all35_all350_cycles_missing_negatives_roles_metrics_historical_consistency',renderer)

# Conservative shape only: all350 originals plus all12 fixed alternates valid,
# 19-digit new cycles and 64 additional independent source SHA pins per new
# measurement. Existing negative facts are copied only in this CPU fixture.
def maxshape():
 synthetic=copy.deepcopy(report);synthetic['qualification_only']=True;synthetic['scientific_output']=False;v=synthetic['derived35'];seed={}
 for row in v['rows']:
  if row['original'].get('valid'):seed.setdefault(row['key']['input_digest'],row['original'])
 additions=0
 for row in v['rows']:
  for field in ['original','alternate']:
   old=row.get(field)
   if old is None or old.get('valid'):continue
   cohort=old['cohort'];role=old['scientific_role'];z=copy.deepcopy(seed.get(row['key']['input_digest'],next(iter(seed.values()))));old_uuid=z.get('uuid','seed');h=hashlib.sha256(('max-shape|'+cohort).encode()).hexdigest();u=h[:8]+'-'+h[8:12]+'-'+h[12:16]+'-'+h[16:20]+'-'+h[20:32]
   z.update(cohort=cohort,scientific_role=role,valid=True,apparent_accepted=True,acceptance_uncertain=False,identity_verified=True,raw_state='SYNTHETIC_CPU_MAX_SHAPE_NOT_SCIENCE',cycles=10**18+int(h[:16],16)%(8*10**18),cell=row['key']['cell'],profile=row['key']['profile'],uuid=u,reasons=[])
   spec=x.read(R/'control/specs'/(cohort+'.json'))
   for spec_key in ['input_digest','input_binding_sha256','core_commit','framework_commit','binary_sha256','cell']:z[spec_key]=spec[spec_key]
   z['expected_ROI']=spec['expected'];z['profile']=spec['downstream_profile']
   z['RESULT_path']=str(R/'analysis'/(cohort+'.RESULT.json'));z['RESULT_sha256']=hashlib.sha256((cohort+'result').encode()).hexdigest()
   z['evidence']={k:val.replace(old_uuid,u) if isinstance(val,str) else val for k,val in z.get('evidence',{}).items()}
   for key in list(z.get('evidence',{})):
    if key.endswith('sha256'):z['evidence'][key]=hashlib.sha256((cohort+key).encode()).hexdigest()
   row[field]=z;additions+=1
   for i in range(64):v['source_pins'].append({'path':'/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/SYNTHETIC_CPU_MAX_SHAPE_NOT_SCIENCE/'+cohort+'/'+u+'/native_restored_small_critical_artifact_'+str(i)+'.json','sha256':hashlib.sha256((cohort+'|'+str(i)).encode()).hexdigest()})
  row['selected']=row['original'];row['reason']='SYNTHETIC_CPU_MAX_SHAPE_NOT_SCIENCE'
 points=[r['key'] for r in v['rows']];selections=[{'key':r['key'],'selected':r['selected']} for r in v['rows']];v['summary']=w.mod.summarize(points,selections,list(md.PROFILES),formal=True);synthetic['original350_summary']=copy.deepcopy(v['summary']);synthetic['coverage']['original_valid']=350;synthetic['coverage']['derived35_selected']=350
 summary={'qualification_only':True,'scientific_output':False,'UTC':v['UTC'],'coverage':synthetic['coverage'],'formal_metrics':True,'original350_summary':b.compact_summary(synthetic['original350_summary']),'named35_summary':b.compact_summary(v['summary']),'historical_fixed3':synthetic['historical_fixed3'],'CH35_status':'NOT_REGISTERED_HOLD_NO_GRANT','namespace_roles_unchanged':True}
 parts={'REPORT.json.gz':gzip.compress(b.rawjson(synthetic),mtime=0),'results.csv.gz':gzip.compress(b.render_table(v,synthetic['original350_summary']),mtime=0),'SUMMARY.json.gz':gzip.compress(b.rawjson(summary),mtime=0),'RESULTS.md':md.render(synthetic)};total=sum(map(len,parts.values()));e.atomic(D/'SYNTHETIC_MAX350_PAYLOAD_BOUNDS.json',{'qualification_only':True,'scientific_output':False,'all350_selected_plus12_fixed_alternates':True,'newly_materialized_measurements':additions,'extra_independent_source_pins_per_new_measurement':64,'cycle_width_digits':19,'member_bytes':{k:len(raw) for k,raw in parts.items()},'total_bytes':total,'limit_bytes':1048576,'within_bound':total<=1048576});assert total<=1048576,'MAX350_SHAPE_PUBLICATION_BOUND_EXCEEDED'
check('synthetic_CPU_all350_plus12_shape_publication_four_members_under_1MiB',maxshape)
qa={'schema':'DTC_BACKGROUND_ANALYSIS_V3_DELTA_CPU_QUALIFICATION_V1','status':'PASS','source_sha256':{n:e.sha(D/n) for n in ['background_analysis.py','analysis_extensions.py','readable_report.py','ready_emitter.py','qualify_v3.py']},'prior_V2_21_checks_reused_not_rerun':True,'checks':checks,'actual_negative_readonly':actual,'actual_formal_seconds':time.monotonic()-start,'actual_formal_payload_bytes':payload,'actual_Markdown_bytes':len(markdown),'actual_original_valid':report['coverage']['original_valid'],'actual_named_selected':report['coverage']['derived35_selected'],'synthetic_bounds':e.read(D/'SYNTHETIC_MAX350_PAYLOAD_BOUNDS.json'),'maxrss_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'production_started':False,'READY_written':False,'Git_operations':0,'models_started':0};e.atomic(D/'CPU_QUALIFICATION.json',qa);print(json.dumps(qa))
