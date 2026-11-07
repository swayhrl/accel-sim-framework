"""A optional128 Source-specific record shell. Keeps raw Base and Ext populations."""
import json,re,hashlib
FROZEN_ACTUAL_FIELD_SETS={'EPL2TVDV2|SUMMARY': ['bank_wait_cycles', 'clean_installs', 'clean_retention_slot_cycles', 'directory_queries', 'dirty_forward_responses', 'dirty_installs', 'icnt_wait_cycles', 'live', 'lookup_wait_cycles', 'mandatory', 'promotions', 'read_responses', 'retention_slot_cycles', 'role_tvd', 'served_sector_bytes', 'served_sectors', 'slice', 'total_retention_slot_cycles', 'wb_wait_cycles'], 'EPL2TVDV3|METADATA_COST': ['completion_cam_ports', 'completion_cam_queries', 'directory_bound_wb_uid_bits', 'extra_packet_identity_bits', 'frontend_cam_ports', 'frontend_cam_queries', 'indexed_control_read_views', 'indexed_control_update_lanes', 'indexed_rollback', 'indexed_wb_accept', 'metadata_PPA', 'metadata_clock_closure', 'native_install_commits', 'native_promotion_commits', 'slice'], 'EPL2TVDX1|SEGMENT': ['PPA', 'bank_count', 'bank_ports', 'base_capacity', 'base_live', 'base_reclaim_cycles', 'base_replays', 'base_selector_cycles', 'ext_capacity', 'ext_indexed_read_views', 'ext_live', 'ext_mandatory', 'ext_queries', 'ext_write_grants', 'ext_write_merges', 'ext_write_ports', 'fallback', 'indexed_ext_read_recheck_cycles', 'invalidations', 'mandatory', 'mode', 'payload_slots', 'selector_reads', 'shared_query_ports', 'slice', 'spills'], 'EPL2TVDX1|CONTROL': ['added_ext_indexed_read_views', 'added_ext_update_lanes', 'ext_clean_installs', 'ext_clean_slot_cycles', 'ext_indexed_reads', 'ext_read_responses', 'ext_reclaimed', 'ext_served_sector_bytes', 'ext_served_sectors', 'old_indexed_read_views', 'old_update_lanes', 'paid_base_bank_reclaims', 'slice', 'unexported_ext_waits']}
def need(v,m):
 if not v:raise ValueError(m)
def uint(v,m):need(type(v)is int and 0<=v<(1<<64),m)
def parse_line(line):
 parts=line.strip().split('|');need(len(parts)>=3,'cost record format')
 typ=(parts[0],parts[1]);need(typ in [('EPL2TVDV2','SUMMARY'),('EPL2TVDV3','METADATA_COST'),('EPL2TVDX1','SEGMENT'),('EPL2TVDX1','CONTROL')],'unreviewed record type')
 out={}
 for part in parts[2:]:
  k,v=part.split('=',1);need(k not in out,'duplicate cost field')
  if k in ['metadata_PPA','metadata_clock_closure','PPA','unexported_ext_waits']:
   need(v=='UNKNOWN','unknown physical/measurement claim');out[k]=v
  else:need(re.fullmatch('[0-9]+',v)is not None,'noninteger cost field');out[k]=int(v);uint(out[k],'counter width/type')
 need(set(out)==set(FROZEN_ACTUAL_FIELD_SETS['|'.join(typ)]),'unknown or missing actual producer field')
 return typ,out
