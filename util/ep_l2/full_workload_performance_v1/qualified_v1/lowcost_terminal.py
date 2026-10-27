"""Streaming lossless-gzip / plain terminal validation components for this Goal.
Only pure frozen math AST is evaluated. No old authority, controller import, actor,
max16/max64 catalog or optional LIFE/R4/R5/ET requirement. Never writes acceptance.
First supported physical profile is REF32x8_L100 (1168/1024/128/16,MSHR128,desc512).
Other finite resource families require a separately reviewed math extension, not silent acceptance.
"""
import ast,copy,gzip,hashlib,json,pathlib,re
P=pathlib.Path
GOAL='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1'
COMMON=P('/root/data/ep_l2_dtc_l1_native_v2/EP/control/parse_main_terminal.py')
FT=COMMON.parents[1]/'src/owner-control/util/ep_l2/ft_lane5'
PINS={str(COMMON):'f518aed003f2f70a4d84afc95c215773da2c14761315349b7600655a1e549c8e',str(FT/'parse_unified_terminal.py'):'536d1a8d55452b7aee5b84168648b228eb35cc5e82b523e81b59634c51db352b'}
PINS[str(FT/'validate.py')]='08a7396a6e11893dbbcb982725765a6c9b12194b1e01e3f0dc70d337f85dd500'
U64=(1<<64)-1;OPTIONAL=('EPL2DETACH_DIAG_V1|','EPL2TAGPRESSUREV1|','EPL2TAGPRESSURE_GEOMETRY_V1|','EPL2LIFEV1|','EPETV1|')
class InvalidEvidence(ValueError):pass
def need(v,msg):
 if not v:raise InvalidEvidence(msg)
def sha(path):
 h=hashlib.sha256()
 with P(path).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def doc(p):return json.loads(P(p).read_bytes())if isinstance(p,(str,P))else copy.deepcopy(p)
def exact(ref):need(sha(ref['path'])==ref['sha256'],'ref drift '+ref['path']);return doc(ref['path'])
class RawPath:
 def __init__(self,p):self.p=P(p.p if isinstance(p,RawPath)else p)
 def __fspath__(self):return str(self.p)
 def open(self,mode='r',**kwargs):
  need(mode in ('r','rt','rb'),'read only parser')
  if self.p.suffix=='.gz':return gzip.open(self.p,'rb'if 'b'in mode else'rt',**kwargs)
  return self.p.open(mode,**kwargs)
def logical_hash(raw):
 h=hashlib.sha256();n=0
 with RawPath(raw).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b);n+=len(b)
 return h.hexdigest(),n

def function(text,name):
 n=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name==name)
 return ''.join(text.splitlines(keepends=True)[n.lineno-1:n.end_lineno])
def assignment(text,name):
 for n in ast.parse(text).body:
  if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets):return ast.literal_eval(n.value)
 raise InvalidEvidence('missing frozen assignment '+name)
def numeric_math():
 for path,digest in PINS.items():need(sha(path)==digest,'frozen numeric source drift')
 text=COMMON.read_text();full=function(text,'parse');marker='    native={};final={};frames={}';need(full.count(marker)==1,'frozen numeric extraction marker changed');body=full[full.index(marker):]
 # Preamble is a new explicit protocol-only contract. Everything from native={} onward remains original bytes.
 pre='def parse(raw,spec,qualification):\n    identity=spec["identity"]; effective=spec["profile_semantics"]["effective_options"]; profile=spec["profile"]\n    mode,copy_free,data_free=PROFILES[profile]; enabled=int(effective["-gpgpu_ep_l2_ms_observer"])\n'
 ns={'Path':RawPath,'re':re,'require':need,'digest':lambda p:logical_hash(p)[0]}
 for name in ['REASONS','PROFILES','EXEMPT']:ns[name]=assignment(text,name)
 for node in ast.parse(text).body:
  if isinstance(node,ast.Expr)and isinstance(node.value,ast.Call)and isinstance(node.value.func,ast.Attribute)and isinstance(node.value.func.value,ast.Name)and node.value.func.value.id=='PROFILES'and node.value.func.attr=='update':ns['PROFILES'].update(ast.literal_eval(node.value.args[0]))
 validator=(FT/'validate.py').read_text();ns['SUMMARY_FIELDS']=assignment(validator,'SUMMARY_FIELDS');ns['integer']=lambda n:type(n)is int and n>=0
 for src,name in [(validator,'validate_summary'),((FT/'parse_unified_terminal.py').read_text(),'parse_structure')]+[(text,n)for n in ['numbers','full_numbers','validate_full_records']]:exec(compile(function(src,name),'PINNED_PURE_'+name,'exec'),ns)
 exec(compile(pre+body,'UNCHANGED_NUMERIC_MATH_NO_OLD_AUTHORITY','exec'),ns)
 return ns['parse'],dict(numeric_body_sha256=hashlib.sha256(body.encode()).hexdigest(),frozen_common_sha256=PINS[str(COMMON)],frozen_validate_sha256=sha(FT/'validate.py'),frozen_structure_sha256=PINS[str(FT/'parse_unified_terminal.py')],authority_inherited=False,old_data_correctness_boolean_interpreted_as_protocol_only=True)

