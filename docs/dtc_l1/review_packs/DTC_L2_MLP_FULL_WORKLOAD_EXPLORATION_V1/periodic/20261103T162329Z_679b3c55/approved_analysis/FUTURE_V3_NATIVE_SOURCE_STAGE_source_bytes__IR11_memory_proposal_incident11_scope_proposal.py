"""Pure exact11 recovery memory-scope proposal; no registration or install."""
import copy
ROLE='INCIDENT_RECOVERY_PERFORMANCE_TRIAL'
def propose_scope_append(oldcfg,q,incident_scope,contract,matrix,scope,canonical,lib):
 lib.validate(oldcfg,q);incident_scope.check_primary(matrix,scope)
 assert contract['scientific_role']==ROLE and contract['primary_statistics_excluded']is True
 assert contract['validated_union_authorized']is False
 assert contract['role_does_not_authorize_aging_fence_bypass']is True
 assert set(contract['scope_cohorts'])==set(incident_scope.rows)and len(incident_scope.rows)==11
 assert contract['incident_id']==incident_scope.plan['incident_id']
 for c in incident_scope.rows:
  spec,h=canonical(c);incident_scope.validate(c,spec,h,q)
  assert c not in q['consumed']and c not in q.get('sealed',[])
  assert contract['scope_cohorts'][c]==incident_scope.authorization_record(c)
 added=sorted(set(incident_scope.rows)-set(oldcfg['allowed_cohorts']))
 assert len(added)==11,'EXACT11_NOT_NEW_UNSPENT_SCOPE'
 new=copy.deepcopy(oldcfg);new['allowed_cohorts']+=added
 newq=copy.deepcopy(q);oldrow=copy.deepcopy(q['additional_operational_overlays'][lib.ID])
 newrow=copy.deepcopy(oldrow);newrow.update(lib.record(new))
 newq['additional_operational_overlays'][lib.ID]=newrow;lib.validate(new,newq)
 assert {k:v for k,v in new.items()if k!='allowed_cohorts'}=={k:v for k,v in oldcfg.items()if k!='allowed_cohorts'}
 return dict(schema='INCIDENT_RECOVERY_EXACT11_CPU2_SCOPE_APPEND_PROPOSAL_V1',old_config=copy.deepcopy(oldcfg),new_config=new,old_full_record=oldrow,new_full_record=newrow,added_cohorts=added,config_only_field='allowed_cohorts',grant_changes=0,production_changes=0)
