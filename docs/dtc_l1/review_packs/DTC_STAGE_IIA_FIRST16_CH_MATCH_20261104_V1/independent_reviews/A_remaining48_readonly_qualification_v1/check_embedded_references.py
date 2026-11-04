from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;plan=json.loads((O/'REMAINING48_PLAN_IDENTITIES.json').read_text());ev=json.loads((O/'QUALIFICATION_EVIDENCE.json').read_text());q=json.loads((O/'CPU_READONLY_QUALIFICATION.json').read_text());spec={r['path']:r for r in ev['old_specs72']};checks=[]
for row in plan['candidates48']:
 cfg=ev['config_profiles'][row['config_profile_reference']]['configs'];assert len(cfg)==4
 for x in cfg:
  p=O/x['readonly_plan_copy'];assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'];checks.append(row['plan_candidate_id']+'_config_reference_'+p.name)
 for role,key in row['old_spec_keys'].items():
  z=spec[key];want=('CH','P0')if role=='original_parent_spec'else('DH',row['profile']);assert(z['cell'],z['profile'])==want;checks.append(row['plan_candidate_id']+'_'+role+'_cell_profile')
q['checks']+=checks;q['loop_assertions']=len(q['checks']);q['additional_embedded_config_reference_checks']=192;q['additional_old_spec_role_profile_checks']=96;(O/'CPU_READONLY_QUALIFICATION.json').write_text(json.dumps(q,ensure_ascii=False,indent=2,sort_keys=True)+'\n');print(q['loop_assertions'])
