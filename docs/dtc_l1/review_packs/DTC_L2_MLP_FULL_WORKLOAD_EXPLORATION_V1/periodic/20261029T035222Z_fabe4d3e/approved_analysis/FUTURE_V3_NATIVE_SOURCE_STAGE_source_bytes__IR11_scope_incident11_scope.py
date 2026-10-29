"""Pure incident-recovery runtime view; never installs/registers/selects work."""
import copy,hashlib,json
ROLE='INCIDENT_RECOVERY_PERFORMANCE_TRIAL'
MARKER='incident_recovery_trial_dispatch_view_v1'
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
class IncidentScope:
 def __init__(self,plan,legacy_nonprimary_cohorts):
  self.plan=copy.deepcopy(plan);self.rows={x['new_cohort']:x for x in plan['rows']};self.keys=tuple(plan['science_projection_keys']);self.legacy=set(legacy_nonprimary_cohorts)
  assert plan['scientific_role']==ROLE and len(self.rows)==len(plan['rows'])==11
  assert len({x['original_cohort']for x in self.rows.values()})==11 and not self.legacy&set(self.rows)
  assert plan['contract']['primary_statistics_excluded']is True and plan['contract']['validated_union_authorized']is False
  self.plan_sha=digest(plan)
 def authorization_record(self,c):
  r=self.rows[c]
  return dict(cohort=c,role=ROLE,incident_id=self.plan['incident_id'],original_cohort=r['original_cohort'],original_uuid=r['original_uuid'],original_negative_RESULT_sha256=r['original_negative_RESULT_sha256'],original_DONE_sha256=r['original_DONE_sha256'],science_projection_sha256=r['science_projection_sha256'],primary_statistics_excluded=True,validated_union_authorized=False)
 def check_primary(self,matrix,scope):
  for v in [matrix,scope]:
   points=v['points'];assert len({x['cohort']for x in points})==len(points)
   assert not set(self.rows)&{x['cohort']for x in points},'INCIDENT_PRIMARY_MATRIX_NONFINAL_HOLD'
   assert all(x.get('scientific_role')is None for x in points),'UNKNOWN_OR_SUPPLEMENTAL_PRIMARY_ROLE_NONFINAL_HOLD'
  return True
 def validate(self,c,spec,canonical_sha,q):
  r=self.rows[c];assert spec['cohort']==c and spec['scientific_role']==ROLE and spec['host_cpu']is None
  assert spec['request']==q['request']and q['admitted_specs'][c]==canonical_sha
  assert digest({k:spec[k]for k in self.keys})==r['science_projection_sha256'],'INCIDENT_SCIENCE_PROJECTION_DRIFT'
  lineage=spec['incident_recovery_trial_lineage'];expected=self.authorization_record(c)
  for k in ['incident_id','original_cohort','original_uuid','original_negative_RESULT_sha256','original_DONE_sha256','science_projection_sha256','primary_statistics_excluded','validated_union_authorized']:assert lineage[k]==expected[k],k
  for k in ['original_pid','original_start_ticks','original_raw_sha256','original_SOURCE_KEEP','original_performance_accepted']:assert lineage[k]==r[k],k
  original_spec=next(x['sha256']for x in r['original_sources']if x['path'].endswith('/ORIGINAL_CANONICAL_SPEC.json'))
  assert lineage['original_canonical_spec_sha256']==original_spec
  assert lineage['reuse_old_UUID']is False and lineage['automatic_retry']is False and lineage['refunds']==0 and lineage['new_grants']==1
  grants=q.get('authorized_incident_recovery_trials',[]);assert len(grants)==11 and {x['cohort']for x in grants}==set(self.rows),'EXACT11_AUTHORIZATION_REQUIRED'
  auth=next(x for x in grants if x['cohort']==c);assert all(auth.get(k)==v for k,v in expected.items()),'INCIDENT_AUTHORIZATION_MAPPING_DRIFT'
  # Initial DRAFT full SHA is provenance only. Only current authoritative SHA
  # above plus invariant science/lineage binds legitimate RSS/limit refreshes.
  return dict(cohort=c,role=ROLE,canonical_sha256=canonical_sha,original_cohort=r['original_cohort'],original_uuid=r['original_uuid'],original_negative_RESULT_sha256=r['original_negative_RESULT_sha256'],science_projection_sha256=r['science_projection_sha256'])
 def check_previous(self,previous,matrix):
  assert MARKER not in previous
  primary={x['cohort']for x in matrix['points']};points=previous['points'];assert len({x['cohort']for x in points})==len(points)
  for p in points:
   c=p['cohort'];role=p.get('scientific_role');assert c not in self.rows and c in primary|self.legacy,'UNKNOWN_RUNTIME_IDENTITY_NONFINAL_HOLD'
   assert role is None if c in primary else role in[None,'ENGINEERING_OBSERVATION_CANARY','SUPPLEMENTAL_NEW_PERFORMANCE_TRIAL'],'UNKNOWN_RUNTIME_ROLE_NONFINAL_HOLD'
  return True
 def dispatch_view(self,previous,matrix,scope,q,canonical):
  self.check_primary(matrix,scope);self.check_previous(previous,matrix);result=copy.deepcopy(previous);checked=[]
  assert set(self.rows)<=set(q['admitted_specs']),'EXACT11_NOT_REGISTERED'
  for c,r in self.rows.items():
   spec,h=canonical(c);checked.append(self.validate(c,spec,h,q))
   result['points'].append(dict(cohort=c,input_digest=spec['input_digest'],program=spec['program'],suite=spec['suite'],profile=spec['profile'],cell=spec['cell'],scientific_role=ROLE,primary_statistics_excluded=True,validated_union_authorized=False))
  result[MARKER]=dict(schema='INCIDENT_RECOVERY_DISPATCH_ONLY_VIEW_V1',plan_semantic_sha256=self.plan_sha,previous_view_semantic_sha256=digest(previous),cohorts=checked,primary_statistics_excluded=True,validated_union_authorized=False)
  return result
 def primary_view(self,view,matrix,scope,q,canonical):
  self.check_primary(matrix,scope);meta=view[MARKER];assert meta['schema']=='INCIDENT_RECOVERY_DISPATCH_ONLY_VIEW_V1'and meta['plan_semantic_sha256']==self.plan_sha
  assert meta['primary_statistics_excluded']is True and meta['validated_union_authorized']is False
  expected={x['cohort']:x for x in meta['cohorts']};assert len(expected)==11 and set(expected)==set(self.rows)
  result=copy.deepcopy(view);kept=[];seen=set()
  for point in result['points']:
   c=point['cohort']
   if c in self.rows:
    assert point['scientific_role']==ROLE and point['primary_statistics_excluded']is True and point['validated_union_authorized']is False and c not in seen
    spec,h=canonical(c);assert self.validate(c,spec,h,q)==expected[c];seen.add(c)
   else:
    assert point.get('scientific_role')!=ROLE,'UNKNOWN_INCIDENT_ROLE_NONFINAL_HOLD';kept.append(point)
  assert seen==set(self.rows);result['points']=kept;del result[MARKER]
  assert digest(result)==meta['previous_view_semantic_sha256'],'PRIOR_RUNTIME_VIEW_MUTATED'
  self.check_previous(result,matrix);return result
 def optional_dispatch_view(self,previous,matrix,scope,q,canonical):
  try:return dict(status='PASS_OPTIONAL_INCIDENT_RUNTIME_VIEW',view=self.dispatch_view(previous,matrix,scope,q,canonical),legacy_queue_usable=True,scientific_final=False)
  except Exception as error:
   try:self.check_primary(matrix,scope);self.check_previous(previous,matrix);legacy=True
   except Exception:legacy=False
   return dict(status='OPTIONAL_INCIDENT_VIEW_NONFINAL_HOLD_LEGACY_QUEUE_CONTINUES'if legacy else'CONTAMINATED_PRIOR_VIEW_NONFINAL_HOLD',view=copy.deepcopy(previous)if legacy else None,legacy_queue_usable=legacy,scientific_final=False,error=str(error))
 def assert_primary_summary(self,summary,matrix,scope):
  self.check_primary(matrix,scope);allowed={x['cohort']for x in matrix['points']}
  def walk(v):
   if isinstance(v,dict):
    if 'cohort'in v:assert v['cohort']in allowed and v.get('scientific_role')is None,'INCIDENT_OR_UNKNOWN_PRIMARY_SUMMARY_NONFINAL_HOLD'
    assert v.get('scientific_role')!=ROLE,'INCIDENT_PRIMARY_SUMMARY_NONFINAL_HOLD'
    for x in v.values():walk(x)
   elif isinstance(v,list):
    for x in v:walk(x)
  walk(summary['table']);return True
