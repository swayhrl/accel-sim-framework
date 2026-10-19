"""Finite, event-proven ownership. PPID/tracer evidence alone only quarantines."""
import os,time
from pathlib import Path
from mapping_roles import require
CONFIRM_SECONDS=2.0

def identity(pid):
 q=Path('/proc')/str(pid)
 s=(q/'stat').read_text().rsplit(')',1)[1].split()
 status=dict(l.split(':',1) for l in (q/'status').read_text().splitlines() if ':' in l)
 return dict(pid=int(pid),start_ticks=int(s[19]),ppid=int(s[1]),state=s[0],tgid=int(status['Tgid']),tracer_pid=int(status['TracerPid']))

class Ownership:
 def __init__(self,root):
  self.tracer=os.getpid();self.root=root;self.confirmed={root:identity(root)};self.pending={};self.events=[];self.retired=[]
 def same(self,pid):
  require(pid in self.confirmed,'UNCONFIRMED_PROCESS_INSTANCE')
  live=identity(pid)
  require(live['start_ticks']==self.confirmed[pid]['start_ticks'],'OWN_PID_REUSED')
  require(live['tracer_pid']==self.tracer,'OWN_TRACER_CHANGED')
  require(live['tgid']==self.confirmed[pid]['tgid'],'OWN_THREAD_GROUP_CHANGED')
  return live
 def retire(self,pid):
  # Called only after consuming this current, unreaped child's terminal wait.
  # /proc may already be gone: never infer a new instance from an exit status.
  require(pid in self.confirmed,'UNCONFIRMED_TERMINAL_WAIT')
  self.retired.append(self.confirmed.pop(pid));self.pending.pop(pid,None)
 def quarantine(self,pid,source):
  live=identity(pid)
  require(live['tracer_pid']==self.tracer and live['state'] in ('t','T'),'PENDING_NOT_OWN_TRACEE_STOP')
  if pid in self.confirmed:self.same(pid);return
  prior=self.pending.get(pid)
  if prior:require(prior['identity']['start_ticks']==live['start_ticks'],'PENDING_PID_REUSED')
  else:self.pending[pid]=dict(identity=live,first_monotonic=time.monotonic(),source=source)
 def confirm(self,parent,child,event):
  require(event in (1,2,3),'NOT_PTRACE_PARENT_EVENT')
  require(parent in self.confirmed,'WRONG_UNCONFIRMED_PARENT')
  par=self.same(parent);new=identity(child)
  require(new['tracer_pid']==self.tracer,'CHILD_WRONG_TRACER')
  require(new['ppid']==parent or (new['tgid']==par['tgid'] and new['ppid']==par['ppid']),'PARENT_EVENT_ANCESTRY_CONTRADICTION')
  require(child not in self.confirmed,'DUPLICATE_FORK_EVENT')
  prior=self.pending.get(child)
  if prior:require(prior['identity']['start_ticks']==new['start_ticks'],'PENDING_PID_REUSED')
  self.confirmed[child]=new;self.pending.pop(child,None)
  row=dict(parent_pid=parent,parent_start_ticks=par['start_ticks'],new_owned_pid=child,child_start_ticks=new['start_ticks'],child_ppid=new['ppid'],child_tgid=new['tgid'],event=event,proof='PTRACE_GETEVENTMSG_FROM_CONFIRMED_PARENT')
  self.events.append(row);return row
 def classify(self,p):
  pid=p['pid']
  if pid in self.confirmed:
   require(p['start_ticks']==self.confirmed[pid]['start_ticks'],'AUTHORITY_OWN_PID_REUSED')
   self.same(pid);return 'CONFIRMED'
  try:live=identity(pid)
  except (OSError,ValueError):return 'UNKNOWN'
  if live['start_ticks']!=p['start_ticks']:return 'UNKNOWN'
  # This admits no ownership: pending makes the whole authority verdict non-PASS.
  if live['tracer_pid']==self.tracer and live['state'] in ('t','T'):
   self.quarantine(pid,'PERIODIC_OBSERVER_BEFORE_PARENT_EVENT');return 'PENDING'
  return 'UNKNOWN'
 def check_deadlines(self):
  for pid,p in self.pending.items():
   require(time.monotonic()-p['first_monotonic']<=CONFIRM_SECONDS,'PARENT_EVENT_CONFIRMATION_TIMEOUT:'+str(pid))
 def snapshot(self):return dict(confirmed=list(self.confirmed.values()),pending=list(self.pending.values()),retired=self.retired,confirmation_seconds=CONFIRM_SECONDS,proof_events=len(self.events))
