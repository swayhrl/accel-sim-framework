"""Exact all-data original-instruction/reference closure, physical cache/WB is N/A."""
import argparse,hashlib,json,re,sys
from pathlib import Path

def require(v,m):
 if not v:raise ValueError(m)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def lines(raw):
 with Path(raw).open() as stream:
  yield from stream

def references(raw):
 blocks=[];block=None;last_native_cycle=None
 for line in lines(raw):
  metric=re.fullmatch(r'gpu_tot_sim_cycle\s*=\s*(\d+)\s*',line)
  if metric:
   last_native_cycle=int(metric[1])
   if block is not None:
    require(block['cycle'] is None or block['cycle']==last_native_cycle,'Reference/native clock association changed')
    block['cycle']=last_native_cycle
  if not line.startswith('EPL2MEMREFV1|'):continue
  parts=line.strip().split('|')[1:]
  if parts[0].startswith('scope='):kind='MAIN'
  else:kind=parts.pop(0)
  row=dict(p.split('=',1) for p in parts)
  if kind=='MAIN':
   if block is not None:
    require(block['cycle'] is not None,'Repeated reference dump without native statistics context')
    blocks.append(block)
   block={'cycle':None,'sections':{},'spaces':{}}
  require(block is not None,'Reference sections without cumulative header')
  if kind=='SPACE':
   sid=int(row['space']);require(sid not in block['spaces'],'Duplicate memory-space scope within final cumulative dump');block['spaces'][sid]=int(row['instructions']);continue
  require(kind in ('MAIN','SNAPSHOTS','IDENTITY','UNIQUENESS') and kind not in block['sections'],'Duplicate/unknown reference terminal section')
  block['sections'][kind]=row
 require(block is not None,'Missing final cumulative reference dump')
 if last_native_cycle is not None:require(block['cycle']==last_native_cycle,'Reference final dump not paired with final native clock')
 blocks.append(block);sections=block['sections'];spaces=block['spaces']
 for previous in blocks[:-1]:
  require(previous['cycle']<=block['cycle'],'Non-monotonic cumulative dump context')
  if previous['cycle']==block['cycle']:require(previous['sections']==sections and previous['spaces']==spaces,'Conflicting reference snapshots at one native cycle')
 require(set(sections)=={'MAIN','SNAPSHOTS','IDENTITY','UNIQUENESS'},'Missing exact cumulative reference terminal sections')
 r=sections['MAIN'];snap=sections['SNAPSHOTS'];ids=sections['IDENTITY'];unique=sections['UNIQUENESS']
 require(r['scope']=='cumulative' and r['mode']=='I_MEM_ALL_DATA' and r['instruction_path']=='NATIVE' and r['data_hierarchy']=='NOT_APPLICABLE','Wrong actual reference path/scope')
 require(snap['scope']==ids['scope']=='cumulative' and snap['data_scope']=='BYTE_ADDRESS_PRODUCER_VERSION_SYMBOLS' and unique['duplicate_policy']=='FAIL_CLOSED','Wrong reference identity/data semantics')
 nums={}
 for label,row in sections.items():
  nums[label]={}
  for key,value in row.items():
   if value.isdigit():nums[label][key]=int(value)
 a,b,c,d=[nums[k] for k in ['MAIN','SNAPSHOTS','IDENTITY','UNIQUENESS']]
 require(a['instructions']==a['instructions_consumed']==d['original_instructions']==sum(spaces.values()),'Original instruction/consume/space identity mismatch')
 require(a['requests']==a['ready']==a['consumed'] and d['native_accesses']<=a['requests'],'Request identity/ready/consume mismatch')
 require(a['stores']==a['store_reference_commits']==c['native_stores_issued']==c['native_stores_committed'] and a['store_fragments']==a['store_fragment_commits'],'Original store not exactly once committed')
 require(b['loads']+b['barriers']+a['stores']==a['instructions'],'Instruction kinds do not close')
 require(b['bytes_ready']==b['bytes_consumed']==b['known_bytes']+b['symbolic_bytes'] and b['ready_digest']==b['consumed_digest'],'Ready/consumed byte snapshots differ')
 require(c['issued_instruction_digest']==c['consumed_instruction_digest'],'Original instruction UID digest differs')
 require(a['pending_requests']==a['pending_instructions']==c['pending_barriers']==c['pending_native_stores']==0 and a['drained']==1,'Reference request/instruction/store/barrier state not drained')
 # These two printed zeroes are asserted by source, not measured stall/violation counters.
 require(a['memory_resource_wait']==a['ready_latency_violations']==0,'Source reference invariant violated')
 return {'selected_cumulative_native_cycle':block['cycle'],'cumulative_dump_count':len(blocks),'records':sections,'space_instructions':{str(k):v for k,v in spaces.items()},'numeric_records':nums,'source_asserted_invariants':{'ready_at_eligible_plus_one_physical_GPUcycle':True,'no_finite_memory_admission_or_response_quota':True,'printed_literal_fields':['memory_resource_wait','ready_latency_violations']},'measured_residual':{'producer_dependency_cycles':a['dependency_cycles'],'reference_ready_to_architectural_consume_cycles':a['ready_to_consume_cycles'],'SM_register_writeback_wait_attempts':a['sm_register_wait_attempts']}}

