"""Finite identity/prior-SHA reuse while another task owns the data lease.

No new full-body hashing, transfer or sender/receiver lease is started. Prefix
reads are bounded to128B per exact frozen file; prior SHA must exist for every
selected file and fstat must match the trusted original freeze.
"""
import json,gzip,time
from pathlib import Path
import copy_engine as c
P=Path

def main():
    queue=json.loads(gzip.decompress((c.TASK/'control/FROZEN_SCOPES.json.gz').read_bytes()))['scopes'];results=[]
    for scope in queue:
        if not all(x.get('sha256') for x in scope['files']):continue
        path=c.TASK/'manifests'/(scope['asset_id']+'.json')
        old=None
        if path.exists():
            old=c.read(path)
            if old.get('schema')=='FROZEN_GENERIC_RESEARCH_FILE_BUNDLE_V2_SYMLINK_META':results.append(dict(asset_id=scope['asset_id'],status='PREPARED_MANIFEST_REUSED'));continue
        request=dict(scope=scope,source_role='TARGET' if scope['source_alias']=='hrl-174-new' else 'SOURCE',true164_bundle=str(c.NAS/scope['asset_id']).replace('/root/share/mnt164','/home/shared',1),metadata_only=True)
        child=c.source_boot('prepare',request)
        out,err=child.communicate(timeout=90)
        if child.returncode:
            reason=err.decode(errors='replace')[-1500:];results.append(dict(asset_id=scope['asset_id'],status='METADATA_HOLD',reason=reason))
            if 'RESOURCE_HOLD' in reason:break
            continue
        rows=[json.loads(z) for z in out.splitlines()];prepared=next(x for x in rows if x['event']=='PREPARED');c.need(prepared['source_new_hashed_bytes']==0,'METADATA_PATH_PERFORMED_NEW_HASH')
        path.parent.mkdir(parents=True,exist_ok=True)
        if old is not None:
            c.need(not (c.NAS/scope['asset_id']).exists(),'CANNOT_UPGRADE_A_PUBLISHED_TRANSACTION')
            c.need(old['members']==prepared['manifest']['members'] and old['source_root_identity']==prepared['manifest']['source_root_identity'],'DRAFT_SOURCE_IDENTITY_CHANGED')
            previous=path.with_suffix('.prepublication-v1.json')
            if not previous.exists():previous.write_bytes(c.canon(old))
        with path.open('wb' if old is not None else 'xb') as f:f.write(c.canon(prepared['manifest']))
        proof=c.TASK/'prehash'/(scope['asset_id']+'.json');proof.parent.mkdir(parents=True,exist_ok=True)
        with proof.open('wb' if old is not None else 'xb') as f:f.write(c.canon({k:v for k,v in prepared.items() if k!='manifest'}))
        results.append(dict(asset_id=scope['asset_id'],status='IDENTITY_AND_PRIOR_FULL_SHA_REUSE_PREPARED',original_bytes=scope['expected_bytes'],files=len(scope['files']),new_full_body_read_bytes=0));print(json.dumps(results[-1]),flush=True)
    p=c.TASK/'control/KNOWN_SHA_METADATA_PREPARATION.json'
    with p.open('w') as f:json.dump(dict(unix=time.time(),results=results,new_sender_or_receiver_started=False,new_payload_transfers=0),f)

if __name__=='__main__':main()
