"""Bounded synthetic scope controls on deep-copied actual51 metadata.

No real reserve/Popen/controller/native/app or raw/trace reads. Fake Q/spec files
are visibly SYNTHETIC and production mode rejects them.
"""
import copy,hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
E=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
TOOLS=E/'util/ep_l2/mechanism_e';sys.path[:0]=[str(HERE),str(TOOLS)]
import detach_successor as n
import detach_diagnostic_policy as dp
from detach_scope_core import sha,spec_sha
P=E/'docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1'
REG=Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
BASE=json.loads(REG.read_text())
APPROVAL=json.loads((P/'approved_four_r1/USER_APPROVAL.json').read_text())
PROPOSAL=json.loads((P/'conditional_followup/PRIMARY_FOUR_EXISTING_POSITIVE_RO_r1/PROPOSAL.json').read_text())
def write(path,obj):path.write_text(json.dumps(obj,sort_keys=True));return n.file_ref(path)
class Fixture:
 def __init__(self,root):
  self.root=root;self.data=copy.deepcopy(BASE);self.item=self.data['mechanism_study_20261019_v1'];self.baseline=copy.deepcopy(self.item)
  a=copy.deepcopy(APPROVAL);a['synthetic_fixture']=True;ar=write(root/'SYNTHETIC_APPROVAL.json',a)
  oldqid=self.item['attempts'][50]['qualification_id'];oldq=self.item['qualifications'][oldqid]['qualification'];scope=copy.deepcopy(oldq['detach_observer_diagnostic']['validation_scope']);scope['synthetic_fixture']=True;scope['observer_decoder']=n.file_ref(P/'parser_recovery/decoder_samecycle_close.py')
  self.specs={};self.qrows={};conds={};cli=root/'SYNTHETIC_PARSE_CLI.py';cli.write_text('# SYNTHETIC metadata CLI, never executed\n');parser=n.file_ref(cli)
  for row in PROPOSAL['primary_scope']:
   cid=row['condition_id'];s=json.loads(Path(row['prospective_exact_spec']['path']).read_text());s['parser']=parser;s['budget_bucket']=a['batch_id'];s.pop('status',None)
   profile=s['profile_semantics']
   q=dict(status='INDEPENDENTLY_QUALIFIED',qualified_by='E',synthetic_fixture=True,campaign_id=n.CAMPAIGN,scientific_scope=n.SCI_SCOPE,source_identity=a['source_identity'],profile_semantics=profile,supported_profiles={'F':profile},input_selection_id=s['selection_id'],terminal_parser=parser,
    detach_observer_diagnostic=dict(validation_scope=scope,trace_content_sha256=s['identity']['trace_content_sha256'],runtime_config_sha256=s['identity']['runtime_config_sha256'],input_selection_id=s['selection_id'],termination_contract=s['identity']['termination_contract'],expected_full_instructions=row['full_instructions']),SYNTHETIC_FIXTURE_NOT_PRODUCTION_QUALIFICATION=True)
   qr=write(root/('SYNTHETIC_Q_'+row['workload']+'.json'),q);s['qualification_id']=qr['sha256'];sr=write(root/('SYNTHETIC_SPEC_'+row['workload']+'.json'),s)
   conds[cid]=dict(selection_id=s['selection_id'],resources=dict(cpu=1,memory_bytes=8*2**30,maximum_result_bytes=n.CAP),identity=s['identity'],spec_ref=sr,spec_sha256=spec_sha(s),qualification=qr,parser=parser,content_refs=[parser])
   self.specs[cid]=s;self.qrows[cid]=dict(path=qr['path'],sha256=qr['sha256'],qualification=q)
  m=dict(schema='E2_EXACT_POSITIVE_RO_FOUR_SUCCESSOR_V1',status='E_SOURCE_BOUND_PRIMARY_FOUR_SEALED',synthetic_fixture=True,campaign_id=n.CAMPAIGN,baseline_actual_starts=51,maximum_new_actual_starts=4,condition_order=list(n.CONDITIONS),batch_id=a['batch_id'],source_identity=a['source_identity'],approval_ref=ar,proposal_ref=n.file_ref(P/'conditional_followup/PRIMARY_FOUR_EXISTING_POSITIVE_RO_r1/PROPOSAL.json'),validation_scope=scope,historical51_seal=n.historical51_seal(self.item,self.data),conditions=conds,pairs=[],endpoint_result_hardcap_bytes=n.CAP,all_four_endpoint_results_hardcap_bytes=4*n.CAP)
  self.m=m;self.mref=write(root/'SYNTHETIC_MANIFEST.json',m);self.scope=n.Scope(self.mref,fixture_mode=True)
 def adopt(self):return self.scope.adopt(self.item,self.data,[],dp.authority().active)
 def register_bind(self,cid):
  s=self.specs[cid];self.item['qualifications'][s['qualification_id']]=copy.deepcopy(self.qrows[cid]);return self.scope.bind(self.item,s,dp.authority().active)
 def reserve(self,cid):
  s=self.specs[cid];aid='SYNTHETIC_E'+str(52+len(self.item['attempts'][51:]));key=sha(s['identity'])
  a=dict(attempt_id=aid,run_key=key,identity=copy.deepcopy(s['identity']),selection_id=s['selection_id'],qualification_id=s['qualification_id'],profile='F',comparison_group=s['comparison_group'],budget_bucket=s['budget_bucket'],labels=s['labels'],state='RESERVED',actual_start=False,maximum_result_bytes=n.CAP,result_directory=str(self.root/aid))
  self.scope.record_reservation(self.item,s,a,dp.authority().active);self.item['attempts'].append(a)
  self.data['runs'][key]=dict(run_key=key,lease_id=aid,identity=a['identity'],experiment_id=n.CAMPAIGN,status='RESERVED',process=None,qualification_id=a['qualification_id'],condition_id=cid,diagnostic_spec_sha256=a['diagnostic_spec_sha256'],scientific_scope=n.SCI_SCOPE,budget_bucket=a['budget_bucket'],cpu_units=1,memory_bytes=8*2**30,disk_growth_bytes=n.CAP,disk_floor_bytes=5*2**30,monitor_reserve_bytes=2*2**30,policy_id=self.item['workspace_disk_policy']['policy_id'])
  self.counts();self.check();return a
 def counts(self):self.item['actual_starts']=sum(a['actual_start'] is True for a in self.item['attempts']);self.item['uncertain_start_intents']=sum(a['state']=='START_INTENT_UNRECONCILED' for a in self.item['attempts'])
 def start(self,a):
  p=dict(pid=9000000+len(self.item['attempts']),start_ticks=len(self.item['attempts']),boot_id='SYNTHETIC_BOOT');a.update(state='RUNNING',actual_start=True,process=p,started_unix=1)
  self.data['runs'][a['run_key']].update(status='RUNNING',process=p,started_unix=1)
  self.scope.record_started(self.item,a);self.counts();self.check()
 def finish(self,a,status):
  a.update(state=status,receipt_path=str(self.root/(a['attempt_id']+'_SYNTHETIC_RECEIPT.json')),receipt_sha256='a'*64)
  self.data['runs'][a['run_key']]['status']=status
  if status=='COMPLETE_VALID':self.item['accepted_results'][a['attempt_id']]=dict(path=a['receipt_path'],sha256=a['receipt_sha256'],identity=a['identity'],run_key=a['run_key'],qualification_id=a['qualification_id'],scientific_scope=n.SCI_SCOPE)
  self.counts();self.check()
 def check(self):
  self.scope.active(self.item,dp.authority().active);self.scope.crosscheck(self.data,self.item,dp.authority().active,dp._legacy_crosscheck_data)