def history_for(s):
 opts=s['expected_effective_options'];need(s['mode']in ['S','F','WV_ZERO_RO'],'formal mode');need(s['geometry']==dict(slices=64,sets=32,ways=8,line_bytes=128),'first physical geometry qualified only')
 fixed={'-gpgpu_ep_l2_wbuf_entries':'16','-gpgpu_ep_l2_payload_mode':'2','-gpgpu_ep_l2_descriptor_pool_size':'512','-gpgpu_ep_l2_wad_entries':'128','-gpgpu_ep_l2_bank_ops':'1','-gpgpu_ep_l2_static_s64':'0','-gpgpu_ep_l2_wb_local_cap':'0','-gpgpu_ep_l2_diag_copy_free':'0','-gpgpu_ep_l2_diag_l2_data_free':'0'}
 need(all(opts[k]==v for k,v in fixed.items()),'new physical/service family needs independent math extension')
 mode=s['mode'];ro=mode=='F';victim=mode!='S';expected={'-gpgpu_ep_l2_ft_mode':str(1 if mode=='S'else 2),'-gpgpu_ep_l2_tvd_clean':str(int(victim)),'-gpgpu_ep_l2_tvd_dirty':str(int(victim)),'-gpgpu_ep_l2_ro_tag_detach':str(int(ro)),'-gpgpu_ep_l2_ro_line_mshr_bypass':str(int(ro))}
 need(all(opts[k]==v for k,v in expected.items()),'formal S/WV-zero/F option mismatch');need(s.get('T')is ro and s.get('M')is ro,'formal T/M declaration')
 feature=dict(payload_capacity_per_slice=1168,nominal_payload_capacity_per_slice=1168,wbuf_entries=16,ops_per_bank_cycle=1,static_s64=False,wb_local_cap=0,unified_wb=mode!='S')
 return dict(identity=dict(feature_vector=feature,termination_contract='ENTIRE_DECLARED_COMMANDLIST_AND_HARDWARE_DRAIN'),profile='S'if mode=='S'else'F',profile_semantics={'effective_options':opts,'research_switches':{'V':int(victim),'T':int(ro),'M':int(ro)}},trace_files=[{'name':'commandlist','path':s['trace_entry']}],entry_trace_name='commandlist')

def scan(raw,s):
 options={};tokens={'core':[],'framework':[]};markers={'core':'gpgpu-sim_git-commit-','framework':'accelsim-commit-'};identity=s['source_identity'];current=None;frames={};scoped={};launches=[];commands=[];native={};normal=False;count=0;optional_count=0
 prefixes={'EPL2B0V1':('slice',64),'EPL2M0AV1':('slice',64),'EPL2DRAMV1':('channel',32),'EPL2L1V1':('scope',1)};dup_prefix=('EPL2FTV1|','EPL2STRUCTV1|','EPL2B0V1|INVARIANT|','EPL2MSV1|','EPL2MSV2|','EPL2TVDV2|','EPL2TVDV3|','EPL2ROC1|','EPL2ROV1|SUMMARY|')
 with RawPath(raw).open(errors='strict')as f:
  for line in f:
   count+=1;optional_count+=int(line.startswith(OPTIONAL));normal|='GPGPU-Sim: *** exit detected ***'in line
   for key,marker in markers.items():
    ts=re.findall(re.escape(marker)+r'([0-9a-f]{7,40})(?![0-9a-f])',line);need(line.count(marker)==len(ts),'malformed banner');tokens[key]+=ts
   m=re.match(r'^(-[^\s]+)\s+(.*?)\s+#',line)
   if m:
    k,v=m.groups();v=' '.join(v.split());need(k not in options or options[k]==v,'conflicting actual option');options[k]=v
   m=re.fullmatch(r'launching kernel name:\s*(\S+)\s+uid:\s*(\d+)\s+cuda_stream_id:\s*(\d+)\s*',line)
   if m:launches.append((int(m[2]),m[1]))
   if line.startswith('Processing kernel '):commands.append(line.strip().rsplit('/',1)[-1])
   if line.startswith('launching memcpy command : '):commands.append(line.strip()[len('launching memcpy command : '):])
   m=re.fullmatch(r'gpu_tot_sim_(cycle|insn)\s*=\s*(\d+)\s*',line)
   if m:
    key,v=m[1],int(m[2]);need(v>0,'empty final counter')
    if key=='cycle':
     need(current is None or v>=current,'clock regression')
     if current!=v:frames={};scoped={p:{}for p in prefixes}
     current=v
    native[key]=v
   m=re.fullmatch(r'gpu_tot_issued_cta\s*=\s*(\d+)\s*',line)
   if m:native['CTA']=int(m[1])
   prefix=line.split('|',1)[0]
   if prefix in prefixes and '|scope=application|'in line:
    fields=line.strip().split('|')[1:];row={}
    for v in fields:
     k,v=v.split('=',1);need(k not in row,'duplicate scoped field');row[k]=v
    key,n=prefixes[prefix];owner=0 if key=='scope'else int(row[key]);need(current is not None and 0<=owner<n,'scoped clock/population')
    if prefix in ['EPL2B0V1','EPL2M0AV1']:need(int(row['completion_cycle'])==current,'scoped completion clock')
    old=scoped[prefix].get(owner);need(old is None or old==row,'same-final-cycle conflicting application owner');scoped[prefix][owner]=row
   if line.startswith(dup_prefix):
    parts=line.strip().split('|');vals=dict(x.split('=',1)for x in parts[2:]if '='in x);key=(parts[0],parts[1],vals.get('slice'),vals.get('reason'),vals.get('kernel_uid'))
    
    if parts[0]=='EPL2B0V1'and parts[1]=='INVARIANT'and vals.get('kernel_uid')!=str(U64):continue
    need(current is not None,'protocol record without clock');old=frames.get(key);need(old is None or old==line.strip(),'same-cycle conflicting physical terminal');frames[key]=line.strip()
 need(normal and set(native)=={'cycle','insn','CTA'},'natural complete native terminal')
 need(options==s['expected_effective_options']and len(options)==282,'all282 actual options mismatch')
 for key,field in [('core','core_source_commit'),('framework','framework_source_commit')]:need(tokens[key]and all(identity[field].startswith(t)for t in tokens[key]),'actual Source banner missing/conflicting '+key)
 expected=[(x['uid'],x['name'])for x in s['expected_kernel_launches']];need(launches==expected and len(set(x[0]for x in launches))==len(launches),'complete ordered launch catalog')
 binding=exact(s['input_binding_ref']);need(commands==binding.get('expectedcommands',binding.get('all_commands')),'full ordered commandlist mismatch')
 need(native['insn']==s['expected_instructions']and native['CTA']==s['expected_CTA'],'exact compatible instruction/CTA population')
 for prefix,(_,n)in prefixes.items():need(set(scoped[prefix])==set(range(n)),'complete final physical scope '+prefix)
 return dict(cycles=native['cycle'],instructions=native['insn'],CTA=native['CTA'],kernel_count=len(launches),ordered_kernel_catalog=launches,actual_options=options,banner_tokens=tokens,application_scopes=scoped,raw_lines=count,optional_records=optional_count)

