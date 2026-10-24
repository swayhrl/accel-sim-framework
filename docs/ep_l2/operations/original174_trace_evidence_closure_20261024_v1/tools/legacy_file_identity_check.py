from closure_local import *
from closure_resources import UTIL
import io,posixpath
d=load(R/'evidence/LEGACY_VM_TRUE164_CURRENT_CANONICAL_RECEIPTS.json')['documents']
manifest=next(z for z in d if z['path'].endswith('/PRIVATE_EXPORT_MANIFEST.tsv'))
hashes=next(z for z in d if z['path'].endswith('/PRIVATE_DESTINATION_FILE_HASHES.tsv'))
assets=list(csv.DictReader(io.StringIO(manifest['text']),delimiter='\t'))
root='/root/share/mnt164/huangrulin/c16_ai_workload/provenance/historical_snapshots/old174_c12_c15_simulation/private_export'
by={a['asset_id']:dict(**a,true164_root=root+'/'+a['destination_relative_path'].removeprefix('old174_private_export/')) for a in assets}
req=[]
for line in hashes['text'].splitlines():
 aid,rel,size,sha=line.split('\t');req.append(dict(asset=aid,path=by[aid]['true164_root']+'/'+rel,size=int(size),expected_sha256=sha))
code=UTIL+'\nreq='+repr(req)+r'''
import collections
groups=collections.defaultdict(lambda:dict(files=0,logical_bytes=0,metadata_mismatches=[],full_payload_SHA_recomputed=False))
for r in req:
 s=meta(r['path']);o=groups[r['asset']];o['files']+=1;o['logical_bytes']+=r['size']
 if s.get('type')!='file' or s.get('size')!=r['size']:o['metadata_mismatches'].append(dict(path=r['path'],expected_size=r['size'],actual=s))
print(json.dumps(dict(utc=time.time(),groups=dict(groups),file_stat_count=len(req),no_payload_reads=True)))
'''
x=remote('hrl-174-new',code,60);save('evidence/LEGACY_VM_ALL494_FILE_METADATA_VS_HISTORICAL_COMPLETE_SHA_RECORDS.json',dict(**x,asset_maps=list(by.values()),manifest_sha256=manifest['sha256'],prior_complete_file_hash_list_sha256=hashes['sha256'],scientific_dependency_caveat='C3/M4I trace symlinks remain external; input dependency closure not inferred from archived raw logs'))
print([(k,v['files'],v['logical_bytes'],len(v['metadata_mismatches'])) for k,v in x['groups'].items()])
