"""Finite exact-census static extraction. No workload, GPU, or simulator execution."""
from pathlib import Path
import os, subprocess, json, hashlib, re, time, shutil, sys

R=Path('/data/c16/cubin_duplicate_extract_cpu_20261024_v1')
T=Path('/usr/local/cuda-12.8/bin/cuobjdump');S=R/'cubin_preserve_extract_v1.so'
PLAN=R/'STATIC_CUBIN_DUPLICATE_CENSUS_V1.json'
D=R/'collision_closure_batch_v1'
LIMIT=512*1024**2
def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return h.hexdigest()
def run(args,cwd,env=None):
    return subprocess.run(['/usr/bin/timeout','--signal=TERM','--kill-after=2','120',
        '/usr/bin/nice','-n','10','/usr/bin/prlimit','--as=2147483648','--cpu=110',
        '--fsize=134217728','--',*map(str,args)],cwd=cwd,env=env,capture_output=True,text=True)
def resources():
    used=sum(p.stat().st_blocks*512 for p in D.rglob('*')if p.is_file())
    assert used<LIMIT,'closed output cap reached'
    assert shutil.disk_usage(D).free>5*1024**3+128*1024**2,'5GiB base plus bounded next output'
    return used
assert len(sys.argv)==2 and sha(PLAN)==sys.argv[1]
qual=json.loads((R/'qualification_preserve_v2/QUALIFICATION.json').read_text())
assert qual['status']=='EXTRACT_ONLY_DUPLICATE_IMAGE_PRESERVATION_CPU_QUALIFICATION_PASS'
assert sha(T)==qual['tool_sha256'] and sha(S)==qual['shim_sha256']
assert sha(R/'cubin_preserve_extract_v1.c')==qual['source_sha256']
rows=[x for x in json.loads(PLAN.read_text())['rows']if x.get('duplicate_basenames')]
assert len(rows)==28
D.mkdir(exist_ok=False);reports=[]
for row in rows:
    resources();src=Path(row['path']);dest=D/row['binary_sha256'];dest.mkdir()
    result={'source':str(src),'source_sha256':row['binary_sha256'],'program':row['program']}
    try:
        assert sha(src)==row['binary_sha256'],'source changed'
        listing=run([T,'--list-elf',src],dest)
        (dest/'list.stdout').write_text(listing.stdout);(dest/'list.stderr').write_text(listing.stderr)
        assert listing.returncode==0 and hashlib.sha256(listing.stdout.encode()).hexdigest()==row['listing_sha256']
        names=re.findall(r'^ELF file\s+\d+: ([A-Za-z0-9_.-]+)$',listing.stdout,re.M)
        assert names==row['cubin_names'] and len(names)==row['cubin_count']
        images=dest/'images';images.mkdir()
        env=dict(os.environ);env.pop('LD_PRELOAD',None)
        env.update(LD_PRELOAD=str(S),EP_CUBIN_OUTPUT_ROOT=str(images),EP_CUBIN_ALLOWED_BASENAMES=':'.join(sorted(set(names))))
        cp=run([T,'--extract-elf','all',src],images,env)
        (dest/'extract.stdout').write_text(cp.stdout);(dest/'extract.stderr').write_text(cp.stderr)
        assert cp.returncode==0,cp.stderr
        assert re.findall(r'^Extracting ELF file\s+\d+: ([A-Za-z0-9_.-]+)$',cp.stdout,re.M)==names
        paths=sorted(images.iterdir());assert len(paths)==len(names)
        items=[]
        for ordinal,(p,name)in enumerate(zip(paths,names),1):
            resources();assert not p.is_symlink() and p.name==('image_%06d__'%ordinal)+name
            assert p.read_bytes()[:4]==b'\x7fELF';before=sha(p)
            outputs={}
            for label,args in [('header',['/usr/bin/readelf','-h',p]),('symbols',['/usr/bin/readelf','-Ws',p]),('sections',['/usr/bin/readelf','-SW',p]),('sass',[T,'--dump-sass',p])]:
                q=run(args,dest);assert q.returncode==0,q.stderr
                output=dest/(p.name+'.'+label+'.txt');output.write_text(q.stdout)
                outputs[label]={'path':str(output),'bytes':output.stat().st_size,'sha256':sha(output),'text':q.stdout}
            assert 'NVIDIA CUDA' in outputs['header']['text']
            arch=re.search(r'\.sm_(\d+)\.cubin$',name);assert arch
            assert 'code for sm_'+arch[1]in outputs['sass']['text']
            functions=re.findall(r'Function\s*:\s*(\S+)',outputs['sass']['text'])
            if functions:assert 'FUNC' in outputs['symbols']['text']and '.text.' in outputs['sections']['text']
            else:assert 'FUNC' not in outputs['symbols']['text']and '.text' not in outputs['sections']['text']
            assert sha(p)==before
            items.append({'ordinal':ordinal,'basename':name,'bytes':p.stat().st_size,'sha256':before,'functions':functions,'empty_code_image':not functions,'cpu_readback':{k:{a:b for a,b in v.items()if a!='text'}for k,v in outputs.items()}})
        assert sha(src)==row['binary_sha256']
        result.update(status='EVERY_LISTED_IMAGE_PRESERVED_AND_FULL_CPU_READBACK_PASS',images=items)
    except Exception as exc:
        result.update(status='EXTRACTION_OR_READBACK_HOLD',reason=repr(exc))
    reports.append(result)
    (dest/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    (D/'PROGRESS.json').write_text(json.dumps({'completed':len(reports),'total':len(rows),'last':result['status']},indent=2)+'\n')
    print(json.dumps({'completed':len(reports),'program':row['program'],'status':result['status']}),flush=True)
out={'status':'FINITE_COLLISION_EXTRACTION_CENSUS_COMPLETE','tool_sha256':sha(T),'shim_sha256':sha(S),'plan_sha256':sha(PLAN),'driver_sha256':sha(Path(__file__)),'results':reports,'success':sum(x['status']=='EVERY_LISTED_IMAGE_PRESERVED_AND_FULL_CPU_READBACK_PASS'for x in reports),'total':len(rows),'allocated_bytes':resources(),'source_keep':True,'GPU_or_simulator_execution':False,'existing_mapper_or_catalog_modified':False,'scope':'Static listed images only; actual loaded code, runtime dependencies and semantic qualification remain independent','unix':time.time()}
(D/'BATCH_RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='results'}))