def validate_case(raw,spec,qualification,sourceq_path,sourceq_sha):
 s=doc(spec);q=doc(qualification);need(s['goal']==GOAL,'new Goal only');need(s['source_identity']['core_source_commit']=='78f4b59e865b136eede74df74c44c210f5b4ca04','exact source only');need(sha(sourceq_path)==sourceq_sha,'SourceQ drift');sq=doc(sourceq_path);need(sq['source_identity']==s['source_identity'],'SourceQ identity mismatch');need(q.get('source_identity')==s['source_identity'],'new NativeQ source mismatch')
 need(all(s['observer_env'].get(k)=='0'for k in ['EPL2_DETACH_DIAG','EPL2_TAGPRESSURE_DIAG','EPL2_TAG_LIFETIME','EP_L2_EVENT_TIMELINE']),'lowcost all4optionalOFF contract');need(sha(s['binary_path'])==s['source_identity']['binary_sha256']and sha(s['static_library_path'])==s['source_identity']['archive_sha256'],'actual producer drift')
 h,n=logical_hash(raw);scopes=scan(raw,s);need(scopes['optional_records']==0,'fourOFF contract contradicted by optional observer wire');hist=history_for(s);parse,receipt=numeric_math();model=parse(RawPath(raw),hist,{})
 need(model['cycles']==scopes['cycles']and model['instructions']==scopes['instructions'],'math/generic native disagreement');model['data_correctness_qualification']=False;model['legacy_numeric_parser_protocol_checks_passed']=True;model['source_map']['mechanism']={'actual_source_identity':s['source_identity'],'legacy_numeric_source_reference_only':str(COMMON),'application_numeric_output':'UNKNOWN'}
 return dict(status='EP_FULL_PERF_VALIDATED_PENDING_MAIN_NOT_APPLICATION_ACCEPTED',goal=GOAL,cohort=s['cohort'],source_identity=s['source_identity'],input_identity_sha256=s['input_identity_sha256'],cycles=model['cycles'],instructions=model['instructions'],CTA=scopes['CTA'],kernel_count=scopes['kernel_count'],hardware_drained=True,raw_logical_sha256=h,raw_uncompressed_bytes=n,raw_stored_sha256=sha(raw),raw_stored_bytes=P(raw).stat().st_size,model=model,application=scopes,math_binding=receipt,optional_observers='ALL4_OFF_NOT_OBSERVED_NOT_MEASURED_ZERO',RO_applicability='ENABLED_EXACT_CERTIFICATE_OUTER_JOIN_REQUIRED'if s['mode']=='F'else'NOT_APPLICABLE',scientific_acceptance_granted=False,numeric_output='UNKNOWN',outer_join_required=['official consumed natural DONE+PID/argv/env/maps/strace','current source/spec/NativeQ full reference binding','exact RO certificate iff F','lossless raw receipt+result resource accounting','true164 closed archive and two sequential native verification restores'])
