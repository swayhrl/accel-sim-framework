from pathlib import Path
import io,tarfile,gzip,json,subprocess,hashlib
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');D=R/'synthetic/archive_v2';D.mkdir(exist_ok=True,parents=True)
def tar(name,body):
    b=io.BytesIO()
    with tarfile.open(fileobj=b,mode='w') as t:
        info=tarfile.TarInfo(name);info.size=len(body);t.addfile(info,io.BytesIO(body))
    return b.getvalue()
a=tar('first/kernel-1.traceg',b'-binary version = 70\nFIRST\n')
b=tar('second/kernel-2.traceg',b'-binary version = 70\nSECOND\n')
fixtures={'concatenated_tar':gzip.compress(a+b),'concatenated_gzip':gzip.compress(a)+gzip.compress(b),'bad_crc':gzip.compress(a)[:-8]+bytes(8),'truncated_gzip':gzip.compress(a)[:-5],'nonzero_invalid_header':gzip.compress(a+b'X'*512+b)}
results=[];good=None
for name,data in fixtures.items():
    path=D/(name+'.tgz');path.write_bytes(data)
    req={'path':str(path),'source_host':'174-new','synthetic_qualification_only':True}
    cp=subprocess.run(['python3','-B',str(R/'tools/archive_worker.py')],input=json.dumps({'authorization':'USER_AUTHORIZED_PARALLEL_READ_ONLY_INVENTORY_20261024','archives':[req]}),text=True,capture_output=True)
    expected=name in ['concatenated_tar','concatenated_gzip']
    assert (cp.returncode==0)==expected,(name,cp.stderr[-1500:])
    if expected:
        result=json.loads(cp.stdout.splitlines()[-1]);assert len(result['members'])==2
        assert all(x.get('sha256') for x in result['members']);assert result['decoded_compression_EOF_integrity_checked']
        assert result['archive_sha256']==hashlib.sha256(data).hexdigest()
        if name=='concatenated_tar':good=(req,result)
    results.append({'test':name,'status':'PASS' if expected else 'PASS_EXPECTED_REJECTION','exit_code':cp.returncode})
req,prior=good;req['prior_index']=prior
cp=subprocess.run(['python3','-B',str(R/'tools/archive_worker.py')],input=json.dumps({'authorization':'USER_AUTHORIZED_PARALLEL_READ_ONLY_INVENTORY_20261024','archives':[req]}),text=True,capture_output=True)
assert cp.returncode==0,cp.stderr
d=json.loads(cp.stdout.splitlines()[-1]);assert d['reused_same_archive_SHA_member_bytes']==sum(x['size'] for x in prior['members']) and d['hashed_member_bytes']==0
results.append({'test':'exact_archive_SHA_cached_member_reuse','status':'PASS'})
req['prior_index']['archive_sha256']='0'*64
cp=subprocess.run(['python3','-B',str(R/'tools/archive_worker.py')],input=json.dumps({'authorization':'USER_AUTHORIZED_PARALLEL_READ_ONLY_INVENTORY_20261024','archives':[req]}),text=True,capture_output=True)
assert cp.returncode!=0 and 'prior cache archive whole SHA differs' in cp.stderr
results.append({'test':'different_archive_SHA_cache_rejected','status':'PASS_EXPECTED_REJECTION'})
proof={'status':'PASS','tests':results,'worker_sha256':hashlib.sha256((R/'tools/archive_worker.py').read_bytes()).hexdigest(),'synthetic_only':True,'scientific_starts':0}
(R/'control/ARCHIVE_V2_QUALIFICATION.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
