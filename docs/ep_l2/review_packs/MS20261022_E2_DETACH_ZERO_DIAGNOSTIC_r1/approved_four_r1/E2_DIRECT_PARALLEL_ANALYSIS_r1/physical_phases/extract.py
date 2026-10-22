#!/usr/bin/env python3
"""Small accepted-metadata projection only. Never reads raw/trace or central APIs."""
import csv, hashlib, json
from pathlib import Path
P=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1/approved_four_r1')
OUT=Path('/tmp/e2_parallel_phase_matrix_r1')
NAMES=('cfd_097k','dwt2d','vectorAdd_4M')
checks=[]
def ck(ok,label):
 checks.append({'check':label,'pass':bool(ok)})
 if not ok: raise ValueError(label)
def ref(p):return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def ratio(n,d):return None if d==0 else n/d
def share(n,d):return {'numerator':n,'denominator':d,'ratio':ratio(n,d),'state':'NA_ZERO_POPULATION' if d==0 else 'MEASURED_SAME_FIELD_EXPOSURE_SHARE'}
source=P/'analysis_r1/terminal_analysis.py'
source_ref=ref(source)
ck(source_ref['sha256']=='208db865c25b9e7e850ab0db743ed10043286b2c1370168ae5f621c933418bc7','reviewed terminal analysis exact final source')
rows=[]; docs={}; provenance=[]; fields=None; contracts={}; exposure_fields=('observed_heads','probed_heads','probe_skipped','requester_ro_candidate','ro_admits','ro_merges','commit_raw_probe_reached','raw_reservation_fail','raw_tag_fail_commit')
for w in NAMES:
 path=P/'results'/w/'INDEPENDENT_TERMINAL_AND_CAUSE_REVIEW.json';before=ref(path);d=json.loads(path.read_text());provenance.append(before)
 ck(d['status']=='INDEPENDENT_REVIEW_OF_EXISTING_CENTRAL_ACCEPTANCE_PASS',w+' accepted independent review')
 ck(d['attempt_id']=={'cfd_097k':'E052_781ed6b2','dwt2d':'E053_14cc809a','vectorAdd_4M':'E054_e4a9813e'}[w],w+' exact accepted attempt')
 g=d['observer_global']['counts']; f=list(g)
 ck(len(f)==212,w+' exact212')
 ck(all(type(v) is int and 0<=v<2**64 for v in g.values()),w+' global uint64 not bool')
 if fields is None: fields=f
 ck(f==fields,w+' same212 order')
 ck(d['actual_fixeddecoder']['schema_fields']==212,w+' existing fixed212 decode')
 ck(len(d['observer_slice_counters'])==64,w+' slice64')
 for k in fields:ck(sum(s[k] for s in d['observer_slice_counters'].values())==g[k],w+' global/slice/'+k)
 phases=d['phase_projection']['rows']; expected={str(x) for x in range(2+len(d['fullkernel_uids']))};ck(set(phases)==expected,w+' exact phases incl UNASSIGNED/OVERLAP_UNKNOWN')
 for k in fields:ck(sum(v['global_samephase_counters'][k] for v in phases.values())==g[k],w+' global/phase/'+k)
 for v in phases.values():
  c=v['global_samephase_counters']; panel=v['global_panels']; phase=v['phase']
  ck(len(v['slice_counters'])==64,w+f' phase{phase}64slice')
  ck(set(c)==set(fields) and all(type(x) is int and 0<=x<2**64 for x in c.values()),w+f' phase{phase}exactuint64')
  ck(not panel['errors'] and panel['derived']['terminal_detached_residual'] is None,w+f' phase{phase}populationNA')
  ck(panel['phase_population_state']['terminal_detached_residual']=='NA_NOT_A_PHASE_LOCAL_POPULATION',w+f' phase{phase}populationNAstate')
  ck(v['oldaccepted_RO_perphase']=='UNKNOWN_NOT_EMITTED_DO_NOT_APPORTION',w+f' phase{phase}oldROunknown')
  for k in fields:ck(sum(s[k] for s in v['slice_counters'].values())==c[k],w+f' phase{phase}/slice/'+k)
  r={'workload':w,'attempt_id':d['attempt_id'],'phase':phase,'kernel_uid':v['kernel_uid'],'kernel_scope':v['kernel_scope'],**c,'probed_heads':c['observed_heads']-c['probe_skipped'],'oldaccepted_RO_perphase':v['oldaccepted_RO_perphase'],'phase_live_detached':None,'phase_live_detached_state':'NA_NOT_A_PHASE_LOCAL_POPULATION'}
  r['exposure_shares']={k:share(r[k],g[k] if k in g else g['observed_heads']-g['probe_skipped']) for k in exposure_fields}
  rows.append(r)
  for item in panel['rows']:
   m=item['metric']; desc={k:item[k] for k in ('domain','unit','denominator_metric','note')};ck(m not in contracts or contracts[m]==desc,'stable metric contract/'+m);contracts[m]=desc
 ranks={}
 for key in exposure_fields:
  population=g[key] if key in g else g['observed_heads']-g['probe_skipped']
  ranks[key]={'population':population,'state':'NA_ZERO_POPULATION' if population==0 else 'RANKED_EXPOSURE_COUNTS_NOT_RUNTIME_SHARE','phases':[{'phase':r['phase'],'kernel_uid':r['kernel_uid'],'value':r[key],**r['exposure_shares'][key]} for r in sorted([x for x in rows if x['workload']==w],key=lambda x:(-x[key],x['phase'])) if r[key]>0]}
 docs[w]={'attempt_id':d['attempt_id'],'status':d['status'],'scientific_scope':d['scientific_scope'],'pair':d['pair'],'fullinstructions':d['fullinstructions'],'cycles':d['cycles'],'fullkernel_uids':d['fullkernel_uids'],'source_identity':d['source_identity'],'identity':d['identity'],'qualification_id':d['qualification_id'],'accepted_pointer':d['evidence']['central_accepted_pointer'],'raw_provenance_from_accepted_metadata_only_not_opened':d['evidence']['raw'],'oldmodel_global_only':d['authoritative_oldmodel_RO']['global'],'global_counts':g,'global_probed_heads':g['observed_heads']-g['probe_skipped'],'global_metric_panels':d['observer_global']['rows'],'ranked_exposures':ranks,'phase_semantics':d['phase_projection']['semantics'],'existing_measured_facts':d['conditional_measured_facts'],'existing_interpretation_limits':d['interpretation_limits']}
 ck(ref(path)==before,w+' source metadata stable read')