def parse(raw,spec):
 require(spec['scientific_scope']=='ALL_DATA_REFERENCE_V1','Another scope cannot use ALL_DATA terminal')
 sys.path.insert(0,str(Path(spec['scope_tool']['path']).parent));require(digest(spec['scope_tool']['path'])==spec['scope_tool']['sha256'],'Frozen source scope tool changed')
 from unified_scope import features
 features(spec['identity'],spec['producer_profile']);require(spec['producer_profile']=='I_MEM_ALL_DATA','Not ALL_DATA profile')
 ref=references(raw);metrics={};normal=False
 for line in lines(raw):
  m=re.fullmatch(r'gpu_tot_sim_(cycle|insn)\s*=\s*(\d+)\s*',line)
  if m:metrics[m[1]]=int(m[2])
  normal|='GPGPU-Sim: *** exit detected ***' in line
 require(normal and set(metrics)=={'cycle','insn'} and metrics['cycle']>0 and metrics['insn']>0,'No complete native execution')
 release=json.loads(Path(spec['qualified_release']).read_text());gate=release['gates']['sector_reference_data'];data=(release['qualified_by']=='lane5' and release['status']=='INDEPENDENTLY_QUALIFIED' and gate['status']=='PASS' and gate['production_driven'] and digest(gate['evidence_path'])==gate['evidence_sha256'])
 return {'diagnostic_scope':'ALL_DATA_REFERENCE_V1','cycles':metrics['cycle'],'instructions':metrics['insn'],'reference_terminal':ref,'hardware_drained':True,'workload_termination':spec['identity']['termination_contract'],'data_correctness_qualification':bool(data),'requester_exact_once_audit':True,'raw_log_sha256':digest(raw),'physical_data_hierarchy':'NOT_APPLICABLE','physical_slice_WB_DRAM_counters':'NOT_APPLICABLE','instruction_fetch':'NATIVE_UNCHANGED','numeric_SASS_output_validated':False}

def validate_reference_summary(summary,identity):
 require(summary['diagnostic_scope']=='ALL_DATA_REFERENCE_V1' and identity['ideal_vector']['mem_all_data'] is True,'Wrong all-data qualification')
 require(summary['cycles']>0 and summary['instructions']>0 and summary['hardware_drained'] is True and summary['workload_termination']==identity['termination_contract'],'Incomplete native/reference termination')
 require(summary['data_correctness_qualification'] is True and summary['requester_exact_once_audit'] is True,'Reference data/request qualification missing')
 require(summary['physical_data_hierarchy']==summary['physical_slice_WB_DRAM_counters']=='NOT_APPLICABLE' and summary['instruction_fetch']=='NATIVE_UNCHANGED' and summary['numeric_SASS_output_validated'] is False,'Physical N/A/numeric scope changed')
 return {'status':'PASS','scope':'Original data-memory instructions/UIDs, native accesses, symbolic byte snapshots, producer/store commits and architectural consume; physical data hierarchy N/A','cycles_scope':'Native cumulative GPU cycles; retained SM/register/barrier and instruction-fetch semantics'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();spec=json.loads(Path('input_spec.json').read_text());a.out.write_text(json.dumps(parse(a.raw,spec),indent=2)+'\n')
if __name__=='__main__':main()
