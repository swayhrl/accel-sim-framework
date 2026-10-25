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
proof={'schema':'LATE4_DRAFT_ACTUAL_FOUR_SCOPE_RESOURCE_FUNCTION_CPU_V1','status':'PASS_DRAFT_SOURCE_ONLY_NOT_ACTIVATION_QUALIFICATION','source_path':str(path),'source_sha256':sha(path),'check_count':len(checks),'checks':checks,'fixture_scope':'Actual resources/_known_writes/output_cap/_point_spec functions; private temporary 4 scopes, authority/RSS/system memory mocked. Imports never call a model. No launch/registration/entry actions.','draft_parent_and_specs_not_frozen':True,'actual_models_started':0,'actual_authority_writes':0,'actual_entry_changes':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
out=R/'control/DRAFT_FOUR_SCOPE_RESOURCE_CPU_QUALIFICATION_V1.json'
with out.open('x') as s:json.dump(proof,s,sort_keys=True,indent=2);s.write('\n')
print(json.dumps({'status':proof['status'],'check_count':len(checks),'path':str(out),'sha256':sha(out)},indent=2))