class Controls(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='e2_four_scope_');self.addCleanup(self.tmp.cleanup);self.f=Fixture(Path(self.tmp.name));self.patch=patch.object(n,'_SCOPE',self.f.scope);self.patch.start();self.addCleanup(self.patch.stop)
 def ready(self):
  self.f.adopt()
  for cid in n.CONDITIONS:self.f.register_bind(cid)
 def test_01_default_unbound_and_synthetic_production_refuse(self):
  with patch.object(n,'_SCOPE',None),patch.object(n,'FINAL_SUCCESSOR_REF',None),self.assertRaisesRegex(ValueError,'UNBOUND'):n.scope()
  with self.assertRaisesRegex(ValueError,'synthetic'):n.Scope(self.f.mref).manifest()
 def test_02_adopt_and_each_exact_Q_bind(self):
  self.ready();self.f.check();self.assertEqual(self.f.item['actual_starts'],51)
 def test_03_normal_four_parallel_rolling_states_to55(self):
  self.ready();rows=[self.f.reserve(c) for c in n.CONDITIONS]
  for a in rows:self.f.start(a)
  for a in reversed(rows):self.f.finish(a,'COMPLETE_VALID')
  self.assertEqual(self.f.item['actual_starts'],55);self.assertEqual(self.f.item['attempts'][:51],self.f.baseline['attempts'])
  self.assertEqual(self.f.item['accepted_results'][self.f.item['attempts'][50]['attempt_id']],self.f.baseline['accepted_results'][self.f.item['attempts'][50]['attempt_id']])
 def test_04_old51_tamper_refuse(self):
  self.ready();self.f.item['attempts'][50]['state']='COMPLETE_VALID'
  with self.assertRaisesRegex(ValueError,'original51'):self.f.check()
 def test_05_old_supplement_pointer_tamper_refuse(self):
  self.ready();aid=self.f.item['attempts'][50]['attempt_id'];self.f.item['accepted_results'][aid]['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'old map'):self.f.check()
 def test_06_old_Q_tamper_refuse(self):
  self.ready();oldqid=self.f.item['attempts'][50]['qualification_id'];self.f.item['qualifications'][oldqid]['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'old map'):self.f.check()
 def test_07_extra_Q_and_input_refuse(self):
  self.ready();self.f.item['qualifications']['0'*64]={}
  with self.assertRaisesRegex(ValueError,'unapproved new'):self.f.check()
  self.f.item['qualifications'].pop('0'*64);self.f.item['input_selections']['extra']={}
  with self.assertRaisesRegex(ValueError,'input/pair'):self.f.check()
 def test_08_spec_semantic_tamper_refuse(self):
  self.ready();s=copy.deepcopy(self.f.specs[n.CONDITIONS[0]]);s['identity']['trace_content_sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'spec/identity'):self.f.scope.check_spec(s)
 def test_09_retry_after_failed_paid_refuse(self):
  self.ready();cid=n.CONDITIONS[0];a=self.f.reserve(cid);self.f.start(a);self.f.finish(a,'FAILED')
  with self.assertRaisesRegex(ValueError,'consumed/no retry'):self.f.reserve(cid)
  self.assertEqual(self.f.item['actual_starts'],52)
 def test_10_coordinated_refund_with_witness_refuse(self):
  self.ready();a=self.f.reserve(n.CONDITIONS[0]);self.f.start(a);a.update(state='CANCELLED_BEFORE_START',actual_start=False);self.f.counts()
  with self.assertRaisesRegex(ValueError,'forbids refund'):self.f.check()
 def test_11_duplicate_start_refuse(self):
  self.ready();a=self.f.reserve(n.CONDITIONS[0]);self.f.start(a)
  with self.assertRaisesRegex(ValueError,'duplicate start'):self.f.scope.record_started(self.f.item,a)
 def test_12_missing_tail_with_canonical_retained_refuse(self):
  self.ready();a=self.f.reserve(n.CONDITIONS[0]);self.f.item['attempts'].pop();self.f.item[n.FIELD]['attempt_ids'].clear();self.f.counts()
  with self.assertRaisesRegex(ValueError,'canonical successor'):self.f.check()
 def test_13_pair_and_wrongQ_row_refuse(self):
  self.ready();self.f.item['accepted_pairs']['NEW_PAIR']={}
  with self.assertRaisesRegex(ValueError,'input/pair'):self.f.check()
  self.f.item['accepted_pairs'].pop('NEW_PAIR');qid=self.f.specs[n.CONDITIONS[0]]['qualification_id'];self.f.item['qualifications'][qid]['qualification']['source_identity']['binary_sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'Q row/bytes'):self.f.check()
 def test_14_failure_spawn_consumes_reservation(self):
  self.ready();cid=n.CONDITIONS[0];a=self.f.reserve(cid);a['state']='FAILED_SPAWN';self.f.data['runs'][a['run_key']]['status']='FAILED';self.f.counts();self.f.check()
  with self.assertRaisesRegex(ValueError,'consumed/no retry'):self.f.reserve(cid)
 def test_15_queue_qualified_subsets_no_union_no_duplicate(self):
  self.ready();refs=[self.f.m['conditions'][c]['spec_ref'] for c in n.CONDITIONS[:2]];self.assertTrue(n.queue_guard(self.f.item,{'specs':refs,'pairs':[]},None,dp.authority().active))
  with self.assertRaisesRegex(ValueError,'unique'):n.queue_guard(self.f.item,{'specs':[refs[0],refs[0]],'pairs':[]},None,dp.authority().active)
  with self.assertRaisesRegex(ValueError,'cannot pair'):n.queue_guard(self.f.item,{'specs':refs,'pairs':[{}]},None,dp.authority().active)
 def test_16_shared_adapter_checks_each_Q(self):
  class Adapter:
   calls=[]
   def check(inner,spec,qrow):inner.calls.append((spec['condition_id'],qrow['sha256']))
  adapter=Adapter()
  with patch.object(n.detach_validation,'INDEPENDENT_SCHEMA_VALIDATION_READY',True),patch.object(n.detach_validation,'_BINDING',self.f.m['validation_scope']),patch.object(n.detach_validation,'_ADAPTER',adapter):
   for cid in n.CONDITIONS:n.prepare_validator(self.f.qrows[cid],self.f.specs[cid],None)
   self.assertEqual(len(adapter.calls),4)
   wrong=copy.deepcopy(self.f.qrows[n.CONDITIONS[0]]);wrong['sha256']='0'*64
   with self.assertRaisesRegex(ValueError,'registered Q'):n.prepare_validator(wrong,self.f.specs[n.CONDITIONS[0]],None)
 def test_17_old_canonical_FAILED_tamper_refuse(self):
  self.ready();old=self.f.item['attempts'][50];self.f.data['runs'][old['run_key']]['status']='COMPLETE_VALID'
  with self.assertRaisesRegex(ValueError,'original canonical'):self.f.check()
 def test_18_history_old_prefix_tamper_refuse(self):
  self.ready();self.f.item['scientific_hold_history'][0]['reason']='tampered'
  with self.assertRaisesRegex(ValueError,'history prefix'):self.f.check()
 def test_19_unmarked_samecampaign_canonical_refuse(self):
  self.ready();self.f.data['runs']['EXTRA_UNMARKED']=dict(experiment_id=n.CAMPAIGN,status='RUNNING',run_key='EXTRA_UNMARKED')
  with self.assertRaisesRegex(ValueError,'canonical successor'):self.f.check()
 def forecast_view(self):
  import coordinator as co
  view=copy.deepcopy(self.f.data);c=self.f.m['conditions'][n.CONDITIONS[0]];key='READONLY_SUBMITTED_FORECAST_'+sha(c['identity']);r=c['resources']
  import socket
  row=dict(run_key=key,status='RESERVED',host=socket.gethostname(),experiment_id=n.CAMPAIGN,owner='E_READONLY_FORECAST_NOT_LEASE',cpu_units=r['cpu'],memory_bytes=r['memory_bytes'],disk_growth_bytes=r['maximum_result_bytes'],monitor_reserve_bytes=2*co.GIB,result_directory=str(co.OUTPUT/key),scan=False,process=None)
  view['runs'][key]=row;return co,view,key,row
 def test_20_readonly_forecast_preserves_full_authority(self):
  self.ready();co,view,key,row=self.forecast_view();self.assertTrue(co.validate_successor_forecast_view(view,self.f.data))
  def stop_before_resource(actual):
   self.assertIs(actual,self.f.data);raise RuntimeError('SYNTHETIC_LEDGER_ROUTE_CONFIRMED_NO_ADMISSION')
  with patch.object(co,'ledger',side_effect=stop_before_resource),self.assertRaisesRegex(RuntimeError,'ROUTE_CONFIRMED'):
   co.resource_gate(view,'simulation',1,8*co.GIB,n.CAP,{},authority_data=self.f.data,read_only_forecast=True)
 def test_21_forecast_underreservation_refuse(self):
  self.ready();co,view,key,row=self.forecast_view();row['monitor_reserve_bytes']-=1
  with self.assertRaisesRegex(ValueError,'underreserve'):co.validate_successor_forecast_view(view,self.f.data)
  row['monitor_reserve_bytes']+=1;row['memory_bytes']-=1
  with self.assertRaisesRegex(ValueError,'underreserve'):co.validate_successor_forecast_view(view,self.f.data)
 def test_22_forecast_policy_or_actualrun_change_refuse(self):
  self.ready();co,view,key,row=self.forecast_view();view['hosts']={}
  with self.assertRaisesRegex(ValueError,'every original nonruns'):co.validate_successor_forecast_view(view,self.f.data)
  co,view,key,row=self.forecast_view();oldkey=next(iter(self.f.data['runs']));view['runs'].pop(oldkey)
  with self.assertRaisesRegex(ValueError,'remove or change'):co.validate_successor_forecast_view(view,self.f.data)
 def test_23_virtual_persistence_rejected_by_scientific_ledger(self):
  self.ready();co,view,key,row=self.forecast_view()
  with self.assertRaisesRegex(ValueError,'canonical successor'):dp.crosscheck_data(view,self.f.item)
 def test_24_unknown_forecast_condition_refuse(self):
  self.ready();co,view,key,row=self.forecast_view();view['runs'].pop(key);row['run_key']='READONLY_SUBMITTED_FORECAST_UNKNOWN';view['runs'][row['run_key']]=row
  with self.assertRaisesRegex(ValueError,'approved condition/runkey'):co.validate_successor_forecast_view(view,self.f.data)
 def test_25_old_start_own_reservation_authority_route_preserved(self):
  self.ready();a=self.f.reserve(n.CONDITIONS[0]);import coordinator as co
  view=copy.deepcopy(self.f.data);view['runs'].pop(a['run_key'])
  def route(actual):
   self.assertIs(actual,self.f.data);raise RuntimeError('SYNTHETIC_ORIGINAL_START_AUTHORITY_ROUTE')
  with patch.object(co,'ledger',side_effect=route),self.assertRaisesRegex(RuntimeError,'ORIGINAL_START_AUTHORITY'):
   co.resource_gate(view,'simulation',1,8*co.GIB,n.CAP,{},authority_data=self.f.data)

 def test_26_tail_profile_labels_comparison_refuse(self):
  self.ready();a=self.f.reserve(n.CONDITIONS[0])
  for field,bad in [('profile','S'),('labels',{}),('comparison_group','OTHER')]:
   before=copy.deepcopy(a[field]);a[field]=bad
   with self.subTest(field=field),self.assertRaisesRegex(ValueError,'profile/labels/comparison'):self.f.check()
   a[field]=before
 def test_27_canonical_resource_reservation_refuse(self):
  self.ready();a=self.f.reserve(n.CONDITIONS[0]);r=self.f.data['runs'][a['run_key']]
  for field in ('cpu_units','memory_bytes','disk_growth_bytes','disk_floor_bytes','monitor_reserve_bytes','policy_id'):
   before=r[field];r[field]=0 if type(before) is int else 'OTHER'
   with self.subTest(field=field),self.assertRaisesRegex(ValueError,'resource reservation changed'):self.f.check()
   r[field]=before

if __name__=='__main__':unittest.main(verbosity=2)
