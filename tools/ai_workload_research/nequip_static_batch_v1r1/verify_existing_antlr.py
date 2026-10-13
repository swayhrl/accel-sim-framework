import pathlib,os,json,zipfile,hashlib,subprocess,sys,importlib.metadata as md
from packaging.utils import parse_wheel_filename
from packaging.tags import sys_tags
root=pathlib.Path(os.environ['TASK_DATA']);raw=root/'raw';r=json.loads((raw/'PACKAGING_EXCEPTION_RECEIPT.json').read_text());assert r['build_attempts']==1 and r['build_returncode']==0
w=next((root/'wheelhouse').glob('antlr4_python3_runtime-4.9.3-*.whl'));name,version,build,tags=parse_wheel_filename(w.name);assert str(version)=='4.9.3' and tags.intersection(set(sys_tags()))
source=next((root/'antlr_build_source').glob('*/bin/pygrun')).read_bytes();setup=next((root/'antlr_build_source').glob('*/setup.py')).read_text();assert 'scripts=["bin/pygrun"]' in setup
with zipfile.ZipFile(w) as z:
 members=z.namelist();scripts=[n for n in members if '.data/scripts/' in n];assert len(scripts)==1 and scripts[0].endswith('/pygrun')
 generated=z.read(scripts[0]);assert generated.split(b'\n',1)[1]==source.split(b'\n',1)[1], 'script body changed'
 assert not any(x in generated for x in [b'urlopen',b'requests.',b'os.system',b'subprocess.'])
 meta=z.read(next(n for n in members if n.endswith('/METADATA'))).decode();wheelmeta=z.read(next(n for n in members if n.endswith('/WHEEL'))).decode();assert '\nVersion: 4.9.3\n' in meta
 for n in members:assert not n.startswith('/') and '..' not in pathlib.PurePosixPath(n).parts
(raw/'ANTLR_WHEEL_METADATA.txt').write_text(meta);(raw/'ANTLR_WHEEL_TAGS.txt').write_text(wheelmeta);(raw/'ANTLR_WHEEL_MEMBERS.json').write_text(json.dumps(members,indent=2)+'\n');(raw/'ANTLR_PYGRUN_SOURCE.py').write_bytes(source);(raw/'ANTLR_PYGRUN_WHEEL.py').write_bytes(generated)
r.update(wheel_filename=w.name,wheel_sha256=hashlib.sha256(w.read_bytes()).hexdigest(),wheel_bytes=w.stat().st_size,wheel_tags=sorted(map(str,tags)),unexpected_scripts=False,expected_script='pygrun declared in official setup.py; body byte-identical, only wheel-standard shebang differs',mechanical_repairs=1,repair='Over-strict no-scripts validator corrected to exact official declared-script verification; no rebuild or wheel edit',build_cache_note='Initial pip wheel also wrote its default global pip wheel cache; retained untouched. Subsequent commands use task-local PIP_CACHE_DIR.')
subprocess.run([sys.executable,'-m','pip','install','--no-deps','--no-index',str(w)],check=True,stdout=(raw/'ANTLR_INSTALL.log').open('w'),stderr=subprocess.STDOUT)
import antlr4
assert md.version('antlr4-python3-runtime')=='4.9.3';r.update(status='PACKAGING_SOURCE_WHEEL_PASS_ANTLR_ONLY',isolated_antlr_import='PASS',import_path=antlr4.__file__,error=None,traceback=None)
(raw/'PACKAGING_EXCEPTION_RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n');(root/'V1R1_DERIVED_WHEEL_LOCK').write_text(json.dumps({'distribution':'antlr4-python3-runtime','version':'4.9.3','official_sdist_sha256':r['sdist_sha256'],'local_wheel_sha256':r['wheel_sha256'],'wheel_filename':w.name,'original_lock_unchanged':True,'scope':'Only ANTLR artifact hash derived; all82 resolved versions unchanged'},indent=2)+'\n');print(json.dumps(r),flush=True)
