"""Narrow /proc disappearance recovery for new attempts;never invent PID evidence."""
import ast,pathlib,hashlib,json,time,os,copy
P=pathlib.Path;PROFILE='OBSERVER_PROC_EXIT_RACE_V1'
def digest(data):return hashlib.sha256(data).hexdigest()
def children(path):
 try:return P(path).read_text().split()
 except (FileNotFoundError,ProcessLookupError):return []
def note(output,launcher,observations,phase):
 record={'schema':PROFILE,'phase':phase,'observed_monotonic_ns':time.monotonic_ns(),'observer_pid':os.getpid(),'launcher_pid':launcher.pid,'actual_launcher_poll_returncode':launcher.poll(),'last_observed_generation':observations[0] if observations else None,'action':'No stale identity synthesized;recheck actual launcher state at next loop condition'}
 with (P(output)/'OBSERVER_PROC_EXIT_RACE_EVENTS.jsonl').open('a') as f:f.write(json.dumps(record)+'\n');f.flush()
def missing_handler(phase,node):
 call=ast.Expr(value=ast.Call(func=ast.Name(id='_observer_race_note',ctx=ast.Load()),args=[ast.Name(id='out',ctx=ast.Load()),ast.Name(id='p',ctx=ast.Load()),ast.Name(id='observations',ctx=ast.Load()),ast.Constant(value=phase)],keywords=[]));handler=ast.ExceptHandler(type=ast.Tuple(elts=[ast.Name(id='FileNotFoundError',ctx=ast.Load()),ast.Name(id='ProcessLookupError',ctx=ast.Load())],ctx=ast.Load()),name=None,body=[call,ast.Continue()]);return ast.copy_location(ast.Try(body=[node],handlers=[handler],orelse=[],finalbody=[]),node)
def transformed(source):
 module=ast.parse(source);matches=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='run_native'];assert len(matches)==1;fn=copy.deepcopy(matches[0]);counts={'children':0,'child_info':0,'faults':0,'process_lookup_exception_extensions':0}
 class Narrow(ast.NodeTransformer):
  def visit_IfExp(self,node):
   text=ast.unparse(node)
   if text=='childfile.read_text().split() if childfile.exists() else []':counts['children']+=1;return ast.copy_location(ast.Call(func=ast.Name(id='_observer_race_children',ctx=ast.Load()),args=[ast.Name(id='childfile',ctx=ast.Load())],keywords=[]),node)
   return self.generic_visit(node)
  def visit_Assign(self,node):
   if len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
    name=node.targets[0].id;text=ast.unparse(node.value)
    if name=='native' and text=="child_info(observations[0]['pid'])":counts['child_info']+=1;return missing_handler('MODEL_IDENTITY_DISAPPEARED_AT_EXIT',node)
    if name=='faults' and "'/proc'" in text and "'stat'" in text and 'observations' not in text and "native['pid']" in text:counts['faults']+=1;return missing_handler('MODEL_STAT_DISAPPEARED_AT_EXIT',node)
   return self.generic_visit(node)
  def visit_ExceptHandler(self,node):
   if isinstance(node.type,ast.Name) and node.type.id=='FileNotFoundError':node.type=ast.Tuple(elts=[ast.Name(id='FileNotFoundError',ctx=ast.Load()),ast.Name(id='ProcessLookupError',ctx=ast.Load())],ctx=ast.Load());counts['process_lookup_exception_extensions']+=1
   elif isinstance(node.type,ast.Tuple) and any(isinstance(n,ast.Name) and n.id=='FileNotFoundError' for n in node.type.elts) and not any(isinstance(n,ast.Name) and n.id=='ProcessLookupError' for n in node.type.elts):node.type.elts.append(ast.Name(id='ProcessLookupError',ctx=ast.Load()));counts['process_lookup_exception_extensions']+=1
   return self.generic_visit(node)
 fn=Narrow().visit(fn);ast.fix_missing_locations(fn);assert counts['children']==counts['child_info']==counts['faults']==1 and counts['process_lookup_exception_extensions']>=2,counts;code=ast.unparse(fn)+'\n';return code,counts
def install(native):
 assert not hasattr(native,'_OBSERVER_PROC_RACE_BINDING'),'Do not re-install'
 base=P(native.__file__);source=base.read_text();code,counts=transformed(source);binding={'profile':PROFILE,'adapter_path':str(P(__file__).resolve()),'adapter_sha256':digest(P(__file__).read_bytes()),'base_native_source_path':str(base),'base_native_source_sha256':digest(base.read_bytes()),'transformed_run_native_source_sha256':digest(code.encode()),'transformation_counts':counts,'identity_snapshots_synthesized':False,'telemetry_or_scientific_completion_rules_changed':False};original_exclusive=native.exclusive
 def exclusive(path,obj):
  if P(path).name.endswith('.INTENT.json') or P(path).name in ['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:obj=dict(obj,observer_exit_race_binding=binding)
  return original_exclusive(path,obj)
 native._observer_race_children=children;native._observer_race_note=note;exec(compile(code,str(P(__file__).resolve())+'::qualified_run_native','exec'),native.__dict__);native.exclusive=exclusive;native._OBSERVER_PROC_RACE_BINDING=binding;return native
