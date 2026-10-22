from pathlib import Path
import difflib,json,hashlib,subprocess
R=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1');S=R/'util/ep_l2/mechanism_e';O=Path(__file__).parent
names=['coordinator.py','workload_policy.py','limits_policy.py','policy_v2.py','runner.py','controller.py']
def replace(s,a,b):
 assert a in s,a
 return s.replace(a,b,1)
patches=[]
for name in names:
 old=(S/name).read_text();s=old
 if name=='workload_policy.py':
  s=replace(s,'import copy\n','import copy\nimport detach_diagnostic_policy as detach_policy\n')
  s=replace(s,"    attempts=item['attempts'][46:]\n", "    if len(item['attempts'])>50:\n        require(detach_policy.active(item),'post50 requires exact new observer adoption')\n    attempts=item['attempts'][46:50]\n")
 if name=='limits_policy.py':
  s=replace(s,'import copy\n','import copy\nimport detach_diagnostic_policy as detach_policy\n')
  for func,call in [('scope_allowed','scope_allowed'),('effective_timeout','effective_timeout'),('assert_condition_unstarted','batch_guard')]:
   s=replace(s,f'def {func}(item,spec):\n',f'def {func}(item,spec):\n    if detach_policy.is_spec(spec):return detach_policy.{call}(item,spec)\n')
 if name=='policy_v2.py':
  s=replace(s,'import capacity_policy\n','import capacity_policy\nimport detach_diagnostic_policy as detach_policy\n')
  s=replace(s,"    bucket = attempt['budget_bucket']\n", "    bucket = attempt['budget_bucket']\n    if attempt.get('scientific_scope')==detach_policy.SCI_SCOPE and attempt.get('diagnostic_spec_sha256'):\n        return bucket  # Independently validated exact observer batch, never contingency\n")
  s=replace(s,'def condition_check(item,spec,digest):\n','def condition_check(item,spec,digest):\n    if detach_policy.is_spec(spec):return detach_policy.condition_check(item,spec,digest)\n')
  s=replace(s,'def combination_qualification(q, digest):\n','def combination_qualification(q, digest):\n    if q.get("detach_observer_diagnostic") is not None:return detach_policy.qualification(q,digest)\n')
 if name=='coordinator.py':
  s=replace(s,'import policy_v2\n','import policy_v2\nimport detach_diagnostic_policy as detach_policy\n')
  s=replace(s,"    workload_policy.active(item)  # exact optional approved four-start workload batch\n", "    detach_policy.active(item)  # Exact optional successor; original50 and old batches sealed\n    workload_policy.active(item)  # exact optional approved four-start workload batch\n")
  marker='    def bind_capacity_runtime(self, qualification_id):\n'
  methods='''    def adopt_detach_observer_batch(self):
        """Append only root-sealed observer scope under original lock; no new scheduler."""
        with self.locked() as (data,item):
            own_scientific = [r for r in data['runs'].values()
                if r.get('experiment_id')==CAMPAIGN and r.get('status') in ACTIVE]
            source_leases = [r for r in data['resource_leases'].values()
                if r.get('experiment_id')==CAMPAIGN and (r.get('role')=='E' or r.get('owner')=='mechanism_E')
                and r.get('status') in ACTIVE]
            require(not own_scientific,'own scientific application must retire before source adoption')
            changed=detach_policy.adopt(item,source_leases)
            counts(item)
            return dict(changed=changed,actual_starts=item['actual_starts'],t0_unix=item['t0_unix'])

    def bind_detach_observer_condition(self, spec):
        with self.locked() as (data,item):
            self.require_no_hold(item,spec['qualification_id'])
            return detach_policy.bind_condition(item,spec,digest)

'''
  s=replace(s,marker,methods+marker)
  s=replace(s,"            if workload_policy.is_workload_spec(spec):workload_policy.batch_guard(item,spec)\n            else:capacity_policy.bucket_guard(item,spec)\n", "            if detach_policy.is_spec(spec):detach_policy.batch_guard(item,spec)\n            elif workload_policy.is_workload_spec(spec):workload_policy.batch_guard(item,spec)\n            else:capacity_policy.bucket_guard(item,spec)\n")
  s=replace(s,"            if workload_policy.is_workload_spec(spec):\n                workload_policy.batch_guard(item,spec)\n", "            if detach_policy.is_spec(spec):\n                detach_policy.batch_guard(item,spec)\n            elif workload_policy.is_workload_spec(spec):\n                workload_policy.batch_guard(item,spec)\n")
  s=replace(s,"            if workload_policy.is_workload_spec(spec):workload_policy.record_reservation(item,spec,row)\n", "            if detach_policy.is_spec(spec):detach_policy.record_reservation(item,spec,row)\n            elif workload_policy.is_workload_spec(spec):workload_policy.record_reservation(item,spec,row)\n")
  s=replace(s,"            counts(item)\n            write_json(self.registry.root/'RUN_REGISTRY.json',data)\n            write_json(self.handoff/'RUN_LEDGER.json',item)\n            if hasattr(process,'release'):process.release()", "            if attempt.get('scientific_scope')==detach_policy.SCI_SCOPE:\n                detach_policy.record_started(item,attempt)\n            counts(item)\n            write_json(self.registry.root/'RUN_REGISTRY.json',data)\n            write_json(self.handoff/'RUN_LEDGER.json',item)\n            if hasattr(process,'release'):process.release()")
  s=replace(s,"                    'run_key':attempt['run_key'],'identity':attempt['identity'],'qualification_id':attempt['qualification_id']}\n", "                    'run_key':attempt['run_key'],'identity':attempt['identity'],'qualification_id':attempt['qualification_id']}\n                if attempt.get('scientific_scope')==detach_policy.SCI_SCOPE:\n                    item['accepted_results'][attempt_id]['scientific_scope']=detach_policy.SCI_SCOPE\n")
 if name=='runner.py':
  s=replace(s,'import durable_exit\n','import durable_exit\nimport detach_diagnostic_policy as detach_policy\nimport detach_validation\n')
  s=replace(s,"    q=qrow['qualification'];contract=q.get('capacity_diagnostic')\n", "    q=qrow['qualification'];contract=q.get('capacity_diagnostic')\n    if detach_policy.is_spec(spec) or q.get('detach_observer_diagnostic') is not None:\n        return detach_validation.validate_summary(summary,spec,qrow,audit)\n    require(summary.get('diagnostic_scope')!=detach_policy.SCI_SCOPE,'observer summary cannot use legacy validator')\n")
  s=replace(s,"    started=time.monotonic()\n", "    if detach_policy.is_spec(spec):result['scientific_scope']=detach_policy.SCI_SCOPE\n    started=time.monotonic()\n")
  s=replace(s,"            coord.require_no_hold(item,record['qualification_id'])\n", "            require(record.get('scientific_scope')!=detach_policy.SCI_SCOPE,'observer diagnostic point cannot be S/F pair')\n            coord.require_no_hold(item,record['qualification_id'])\n")
 if name=='controller.py':
  s=replace(s,'import durable_exit\n','import durable_exit\nimport detach_diagnostic_policy as detach_policy\n')
  s=replace(s,"        pending=[];snapshot=coord.snapshot()\n", "        pending=[];snapshot=coord.snapshot()\n        detach_policy.queue_guard(snapshot,queue,digest)\n")
 if name=='coordinator.py':
  s=replace(s,"    detach_policy.active(item)  # Exact optional successor; original50 and old batches sealed\n", "    detach_policy.active(item)  # Exact optional successor; original50 and old batches sealed\n    detach_policy.crosscheck_data(data,item)\n")
  s=replace(s,"            counts(item)\n            write_json(self.handoff/'RUN_LEDGER.json',item)\n", "            counts(item)\n            detach_policy.crosscheck_data(data,item)\n            write_json(self.handoff/'RUN_LEDGER.json',item)\n")
  s=replace(s,"disk_floor_bytes=None, monitor_reserve_bytes=None,disk_draw_bytes=None):\n    item=ledger(data)\n", "disk_floor_bytes=None, monitor_reserve_bytes=None,disk_draw_bytes=None,authority_data=None):\n    if authority_data is not None:\n        require(data[FIELD]==authority_data[FIELD] and data['resource_leases']==authority_data['resource_leases'],\n                'resource recheck view must preserve canonical campaign/leases')\n        removed=set(authority_data['runs'])-set(data['runs'])\n        require(len(removed)==1 and not set(data['runs'])-set(authority_data['runs']) and\n                all(row==authority_data['runs'][key] for key,row in data['runs'].items()),\n                'resource recheck may exclude only its one held reservation')\n        oldrow=authority_data['runs'][next(iter(removed))]\n        require(oldrow.get('experiment_id')==CAMPAIGN and oldrow['status']=='RESERVED',\n                'resource recheck must exclude one own RESERVED run')\n    item=ledger(data if authority_data is None else authority_data)\n")
  s=replace(s,"                          monitor_reserve_bytes=row['monitor_reserve_bytes'])\n", "                          monitor_reserve_bytes=row['monitor_reserve_bytes'],authority_data=data)\n")
  s=replace(s,"            return row\n\n    def start_application", "            if detach_policy.is_spec(spec):\n                data['runs'][key].update(scientific_scope=detach_policy.SCI_SCOPE,\n                    diagnostic_spec_sha256=detach_policy.spec_sha(spec),condition_id=spec['condition_id'],\n                    qualification_id=spec['qualification_id'],budget_bucket=spec['budget_bucket'])\n            detach_policy.crosscheck_data(data,item)\n            return row\n\n    def start_application")
 (O/name).write_text(s)
 patches.extend(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='a/util/ep_l2/mechanism_e/'+name,tofile='b/util/ep_l2/mechanism_e/'+name))
(O/'MINIMAL_PATCH.diff').write_text(''.join(patches))
core=Path('/tmp/e2_detach_central_candidate/detach_diagnostic_policy.py').read_text();core=core[:core.index('    def reserve_synthetic(')]
(O/'detach_scope_core.py').write_text(core+'\n')
schema=subprocess.check_output(['git','show','0ef8b65971f8a853d29b6cea1074c08d004727d5:docs/ep_l2/review_packs/MS20261022_A2_DETACH_OBSERVER_PRODUCER_r1/COUNTER_SCHEMA.json'],cwd=R)
(O/'A2_COUNTER_SCHEMA_EARLY.json').write_bytes(schema)
(O/'SOURCE_BASELINE.json').write_text(json.dumps({'original_files':{n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in names},'actual_A2_schema_commit':'0ef8b65971f8a853d29b6cea1074c08d004727d5','A2_schema_sha256':hashlib.sha256(schema).hexdigest()},indent=2)+'\n')
