import pathlib,json,hashlib
r=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/D/raw_reason_v1');info=json.loads((r/'LAST_SCAN.json').read_bytes());sidecar=json.loads(pathlib.Path(info['output']).read_bytes());out=[]
for row in sidecar['rows']:
 if row['program']not in['ATAX','MVT','BICG']or row['profile']!='P0':continue
 p=pathlib.Path(row['result_path']);b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==row['result_sha256'];v=json.loads(b);pr=v['proof'];t=pr['traffic'];bucket=t['L2_buckets'];miss=[n for k,n in bucket.items()if k.partition(':')[0].endswith('_R')and k.partition(':')[2]in['MISS','SECTOR_MISS']]
 out.append(dict(sidecar=row,cycles=v['cycles'],L2_accepted_read_32B_sectors=t['L2_accepted_read_32B_sectors'],L2_read_miss_32B_sectors=sum(miss)if miss else None,DRAM_read_atoms=t['DRAM_issued_read_atoms'],DRAM_read_bytes=t['DRAM_read_payload_bytes'],source_result_path=str(p),source_result_sha256=hashlib.sha256(b).hexdigest(),core_commit=pr['core_commit'],framework_commit=pr['framework_commit'],binary_sha256=pr['binary_sha256']))
print(json.dumps(dict(sidecar_path=info['output'],sidecar_sha256=info['sha256'],sidecar_utc=sidecar['utc'],rows=out),indent=2))
