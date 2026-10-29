from pathlib import Path
import json,hashlib,datetime
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
R=Path('/root/data/dtc_l2_mlp_exploration_20261027_v1')
O=A/'agents/E/cpu_shared_main_review_v2'
D=R/'control/operational_amendments/cpu_shared_timeslice_v1/actual_install_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 b=(json.dumps(v,indent=2,sort_keys=True)+'\n').encode()
 with(O/n).open('xb')as f:f.write(b)
 return hashlib.sha256(b).hexdigest()
cp=D/'CONFIGURATION.json';assert sha(cp)=='52379add4a38f4831ec5485ed6d787410c512b11375a8f3f38b7b9e6d5e7bcc4'
cfg=read(cp);source=Path(cfg['installer_path'])
assert sha(source)==cfg['installer_sha256']=='0baca56f31c65c893021f19214c77802d539c637115fa5594219005f03f632de'
assert cfg['root']==str(R)and cfg['directory']==str(D)and cfg['schema']=='MAIN_CPU_SHARED_EXACT1_INSTALL_CONFIG_V1'
assert cfg['owner']=={'pid':1498278,'start_ticks':977758783}and cfg['new_grants']==0
assert cfg['approved_scope']=='ACTUAL_SINGLE_ENGINEERING_QUALIFICATION_ONLY_NO_PRIMARY_ROLLOUT'
assert set(cfg['expected_frame_object_ids'])=={'pool','claims','running','post','registry'}and all(type(v)is int and v>0 for v in cfg['expected_frame_object_ids'].values())
pins=[]
for p,h in cfg['source_pins'].items():assert sha(p)==h,p;pins.append(dict(path=p,sha256=h))
assert sha(R/'control/MATRIX_CURRENT.json')==cfg['matrix_sha256']and sha(R/'control/SCOPE.json')==cfg['scope_sha256']
assert sha(cfg['old_memory_active_path'])==cfg['old_memory_active_sha256']=='b7cdb2ac044ea668960e2e3ba8c5a0e6eb20e177db673e9b6fa3411fdce08a8f'
rp=Path(cfg['resource_configuration_path']);op=Path(cfg['observation_configuration_path'])
assert sha(rp)=='83e2bf723a554abe2f750dfe5b8c9898e4fef79ace60fcd860ffb147c4c996ae'and sha(op)=='64517f39b82ecf91be76ccbe6c44a40c63049a91412b24f8420a05019db74e01'
r,o=read(rp),read(op);C='E2-DTCL2MLP-731af5428c4b8155-DH-P0-OBSCTRL-V1'
assert r['allowed_cohorts']==[C]and r['max_shared_running']==1 and o['modes']=={C:'DEFAULT_CONTROL'}and o['future_primary_policy']=='NONE'
assert o['resource_configuration_path']==str(rp)and o['resource_configuration_sha256']==sha(rp)
assert cfg['modules']['library']==r['source_paths']['library']and cfg['modules']['producer']==o['source_paths']['producer']and cfg['modules']['consumer']==o['source_paths']['consumer']
for component in [r,o]:
 for role,p in component['source_paths'].items():assert sha(p)==component['qualified_sources'][role]
 for p,h in component['expected_pins'].items():assert sha(p)==h
 for key in ['QA','readback']:assert sha(component[key+'_path'])==component[key+'_sha256']
 assert component['qualification_only']is False
binding=D/'MAIN_SOURCE_BINDING.json';assert sha(binding)=='b3b31aab0b97535bfe6131dc1cc31b06271994929803045c6df0c1116d4b793f'
b=read(binding);assert b['installer_path']==str(source)and b['installer_sha256']==sha(source)and b['configuration_path']==str(cp)and b['configuration_sha256']==sha(cp)
prep=A/'coordinator/CPU_SHARED_MAIN_PREPARED_INSTALL_V1/PREPARATION.json';assert sha(prep)=='95d66421b686d7a564db3ad10c9a0e7338ee5df114a8215800429a60b8eb09a5'
p=read(prep);assert p['installer_sha256']==sha(source)and p['configuration_sha256']==sha(cp)and p['new_grants']==p['models_started']==p['registry_mutations']==p['owner_callbacks_queued']==0
assert sha(D/'OWNER_APPLY.py')==p['adapter_sha256']=='70f7f1426acd98469cb5fba60a21ad1a8094523719a160a25d3a246e3455e13f'
assert sha(D/'pending_payload_builder.py')==p['outer_builder_sha256']=='ea5a1c26be337e2bda200f2ecc9747893754c95c93cff89c6d01912b4c07c1d5'
for src,name in [(cp,'CONFIGURATION.source.json'),(binding,'MAIN_SOURCE_BINDING.source.json'),(D/'OWNER_APPLY.py','OWNER_APPLY.source.py')]:
 with(O/name).open('xb')as f:f.write(src.read_bytes())
