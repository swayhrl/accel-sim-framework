"""Finite CPU-only extraction proof. Never executes an application or GPU code."""
from pathlib import Path
import os, subprocess, hashlib, json, re, time, collections

R=Path('/data/c16/cubin_duplicate_extract_cpu_20261024_v1')
T=Path('/usr/local/cuda-12.8/bin/cuobjdump')
S=R/'cubin_preserve_extract_v1.so'
D=R/'qualification_preserve_v2'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,cwd,env=None):
    return subprocess.run(['/usr/bin/timeout','--signal=TERM','--kill-after=2','120',
        '/usr/bin/prlimit','--as=2147483648','--cpu=110','--fsize=134217728','--',
        *map(str,args)],cwd=cwd,env=env,capture_output=True,text=True)
assert sha(T)=='9d515ac6f60c246ef63fe87b0a95d209b00ff3e25b716f8f263520010760e8f8'
D.mkdir(exist_ok=False)
repro=json.loads((R/'evidence/TOOL_OPTIONS_AND_REPRO_V1.json').read_text())
cases=[]
for k,case in enumerate(repro['cases']):
    src=Path(case['input']); assert sha(src)==case['input_sha256']
    dest=D/('case_%d'%k);dest.mkdir()
    listed=run([T,'--list-elf',src],dest)
    (dest/'list.stdout').write_text(listed.stdout);(dest/'list.stderr').write_text(listed.stderr)
    names=re.findall(r'^ELF file\s+\d+: ([A-Za-z0-9_.-]+)$',listed.stdout,re.M)
    if not names:
        assert k==2 and listed.returncode!=0 and 'does not contain device code' in listed.stderr
        cases.append({'input':str(src),'input_sha256':sha(src),'status':'NO_DEVICE_CODE_REJECTED_NOT_EMPTY_SUCCESS','list_exit':listed.returncode})
        continue
    assert listed.returncode==0
    out=dest/'images';out.mkdir()
    env=dict(os.environ);env.pop('LD_PRELOAD',None)
    env.update(LD_PRELOAD=str(S),EP_CUBIN_OUTPUT_ROOT=str(out),EP_CUBIN_ALLOWED_BASENAMES=':'.join(sorted(set(names))))
    extracted=run([T,'--extract-elf','all',src],out,env)
    (dest/'extract.stdout').write_text(extracted.stdout);(dest/'extract.stderr').write_text(extracted.stderr)
    assert extracted.returncode==0,extracted.stderr
    messages=re.findall(r'^Extracting ELF file\s+\d+: ([A-Za-z0-9_.-]+)$',extracted.stdout,re.M)
    assert messages==names
    files=sorted(out.iterdir());assert len(files)==len(names)
    images=[]
    for index,(p,original) in enumerate(zip(files,names),1):
        assert not p.is_symlink() and p.name==('image_%06d__'%index)+original
        assert p.read_bytes()[:4]==b'\x7fELF'
        before=sha(p)
        hdr=run(['/usr/bin/readelf','-h',p],dest);sym=run(['/usr/bin/readelf','-Ws',p],dest)
        sections=run(['/usr/bin/readelf','-SW',p],dest)
        sass=run([T,'--dump-sass',p],dest)
        for label,cp in [('header',hdr),('symbols',sym),('sections',sections),('sass',sass)]:
            assert cp.returncode==0,cp.stderr
            (dest/(p.name+'.'+label+'.txt')).write_text(cp.stdout)
        assert 'NVIDIA CUDA' in hdr.stdout and 'sm_89' in sass.stdout
        functions=re.findall(r'Function\s*:\s*(\S+)',sass.stdout)
        if functions:
            assert 'FUNC' in sym.stdout and '.text.' in sections.stdout
        else:
            assert 'FUNC' not in sym.stdout and '.text' not in sections.stdout
        assert sha(p)==before
        images.append({'ordinal':index,'original_basename':original,'path':str(p),'bytes':p.stat().st_size,'sha256':before,'functions':functions,'empty_code_image':not functions,'sass_sha256':hashlib.sha256(sass.stdout.encode()).hexdigest(),'header_sha256':hashlib.sha256(hdr.stdout.encode()).hexdigest(),'symbol_sha256':hashlib.sha256(sym.stdout.encode()).hexdigest(),'sections_sha256':hashlib.sha256(sections.stdout.encode()).hexdigest()})
    assert sha(src)==case['input_sha256']
    cases.append({'input':str(src),'input_sha256':sha(src),'listed_images':len(names),'retained_images':len(images),'duplicate_names':len(set(names))!=len(names),'images':images,'status':'EVERY_LISTED_IMAGE_PRESERVED_AND_CPU_ELF_SYMBOL_SASS_READBACK_PASS'})

collision=cases[0]
assert collision['duplicate_names'] and collision['retained_images']==2
assert collision['images'][-1]['sha256']=='15de6d3a4ab42873350b0e378bd5dfba73e579747576b36115496f48eea25254'
# Different bytes establish the preexisting overwrite lost a distinct image.
assert len({x['sha256']for x in collision['images']})==2
assert not cases[1]['duplicate_names'] and cases[1]['retained_images']==2

# No supported output directory: listed-output truncation must fail closed.
bad=D/'negative_wrong_root';bad.mkdir()
env=dict(os.environ);env.update(LD_PRELOAD=str(S),EP_CUBIN_OUTPUT_ROOT=str(D/'case_0/images'),EP_CUBIN_ALLOWED_BASENAMES='3mm.sm_89.cubin')
cp=run([T,'--extract-elf','all',repro['cases'][0]['input']],bad,env)
(D/'negative_wrong_root.stdout').write_text(cp.stdout);(D/'negative_wrong_root.stderr').write_text(cp.stderr)
assert cp.returncode!=0 and not list(bad.iterdir())

receipt={'status':'EXTRACT_ONLY_DUPLICATE_IMAGE_PRESERVATION_CPU_QUALIFICATION_PASS','scope':'Pinned cuobjdump12.8 / actual listed ELF images; not loaded-image coverage, producer semantic qualification or GPU execution','tool_sha256':sha(T),'source_sha256':sha(R/'cubin_preserve_extract_v1.c'),'shim_sha256':sha(S),'qualifier_sha256':sha(Path(__file__)),'cases':cases,'negative_wrong_root_rejected':True,'all_input_bytes_unchanged':True,'GPU_or_simulator_execution':False,'unix':time.time()}
(D/'QUALIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':receipt['status'],'images':sum(x.get('retained_images',0)for x in cases),'sha256':sha(D/'QUALIFICATION.json')}))
