import os,sys,subprocess,resource,json
os.nice(15);resource.setrlimit(resource.RLIMIT_AS,(4<<30,4<<30))
a=[x for x in sys.argv[1:] if x not in ["-g","-g0","-g1","-g2","-g3","-ggdb","-ggdb3"]]
a+=["-g0","-UNDEBUG"]
fd=os.open("/root/share/mnt164/huangrulin/ep_l2_next_cost_aware_20261107_v1/agent_a/FINAL_COMPILER_EFFECTIVE_ARGV.jsonl",os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
os.write(fd,(json.dumps(dict(pid=os.getpid(),argv=a,cwd=os.getcwd(),assertions_enabled=True))+"\n").encode());os.close(fd)
raise SystemExit(subprocess.run(a,timeout=300).returncode)
