from pathlib import Path
import json,hashlib,tarfile,sys
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy as e
root=e.NAS/'rtx4080_sm89/bulk_20261024_v1/objects';e.Resources()(True);results=[]
pins=[('stage_evidence_ada7_109_20261024_v1','e4bf2a9a43696a92886428eb8bfbf23c32e7d498be72ab8ed6ac5cfcc3192213','fb353f651f103fd3a1957651890e2cf8ef550d665dad41514dd34cd3056d715d'),('stage_evidence_ada7_174new_20261024_v1','e281c3760ee20d9bced68d05c755623d38fd08722ed8b82873ce047badb5a6ed','72b871f10b779091d02e57a9fb670644d1510eb779cca9fcb467391215b67674')]
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
receipt={'status':'PASS','objects':results,'scope':'Ada stage1 engineering evidence; not entire RTX4080 campaign completion'}
(R/'control/ADA_STAGE1_PARENT_ARCHIVE_READBACK.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
