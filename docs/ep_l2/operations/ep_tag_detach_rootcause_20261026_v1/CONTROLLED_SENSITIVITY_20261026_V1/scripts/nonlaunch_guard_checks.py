#!/usr/bin/env python3
"""Synthetic controller/route guards only: no simulator process or real authority write."""
import sys
sys.dont_write_bytecode=True
import copy, hashlib, importlib.util, json, os, pathlib, subprocess, tempfile, types
P=pathlib.Path;ROOT=P('/root/data/ep_memory_path_sensitivity_20261026_v1')
sys.path.insert(0,str(ROOT/'tools'))
import experiment_runtime as v
checks=[]
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='nonlaunch_',dir=ROOT) as folder:
 t=P(folder);B=t/'case';LED=t/'ledger';REG=t/'authority/REGISTRY.json';EPOCH=t/'authority/EPOCH.json'
 for p in [B/'control',B/'env',B/'run/results',B/'run/tmp',B/'run/cache',LED,REG.parent/'request_history']:p.mkdir(parents=True,exist_ok=True)
 (REG.parent/'REGISTRY_UPDATE.lock').write_text('')
 for i in range(5):(B/'env'/('config-'+str(i)+'.config')).write_text('SYNTHETIC_NO_MODEL\n')
 s={'cohort':v.E1,'application_budget':1,'automatic_retry':False,'reserved_write_bytes':512*2**20,
    'advertised_peer_reservation_bytes':int(3.5*2**30),'shared_floor_compatibility_margin_bytes':3*2**30,
    'binary_path':'/SYNTHETIC_NEVER_EXECUTED','trace_entry':'/SYNTHETIC_NO_TRACE','host_cpu':16,
    'memory_cap_bytes':9*2**30,'result_cap_bytes':128*2**20,'temporary_cap_bytes':128*2**20,'wall_timeout_seconds':7200,'source_identity':{}}
 put(B/'control/FROZEN_SPEC.json',s);put(B/'control/USER_AUTHORIZATION.json',{'SYNTHETIC':True})
 put(B/'control/NATIVE_PRELAUNCH_QUALIFICATION.json',{'status':'NATIVE_PRELAUNCH_QUALIFIED_NOT_APPLICATION_ACCEPTED','spec_sha256':sha(B/'control/FROZEN_SPEC.json')})
 peer={'project':'DTC_L1','state':'RUNNING','budget':9,'consumed':{'old':{'preserve':'unchanged'}},'reserved_write_bytes':123}
 put(REG,{'registered_future_requests':{'FOREIGN':copy.deepcopy(peer)},'new_scientific_budget_remaining':7})
 put(EPOCH,{'epoch':2,'holder':os.uname().nodename,'native_registry_sha256':sha(REG)})
 v.B=B;v.C=v.E1;v.LED=LED;v.REG=REG;v.EPOCH=EPOCH
 v.prepare=lambda:{'SYNTHETIC_PREPARE_ONLY':True}
 # Direct call without exact native entry flag must fail before any consume.
 os.environ.pop('EP_MEMORY_NATIVE_ENTRY',None)
 try:v.run();raise AssertionError('direct run allowed')
 except RuntimeError as e:assert 'sole entry required' in str(e)
 checks.append('direct_engine_run_rejected_before_consume')
 os.environ['EP_MEMORY_NATIVE_ENTRY']='1'
 v.register();reg=json.loads(REG.read_text())
 assert reg['new_scientific_budget_remaining']==8 and reg['registered_future_requests']['FOREIGN']==peer
 assert reg['registered_future_requests'][v.E1]['reserved_write_bytes']==int(3.5*2**30)
 checks.append('new_budget_registered_without_peer_mutation_and_explicit_margin')
 observed=[]
 def no_model(argv,**kwargs):
  reg=json.loads(REG.read_text());row=reg['registered_future_requests'][v.E1]
  assert row['consumed']==1 and reg['new_scientific_budget_remaining']==7
  assert (LED/(v.E1+'.INTENT.json')).exists() and row['state']=='CONSUMED_RUNNING_OR_UNRESOLVED'
  observed.append(True);raise RuntimeError('SYNTHETIC_NO_MODEL_FORK')
 v.subprocess=types.SimpleNamespace(Popen=no_model,TimeoutExpired=subprocess.TimeoutExpired,STDOUT=subprocess.STDOUT)
 receipt=v.run()
 if observed!=[True] or not receipt['stop_reason'].endswith('SYNTHETIC_NO_MODEL_FORK'):print(json.dumps({'debug_receipt':receipt,'observed':observed}),file=sys.stderr)
 assert observed==[True] and receipt['stop_reason'].endswith('SYNTHETIC_NO_MODEL_FORK')
 assert json.loads(REG.read_text())['registered_future_requests']['FOREIGN']==peer
 checks.append('intent_and_charge_precede_mock_fork_no_real_process')
 before=REG.read_bytes()
 try:v.run();raise AssertionError('consumed request retried')
 except RuntimeError as e:assert 'no exact unused budget' in str(e)
 assert REG.read_bytes()==before
 checks.append('consumed_request_no_retry_no_refund')
 # Route shells are replaced with inert argv recorders in a temporary copy.
 prior=t/'prior.sh';prior.write_text('#!/bin/sh\nprintf "OLD\\n"\nprintf "%s\\n" "$@"\n')
 ep=t/'ep.sh';ep.write_text('#!/bin/sh\nprintf "EP\\n"\nprintf "%s\\n" "$@"\n')
 raw=(ROOT/'tools/native_entry_candidate.sh').read_text()
 raw=raw.replace('/usr/bin/python3 -B '+str(ROOT/'tools/native_dispatch.py'),'/bin/sh '+str(ep))
 raw=raw.replace(str(ROOT/'tools/prior_native_entry.sh'),str(prior))
 wrapper=t/'native.sh';wrapper.write_text(raw)
 for args,label in [(['experiment','prepare',v.E1,'--project','EP_L2'],'EP'),(['experiment','prepare',v.E2,'--project','EP_L2'],'EP'),(['experiment','inspect','DTC_UNCHANGED','--project','DTC_L1','arg with spaces'],'OLD'),(['asset','ensure','EP_VECTORADD_S'],'OLD')]:
  got=subprocess.check_output(['/bin/sh',str(wrapper),*args],text=True).splitlines()
  assert got==[label,*args]
 checks.append('exact_EP_routing_and_unchanged_peer_argv_delegation')
result={'status':'PASS_SYNTHETIC_NONLAUNCH_GUARDS_ONLY','checks':checks,'real_simulator_forks':0,'real_authority_mutations':0,'scientific_acceptance_granted':False}
print(json.dumps(result,indent=2))