review={
 'status':'APPROVED_FOR_EXPLICIT_SAME_OWNER_EXACT_ONE_CANARY_INSTALL',
 'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'owner_source_sha256':sha(source),'owner_config_sha256':sha(cp),'resource_configuration_sha256':sha(rp),'observation_configuration_sha256':sha(op),
 'actual_models_qualified':False,'actual_archive_transport_qualified':False,'primary_rollout_eligible':False,
 'blocking_findings':[],
 'approved_action':'One actual-owner contained callback using the exact reviewed source/config to install closed, then explicitly arm the existing exact1 engineering identity. No callback directly launches a model or adds a grant.',
 'exact_scope':{'cohort':C,'mode':'DEFAULT_CONTROL','reference_cycles':8551,'max_shared_running':1,'new_grants':0,'new_scientific_identity':False,'primary_statistics_excluded':True,'validated_union_authorized':False},
 'specific_checks':[
  'All concrete installer source pins match; modules point to the same qualified native resource/observation roles. Both complete component configs are the previously reviewed83e2/6451 and exactly linked.',
  'Concrete config names the actual Main PID/start and all five preserved frame-object IDs. This review validates their populated shape, not a live-process attachment; the installer freshly compares them against the actual scheduler frame before mutation.',
  'Real primary MATRIX/SCOPE and old CPU2 ACTIVE match the reviewed preimages. Resource and observation scope are exactly one existing registered engineering identity and no primary rollout.',
  'Hash-bound OWNER_APPLY points to the reviewed0baca source and52379 configuration. Native MAIN_SOURCE_BINDING matches exact reviewed values and SHA; the outer payload wraps source load/exec and contains BaseException.',
  'Previous source review confirms prearm-before-consumer, explicit B closed install, pure locked-q operational record CAS, E-before-B routing, precise spent/unused/unknown failure containment, old3 engineering readiness mask and no blind rollback.',
  'The prepared-install receipt is source preparation only with zero callbacks/grants/models/registry mutations. No CPU mock physics, cadence or archive result is promoted as actual performance evidence.'
 ],
 'required_after_explicit_install':[
  'Observe actual contained callback ACK/ERROR and current identity; preserve any concurrently born UUID and every durable operational record without refund/retry.',
  'Require the first actual native point to naturally complete pristine full physics/progress/resource-cadence plus actual Shared/IO/new observation/ref8551/count strict and true164/native archive restoration.',
  'Keep the explicitly documented other3-old-engineer admission mask while Shared is outer; restore only through the guarded B then E sequence and explicit Main restoration of saved worker/chooser masking.',
  'Four-point/broad rollout still requires a versioned mixed-generation real-four gate; this one trial never self-qualifies four, primary/IR broad scope or a recovery statistical union.'
 ],
 'source_only_review_reference':{'path':str(A/'agents/E/cpu_shared_main_review_v1/REVIEW.json'),'sha256':'57d8437ffab027fb8984b847e87962880160e864380c9cb900b9082a28fffc88'},
 'binding_sha256':sha(binding),'preparation_sha256':sha(prep),'source_pin_count':len(pins),'source_pins':pins,
 'actions':{'production_changes':0,'callbacks_queued':0,'new_grants':0,'models_started':0,'signals':0,'old_tests_rerun':0,'Git_actions':0}
}
h=put('REVIEW.json',review)
mh=put('MANIFEST.json',{'schema':'CPU_SHARED_EXACT1_FINAL_MAIN_CONFIG_REVIEW_MANIFEST_V1','files':[{'path':p.name,'sha256':sha(p)}for p in sorted(O.iterdir())if p.is_file()and p.name!='MANIFEST.json']})
print(json.dumps({'REVIEW':str(O/'REVIEW.json'),'review_sha256':h,'manifest_sha256':mh,'source_pin_count':len(pins)}))
