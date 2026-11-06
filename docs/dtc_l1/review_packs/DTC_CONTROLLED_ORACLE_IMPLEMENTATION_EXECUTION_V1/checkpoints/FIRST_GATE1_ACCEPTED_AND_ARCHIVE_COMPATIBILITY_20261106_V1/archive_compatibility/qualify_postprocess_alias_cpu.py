import pathlib,hashlib,json,tempfile,types,copy,ast
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1');O=A/'agents/R_outbox_metadata_alias_amendment_v1';src=O/'oracle_postprocess_alias.py'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):m=types.ModuleType(n);m.__file__=str(p);exec(compile(P(p).read_bytes(),str(p),'exec'),m.__dict__);return m
m=load('R_CPU_PRIVATE_POSTPROCESS_ALIAS',src);checks=[]
def ck(n,v):
 if not v:raise AssertionError(n)
 checks.append(n)
def reject(n,fn):
 try:fn()
 except AssertionError:checks.append(n);return
 raise AssertionError('ACCEPTED_BAD:'+n)
with tempfile.TemporaryDirectory(dir=O,prefix='CPU_alias_')as td:
 d=P(td);approval=d/'approval.json';primitive=d/'primitive.py';outbox=d/'outbox.py';other=d/'other.json'
 approval.write_text('{"cohorts":["CPU_ONLY"],"budget":32}');primitive.write_bytes(b'CPU_PRIMITIVE_SOURCE');outbox.write_bytes(b'CPU_REGISTERED_WRAPPER');other.write_text('{}')
 value=json.loads(approval.read_text());sentinel={};original=lambda p:value if P(p)==approval else sentinel
 alias=m.make_exact_read_alias(original,approval,sha(approval),primitive,sha(primitive),outbox,sha(outbox))
 observed=alias(approval);ck('exact_legacy_key_uses_primitive_not_wrapper',observed['outbox_sha256']==sha(primitive)and observed['outbox_sha256']!=sha(outbox))
 ck('original_approval_dict_not_mutated','outbox_sha256'not in value and observed is not value)
 ck('other_reads_exact_object_unchanged',alias(other)is sentinel)
 for title,args in [('wrongapproval',('0'*64,sha(primitive),sha(outbox))),('wrongprimitive',(sha(approval),'0'*64,sha(outbox))),('wrongregisteredwrapper',(sha(approval),sha(primitive),'0'*64))]:
  reject(title,lambda args=args:m.make_exact_read_alias(original,approval,args[0],primitive,args[1],outbox,args[2]))
 value['outbox_sha256']='CONFLICT';reject('real_conflicting_field_not_overwritten',lambda:alias(approval));value.pop('outbox_sha256')
 # Future private ops loader installs the consumer before context publication;
 # every other load preserves its actual returned object.
 root=P('/CPU_ONLY_SCOPE');consumer=types.SimpleNamespace(__file__=str(root/'tools/oracle_results.py'),load=lambda n,f:sentinel)
 ops=types.SimpleNamespace(load=lambda n,p:consumer if P(p).name=='oracle_results.py'else sentinel)
 m.wrap_ops(ops);ck('future_ops_consumer_hook_before_context',getattr(ops.load('future',root/'tools/oracle_results.py'),m.MARKER,False))
 ck('future_ops_other_loads_unchanged',ops.load('other',root/'tools/oracle_native.py')is sentinel)
 old=consumer.load;m.wrap_consumer(consumer,root);ck('idempotent_consumer_install_no_doublewrap',consumer.load is old)
# Actual frozen, naturally closed UUID: build the private archive primitive and
# examine ONLY its projected read. No archive/start/registry mutation here.
R=P('/root/data/dtc_controlled_oracle_20261106_v1/initial8');c='E2-DTCORACLE-I8-e7bb67e63e3c3847-DH-OFF_MATCHED-V1';out=R/'DTC/run/results/c5dda178-aa29-45b7-9fc1-1638d67c14b8'
pins={str(p):sha(p)for p in [out/'NATIVE_EXIT.json',out/'L2_STRICT.json',out/'raw.log.gz',R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',R/'control/EXECUTION_PLAN.json',R/'tools/oracle_outbox.py']}
o=load('R_ACTUAL_CLOSED_OUTBOX_PRIVATE_READ_ONLY',R/'tools/oracle_outbox.py');m.wrap_outbox(o,R);b=o.adapted(c)
projected=b.read(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json');ck('actual_closed_UUID_legacy_selfcheck_projection_PASS',projected['outbox_sha256']==m.PRIMITIVE_SHA==sha(m.PRIMITIVE))
e,q,plan,intent,done,actualout=o.closed(c);ck('actual_registered_wrapper_pin_kept',q['outbox_sha256']==sha(R/'tools/oracle_outbox.py')and q['outbox_sha256']!=m.PRIMITIVE_SHA)
ck('actual_same_UUID_strict_natural_identity',done['uuid']==intent['uuid']=='c5dda178-aa29-45b7-9fc1-1638d67c14b8'and done['stop_reason']is None and done['launcher_wait_returncode']==0)
ck('all_frozen_model_and_approval_plan_source_bytes_unchanged',pins=={p:sha(p)for p in pins})
ck('source_no_manifest_changes_or_sciencecalls',all(x not in src.read_text()for x in ['manifest_for=','run-native','update_authority(','os.kill','Popen(','ThreadPoolExecutor']))
report=dict(status='PASS_POSTPROCESS_ONLY_PRIVATE_ALIAS_CPU_AND_ACTUAL_CLOSED_READ',checks=checks,check_count=len(checks),source_sha256=sha(src),actual_closed_UUID=done['uuid'],actual_frozen_pins=pins,original_primitive_sha256=m.PRIMITIVE_SHA,actual_registered_outbox_sha256=q['outbox_sha256'],actual_approval_original_sha256=q['spec_request_sha256'],production_owner_installs=0,actual_archives_started_by_CPU_fixture=0,models_restarted=0,registry_writes=0,original_files_changed=0)
(O/'CPU_QUALIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status=report['status'],checks=len(checks),source_sha256=report['source_sha256'])))
