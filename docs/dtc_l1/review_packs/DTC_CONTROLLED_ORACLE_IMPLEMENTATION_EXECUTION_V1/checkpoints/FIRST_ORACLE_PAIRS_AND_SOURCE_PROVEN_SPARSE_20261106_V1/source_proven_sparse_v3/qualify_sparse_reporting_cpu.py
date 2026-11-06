from pathlib import Path
import types,json,hashlib,gzip,re,traceback
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1/agents/R_source_proven_sparse_reporting_v3');R=Path('/root/data/dtc_controlled_oracle_20261106_v1/initial8')
def load(p):
 m=types.ModuleType('cpu_'+p.stem);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
h=load(A/'oracle_sparse_reporting.py');l=load(h.LEGACY);e=load(R/'tools/oracle_native.py');q=e.registered()[2];tests=[]
def ok(name,f):
 try:f();tests.append({'name':name,'status':'PASS'})
 except Exception as x:tests.append({'name':name,'status':'FAIL','error':repr(x),'stack':traceback.format_exc()})
def reject(f):
 try:f()
 except (AssertionError,ValueError,KeyError):return
 raise AssertionError('MALFORMED_NOT_REJECTED')
c='E2-DTCORACLE-I8-e7bb67e63e3c3847-DH-M_DATAREAD-V1';s=e.spec_for(c);u=q['consumed'][c]['uuid'];out=R/'DTC/run/results'/u;raw=gzip.decompress((out/'raw.log.gz').read_bytes()).decode();block=raw[raw.index('kernel_name = '):]
pins=[R/'control/EXECUTION_PLAN.json',R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',out/'raw.log.gz',out/'NATIVE_EXIT.json',R/'tools/oracle_strict.py',R/'tools/oracle_population.py'];before={str(p):sha(p)for p in pins}
v=h.nullable_traffic(l.traffic,block)
ok('ACTUAL_PRINTED_TOTAL_NULL_DERIVED_ZERO_WITH_FULL_PROOF',lambda:exec("assert v['L2_reported_GLOBAL_ACC_R_TOTAL_ACCESS']is None and v['L2_accepted_read_32B_sectors']is None and v['L2_derived_accepted_read_32B_sectors']==0 and v['sparse_partition_proof']['global_accesses']==750000 and v['L2_accepted_read_bucket_partition'].startswith('PASS_SOURCE')"))
mutations={
 'MISSING_ONE_READ_STATUS':block.replace('L2_cache_stats_breakdown[GLOBAL_ACC_R][HIT] = 0','UNPRINTED_L2[GLOBAL_ACC_R][HIT] = 0',1),
 'MISSING_OTHER_KIND_STATUS':block.replace('L2_cache_stats_breakdown[CONST_ACC_R][HIT] = 0','UNPRINTED_L2[CONST_ACC_R][HIT] = 0',1),
 'MISSING_TOTAL_NONZERO_STATUS':block.replace('L2_cache_stats_breakdown[GLOBAL_ACC_R][HIT] = 0','L2_cache_stats_breakdown[GLOBAL_ACC_R][HIT] = 1',1),
 'DUPLICATE_READ_STATUS':block+'\nL2_cache_stats_breakdown[GLOBAL_ACC_R][HIT] = 0\n',
 'BAD_PRINTED_KIND_TOTAL':block.replace('L2_cache_stats_breakdown[GLOBAL_ACC_W][TOTAL_ACCESS] = 750000','L2_cache_stats_breakdown[GLOBAL_ACC_W][TOTAL_ACCESS] = 750001',1),
 'ZERO_KIND_TOTAL_WRONGLY_PRINTED':block+'\nL2_cache_stats_breakdown[CONST_ACC_R][TOTAL_ACCESS] = 0\n',
 'INDEPENDENT_ACCESS_MISMATCH':block.replace('L2_total_cache_accesses = 750000','L2_total_cache_accesses = 750001',1),
 'MISSING_GLOBAL_ACCESS':block.replace('L2_total_cache_accesses =','L2_missing_cache_accesses =',1),
 'MISSING_BANK':block.replace('L2_cache_bank[39]:','MISSING_L2_bank[39]:',1),
 'BANK_ACCESS_MISMATCH':block.replace('L2_cache_bank[0]: Access = 18816','L2_cache_bank[0]: Access = 18817',1),
 'MISSING_DRAM':block.replace('DRAM[19]:','MISSING_DRAM[19]:',1),
 'MISSING_DRAM_REQUIRED_FIELD':block.replace('n_rd=0 ','',1),
 'UINT32_OVERFLOW':block.replace('L2_cache_stats_breakdown[GLOBAL_ACC_R][HIT] = 0','L2_cache_stats_breakdown[GLOBAL_ACC_R][HIT] = 4294967296',1),
}
for label,key in [('MISS','cache_misses'),('PENDING','cache_pending_hits'),('RESFAIL','cache_reservation_fails')]:
 m=re.search(r'^(L2_total_'+key+r' = )(\d+)',block,re.M);assert m
 mutations['INDEPENDENT_'+label+'_MISMATCH']=block[:m.start(2)]+str(int(m[2])+1)+block[m.end(2):]
for name,bad in mutations.items():
 assert bad!=block,name+'_MUTATION_MUST_CHANGE_BLOCK'
 ok(name+'_REJECTED',lambda bad=bad:reject(lambda:h.nullable_traffic(l.traffic,bad)))
strict=h.wrap_strict(load(R/'tools/oracle_strict.py'),R);actual=[]
for cohort in [c,'E2-DTCORACLE-I8-f437190767aaed49-DH-L1_DATAREADY-V1']:
 try:
  proof=strict.terminal(cohort);actual.append(dict(cohort=cohort,uuid=proof['uuid'],cycles=proof['cycles'],exposure=proof['actual_mechanism_exposure'],traffic=proof['traffic']));tests.append({'name':'ACTUAL_FULL_STRICT_READONLY_'+cohort,'status':'PASS'})
 except Exception as x:tests.append({'name':'ACTUAL_FULL_STRICT_READONLY_'+cohort,'status':'FAIL','error':repr(x),'stack':traceback.format_exc()})
off='E2-DTCORACLE-I8-e7bb67e63e3c3847-DH-OFF_MATCHED-V1';original=load(R/'tools/oracle_strict.py').terminal(off);adapted=strict.terminal(off)
ok('ACTUAL_OFF_STRICT_PROOF_EXACT_ORIGINAL',lambda:exec('assert original==adapted'))
domain=json.loads(Path(s['input_binding_path']).read_bytes())['qualification'];pop=h.wrap_population(load(R/'tools/oracle_population.py'),R)
for key in ['DTC_L1_lower_credit_released','DTC_L1_oo_completion_dependency_closed','DTC_L1_oo_active_refs','DTC_SERVICE_V1_fully_ready_to_complete_sum']:
 m=re.search(r'^(\s*'+key+r'\s*=\s*)(\d+)(\s*)$',raw,re.M);assert m
 bad=raw[:m.start(2)]+str(int(m[2])+1)+raw[m.end(2):]
 ok('ACTUAL_LIFECYCLE_MUTATION_'+key,lambda bad=bad:reject(lambda:pop.population_from_verified_closed_text(bad,s,domain)))
# Existing alias remains and future consumer gets new private hooks.
alias=load(A.parent/'R_outbox_metadata_alias_amendment_v1/oracle_postprocess_alias.py');consumer=alias.wrap_consumer(load(R/'tools/oracle_results.py'),R);h.wrap_consumer(consumer,R)
ok('EXISTING_APPROVAL_ALIAS_PRESERVED',lambda:exec("assert getattr(consumer.load('cpuoutbox','oracle_outbox.py'),alias.MARKER)"))
ops=types.ModuleType('cpuops');ops.load=lambda name,path:alias.wrap_consumer(load(Path(path)),Path(path).parents[1])if Path(path).name=='oracle_results.py'else load(Path(path));h.wrap_ops(ops);future=ops.load('future',R/'tools/oracle_results.py')
ok('FUTURE_CONSUMER_BOTH_HOOKS_PRESERVED',lambda:exec('assert getattr(future,h.MARKER)and getattr(future,alias.MARKER)'))
ok('SOURCE_PLAN_APPROVAL_RAW_EXIT_IDENTITIES_UNCHANGED',lambda:exec('assert before=={str(p):sha(p)for p in pins}'))
report=dict(status='PASS'if all(x['status']=='PASS'for x in tests)else'FAIL',source_sha256=sha(A/'oracle_sparse_reporting.py'),checks=tests,actual_closed_results=actual,unchanged_identity_pins=before,actual_installs=0,model_starts=0,scientific_registration_mutations=0,raw_or_strict_source_writes=0,scientific_release='PENDING_INDEPENDENT_AND_MAIN_REVIEW')
with(A/'CPU_QUALIFICATION.json').open('x')as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(dict(status=report['status'],checks=tests,actual=[{k:x[k]for k in ['cohort','uuid','cycles','exposure']}for x in actual]),indent=2))
