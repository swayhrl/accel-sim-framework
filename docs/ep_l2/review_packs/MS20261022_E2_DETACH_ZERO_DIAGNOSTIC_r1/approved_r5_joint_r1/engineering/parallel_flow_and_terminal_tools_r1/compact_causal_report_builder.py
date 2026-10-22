#!/usr/bin/env python3
"""Compact read-only projection of existing independently accepted r5 metadata.
No raw/trace/binary reads, controller/registry/source writes, launches or polling.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
RAW=('HIT','HIT_RESERVED','MISS','RESERVATION_FAIL','SECTOR_MISS','MSHR_HIT','WRITE_ALLOCATED','UNKNOWN')
APP=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1/approved_r5_joint_r1');CORE=Path('/workspace/worktrees/gpgpu-sim-ep-l2-ms20261022-e2-tagpressure-r5-v1')
MANIFEST_SHA='25d1b8cf8b80d53bfe677f58d5273f35115cf40599660b1c0038a9be7ed58b69';CAP=64*2**20

def need(ok,m):
 if not ok:raise ValueError(m)
def uint(v):need(type(v)is int and 0<=v<2**64,'invalid uint64');return v
def unique(pairs):
 d={}
 for k,v in pairs:need(k not in d,'duplicate JSON key');d[k]=v
 return d
def load(p):p=Path(p);need(p.is_file()and p.stat().st_size<=CAP,'bounded metadata absent/oversized');return json.loads(p.read_bytes(),object_pairs_hook=unique)
def ref(p):p=Path(p);need(p.is_file()and p.stat().st_size<=CAP,'bounded source/ref absent/oversized');return {'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def sparse(rows,width):
 d={}
 for row in rows:
  need(isinstance(row,list)and len(row)==width,'wrong tuple width');tuple(uint(x)for x in row);key=tuple(row[:-1]);need(key not in d and row[-1]>0,'duplicate/nonpositive sparse tuple');d[key]=row[-1]
 return d

def project(g):
 """Only source-declared actual joints; no inferred combination of marginals."""
 h=g['histograms_exact_source'];H=sparse(h['heads_raw_reserved'],3);I=sparse(h['heads_raw_reserved_invalid'],4);E=sparse(h['heads_raw_reserved_eligible'],4);J=sparse(g['same_head_route_joint']['rows'],8);covered=uint(g['counts']['covered']);need(sum(H.values())==sum(I.values())==sum(J.values())==covered,'lost covered exposure population')
 for (raw,r),n in H.items():
  need(raw<8 and r<=16,'unknown raw/reserved coordinate');need(sum(v for (a,b,c),v in I.items()if(a,b)==(raw,r))==n,'invalid histogram raw/r projection differs');need(sum(v for (a,b,c,d,e,f,z),v in J.items()if(a,b)==(raw,r))==n,'requester joint raw/r projection differs')
 need(all((raw,r)in H and inv<=16-r for(raw,r,inv)in I),'invalid way population outside raw/r head scope')
 need(all((raw,r)in H and elig<=16 for(raw,r,elig)in E),'eligible population outside raw/r scope')
 raw={RAW[i]:sum(v for(a,r),v in H.items()if a==i)for i in range(8)};r16={RAW[i]:H.get((i,16),0)for i in range(8)}
 eligible_by_raw={RAW[i]:sum(v for(a,r,req,elig,route,admit,early),v in J.items()if a==i and elig==2)for i in range(8)}
 for (a,r),n in H.items():need(sum(v for(ra,rr,e),v in E.items()if(ra,rr)==(a,r)and e>0)==sum(v for(ra,rr,req,e,route,adm,early),v in J.items()if(ra,rr)==(a,r)and e==2),'eligible truejoint projection differs')
 need(sorted(g['new_tag_demand_same_head_joint'])==sorted([list(k)+[v]for k,v in J.items()if k[0]in(2,3)]),'newTag declared joint differs from exact source joint filter')
 miss_no_invalid={str(r):I.get((2,r,0),0)for r in range(17)if I.get((2,r,0),0)}
 return {'domain':'FRONTEND_HEAD_CYCLE_SAME_TARGET_SET_EXPOSURES_NOT_UNIQUE_REQUESTS','covered_head_cycle_exposures':covered,'max_RESERVED_ways_covered':max((r for a,r in H),default=None),'max_RESERVED_ways_newTag_MISS_FAIL':max((r for a,r in H if a in(2,3)),default=None),'raw_counts':raw,'r16_raw_counts':r16,'MISS_invalid0_by_RESERVED_count':miss_no_invalid,'MISS_all16_nonreserved_noninvalid_clean_or_dirty_head_cycle_exposures':I.get((2,0,0),0),'MISS_any_RESERVED_count_invalid0_head_cycle_exposures':sum(miss_no_invalid.values()),'structurally_eligible_head_cycle_exposures':sum(eligible_by_raw.values()),'structurally_eligible_by_raw':eligible_by_raw,'newTag_MISS_FAIL_certifiedRO_and_eligible_head_cycle_exposures':sum(v for(a,r,req,elig,route,admit,early),v in J.items()if a in(2,3)and req==0 and elig==2),'newTag_MISS_FAIL_true_requester_eligibility_route_joint':g['new_tag_demand_same_head_joint'],'joint_columns':g['same_head_route_joint']['columns'],'coverage':g['coverage'],'head_way_denominators':g['denominators'],'not_joined_marginals':'reason mask/wayclass/way predicate distributions are not joined to requester/route by multiplying marginals; see original independentreview exact source histograms'}

def summarize(review):
 """Pure numerical layer; caller separately binds real accepted metadata/source."""
 cause=review['cause'];G=project(cause['global']);c=cause['old212_commit_and_lifecycle'];p=[]
 for key,v in cause['physical_phases'].items():
  q=project(v);p.append({'physical_phase':int(key),'kernel_uid':v['kernel_uid'],'kernel_scope':v['kernel_scope'],'covered_head_cycle_exposures':q['covered_head_cycle_exposures'],'raw_MISS':q['raw_counts']['MISS'],'raw_FAIL':q['raw_counts']['RESERVATION_FAIL'],'max_RESERVED_covered':q['max_RESERVED_ways_covered'],'max_RESERVED_newTag_MISS_FAIL':q['max_RESERVED_ways_newTag_MISS_FAIL'],'structurally_eligible_head_cycle_exposures':q['structurally_eligible_head_cycle_exposures'],'MISS_all16_nonreserved_noninvalid_exposures':q['MISS_all16_nonreserved_noninvalid_clean_or_dirty_head_cycle_exposures'],'old_RO_phase':'UNKNOWN_NOT_EMITTED','phase_detach_minus_retire':'NA_NOT_A_PHASE_LOCAL_POPULATION'})
 need(sum(x['covered_head_cycle_exposures']for x in p)==G['covered_head_cycle_exposures'],'phase coverage rollup differs');facts=[]
 if G['covered_head_cycle_exposures']==0:facts.append('NO_COVERED_PROBES: raw/set pressure is NA for skipped paths; no global no-pressure claim.')
 elif G['raw_counts']['RESERVATION_FAIL']==0:facts.append('NO_RAW_FAIL_IN_COVERED_HEAD_CYCLES: matching-tag outcomes/full VALID-MODIFIED occupancy remain distinct from all16 RESERVED newTag failure; skipped paths NA.')
 else:facts.append('COVERED_RAW_PRESSURE_PRESENT: evaluate emitted same-head requester/eligibility/route joint and separately actual commit relief counters; do not force head-cycle exposures equal commits.')
 if uint(c['detach_success'])>0:facts.append('NONZERO_DETACH_PRESERVED: victim success/retirement and triggering invocation accept/deny are separate; later denial does not invalidate victim detach.')
 elif uint(c['raw_tag_fail_commit'])==0 and uint(c['relieve_calls'])==0:facts.append('ZERO_DETACH_WITH_NO_COMMIT_TAG_FAIL_OR_RELIEVE: measured immediate production trigger absent; not evidence that structural eligible candidates or RO activity are absent.')
 else:facts.append('ZERO_DETACH_AFTER_TRIGGER_STAGE: retain actual relief/eligible/deny events; no counterfactual or unique-victim count inferred from marginal exposures.')
 return {'measured':G,'actual_commit_and_lifecycle':c,'authoritative_RO_model_domain':cause['authoritative_oldmodel_RO_global'],'physical_phase_table':sorted(p,key=lambda x:x['physical_phase']),'conditional_facts':facts,'scope_limits':['Only this accepted newr5 diagnostic F point; no newS/F pair, cross-binary speedup, native branch coverage or oldbinary backfill.','Covered targetset distributions do not observe skipped upstream gate paths; absence/skip dimensions are NA, not invented zero occupancy.','Counts are head-cycle/way exposure or explicitly labeled transactions/requesters/commits; never unique requests/victims.','Kernel phase is physical event-time context, not requester/victim causal attribution. No phase-local live population from detach minus retirement.','Full valid/dirty occupancy is not all16 RESERVED pressure. Dirty fallback is source-proved for this exact release, not generalized to other simulators.','Finite same-source observer positives support wiring on exercised paths; application zero/nonzero does not prove all212 branches or performance benefit.']}

def build(path):
 r=load(path);need(r['schema']=='E2_R5_INDEPENDENT_FULL_APPLICATION_TERMINAL_AND_CAUSE_REVIEW_V1'and r['status']=='INDEPENDENT_REVIEW_OF_EXISTING_CURRENT_ACCEPTED_DIAGNOSTIC_POINT_PASS','not independently accepted actualr5 metadata');m=load(APP/'FINAL_MANIFEST.json');need(ref(APP/'FINAL_MANIFEST.json')['sha256']==MANIFEST_SHA,'frozen final manifest changed');need(r['source_identity']==m['source_identity']and r['condition_id']in m['conditions']and r['pair']is False,'wrong actual producer/condition');need(r['evidence']['final_manifest']['sha256']==MANIFEST_SHA and r['observer_independent_decode']['registered_count']==64 and r['observer_independent_decode']['selected64']is True and r['observer_independent_decode']['global_closed']is True,'not true closed64 source-bound independent review')
 c=m['conditions'][r['condition_id']];q=load(c['qualification']['path']);need(ref(c['qualification']['path'])['sha256']==c['qualification']['sha256']==r['qualification_id']and r['identity']==c['identity'],'wrong actual perinput Q/identity');need(r['workload']==r['identity']['workload']and r['instructions']==q['terminal_acceptance_required']['expected_instructions']and r['kernel_uids']==q['terminal_acceptance_required']['kernel_uids'],'wrong fullinput denominator/catalog')
 src={}
 for f in ('gpu-cache.cc','gpu-cache.h','ep-l2-ft-cache.inc','ep-l2-ro-runtime.inc'):
  p=CORE/'src/gpgpu-sim'/f;b=p.read_bytes();frozen=subprocess.check_output(['git','show',m['source_identity']['core_source_commit']+':src/gpgpu-sim/'+f],cwd=CORE);need(b==frozen,'actualsource differs from frozen producer');src[f]=ref(p)
 out=summarize(r);out.update(schema='E2_R5_COMPACT_SOURCE_BOUND_CAUSAL_REPORT_V1',status='PASS_EXISTING_ACCEPTED_METADATA_AND_FROZEN_SOURCE_REVIEW_ONLY',input_ref=ref(path),attempt_id=r['attempt_id'],workload=r['workload'],source_identity=r['source_identity'],instructions=r['instructions'],cycles=r['cycles'],pair=False,source_proof={'refs':src,'criterion':'For a newTag miss, everyway RESERVED causes Tag RESERVATION_FAIL; matching-tag HIT/HIT_RESERVED/SECTOR_MISS are returned earlier. Any nonreserved way permits INVALID/clean/allowed dirty/oldest-dirty fallback selection; full valid/dirty occupancy alone is not the trigger.','source_lines':{'gpu-cache.cc':'354-440','gpu-cache.h':'409-415,1097-1108','ep-l2-ft-cache.inc':'325-329','ep-l2-ro-runtime.inc':'241-249'}},actions={'raw_scans':0,'trace_binary_scans':0,'native_or_app_starts':0,'registry_source_repo_mutations':0});return out

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--review',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();need(a.out.resolve().is_relative_to(Path('/tmp'))and not a.out.exists(),'new unused /tmp output only');a.out.parent.mkdir(parents=True,exist_ok=True)
 try:r=build(a.review);code=0
 except Exception as e:r={'status':'COMPACT_CAUSAL_REVIEW_FAILED_CLOSED','error':type(e).__name__+': '+str(e),'acceptance_granted':False};code=1
 data=json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)+'\n';need(len(data.encode())<=8*2**20,'compact artifact cap8MiB');a.out.write_text(data);return code
if __name__=='__main__':raise SystemExit(main())
