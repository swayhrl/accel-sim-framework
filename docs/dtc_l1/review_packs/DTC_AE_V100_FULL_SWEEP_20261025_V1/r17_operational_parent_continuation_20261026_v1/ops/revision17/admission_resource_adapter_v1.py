"""R17 parent admission only: exclude three proven departed original generations.

No scientific receipt, model, entry, registry, disk, runtime guard, floor or hard
limit changes. The frozen four-scope resource function remains the base sample.
"""
import copy,hashlib,json,pathlib
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');G=1024**3
ORIGINAL='DTC_AE_V100_FULL_SWEEP_20261025_V1';SCHEMA='DTC_FOUR_SCOPE_LATE_FAILURE_ACTUAL_RAM_KNOWN_WRITES_V1';BASE_SHA='ba8a1fa5ac798265ccae019b73e4b2dbdb118d3e97e9e3baf8dd4e58e89193f0'
ALLOWED={'E2-AEV100-09f94fcc7494a03b-CM':'df5fda68-3c3d-4b37-844f-d7ea6a1d5293','E2-AEV100-85700545918390d7-DM':'97c43b01-9628-490f-839e-4a2a8126122e','E2-AEV100-e7c791ce2e4b09ee-DM':'f6c79f5f-6b0e-42d7-a5be-c3013fa7aaba'}
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def require(ok,why):
 if not ok:raise RuntimeError(why)
def verified_departed(registry,certificate):
 """Unknown, active, re-used PID, changed receipt or claimed generations retain RAM."""
 require(certificate['schema']=='R17_THREE_DEPARTED_ORIGINAL_RAM_EVIDENCE_V1' and certificate['request']==ORIGINAL,'wrong certificate schema/request')
 require({x['cohort']:x['uuid'] for x in certificate['targets']}==ALLOWED and len(certificate['targets'])==3,'certificate allowlist changed')
 for p in certificate['forensic_pins']:require(sha(p['path'])==p['sha256'],'forensic proof changed')
 q=registry['registered_future_requests'][ORIGINAL];claims=read(T/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];valid={};retained=[]
 for target in certificate['targets']:
  c=target['cohort'];row=q['consumed'].get(c)
  if not row or row['uuid']!=target['uuid'] or 'execution_receipt' in row or c in claims:retained.append(dict(cohort=c,reason='receipt/claim/identity changed'));continue
  ip=T/'control/qualification_ledger'/(c+'.INTENT.json');out=T/'DTC/run/results'/target['uuid'];pp=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json';lp=out/'NATIVE_LAUNCH.json'
  require(str(ip)==target['intent_path'] and str(out)==target['output'],'certificate paths not exact native roots')
  require(row['intent_sha256']==target['intent_sha256']==sha(ip) and sha(pp)==target['PID_receipt_sha256'] and sha(lp)==target['launch_receipt_sha256'],'immutable native identity changed')
  intent=read(ip);pid=read(pp);launch=read(lp)
  require(intent['cohort']==c and intent['uuid']==target['uuid'] and intent['output']==str(out),'INTENT identity changed')
  require((pid['pid'],pid['start_ticks'],launch['launcher_pid'])==(target['model_pid'],target['model_start_ticks'],target['launcher_pid']),'generation binding changed')
  if ip.with_name(c+'.DONE.json').exists() or(out/'NATIVE_EXIT.json').exists():retained.append(dict(cohort=c,reason='new closure metadata requires separate review'));continue
  # Absence is deliberately stricter than !live: zombies or unrelated re-used
  # PIDs are retained rather than being treated as the departed old generation.
  if (P('/proc')/str(pid['pid'])).exists() or(P('/proc')/str(launch['launcher_pid'])).exists():retained.append(dict(cohort=c,reason='model or launcher PID currently present'));continue
  valid[c]=target['uuid']
 return valid,retained
def adjust_sample(base,spec,eligible,retained=()):
 require(base['schema']==SCHEMA,'wrong base resource semantics')
 require(spec.get('request',ORIGINAL)==ORIGINAL,'only original parent admission may be adjusted')
 entries=base['RAM_reservation_entries'];excluded=[]
 for c,uid in eligible.items():
  matching=[e for e in entries if e['request']==ORIGINAL and e['cohort']==c]
  if not matching:continue
  require(len(matching)==1,'duplicate ghost RAM entry');e=matching[0]
  require(uid==ALLOWED[c] and e['RSS_bytes']==0 and e['working_set_floor_bytes']==4*G and e['envelope_bytes']==4*G and e['additional_reserved_bytes']==4*G,'ghost entry is not exact zero-RSS4GiB initial floor')
  excluded.append(dict(cohort=c,uuid=uid,excluded_future_RAM_bytes=e['additional_reserved_bytes']))
 released=sum(e['excluded_future_RAM_bytes'] for e in excluded);projected=base['reserved_additional_live_and_candidate_RAM_bytes'];require(0<=released<=12*G and projected>=released,'RAM release exceeds certified projection')
 need=projected-released;effective=base['cgroup_effective_headroom_bytes'];passed=base['host_MemAvailable_bytes']>=64*G+need and(effective is None or effective>=48*G+need)
 result=dict(base);result['physical_RAM_pass']=passed;result['parent_admission_departed_generation_adjustment']=dict(schema='R17_PARENT_ADMISSION_EXACT_DEPARTED_RAM_ONLY_V1',prior_physical_RAM_pass=base['physical_RAM_pass'],base_projected_additional_RAM_bytes=projected,effective_projected_additional_RAM_bytes=need,excluded_future_RAM_bytes=released,excluded=excluded,retained_uncertain=list(retained),host_floor_bytes=64*G,cgroup_floor_bytes=48*G,initial_working_set_floor_bytes=4*G,lava96GiB_estimate_preserved=True,scope='ORIGINAL_NEW_ADMISSION_ONLY_NOT_FRONTEND_RUNTIME',historical_receipts_created=0,old_q_or_scientific_count_changes=0)
 return result
def make_wrapper(original,authority,certificate_path,certificate_sha256):
 """Install only in the new parent's private late module or call explicitly.

The caller must pin this source/certificate and preserve the original frontend
modules. No monkey patch or active-process operation is performed here.
"""
 require(sha(original.__code__.co_filename)==BASE_SHA,'frozen base resource function changed')
 def resources(spec,fresh_source=False):
  base=original(spec,fresh_source)
  if not fresh_source or spec.get('request',ORIGINAL)!=ORIGINAL:return base
  try:
   require(sha(certificate_path)==certificate_sha256,'certificate SHA changed');certificate=read(certificate_path);eligible,retained=verified_departed(authority()[0],certificate);return adjust_sample(base,spec,eligible,retained)
  except (OSError,ValueError,KeyError,RuntimeError) as error:
   # A missing or changed proof never releases RAM. Preserve every original
   # gate/counter, rather than terminating the parent that guards old models.
   result=dict(base);result['parent_admission_departed_generation_adjustment']=dict(status='NO_RAM_RELEASE_UNCERTAIN_EVIDENCE',error=repr(error),excluded_future_RAM_bytes=0,host_floor_bytes=64*G,cgroup_floor_bytes=48*G);return result
 return resources