ck(ref(source)==source_ref,'analysis source stable read')
limits=[
 'Only already accepted CFD E052, DWT E053 and Vector E054 metadata. Conv remains active/not represented as accepted.',
 'Physical active-kernel phase labels are event-time state buckets, never requester/victim causal kernel ownership; exposure shares are not walltime or criticalpath shares.',
 'All212 source-emitted phase counters are copied. No raw/trace body opened or rescanned. Global/slice and phase/slice same-field rollups checked only on existing metadata.',
 'Observed/probed headphysicalcycles, actual commit probes, transaction creations, merged requesters, responses, packets and sectors remain different domains.',
 'TVD-skipped raw probes are NA, never zero-filled; raw outcome zero only applies to covered probes, not globally sufficient Tags.',
 'Live-victim/eligibility/way/reuse/preview-relief funnel pressure fields zero with rawpressure population0 are NOT_EXERCISED, not proof that no liveRO or reuse existed.',
 'Oldmodel accepted RO per phase remains UNKNOWN_NOT_EMITTED_DO_NOT_APPORTION. Observer phase ro_admits/ro_merges are measured event counts; no old acceptedRO apportionment.',
 'Phase success-minus-retire difference is not a phase-local live population; phase_live_detached is explicit NA even if difference nonnegative. Global terminal population remains separate.',
 'Capacity notconsulted/unobserved/lineNA are not capacity pass/fail; lineNA subset cannot be double counted. No marginal rate products or invented head-to-commit joins.',
 'No oldmain61 dynamic backfill, S/F speedup, new S anchor, isolated T benefit, or accepted-result/qualification changes.'
]
out={'schema':'E2_ACCEPTED_CFD_DWT_VECTOR_PHYSICAL_PHASE_EXPOSURE_MATRIX_R1','status':'READONLY_ACCEPTED_METADATA_PROJECTION_COMPLETE_NOT_NEW_QUALIFICATION','source_refs':provenance+[source_ref],'workloads':docs,'phase_rows':rows,'metric_contracts':contracts,'limits':limits}
(OUT/'PHASE_MATRIX.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
with (OUT/'PHASE_ALL212.csv').open('w',newline='') as fp:
 names=['workload','attempt_id','phase','kernel_uid','kernel_scope']+fields+['probed_heads','oldaccepted_RO_perphase','phase_live_detached_state']
 wr=csv.DictWriter(fp,fieldnames=names,extrasaction='ignore');wr.writeheader();wr.writerows(rows)
focus=['observed_heads','probe_skipped','probed_heads','raw_hit','raw_hit_reserved','raw_miss','raw_reservation_fail','raw_sector_miss','requester_ro_candidate','certified_resident_hits','candidate_deferred_or_native','ro_capacity_consulted','ro_capacity_not_consulted','ro_admits','ro_merges','ro_retired','commit_raw_probe_reached','raw_tag_fail_commit','relieve_calls','detach_calls','detach_success','detached_retired']
with (OUT/'PHASE_FOCUS.csv').open('w',newline='') as fp:
 names=['workload','attempt_id','phase','kernel_uid','kernel_scope']+focus+[k+'_share' for k in exposure_fields]+['oldaccepted_RO_perphase','phase_live_detached_state']
 wr=csv.DictWriter(fp,fieldnames=names,extrasaction='ignore');wr.writeheader()
 for r in rows:wr.writerow({**r,**{k+'_share':v['ratio'] for k,v in r['exposure_shares'].items()}})
(OUT/'CHECKS.json').write_text(json.dumps({'check_count':len(checks),'passed':sum(x['pass'] for x in checks),'failed':sum(not x['pass'] for x in checks),'failures':[x for x in checks if not x['pass']],'coverage':['source digest and stable read','exact accepted attempt/status','uint64 nonbool','global64slice rollups all212','globalphase rollups all212','phase64slice rollups all212','phase population NA','oldmodel perphase UNKNOWN','same metric contract across phases']},indent=2)+'\n')
print(json.dumps({'status':out['status'],'phase_rows':len(rows),'all212_samefield_checks':len(checks),'failed':sum(not x['pass'] for x in checks),'files':{n:ref(OUT/n) for n in ('PHASE_MATRIX.json','PHASE_ALL212.csv','PHASE_FOCUS.csv','CHECKS.json')}}))