def validate_slice(v,c,x,y,mode):
 need(type(mode)is int and mode in[0,1,2],'unknown Source profile')
 sid=v['slice'];need(c['slice']==sid,'base cost slice mismatch')
 for k,z in [('frontend_cam_ports',1),('completion_cam_ports',1),('directory_bound_wb_uid_bits',32),('extra_packet_identity_bits',0),('indexed_control_read_views',3),('indexed_control_update_lanes',3)]:
  need(type(c[k])is int and c[k]==z,'old cost field changed '+k)
 need(c['metadata_PPA']==c['metadata_clock_closure']=='UNKNOWN','physical proof invented')
 need(v['mandatory']==0 and v['dirty_forward_responses']<=v['read_responses']and v['served_sector_bytes']==32*v['served_sectors'],'original base response/lifecycle invariants')
 uint(v['live'],'base live');uint(v['role_tvd'],'global TVD role');need(v['live']<=128,'base128 capacity')
 if mode==0:
  need(x is None and y is None,'mode0 unexpectedly has Ext hardware records')
  need(v['live']==v['role_tvd'],'legacy base/global role mismatch')
  ext=None
 else:
  need(x is not None and y is not None and x['slice']==y['slice']==sid and x['mode']==mode,'exact Ext source profile/slice')
  fixed=dict(base_capacity=128,ext_capacity=128,shared_query_ports=1,base_selector_cycles=2,indexed_ext_read_recheck_cycles=2,ext_write_ports=1,ext_indexed_read_views=1,base_reclaim_cycles=2,payload_slots=1168,bank_count=4,bank_ports=1)
  for k,z in fixed.items():need(type(x[k])is int and x[k]==z,'unreviewed Ext resource '+k)
  need(x['PPA']=='UNKNOWN','unproved Ext PPA')
  need(x['base_live']==v['live']and x['base_live']+x['ext_live']==v['role_tvd'],'Base-only SUMMARY must join Ext; no raw population rewrite')
  need(0<=x['base_live']<=128 and 0<=x['ext_live']<=128 and x['mandatory']==x['ext_mandatory']==0,'segment capacity/mandatory not closed')
  for k,z in [('old_indexed_read_views',3),('added_ext_indexed_read_views',1),('old_update_lanes',3),('added_ext_update_lanes',1)]:
   need(type(y[k])is int and y[k]==z,'Ext additive resource relation '+k)
  for k in ['ext_read_responses','ext_served_sectors','ext_served_sector_bytes','ext_clean_installs','ext_reclaimed','ext_clean_slot_cycles']:
   uint(y[k],'missing real Ext stats '+k)
  need(y['ext_served_sector_bytes']==32*y['ext_served_sectors'],'Ext sector/byte conservation')
  need(y['unexported_ext_waits']=='UNKNOWN','missing waits cannot become0')
  if mode==1:
   need(x['ext_live']==x['spills']==y['ext_clean_installs']==y['ext_read_responses']==y['ext_served_sectors']==0,'disabled-install cost control used extension')
  ext={k:y[k]for k in ['ext_read_responses','ext_served_sectors','ext_served_sector_bytes','ext_clean_installs','ext_reclaimed','ext_clean_slot_cycles']}
 return dict(slice=sid,base_raw_summary=v,base_raw_cost=c,extension_raw_segment=x,extension_raw_control=y,base_stats_scope='BASE_ONLY',extension_stats_scope='EXT_ONLY_NOT_QUERY_COUNTS',known_total_read_responses=v['read_responses']+(ext['ext_read_responses']if ext else 0),known_total_served_sector_bytes=v['served_sector_bytes']+(ext['ext_served_sector_bytes']if ext else 0),Ext_waits='NOT_APPLICABLE'if mode==0 else'UNKNOWN_NOT_EXPORTED',role_tvd_global=v['role_tvd'],scientific_acceptance=False)
def validate_final_frame(lines,mode,source_contract):
 need(source_contract.get('status')=='ACTUAL_SOURCE_AND_RECORD_ABI_FROZEN','unqualified A Source-specific shell')
 need(source_contract.get('actual_option_name')=='-gpgpu_ep_l2_victim_extension','actual A flag ABI')
 need(source_contract.get('record_field_sets')==FROZEN_ACTUAL_FIELD_SETS,'actual final producer field schema not pinned')
 records={}
 for line in lines:
  typ,r=parse_line(line);key=(*typ,r['slice']);need(key not in records,'duplicate final frame');records[key]=r
 kinds=[('EPL2TVDV2','SUMMARY'),('EPL2TVDV3','METADATA_COST')]+([('EPL2TVDX1','SEGMENT'),('EPL2TVDX1','CONTROL')]if mode else[])
 need(set(records)=={(*k,s)for k in kinds for s in range(64)},'exact64 Base/Ext record population')
 rows=[validate_slice(records['EPL2TVDV2','SUMMARY',s],records['EPL2TVDV3','METADATA_COST',s],records.get(('EPL2TVDX1','SEGMENT',s)),records.get(('EPL2TVDX1','CONTROL',s)),mode)for s in range(64)]
 return dict(status='SOURCE_SPECIFIC_A_COST_POPULATION_PASS_NOT_APPLICATION_ACCEPTANCE',rows=rows,unchanged_math_body_and_payload_full_command_validator_required=True,external_Source5_input_fullconfig_and_production_CPU_qualification_required=True,new_model_authority=False)
