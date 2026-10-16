"""Resume after read-only durable remote SHA proof; never repeat completed deletions."""
from cleanup import *
remote='/tmp/aiarch_109_firstbatch_sha_20261016_lane_m_v1/final.json'
p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','hrl174new','cat',remote],text=True,capture_output=True,timeout=45)
assert p.returncode==0,'REMOTE_FULL_SHA_NOT_FINISHED'
v=json.loads(p.stdout);assert v['status']=='PASS_FULL_CURRENT_164_PAYLOAD_SHA256'
assert len(v['files'])==110+9062
save('remote_payload_hashes.json',v)
local=json.loads((R/'local_payload_hashes.json').read_text());assert local['status']=='PASS'
remote_rows={x['path']:x for x in v['files']}
slugs={'deepseek_v2_lite':'deepseek-v2-lite','qwen3_8b':'qwen3-8b','qwen2p5_7b_instruct_raw':'qwen2.5-7b-instruct-raw','qwen2p5_7b_instruct_awq':'qwen2.5-7b-instruct-awq','qwen2p5_0p5b_instruct':'qwen2.5-0.5b-instruct'}
for row in local['files']:
 path=Path(row['path'])
 if '/models/.incoming/' in str(path):
  part=path.relative_to(BASE/'models/.incoming');mapped='/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/'+slugs[part.parts[0]]+'/'+str(Path(*part.parts[1:]))
 else:mapped='/root/share/mnt164/huangrulin/c16_ai_workload/raw/'+E1+'/traces/'+path.name
 assert remote_rows[mapped]['sha256']==row['sha256'] and remote_rows[mapped]['bytes']==row['bytes']
inv=json.loads((R/'predelete_inventory.json').read_text())
for x in TARGETS[2:7]:delete(x,inv[str(x)])
assert inventory(RAW)==inv[str(RAW)] and inventory(LINK)==inv[str(LINK)]
delete(RAW,inv[str(RAW)]);remaining=inventory(LINK);assert [{**x,'nlink':2} for x in remaining]==inv[str(LINK)];delete(LINK,remaining)
start=json.loads((R/'start.json').read_text());free=shutil.disk_usage(BASE).free
save('finished.json',{'status':'PASS_FIRST_BATCH_CLEANUP','free_before_bytes':start['free_before_bytes'],'free_after_bytes':free,'net_free_increase_bytes':free-start['free_before_bytes'],'deleted_targets':[str(x) for x in TARGETS],'remote_verified_files':len(v['files']),'local_verified_payload_files':len(local['files']),'archive_modified':False,'A61_A26GR1_modified':False,'GPU_lock_attempts':0})
print('PASS_FIRST_BATCH_CLEANUP',free,flush=True)
