from pathlib import Path
import json,hashlib,tarfile,sys
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy as e
root=e.NAS/'rtx4080_sm89/bulk_20261024_v1/objects';e.Resources()(True);results=[]
pins=[('stage_evidence_ada8_109_20261024_v1','059ddf05d9bec1662050f6d98b963457dc68d52e281efec098aba37b68d34366','16add50a7f411c67024e550cd5a9f8668c8d97a78d6b71b29a2f4c40e94ff69c'),('stage_evidence_ada8_174new_20261024_v1','004f554451a2e631cd8c4cab5d3a563a98c4f8a4b2d26a00cceef50464b124ff','94dc4bdc90727b28eefbae94790bff0224e934afce3d904ddced6a3dfa645d3e')]
for name,tar_sha,manifest_sha in pins:
    directory=root/name;raw=(directory/'MANIFEST.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==manifest_sha
    manifest=json.loads(raw);commit=json.loads((directory/'COMMIT.json').read_bytes())
    assert manifest['kind']==commit['kind']=='ENGINEERING_STAGE_NOT_FORMAL_WORKLOAD'
    assert commit['archive_sha256']==tar_sha and commit['manifest_sha256']==manifest_sha
    assert hashlib.sha256((directory/'CLOSED_READBACK.json').read_bytes()).hexdigest()==commit['readback_sha256']
    before=e.identity(directory/'payload.tar');assert e.hash_file(directory/'payload.tar')==tar_sha
    expected={x['member']:x for x in manifest['files']};assert len(expected)==len(manifest['files']);seen=set()
    with tarfile.open(directory/'payload.tar','r:',ignore_zeros=True) as archive:
        for member in archive:
            assert member.isfile() and member.name in expected and member.name not in seen
            assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
            row=expected[member.name];assert member.size==row['identity']['size'];h=hashlib.sha256();count=0
            with archive.extractfile(member) as source:
                while True:
                    block=source.read(1024**2)
                    if not block:break
                    count+=len(block);h.update(block)
            assert count==member.size and h.hexdigest()==row['sha256'];seen.add(member.name)
    assert seen==set(expected) and e.same_source(before,e.identity(directory/'payload.tar'))
    proof={'status':'PARENT_INDEPENDENT_FULL_ARCHIVE_AND_EVERY_MEMBER_SHA_PASS','kind':'ENGINEERING_STAGE_NOT_FORMAL_WORKLOAD','object':name,'archive_sha256':tar_sha,'manifest_sha256':manifest_sha,'members':len(seen),'archive_bytes':before['size'],'scientific_qualification_granted':False,'original_hot_copies_deleted':False}
    e.publish_bytes(directory/'PARENT_FULL_READBACK.json',e.canon(proof),e.v9());results.append(proof)
receipt={'status':'PASS','objects':results,'scope':'Ada stage2 engineering evidence; not entire RTX4080 campaign completion'}
(R/'control/ADA_STAGE2_PARENT_ARCHIVE_READBACK.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
