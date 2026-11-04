import pathlib,json,hashlib
V=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_cpu_preparation_20261105_v1');A=V/'agents/A_tag_liveness_v1';D=V/'agents/D_independent_review_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
j=json.loads((A/'A1_PARAMETER_CONFIGS_AND_PLAN16.json').read_text());authority=json.loads(pathlib.Path(j['authority_path']).read_text());checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
ck('Authority source exact SHA',sha(pathlib.Path(j['authority_path']))==j['authority_sha256']=='0b9cd6dfe3c397e32ce286ef068717ac4dd563b65855dd245a4fceb08fdadfa1');ck('Exactly16 plans2uniformorganizations',len(j['rows'])==16 and len(j['variants'])==2)
byprogram={x['population']['program']:x for x in authority['inputs']};seen=set();configseen=set();topvariants={z['variant']:z for z in j['variants']}
for r in j['rows']:
 ident=r['program']+r['variant'];base=next(z for z in byprogram[r['program']]['P0_references'] if z['source_cell']=='DH');v=topvariants[r['variant']]
 ck('Frozen program/input '+ident,r['input_digest']==byprogram[r['program']]['population']['input_digest']==base['input_digest']);ck('Not authorized or consumed '+ident,r['science_execution_authorized'] is False and r['native_cohort'] is None and r['native_UUID'] is None)
 opts=r['expected_effective_options270'];expected=dict(base['effective_options']);expected['-gpgpu_dtc_l1_logical_sets']=[str(v['logical_sets'])];expected['-gpgpu_dtc_l1_logical_ways']=[str(v['ways'])];ck('Only2Tagshape flags '+ident,len(opts)==270 and opts==expected);ck('Still512Tags640physical128PIB '+ident,v['logical_sets']*v['ways']==512 and v['physical_lines']==640 and opts['-gpgpu_dtc_l1_physical_lines']==['640'] and opts['-gpgpu_dtc_l1_oo_pib_entries']==['128']);ck('Same input expected execution '+ident,r['expected']==base['expected']);ck('Same pinned binding '+ident,r['input_binding']==base['input_binding']);pin=r['input_binding'];ck('Binding SHA '+ident,sha(pathlib.Path(pin['path']))==pin['sha256']);ck('Accepted exact original DH-P0 source '+ident,sha(pathlib.Path(base['source_RESULT_path']))==base['source_RESULT_sha256'] and base['accepted'])
 for c in r['configs']:
  if c['path'] in configseen:continue
  configseen.add(c['path']);ck('Tag config bytes '+c['path'],sha(pathlib.Path(c['path']))==c['sha256'])
 seen.add((r['input_digest'],r['variant']))
ck('16 distinct inputorganization pairs',len(seen)==16);ck('No requests/models and largerTagHOLD unchanged',j['no_requests_registered'] is True and j['models_started']==0 and j['original_V1_Tag16_HOLD_unchanged'] is True)
p=D/'INDEPENDENT_A1_PLAN16_REVIEW.json';assert not p.exists();p.write_text(json.dumps({'checks':checks,'A1_matrix_path':str(A/'A1_PARAMETER_CONFIGS_AND_PLAN16.json'),'A1_matrix_sha256':sha(A/'A1_PARAMETER_CONFIGS_AND_PLAN16.json'),'scope':'16 separately proposed Tag512 parameter plans; exact frozen input/baseline/config/options, no registration/UUID/execution approval. Retain documented fixed-domain conditional liveness, mapping+associativity coupling and hardware timing boundaries.','new_models':0},indent=2)+'\n');print(json.dumps({'checks':len(checks),'PASS':True,'sha256':sha(p)}))
