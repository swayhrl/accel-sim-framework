"""Read-only existing six scopes plus exact18 forecasts;4GiB estimates,16GiB caps."""
import pathlib,json,hashlib,importlib.util,os,datetime
P=pathlib.Path;R=P('/root/data/dtc_hash_downstream18_20261027_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');REQ='DTC_HASH_DOWNSTREAM18_20261027_V1';G=1024**3;M=1024**2
def read(p):return json.loads(P(p).read_bytes())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def resources(s,fresh_source=False):
 p=read(R/'control/EXECUTION_PLAN.json');src=p['six_scope_resource_source'];assert sha(src['path'])==src['sha256'];old=load('ds18_existing_six_resources',P(src['path']));b=old.resources({'request':old.ORIG,'cohort':'DS18_RESOURCE_METADATA'},False);reg,ep=old.authority();q=reg['registered_future_requests'][REQ];claims=read(R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];ram=[];own=G;entries=[]
 for c,row in q['consumed'].items():
  spec=read(R/'control/specs'/(c+'.json'));assert sha(R/'control/specs'/(c+'.json'))==q['admitted_specs'][c];out=R/'DTC/run/results'/row['uuid'];size=old.size(out);closed=bool(row.get('execution_receipt'));archived=(R/'control'/(c+'_ARCHIVE_RECEIPT.json')).exists()
  if archived:continue
  needed=size+16*M if closed else max(0,2*spec['limits']['max_result_directory_bytes']-size);own+=needed;entries.append(dict(cohort=c,remaining_write_and_restore_bytes=needed))
  if not closed:
   rss,live=old.rss(R,row);estimate=spec['estimated_peak_model_RAM_bytes'];assert estimate==4*G and spec['limits']['max_process_tree_rss_bytes']==16*G;ram.append(dict(cohort=c,kind='OBSERVED_MODEL'if live else'UNRESOLVED_GENERATION',RSS_bytes=rss,additional_reserved_bytes=max(0,estimate-rss)))
 pending=set(claims)-set(q['consumed'])
 if fresh_source and s['cohort']not in q['consumed']:pending.add(s['cohort'])
 for c in pending:
  spec=read(R/'control/specs'/(c+'.json'));assert sha(R/'control/specs'/(c+'.json'))==q['admitted_specs'][c];estimate=spec['estimated_peak_model_RAM_bytes'];assert estimate==4*G
  if c in claims:assert claims[c]['result_cap_bytes']==spec['limits']['max_result_directory_bytes']
  own+=2*spec['limits']['max_result_directory_bytes'];ram.append(dict(cohort=c,kind='CLAIM_OR_CANDIDATE',RSS_bytes=0,additional_reserved_bytes=estimate))
 projected=b['reserved_additional_live_and_candidate_RAM_bytes']+sum(v['additional_reserved_bytes']for v in ram);need=projected if fresh_source else 0;eff=b['cgroup_effective_headroom_bytes'];assert q['reserved_write_bytes']==(G if q['state']=='CLOSED'else 10*G);bound=own<=q['reserved_write_bytes'];ours=next((v['reserved_write_bytes']for v in b['peer_reservations']if v['request']==REQ),0);assert ours==10*G or q['state']=='CLOSED';required=b['required_free_bytes']+(0 if ours else own)
 return dict(b,schema='HASH18_EXISTING6_PLUS_NEW18_RESOURCE_V1',source_module_sha256=sha(__file__),own_ram_forecasts=ram,own_write_entries=entries,own_remaining_write_and_restore_bytes=own,own_reserved_write_ceiling_bytes=q['reserved_write_bytes'],own_write_ceiling_pass=bound,total_projected_additional_RAM_bytes=projected,required_free_bytes=required,physical_RAM_pass=b['host_MemAvailable_bytes']>=64*G+need and(eff is None or eff>=48*G+need),physical_disk_pass=b['physical_disk_pass']and bound and b['native_free_bytes']>required,initial_working_set_floor_bytes=4*G,unchanged_runtime_floors=[64*G,48*G,5*G])
