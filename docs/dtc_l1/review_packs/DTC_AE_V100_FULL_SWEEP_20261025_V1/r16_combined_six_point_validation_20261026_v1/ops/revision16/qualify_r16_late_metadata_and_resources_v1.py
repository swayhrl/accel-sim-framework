import pathlib,json,hashlib,importlib.util,tempfile,types,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');R=F/'validation_late_failure_v1'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def dump(p,d):P(p).parent.mkdir(parents=True,exist_ok=True);P(p).write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
path=R/'tools/late_native_v1.py';sp=importlib.util.spec_from_file_location('late4_cpu',path);n=importlib.util.module_from_spec(sp);sp.loader.exec_module(n)
checks=[]
def ok(name,condition):assert condition,name;checks.append(name)
with tempfile.TemporaryDirectory(prefix='FOUR_SCOPE_CPU_',dir=R/'analysis') as td:
 d=P(td);n.T=d/'orig';n.R1=d/'oldrepair';n.R2=d/'lava';n.R=d/'late';roots=[n.T,n.R1,n.R2,n.R];ids=[n.ORIGINAL,n.PRIOR_REPAIR,n.LAVA,n.REQ]
 for root in roots:dump(root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
 dump(n.R2/'control/EXECUTION_PLAN_V2.json',{'estimated_peak_model_RAM_bytes':96*n.G})
 specs={}
 for root,rid,cell,cap,hard in [(n.T,n.ORIGINAL,'o',256*n.M,16*n.G),(n.R1,n.PRIOR_REPAIR,'p',32*n.M,16*n.G),(n.R2,n.LAVA,'l',256*n.M,128*n.G),(n.R,n.REQ,'a',256*n.M,16*n.G),(n.R,n.REQ,'b',256*n.M,16*n.G)]:
  s={'request':rid,'cohort':cell,'limits':{'max_result_directory_bytes':cap,'max_process_tree_rss_bytes':hard}};specs[cell]=s;dump(root/'control'/((cell+'_SPEC.json') if root==n.T else ('specs/'+cell+'.json')),s)
 qs={rid:{'consumed':{},'reserved_write_bytes':100*n.G} for rid in ids};qs['unrelated']={'state':'ARMED','reserved_write_bytes':7*n.G}
 for rid,cell in [(n.ORIGINAL,'o'),(n.PRIOR_REPAIR,'p'),(n.LAVA,'l')]:qs[rid]['consumed'][cell]={'uuid':'u'+cell}
 n.authority=lambda:({'registered_future_requests':qs},{})
 n.plan=lambda:{'estimated_peak_model_RAM_bytes':4*n.G,'max_process_tree_rss_bytes':16*n.G}
 rss={'uo':2*n.G,'up':6*n.G,'ul':30*n.G};n._rss=lambda row,root:rss.get(row['uuid'],0)
 fake=d/'system';(fake/'cg').mkdir(parents=True);mem=fake/'meminfo';(fake/'cg/memory.current').write_text('0');(fake/'cg/memory.stat').write_text('file 0\ninactive_file 0\n')
 def memory(host=1024,cg=1024):mem.write_text('MemAvailable: '+str(host*n.G//1024)+' kB\n');(fake/'cg/memory.max').write_text(str(cg*n.G))
 memory();n.P=lambda p:P(mem if str(p)=='/proc/meminfo' else fake/'cg' if str(p)=='/sys/fs/cgroup' else p)
 n.os=types.SimpleNamespace(statvfs=lambda p:types.SimpleNamespace(f_bavail=1024*n.G,f_frsize=1,f_favail=1000000))
 a=n.resources(specs['a'],True);by={x['cohort']:x for x in a['RAM_reservation_entries']}
 ok('NEW4_candidate4G_not96G',by['a']['envelope_bytes']==4*n.G)
 ok('ORIGINAL2G_to4G_floor',by['o']['additional_reserved_bytes']==2*n.G)
 ok('R1_actual6G_no_extra',by['p']['envelope_bytes']==6*n.G and by['p']['additional_reserved_bytes']==0)
 ok('LAVAMEM_peer30G_still96G_estimate',by['l']['envelope_bytes']==96*n.G and by['l']['additional_reserved_bytes']==66*n.G)
 ok('four_scope_projected_exact72G',a['reserved_additional_live_and_candidate_RAM_bytes']==72*n.G)
 ok('all_owned_ceiling_dedup_only7G_unrelated',a['other_outstanding_write_reservations_bytes']==7*n.G and len(a['peer_reservations'])==1)
 expected=5*n.G+4*n.G+512*n.M+64*n.M+512*n.M+512*n.M+7*n.G
 ok('four_owned_knownwrites_exact',a['required_free_bytes']==expected)
 rss['ul']=110*n.G;b=n.resources(specs['a'],True);by={x['cohort']:x for x in b['RAM_reservation_entries']}
 ok('LAVA_actual110G_above96G_preserved',by['l']['envelope_bytes']==110*n.G and by['l']['additional_reserved_bytes']==0)
 dump(n.R/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{'b':{'result_cap_bytes':256*n.M}}});c=n.resources(specs['a'],True);by={x['cohort']:x for x in c['RAM_reservation_entries']}
 ok('NEW4_claim_plus_fresh_each4G',by['a']['additional_reserved_bytes']==by['b']['additional_reserved_bytes']==4*n.G)
 ok('fresh_candidate_not_double_counted_after_claim',len([x for x in c['RAM_reservation_entries'] if x['cohort']=='b'])==1)
 memory(1024,57);ok('projected10G_plus48G_floor_rejects57G',not n.resources(specs['a'],True)['physical_RAM_pass'])
 ok('runtime57G_actual_still_passes',n.resources(specs['a'],False)['physical_RAM_pass'])
 memory(63,1024);ok('runtime_host64G_floor_preserved',not n.resources(specs['a'],False)['physical_RAM_pass'])
 memory(1024,47);ok('runtime_cgroup48G_floor_preserved',not n.resources(specs['a'],False)['physical_RAM_pass'])
 memory();qs[n.REQ]['reserved_write_bytes']=n.G;ok('own_write_ceiling_fail_closed',not n.resources(specs['a'],True)['physical_disk_pass'])
 dump(n.R/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{'b':{'result_cap_bytes':1}}})
 try:n.resources(specs['a'],True)
 except AssertionError:ok('claim_cap_mismatch_rejected',True)
 else:raise AssertionError('mismatch accepted')

 # Prove serialized write gating independently of abundant physical RAM/disk.
 memory();qs[n.REQ]['reserved_write_bytes']=100*n.G;qs[n.LAVA]['reserved_write_bytes']=n.G+512*n.M
 dump(n.R/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
 second=dict(specs['l'],cohort='l2');dump(n.R2/'control/specs/l2.json',second)
 outlava=n.R2/'DTC/run/results/ul';outlava.mkdir(parents=True)
 with (outlava/'size_fixture.bin').open('wb') as stream:stream.truncate(256*n.M)
 sample=n.resources(second,True)
 ok('LAVA1_5G_ceiling_rejects_second_live_even_with_highRAM_disk',sample['physical_RAM_pass'] and not sample['physical_disk_pass'])
 qs[n.LAVA]['consumed']['l']['execution_receipt']={'CPU_FIXTURE_DONE':True}
 sample=n.resources(second,True)
 ok('LAVA1_5G_ceiling_rejects_second_DONE_beforearchive',sample['physical_RAM_pass'] and not sample['physical_disk_pass'])
 dump(n.R2/'control/l_ARCHIVE_RECEIPT.json',{'CPU_FIXTURE_ARCHIVED':True})
 sample=n.resources(second,True)
 ok('LAVA1_5G_ceiling_admits_second_only_afterarchive',sample['physical_RAM_pass'] and sample['physical_disk_pass'] and sample['known_remaining_writes_by_request'][n.LAVA]==n.G+512*n.M)


canonical=P('/root/data/dtc_failure_repair_20261025_v1/validation_late_failure_v1');read=lambda p:json.loads(P(p).read_bytes());q=read(canonical/'control/REGISTRY_REQUEST_CANDIDATE_V1.json');plan=read(canonical/'control/EXECUTION_PLAN_V1.json');runtime={}
assert q['budget']==q['remaining']==4 and q['consumed']=={} and q['reserved_write_bytes']==3*1024**3
for item in plan['source_pins']:assert sha(item['path'])==item['sha256']
ok('all_final_LATE4_plan_sourcepins_match',True)
for cell,digest in q['admitted_specs'].items():
 sp=canonical/'control/specs'/(cell+'.json');s=read(sp);old=read(s['prior_original_point']['prior_frozen_spec_path'])
 ok(cell+'_exact_alias_and_admitted_SHA',sha(sp)==digest==sha(canonical/'control'/(cell+'_SPEC.json')))
 for key in ['expected_options','expected','configs','input_digest','input_binding_sha256','original_environment']:ok(cell+'_unchanged_'+key,s[key]==old[key])
 ok(cell+'_all270_and_traceargv_unchanged',len(s['expected_options'])==270 and s['native_simulator_argv'][1:]==old['native_simulator_argv'][1:])
 ok(cell+'_fixed_Core_FW_hard16',s['core_commit']=='9eedb3131937748f0492fa83aad37d3691118d70' and s['framework_commit']=='02775fd795cde5aae1480d81cee6eb481d0a08f4' and s['limits']['max_process_tree_rss_bytes']==16*1024**3)
 for item in s['runtime_files']:runtime[item['actual_realpath']]=item['sha256']
 for key in ['INTENT','DONE']:ok(cell+'_prior_'+key+'_preserved',sha(s['prior_original_point'][key+'_path'])==s['prior_original_point'][key+'_sha256'])
for p,h in runtime.items():assert sha(p)==h
ok('all_runtime_current_SHA_match',True)

proof={'schema':'LATE4_DRAFT_ACTUAL_FOUR_SCOPE_RESOURCE_FUNCTION_CPU_V1','status':'PASS_FINAL_FROZEN_SOURCE_ACTUAL_RESOURCE_CPU','source_path':str(path),'source_sha256':sha(path),'metadata_source_pins':[{'path':str(p),'sha256':sha(p)} for p in sorted((canonical/'control').glob('*.json')) if p.name not in ['POOL_DISPATCH_RESERVATIONS.json','DRAFT_FOUR_SCOPE_RESOURCE_CPU_QUALIFICATION_V1.json']],'check_count':len(checks),'checks':checks,'fixture_scope':'Actual resources/_known_writes/output_cap/_point_spec functions; private temporary 4 scopes, authority/RSS/system memory mocked. Imports never call a model. No launch/registration/entry actions.','draft_parent_and_specs_not_frozen':False,'actual_models_started':0,'actual_authority_writes':0,'actual_entry_changes':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
out=canonical/'control/FINAL_FOUR_SCOPE_RESOURCE_CPU_QUALIFICATION_R16_V1.json'
with out.open('x') as s:json.dump(proof,s,sort_keys=True,indent=2);s.write('\n')
print(json.dumps({'status':proof['status'],'check_count':len(checks),'path':str(out),'sha256':sha(out)},indent=2))
