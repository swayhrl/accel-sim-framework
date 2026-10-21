from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
SRC=ROOT/'util/ep_l2/mechanism_e'
DST=HERE/'candidate'
# Copy only the three production modules requiring minimal edits.
for name in ('limits_policy.py','policy_v2.py','coordinator.py'):
 s=(SRC/name).read_text()
 if name=='limits_policy.py':
  s=s.replace('import copy\n','import copy\nimport workload_policy\n',1)
  s=s.replace('def scope_allowed(item,spec):\n','def scope_allowed(item,spec):\n    if workload_policy.is_workload_spec(spec):return workload_policy.scope_allowed(item,spec)\n',1)
  s=s.replace('def effective_timeout(item,spec):\n','def effective_timeout(item,spec):\n    if workload_policy.is_workload_spec(spec):return workload_policy.effective_timeout(item,spec)\n',1)
  s=s.replace('def assert_condition_unstarted(item,spec):\n','def assert_condition_unstarted(item,spec):\n    if workload_policy.is_workload_spec(spec):return workload_policy.assert_condition_unstarted(item,spec)\n',1)
 if name=='policy_v2.py':
  s=s.replace('import capacity_policy\n','import capacity_policy\nimport workload_policy\n',1)
  s=s.replace('    bucket = attempt[\'budget_bucket\']\n', "    bucket = attempt['budget_bucket']\n    if attempt.get('condition_id') in workload_policy.CONDITIONS and bucket==workload_policy.CONDITIONS[attempt['condition_id']][0] and attempt.get('workload_spec_sha256'):\n        return bucket  # approved independent batches never consume old contingency\n",1)
  s=s.replace('def condition_check(item,spec,digest):\n','def condition_check(item,spec,digest):\n    if workload_policy.is_workload_spec(spec):\n        return workload_policy.condition_check(item,spec,digest)\n',1)
 if name=='coordinator.py':
  s=s.replace('import limits_policy\n','import limits_policy\nimport workload_policy\n',1)
  s=s.replace('    concurrency_policy.active(item)  # exact optional user concurrency amendment\n','    workload_policy.active(item)  # exact optional approved four-start workload batch\n    concurrency_policy.active(item)  # exact optional user concurrency amendment\n',1)
  marker='    def bind_capacity_runtime(self, qualification_id):\n'
  methods='''    def adopt_workload_pipeline(self, approval_path):
        """Append the exact user-approved four-start scope under the original lock."""
        with self.locked() as (data,item):
            require(not any(r.get('experiment_id')==CAMPAIGN and r['status'] in ACTIVE
                    for group in ('runs','resource_leases') for r in data[group].values()),
                    'campaign work must retire before workload source adoption')
            changed=workload_policy.amend(item,approval_path,time.time())
            counts(item)
            return dict(changed=changed,actual_starts=item['actual_starts'],
                        t0_unix=item['t0_unix'],approval=workload_policy.approval_ref())

    def bind_workload_condition(self, spec):
        """Only append a sealed independent condition; never overwrite a binding."""
        with self.locked() as (data,item):
            self.require_no_hold(item,spec['qualification_id'])
            return workload_policy.bind_condition(item,spec,digest)

    def adopt_workload_selection(self, selection_path):
        """Approved independent SGEMM adoption; preserve all original D selections."""
        raw=Path(selection_path).read_bytes();selection=json.loads(raw)
        with self.locked() as (data,item):
            return workload_policy.adopt_selection(item,selection_path,raw,selection,digest)

'''
  assert marker in s;s=s.replace(marker,methods+marker,1)
  s=s.replace("            capacity_policy.bucket_guard(item,spec)\n", "            if workload_policy.is_workload_spec(spec):workload_policy.batch_guard(item,spec)\n            else:capacity_policy.bucket_guard(item,spec)\n",1)
  old="""            bucket=spec['budget_bucket'];require(bucket in item['reservations'],'unknown reserved budget bucket')
            used=sum(policy_v2.charged_bucket(a,item['reservations'])==bucket and
                     (a.get('actual_start') or a['state'] in ('RESERVED','START_INTENT_UNRECONCILED')) for a in item['attempts'])
            require(limits_policy.scope_allowed(item,spec) or used<item['reservations'][bucket],
                    'reserved matrix budget exhausted; preserve other controls')
"""
  new="""            bucket=spec['budget_bucket']
            if workload_policy.is_workload_spec(spec):
                workload_policy.batch_guard(item,spec)
            else:
                require(bucket in item['reservations'],'unknown reserved budget bucket')
                used=sum(policy_v2.charged_bucket(a,item['reservations'])==bucket and
                         (a.get('actual_start') or a['state'] in ('RESERVED','START_INTENT_UNRECONCILED')) for a in item['attempts'])
                require(limits_policy.scope_allowed(item,spec) or used<item['reservations'][bucket],
                        'reserved matrix budget exhausted; preserve other controls')
"""
  assert old in s;s=s.replace(old,new,1)
  s=s.replace("            item['attempts'].append(row)\n", "            if workload_policy.is_workload_spec(spec):workload_policy.record_reservation(item,spec,row)\n            item['attempts'].append(row)\n",1)
 (DST/name).write_text(s)
