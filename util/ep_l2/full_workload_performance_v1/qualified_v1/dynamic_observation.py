# Exact low-level observation helpers from17b; modifications explicitly indexed.
import os,json,re,pathlib,hashlib,stat
P=pathlib.Path;M=1<<20;G=1<<30
N=P('/root/data/ep_l2_dtc_l1_native_v2')
class Hold(RuntimeError):pass
def need(x,msg):
 if not x:raise Hold(msg)
def sha(path):
 h=hashlib.sha256()
 with P(path).open('rb')as f:
  for b in iter(lambda:f.read(M),b''):h.update(b)
 return h.hexdigest()

def syscall_proof(path,s,model_pid=None):
 # This is the only changed baseline helper function. No process is launched.
 need(type(model_pid)is int and model_pid>0,'actual observed model PID required')
 kernels=s['all_unique_kernel_members'];need(type(kernels)is list and kernels,'frozen complete unique kernel table required; no inherited64 cap')
 for item in kernels:need(type(item)is dict and type(item.get('path'))is str and item['path']and len(item.get('sha256',''))==64,'exact frozen kernel member path/content identity')
 expected={str(P(s['trace_entry'])):0}
 for item in kernels:
  filename=str(P(item['path']));need(filename not in expected,'duplicate unique member path');expected[filename]=0
 records=[];edges={};unfinished={};execs=0;forks=0
 def pid_body(line):
  m=re.match(r'^\s*(?:\[pid\s+(\d+)\]|(\d+))\s+(.*)$',line)
  need(m is not None,'strace PID prefix absent; cannot infer process scope')
  return int(m.group(1)or m.group(2)),m.group(3)
 with P(path).open(errors='replace')as stream:
  for line in stream:
   need('connect('not in line,'unexpected traced network connect')
   pid,body=pid_body(line.rstrip('\n'))
   if '<unfinished ...>'in body:unfinished[pid]=body.split('<unfinished ...>',1)[0];continue
   resumed=re.match(r'<\.\.\. (\w+) resumed>(.*)',body)
   if resumed:
    need(pid in unfinished and unfinished[pid].lstrip().startswith(resumed.group(1)+'('),'unmatched resumed syscall')
    body=unfinished.pop(pid)+resumed.group(2)
   if re.search(r'\bexecve(?:at)?\(',body):
    execs+=1;need(not re.search(r'(?i)(?:^|[/ ])ssh(?:[ .,/]|$)',body.replace(chr(34),' ').replace(chr(39),' ')),'unexpected traced ssh exec')
   fork=re.match(r'(?:fork|vfork|clone|clone3)\(.*\)\s*=\s*(\d+)(?:\s|$)',body)
   if fork:
    forks+=1;child=int(fork.group(1))
    if child>0:
     need(child not in edges or edges[child]==pid,'ambiguous traced child parent');edges[child]=pid
   if re.search(r'\bopen(?:at|at2)?\(',body)and re.search(r'\)\s*=\s*[0-9]+(?:\s|$)',body):records.append((pid,body))
 permitted={model_pid}
 for _ in range(len(edges)+1):
  nxt=permitted|{child for child,parent in edges.items()if parent in permitted}
  if nxt==permitted:break
  permitted=nxt
 opened_pids={}
 for pid,body in records:
  if pid not in permitted:continue
  for filename in expected:
   if json.dumps(filename)in body:expected[filename]+=1;opened_pids.setdefault(filename,set()).add(pid)
 need(all(expected.values()),'actual successful open missing for declared commandlist/unique kernel member')
 return {'status':'CLOSED_LOCAL_SYSCALL_INPUT_NETWORK_PROOF_PASS','syscall_log_sha256':sha(path),'successful_input_opens':expected,'successful_input_open_pids':{p:sorted(v)for p,v in opened_pids.items()},'no_connect':True,'no_ssh_exec':True,'traced_exec_calls':execs,'traced_fork_calls':forks,'model_pid':model_pid,'permitted_model_descendant_pids':sorted(permitted),'input_open_scope':'exact observed model PID and proven traced descendants only; successful return required','unique_kernel_members_required':len(kernels),'kernel1_special_case_removed':True}



