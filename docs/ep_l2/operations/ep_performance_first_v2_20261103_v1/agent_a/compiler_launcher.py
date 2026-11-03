import os,sys,pathlib,subprocess,json,fcntl,time,resource
A=pathlib.Path(__file__).resolve().parent
os.sched_setaffinity(0,{18,19});resource.setrlimit(resource.RLIMIT_AS,(4<<30,4<<30))
a=[v for v in sys.argv[1:] if v not in ['-g','-g0','-g1','-g2','-g3','-ggdb','-ggdb3']]+['-g0']
t=time.monotonic();p=subprocess.run(a,env=dict(os.environ,CUDA_VISIBLE_DEVICES=''),timeout=300)
with (A/'COMPILER_COMMANDS.jsonl').open('a') as f:
 fcntl.flock(f,fcntl.LOCK_EX);f.write(json.dumps({'effective':a,'returncode':p.returncode,'seconds':time.monotonic()-t})+'\n')
sys.exit(p.returncode)
