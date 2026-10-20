set pagination off
set confirm off
set print elements 24
set print repeats 4
set auto-load safe-path /usr/share/gdb/auto-load:/usr/lib/x86_64-linux-gnu
handle SIGABRT stop print nopass
python
import gdb,json,os,time
sysroot=os.getcwd()
path=os.path.join(sysroot,'NATIVE_STARTED.json')
for i in range(600):
 if os.path.exists(path): break
 time.sleep(.05)
identity=json.load(open(path))['process'];pid=identity['pid']
actual=int(open('/proc/%d/stat'%pid).read().rsplit(')',1)[1].split()[19])
assert actual==identity['start_ticks'] and open('/proc/sys/kernel/random/boot_id').read().strip()==identity['boot_id']
gdb.execute('attach %d'%pid)
json.dump({'attached_process':identity,'debugger_pid':os.getpid()},open(os.path.join(sysroot,'GDB_ATTACHED.json'),'w'))
try:
 import sys
 sys.path.insert(0,'/usr/share/gcc/python')
 import libstdcxx.v6.printers
 libstdcxx.v6.printers.register_libstdcxx_printers(None)
except Exception as e:gdb.write('PRINTER_NOTE|'+str(e)+'\n')
end
continue
thread apply all bt 24
python
row={'schema':'E_ACTUAL_MAIN773_ABORT_REPLAY_STATE_V1','scope':'READ_ONLY_FAILED_FULL_INPUT_REPLAY_NO_INFERIOR_FUNCTION_CALLS','frames':[],'current_mf':None,'pending':None}
pid=gdb.selected_inferior().pid;row['inferior_pid']=pid
row['start_ticks']=int(open('/proc/%d/stat'%pid).read().rsplit(')',1)[1].split()[19]);row['boot_id']=open('/proc/sys/kernel/random/boot_id').read().strip()
try:row['stop_signal']=int(gdb.parse_and_eval('$_siginfo.si_signo'))
except Exception as e:row['signal_error']=str(e)
row['captured_sigabrt']=row.get('stop_signal')==6
f=gdb.newest_frame();directory=None
while f:
 name=f.name() or '';item={'name':name}
 try:item['line']=f.find_sal().line;item['source']=f.find_sal().symtab.fullname() if f.find_sal().symtab else None
 except Exception:pass
 if 'preview_access' in name:
  try:
   obj=f.read_var('this').dereference();p=obj['m_ft_pending'];mf=f.read_var('mf')
   row['current_mf']=int(mf);row['current_uid']=int(mf.dereference()['m_request_uid'])
   row['pending']={k:int(p[k]) for k in ['tag_index','victim_address','dirty','wad','bound','phase']}
   row['pending']['request']=int(p['request']);row['pending']['uid']=int(p['request'].dereference()['m_request_uid'])
   row['pending']['same_request']=int(p['request'])==int(mf)
   row['pending']['wad_ticket']={k:int(p['wad_ticket'][k]) for k in ['index','incarnation']}
   row['pending']['victim']={k:int(p['victim'][k]) for k in ['payload_id','generation']}
   row['request']={k:int(mf.dereference()[k]) for k in ['m_request_uid','m_sid','m_tpc','m_wid']}
   row['request']['access']={}
   for k in ['m_addr','m_type','m_write','m_req_size','m_sector_mask']:
    try:row['request']['access'][k]=str(mf.dereference()['m_access'][k])
    except Exception as e:row['request']['access'][k+'_error']=str(e)
   try:
    ptrs=list(gdb.default_visualizer(obj['m_tvd']).children())
    for n,v in ptrs:
     if v.type.code==gdb.TYPE_CODE_PTR and int(v):directory=v.dereference();break
   except Exception as e:item['cache_directory_error']=str(e)
  except Exception as e:item['state_error']=str(e)
 if 'preview_install' in name:
  for k in ['line','dirty','native_owner_proven_unique']:
   try:item[k]=int(f.read_var(k))
   except Exception as e:item[k+'_error']=str(e)
  if directory is None:
   try:directory=f.read_var('this').dereference()
   except Exception as e:item['directory_error']=str(e)
 row['frames'].append(item);f=f.older()
if directory is not None and row['pending'] is not None:
 target=row['pending']['victim_address'];matches=[]
 try:
  vis=gdb.default_visualizer(directory['m_entries'])
  if vis:
   for i,(n,e) in enumerate(vis.children()):
    if int(e['status']) and int(e['line'])==target:
     entry={k:int(e[k]) for k in ['status','line','incarnation','readers','wb_uid_bound','wb_request_uid']}
     entry['index']=i;entry['payload']={k:int(e['payload'][k]) for k in ['payload_id','generation']};matches.append(entry)
  row['matching_existing_rows']=matches
 except Exception as e:row['existing_rows_error']=str(e)
json.dump(row,open(os.path.join(sysroot,'ABORT_STATE.json'),'w'),indent=2)
gdb.write('\nE_CONV_F_ABORT_REPLAY_STATE|'+json.dumps(row,sort_keys=True)+'\n')
end
kill
quit
