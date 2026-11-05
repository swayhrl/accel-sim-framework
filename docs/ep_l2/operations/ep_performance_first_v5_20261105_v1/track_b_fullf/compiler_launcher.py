import hashlib,json,os,subprocess,sys,time,uuid
from pathlib import Path
V=Path(__file__).resolve().parent
args=sys.argv[1:];assert args and Path(args[0]).name in ['c++','g++','gcc','cc','clang++']
args=['-g0'if x=='-g3'else x for x in args]
if '-c'in args:args+=['-UNDEBUG']
began=time.monotonic();p=subprocess.run(args);record=dict(argv=args,returncode=p.returncode,seconds=time.monotonic()-began)
if '-c'in args:
 src=Path(args[args.index('-c')+1]);obj=Path(args[args.index('-o')+1]);record.update(source=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),object=str(obj.resolve()))
 if p.returncode==0:record['object_sha256']=hashlib.sha256(obj.read_bytes()).hexdigest()
 (V/'build_records'/(hashlib.sha256(str(src).encode()).hexdigest()+'.json')).write_text(json.dumps(record,indent=2)+'\n')
sys.exit(p.returncode)
