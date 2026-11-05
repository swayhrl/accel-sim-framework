import os,sys,subprocess,resource
os.nice(15)
resource.setrlimit(resource.RLIMIT_AS,(4<<30,4<<30))
a=[x for x in sys.argv[1:] if x not in ['-g','-g0','-g1','-g2','-g3','-ggdb','-ggdb3']]
raise SystemExit(subprocess.run(a+['-g0'],timeout=300).returncode)
