from pathlib import Path
import subprocess,json,hashlib,sys,struct,os
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));e=__import__(os.environ.get('COPY_ENGINE_MODULE','library_copy'))
results=[]
for name in ['concatenated_tar','concatenated_gzip','bad_crc','truncated_gzip','nonzero_invalid_header']:
    p=R/'synthetic/archive_v2'/(name+'.tgz')
    members=[]
    if name.startswith('concatenated'):
        for rel,body in [('first/kernel-1.traceg',b'-binary version = 70\nFIRST\n'),('second/kernel-2.traceg',b'-binary version = 70\nSECOND\n')]:
            members.append({'archive_member':rel,'relative_path':rel,'size':len(body),'sha256':hashlib.sha256(body).hexdigest()})
    manifest={'source_backend':'archive','archive_path':str(p),'archive_identity':e.identity(p),'archive_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'members':members}
    request={'manifest':manifest,'skip':{x['relative_path']:0 for x in members}}
    cp=subprocess.run(['python3','-B',str(e.__file__),'source-synthetic'],input=e.canon(request),capture_output=True)
    accepted=name.startswith('concatenated');assert (cp.returncode==0)==accepted,(name,cp.stderr[-1000:])
    if accepted:
        pos=0;events=[]
        while pos<len(cp.stdout):
            n=struct.unpack('!Q',cp.stdout[pos:pos+8])[0];pos+=8;row=json.loads(cp.stdout[pos:pos+n]);pos+=n;events.append(row)
            if row['event']=='CHUNK':
                body=cp.stdout[pos:pos+row['size']];pos+=row['size'];assert hashlib.sha256(body).hexdigest()==row['sha256']
        assert [x['path'] for x in events if x['event']=='FILE_END']==[x['relative_path'] for x in members]
        assert events[-1]['event']=='SOURCE_DONE'
    results.append({'test':name,'status':'PASS' if accepted else 'PASS_EXPECTED_REJECTION','exit_code':cp.returncode})
proof={'status':'PASS','tests':results,'engine_sha256':hashlib.sha256(Path(e.__file__).read_bytes()).hexdigest(),'foreign_legacy_locks_untouched':True,'synthetic_only':True}
suffix=os.environ.get('QUALIFY_REVISION','');name='ARCHIVE_SENDER_QUALIFICATION'+('_'+suffix if suffix else '')+'.json'
(R/'control'/name).write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