def command(s,out=None):
 args=[str(N/'common-lib/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(N/'EP/env/lib'),s['binary_path'],'-trace',s['trace_entry']]
 for c in s['ordered_configs']:args+=['-config',str(P(out)/P(c['path']).name) if out is not None else c['path']]
 return args


def launch_command(s,out):
 return [str(N/'common-lib/ld-linux-x86-64.so.2'),'--library-path',str(N/'tools/lib')+':'+str(N/'common-lib'),str(N/'tools/bin/strace'),'-f','-e','trace=%file,process,network','-o',str(P(out)/'actual_file_process_network.log'),'--',*command(s,out)]


def info(pid):
 p=P('/proc')/str(pid);parts=(p/'stat').read_text().rsplit(')',1)[1].split()
 return {'pid':pid,'parent_pid':int(parts[1]),'start_ticks':int(parts[19]),'process_state':parts[0],
  'boot_id':P('/proc/sys/kernel/random/boot_id').read_text().strip(),
  'mnt_namespace':os.readlink(p/'ns/mnt'),'exe':os.readlink(p/'exe'),
  'cmdline':(p/'cmdline').read_bytes().split(b'\0')[:-1],
  'environment':dict(x.split(b'=',1) for x in (p/'environ').read_bytes().split(b'\0') if b'=' in x),
  'maps':(p/'maps').read_text(),'limits':(p/'limits').read_text(),
  'affinity':sorted(os.sched_getaffinity(pid)),'nice':os.getpriority(os.PRIO_PROCESS,pid)}


def serializable_info(v):
 return {**v,'cmdline':[x.decode(errors='replace') for x in v['cmdline']],
  'environment':{a.decode():b.decode() for a,b in v['environment'].items()}}


def process_tree(pid):
 stack=[pid];seen=set()
 while stack:
  n=stack.pop()
  if n in seen:continue
  seen.add(n);need(len(seen)<=32,'unexpected process tree')
  p=P('/proc')/str(n)/'task'/str(n)/'children'
  try:stack += [int(x) for x in p.read_text().split()]
  except (FileNotFoundError,ProcessLookupError):pass
 return sorted(seen)


def rss(pid):
 try:return int(next(x.split()[1] for x in (P('/proc')/str(pid)/'status').read_text().splitlines() if x.startswith('VmRSS:')))*1024
 except (FileNotFoundError,ProcessLookupError,StopIteration):return 0


def pid_generation_live(v):
 try:
  parts=(P('/proc')/str(v['pid'])/'stat').read_text().rsplit(')',1)[1].split()
  return int(parts[19])==v['start_ticks'] and parts[0] not in ('Z','X')
 except (FileNotFoundError,ProcessLookupError):return False


def verify_actual(v,s,args,env):
 need(v['mnt_namespace']=='mnt:[4026535153]' and v['boot_id']=='59e1e1a4-84b6-431f-ac2d-03e340207019','actual native domain drift')
 need(v['cmdline']==[x.encode() for x in args] and v['environment']=={k.encode():v.encode() for k,v in env.items()},'actual command/environment drift')
 need(v['affinity']==[s['host_cpu']] and v['nice']==10,'actual CPU/nice drift')
 need(s['binary_path'] in v['maps'],'new ELF not mapped')
 need('/root/data/ep_l2_dtc_l1_native_v2/EP/src/' not in v['maps'],'protected old core unexpectedly mapped')
 mapped=[]
 for line in v['maps'].splitlines():
  fields=line.split(maxsplit=5)
  if len(fields)==6 and fields[5].startswith('/'):
   path=fields[5]
   if path.endswith(' (deleted)'):raise Hold('deleted mapped file')
   if path not in mapped:mapped.append(path)
 allowed={s['binary_path']:s['source_identity']['binary_sha256']}
 # Exact loader/libs, old copies remain read-only runtime assets, not old Core.
 allowed.update({p:h for p,h in s['pinned_files'].items() if '/env/lib/' in p or '/common-lib/' in p})
 for path in mapped:need(path in allowed and sha(path)==allowed[path],'unqualified actual mapped ELF/library '+path)
 match=re.search(r'^Max address space\s+(\d+)\s+(\d+)\s+bytes',v['limits'],re.M);need(match and int(match[1])==int(match[2])==s['limits']['AS_bytes'],'actual exact dynamicAS cap drift')
 return {'mapped_file_sha256':{p:allowed[p] for p in mapped},'actual_environment_exact':True}


def tree_bytes(root,limit=20000):
 root=P(root);total=0;count=0
 if not root.exists():return 0
 for parent,dirs,files in os.walk(root,followlinks=False):
  for d in dirs:need(not (P(parent)/d).is_symlink(),'unexpected directory link')
  for name in files:
   p=P(parent)/name;t=p.lstat();count+=1
   need(count<=limit and stat.S_ISREG(t.st_mode),'unbounded/nonregular output')
   total+=t.st_size
 return total


def footprint(root):
 root=P(root)
 if not root.exists():return 0
 seen=set();logical=allocated=0
 def observe(p):
  nonlocal logical,allocated
  st=p.lstat();need(stat.S_ISDIR(st.st_mode)or stat.S_ISREG(st.st_mode),'unexpected output link/special file')
  identity=(st.st_dev,st.st_ino)
  if identity in seen:return
  seen.add(identity);allocated+=st.st_blocks*512
  if stat.S_ISREG(st.st_mode):logical+=st.st_size
 observe(root)
 for parent,dirs,files in os.walk(root,followlinks=False):
  for name in dirs+files:observe(P(parent)/name)
 return max(logical,allocated)
