"""V2 optional, explicitly source-pinned read-only terminal/provider adapters."""
import hashlib,json,pathlib,importlib.util,os
P=pathlib.Path
H_SHA='37dc9021ab6cc016acc13017c65b78cacc2a72af413f4497e41356b63eb6904e'
F_SHA='40395989afe28dbb874f6f790e676c511e1e85f325970ca1a807fea111dac3be'
F_ID='DTC_MAIN_NEGATIVE_ARCHIVE_AUTOCLOSE_OWNER_V1'
FAIL='FAIL_L2MLP_ARCHIVED_NO_RETRY'
def require(v,m):
 if not v:raise ValueError('EXTENSION_HOLD:'+m)
def encode(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def pinned(ref):
 p=P(ref['path']);raw=p.read_bytes();require(hashlib.sha256(raw).hexdigest()==ref['sha256'],'pinned artifact drift '+str(p));return json.loads(raw)
def policy(config,qualification_only=False):
 ref=config.get('negative_terminal_policy')
 if ref is None:return None
 p=pinned(ref);require(p['schema']=='DTC_NEGATIVE_TERMINAL_POLICY_V2' and p['approved'] is True,'Root policy approval')
 require(not p.get('qualification_only',False) or qualification_only,'CPU policy cannot authorize production')
 require(p['helper']['sha256']==H_SHA and sha(p['helper']['path'])==H_SHA,'H helper source')
 require(P(p['root'])==P(config['root']) and p['request']==config['request'],'fixed Root request')
 seen=set();require(p['installations'],'explicit installed collector records required')
 for inst in p['installations']:
  require(set(inst['allowed_cohorts'])<=set(p['scope']) and set(inst['exact_certificate_sha256'])<=set(inst['allowed_cohorts']),'fixed installation role scope')
  require(type(inst['future_certificates_allowed']) is bool,'explicit future certificate mode')
  if not inst['future_certificates_allowed']:require(set(inst['allowed_cohorts'])==set(inst['exact_certificate_sha256']),'historical installation exact certificate allowlist')
  source=inst['collector'];require(sha(source['path'])==source['sha256'],'Root exact collector source')
  cfg=pinned(inst['configuration']);approval=pinned(inst['approval']);run=pinned(inst['collector_run']);ack=pinned(inst['main_ack']);sid=inst['collector_schema']
  identity=(source['sha256'],inst['configuration']['sha256'],inst['approval']['sha256'],inst['collector_run']['sha256']);require(identity not in seen,'duplicate installation identity');seen.add(identity)
  require(cfg['schema']==run['schema']==ack['schema']==sid and cfg['source_sha256']==run['source_sha256']==ack['source_sha256']==approval['source_sha256']==source['sha256'],'collector generation source/schema')
  require(cfg['qualification_only'] is False and approval['qualification_only'] is False and approval['approved'] is True and approval['archive_only'] is True,'actual Root installation approval')
  require(cfg['root']==p['root'] and cfg['request']==p['request'] and cfg['helper_sha256']==run['helper_sha256']==H_SHA,'installed request/helper')
  require(run['configuration_sha256']==ack['configuration_sha256']==approval['configuration_sha256']==inst['configuration']['sha256'],'installed config SHA')
  require(run['approval_path']==inst['approval']['path'] and run['approval_sha256']==ack['approval_sha256']==inst['approval']['sha256'],'installed approval SHA')
  require(ack['status']=='ARCHIVE_ONLY_DAEMON_STARTED' and ack['all_original_references_preserved'] is True and ack['models_started']==ack['new_grants']==ack['model_retries']==0,'actual archive-only Main ACK')
  require(run['models_started']==run['new_grants']==0 and run['owner']==cfg['owner']==approval['owner'],'same actual Main process birth')
  require(str(P(inst['collector_run']['path']).parent)==cfg['run_directory']==ack['run_directory'],'actual collector run directory')
  for path,h in cfg['source_pins'].items():require(sha(path)==h,'installed config source pin '+path)
  chain=inst['put_callback_chain'];wrapper=chain['wrapper'];target=chain['original_target']
  require(wrapper['sha256']=='59d7ea79e05fd26bb23bc46c73e35aff50ce0ea7831ffa9c162cec94c3ed8973' and wrapper['qualname']=='install_private_module.<locals>.put' and wrapper['freevars']==['original_put'],'exact qualified IO wrapper')
  require(target['sha256']=='6cc6cc30a71740df951327414d094953effb73a406e7036358ad0b702ebb0403' and target['qualname']=='put' and target['freevars']==[],'exact original put target')
  require(sha(wrapper['file'])==wrapper['sha256'] and sha(target['file'])==target['sha256'],'actual callback source files')
 return p

def negative_terminal(c,result,root,q,p):
 """Reuse the Root-qualified full callback/H/F closure; rejoin small critical bytes.
 No execution, archive copying or large raw replay occurs in this reader.
 """
 require(p is not None,'Root negative terminal policy absent')
 root=P(root);require(root==P(p['root']),'fixed policy root');rule=p['scope'][c];spec_path=root/'control/specs'/(c+'.json');require(sha(spec_path)==rule['spec_sha256'],'fixed current spec source identity');require(c in q['admitted_specs'],'outside current registered request')
 require(result['state']==FAIL and result['cycles'] is None and result['proof']['performance_accepted'] is False and result['proof'].get('accepted_cycles') is None,'negative must never be performance accepted')
 require(result['cohort']==c and result['validated_union_authorized'] is False and result['model_retries']==0,'cohort/union/retry')
 require(result['scientific_role']==rule['scientific_role'] and result['primary_statistics_excluded'] is rule['primary_statistics_excluded'],'fixed source role')
 ip=root/'control/qualification_ledger'/(c+'.INTENT.json');i=read(ip);d=read(ip.with_name(c+'.DONE.json'));out=P(i['output']);qr=q['consumed'][c]
 require(out==root/'DTC/run/results'/qr['uuid'],'exact native output UUID namespace')
 require(d==read(out/'NATIVE_EXIT.json')==qr['execution_receipt'],'DONE EXIT authority equality')
 require(i['uuid']==d['uuid']==qr['uuid']==result['uuid'] and d['cohort']==c and sha(ip)==qr['intent_sha256'],'exact UUID INTENT')
 require(bool(d.get('stop_reason') or d.get('launcher_wait_returncode')) and d.get('automatic_retry') is False and d.get('source_disposition')=='SOURCE_KEEP','failed immutable execution SOURCE_KEEP')
 require(result['proof']['raw_sha256']==d['raw_sha256'] and result['proof']['raw_uncompressed_sha256']==d['raw_uncompressed_sha256'],'negative raw receipt')
 rp=root/'analysis'/(c+'.RESULT.json');result_sha=sha(rp)
 cert_path=root/'analysis'/(c+'.NEGATIVE_ARCHIVE_CLOSURE_CERTIFICATE.json');closure=read(cert_path)
 require(closure['schema']=='DTC_MAIN_NEGATIVE_ARCHIVE_CLOSURE_CERTIFICATE_V2' and closure['cohort']==c and closure['uuid']==d['uuid'] and closure['result_sha256']==result_sha,'installed F same-UUID closure certificate required')
 matches=[inst for inst in p['installations'] if closure['collector_source_sha256']==inst['collector']['sha256'] and closure['configuration_sha256']==inst['configuration']['sha256'] and closure['approval_sha256']==inst['approval']['sha256'] and closure['collector_run_path']==inst['collector_run']['path'] and closure['collector_run_sha256']==inst['collector_run']['sha256']]
 require(len(matches)==1,'no exact Root-authorized collector installation');inst=matches[0]
 require(c in inst['allowed_cohorts'],'cohort outside exact installation scope')
 if c in inst['exact_certificate_sha256']:require(sha(cert_path)==inst['exact_certificate_sha256'][c],'historical certificate bytes immutable')
 else:require(inst['future_certificates_allowed'] is True,'new certificate not authorized for historical installation')
 require(closure['helper_sha256']==H_SHA and closure['source_disposition']=='SOURCE_KEEP' and closure['performance_accepted'] is False and closure['cycles'] is None,'F sourcebound closure negative identity')
 require(closure['request']==p['request'] and closure['scientific_role']==rule['scientific_role'] and closure['primary_statistics_excluded'] is rule['primary_statistics_excluded'] and closure['validated_union_authorized'] is False,'closure request and immutable source role')
 require(closure['original_archive_source_sha256']=='6cc6cc30a71740df951327414d094953effb73a406e7036358ad0b702ebb0403' and closure['outbox_source_sha256']=='d4b58b362a39c9d198a40e5c252f6eb07ba780e4707ffd79f6724569e349c4a5','original full archive callback/outbox source pins')
 require(closure['put_callback_chain']==inst['put_callback_chain'],'exact actual put callback chain')
 wrapper=inst['put_callback_chain']['wrapper'];target=inst['put_callback_chain']['original_target']
 require(closure['original_put_source_path']==wrapper['file'] and closure['original_put_source_sha256']==wrapper['sha256'] and closure['original_put_target_source_path']==target['file'] and closure['original_put_target_source_sha256']==target['sha256'],'honest IO wrapper and original put target identity')
 require(closure['automatic_retry'] is False and closure['model_retries']==0,'no retry in closure')
 require(type(closure['main_thread_ident']) is int and closure['main_thread_ident']>0 and type(closure['archive_thread_ident']) is int and closure['archive_thread_ident']>0,'explicit Main/archive thread provenance')
 require(closure['qualification_only'] is False,'CPU fixture cannot authorize production terminal completion')
 require(closure['collector_run_path']==inst['collector_run']['path'] and closure['collector_run_sha256']==inst['collector_run']['sha256'],'actual collector run certificate source')
 require(closure['intent_sha256']==sha(ip) and closure['done_sha256']==sha(ip.with_name(c+'.DONE.json')) and closure['exit_sha256']==sha(out/'NATIVE_EXIT.json') and closure['execution_receipt_sha256']==hashlib.sha256(encode(d)).hexdigest(),'certificate exact execution small source hashes')
 run=pinned(inst['collector_run']);require(closure['configuration_sha256']==run['configuration_sha256'] and closure['approval_sha256']==run['approval_sha256'],'Root installed config/approval certificate join')
 require(sha(closure['configuration_path'])==closure['configuration_sha256'] and sha(closure['approval_path'])==closure['approval_sha256'],'actual installed config/Root approval source pins')
 require(closure['main_pid']==run['owner']['pid'] and closure['main_start_ticks']==run['owner']['start_ticks'],'same actual Main process birth')
 archive=result['archive'];receipt=archive['receipt'];bundle=P(receipt['target_mount_path']);restore=P(receipt['native_restore'])
 require(receipt==read(root/'control'/(c+'_ARCHIVE_RECEIPT.json'))==read(bundle/'RECEIPT.json'),'archive receipts equality')
 require(receipt['cohort']==c and receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET' and receipt['source_disposition']=='SOURCE_KEEP','archive status')
 require(receipt['scientific_acceptance_granted_by_archive'] is False,'archive cannot grant acceptance')
 require(bundle.resolve().is_relative_to(P(p['archive_results_root']).resolve()) and receipt['true164_root'].startswith('/home/shared/'),'true164 namespace')
 require(restore.resolve().is_relative_to(root/'DTC/run/recovery') and restore.stat().st_dev==root.stat().st_dev==p['native_device'],'native namespace/device')
 manifest=read(bundle/'SOURCE_MANIFEST.json');require(hashlib.sha256(encode(manifest)).hexdigest()==receipt['manifest_sha256'],'canonical full manifest SHA')
 require(manifest['cohort']==c and manifest['source_root']==str(out) and manifest['source_disposition']=='SOURCE_KEEP','full source manifest identity')
 entries={x['path']:x for x in manifest['entries']};restored=read(bundle/'RESTORE_VERIFIED_NATIVE_TARGET.json');rows={x['path']:x for x in restored['rows']}
 require(len(entries)==len(manifest['entries'])==len(rows)==len(restored['rows'])==archive['independently_verified_entries'],'complete archive/native population')
 for name,x in entries.items():
  r=rows[name];require(x['type']==r['type'],'native entry type')
  if x['type']=='file':require(x['sha256']==r['sha256'],'complete native verification SHA')
  elif x['type']=='symlink':require(x.get('target')==r.get('target'),'native link target')
 require(closure['manifest_sha256']==receipt['manifest_sha256'] and closure['archive_sha256']==receipt['archive_sha256'] and closure['result_archive_sha256']==hashlib.sha256(encode(archive)).hexdigest() and closure['native_restore']==str(restore) and closure['native_device']==p['native_device'] and closure['independently_verified_entries']==archive['independently_verified_entries'],'F complete archive/native certificate binding')
 index=read(bundle/'ARCHIVE_INDEX.json');require(index['archive_sha256']==receipt['archive_sha256'] and index['archive_bytes']==receipt['archive_bytes'] and sum(x['size'] for x in index['chunks'])==receipt['archive_bytes'],'complete archive index receipt')
 cert=archive['additional_strace_bpf_negative_archive_verification'];require(cert['schema']=='BROAD_SHARED_NEGATIVE_ARCHIVE_CLOSURE_V1' and cert['status']=='NEGATIVE_EVIDENCE_ARCHIVED_AND_NATIVE_RESTORED' and cert['cohort']==c and cert['performance_accepted'] is False,'qualified H full callback closure certificate')
 require(closure['H_required_files']==cert['required_files'] and closure['archive_target_mount_path']==str(bundle) and closure['archive_receipt_sha256']==sha(root/'control'/(c+'_ARCHIVE_RECEIPT.json')),'F H certificate and exact receipt source')
 require(cert['manifest_sha256']==receipt['manifest_sha256'] and cert['native_restore']==str(restore),'H certificate receipt binding')
 required={x['path']:x for x in cert['required_files']};names={'STRACE_BPF_OBSERVATION_SNAPSHOT.json','STRACE_BPF_ACTIVATION.json','STRACE_BPF_FORK_PLAN.json','NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json','NATIVE_EXIT.json','raw.log.gz','CPU_SHARED_TIMESLICE_SNAPSHOT.json','SHARED_JSON_IO_SNAPSHOT.json'}
 require(set(required)==names,'complete H negative critical certificate')
 pins={str(spec_path):rule['spec_sha256'],str(ip):sha(ip),str(ip.with_name(c+'.DONE.json')):sha(ip.with_name(c+'.DONE.json')),str(rp):result_sha,str(cert_path):sha(cert_path)}
 for name,x in required.items():
  require(x['sha256']==entries[name]['sha256']==rows[name]['sha256'] and x['bytes']==entries[name]['size'],'H certificate all critical manifest hashes')
  if name=='raw.log.gz':require(x['sha256']==d['raw_sha256'],'archived original raw receipt');continue
  require(not(out/name).is_symlink() and not(restore/name).is_symlink() and sha(out/name)==sha(restore/name)==x['sha256'],'small critical source/native content SHA')
  pins[str(out/name)]=x['sha256'];pins[str(restore/name)]=x['sha256']
 for name in ['SOURCE_MANIFEST.json','RECEIPT.json','ARCHIVE_INDEX.json','RESTORE_VERIFIED_NATIVE_TARGET.json']:pins[str(bundle/name)]=sha(bundle/name)
 if rule['primary_statistics_excluded']:require(read(root/'analysis/incident_recovery_results'/(c+'.RESULT.json'))==result,'IR negative mirror exact')
 return {'terminal':True,'accepted':False,'cycles':None,'role':rule['scientific_role'],'RESULT_sha256':result_sha,'same_uuid':d['uuid'],'evidence_mode':'ROOT_INSTALLED_FULL_ARCHIVE_CALLBACK_AND_PINNED_H_F_CERTIFICATE_REUSE_WITH_COMPLETE_MANIFEST_NATIVE_HASH_JOIN_AND_SMALL_CRITICAL_REHASH','source_pins':pins}

def historical(config,previous=None):
 ref=config.get('historical_provider')
 if ref is None:return {'configured':False,'status':'NOT_CONFIGURED_NOT_IN_AUTHORIZED_SCOPE','completion':{'scope_object_count':0,'all_fixed_objects_terminal':None},'signature':None}
 require(sha(ref['source_path'])==ref['source_sha256'] and sha(ref['scope_path'])==ref['scope_sha256'],'Root-pinned historical source/scope')
 s=importlib.util.spec_from_file_location('qualified_historical_provider',ref['source_path']);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 v=m.collect(previous=previous);require(v['schema']=='HISTORICAL_LONGTAIL_PROVIDER_V2' and v['scope_sha256']==ref['scope_sha256'],'provider schema/scope identity')
 expected={(x['cohort'],x['uuid']) for x in ref['fixed_objects']};actual={(x['cohort'],x['uuid']) for x in v['objects']}
 require(len(v['objects'])==len(expected)==3 and actual==expected,'only three fixed historical UUIDs')
 for x in v['objects']:
  require(type(x['terminal']) is bool and type(x['accepted']) is bool,'explicit historical state flags')
  if x['terminal']:require(x['status'] in ('STRICT_ACCEPTED','EXPLICIT_UNACCEPTED'),'unknown historical terminal status')
  if x['accepted']:require(x['status']=='STRICT_ACCEPTED' and x['terminal'] and type(x['cycles']) is int and x['cycles']>0,'historical own strict cycles')
  else:require(x['cycles'] is None,'unaccepted historical cycles missing, never zero')
 c=v['completion'];require(c['scope_object_count']==3 and c['terminal_object_count']==sum(x['terminal'] for x in v['objects']) and type(c['all_fixed_objects_terminal']) is bool and c['all_fixed_objects_terminal']==all(x['terminal'] for x in v['objects']),'historical separate completion')
 require(isinstance(v['signature'],str) and len(v['signature'])==64,'historical stable state signature')
 return dict(v,configured=True,separate_from_DTC_population=True)
