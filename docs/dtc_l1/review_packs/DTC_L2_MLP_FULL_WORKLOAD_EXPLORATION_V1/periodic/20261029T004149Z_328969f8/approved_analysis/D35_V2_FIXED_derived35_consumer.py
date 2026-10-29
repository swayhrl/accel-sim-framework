"""Independent named Derived35 analysis. Import is inert; never edits runtime data.

Accepted native/archive receipts are source-bound and reused, not re-certified by
reading the large raw streams. Formal metric generation requires publication and
CPU qualification records; dry validation emits coverage only.
"""
import copy, datetime, hashlib, json, math, pathlib, re, types
P = pathlib.Path
R = P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
A = P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
CONTRACT = A/'coordinator/DERIVED35_SAME_PHYSICS_NAMED_ANALYSIS_CONTRACT_V1/CONTRACT.json'
CONTRACT_SHA = 'ec62fdbbe4c161a82c1229cdccd9de24d3104b82a7a85af0a9478a6696724210'
SCOPE_SHA = '5f079aed36eca8dd62906bdfaa68006d3b3f27964c506a03361f2fab0908d1d2'
MAP_SHA = 'cc54c2cfc9fc17e807764181634e3a912a766db785c10dba02993c376ff56501'
OLD_CONSUMER_SHA = '6cc6cc30a71740df951327414d094953effb73a406e7036358ad0b702ebb0403'
GENERATOR_SHA = '9c22cbdebce13c729768ac7dd1162d16aefbba5fb24dc0f018051b4588bfa281'
IR_PLAN_SHA = '72ce5472b5d3fc76d4f8d27c3aa3f4f7ad3d224a5ada3eaba88b3f1a2e6feff5'
BUILD = dict(core_commit='9eedb3131937748f0492fa83aad37d3691118d70', framework_commit='02775fd795cde5aae1480d81cee6eb481d0a08f4', binary_sha256='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d')
PASS = 'PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'
REUSE = 'REFERENCE_ACCEPTED_NO_NEW_START'
ARCHIVE_PASS = 'ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
METRICS = ('DH_speedup','CH_speedup','relative_DTC_improvement','CH_over_DH')

class EvidenceHold(ValueError): pass
def require(v, reason):
    if not v: raise EvidenceHold(reason)
def read(path): return json.loads(P(path).read_bytes())
def sha(path): return hashlib.sha256(P(path).read_bytes()).hexdigest()
def jsonsha(v): return hashlib.sha256((json.dumps(v,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
def compactsha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load(name,path,expected=None):
    raw=P(path).read_bytes()
    if expected: require(hashlib.sha256(raw).hexdigest()==expected,'source SHA mismatch: '+str(path))
    m=types.ModuleType(name);m.__file__=str(path);exec(compile(raw,str(path),'exec'),m.__dict__);return m
def key(row): return tuple(row[k] for k in ('input_digest','cell','profile'))
def assert_identity(spec, target, science_keys):
    require(all(spec.get(k)==v for k,v in BUILD.items()),'wrong frozen build')
    require(spec.get('correctness_validation_only') is False and spec.get('performance_scope')=='NEW_L2_MLP_ONLY_NEVER_ORIGINAL','not frozen performance scope')
    require(len(spec.get('expected_options',{}))==270,'incomplete option vector')
    require(all(k in spec and k in target and spec[k]==target[k] for k in science_keys),'frozen science/input/ROI/hash/config mismatch')
    require(spec.get('cell')==target.get('cell') and spec.get('downstream_profile')==target.get('downstream_profile'),'wrong design/profile')

def assert_proof(proof, spec, cycles, ratified_reference=False):
    require(type(cycles) is int and cycles>0 and proof.get('cycles')==cycles,'invalid cycles')
    require(proof.get('performance_accepted') is True and proof.get('status') in ('L2_MLP_NATIVE_TRACE_PERFORMANCE_QUALIFIED','DOWNSTREAM18_NATIVE_TRACE_PERFORMANCE_QUALIFIED'),'strict not accepted')
    for k,v in BUILD.items(): require(proof.get(k)==v==spec[k],'strict build mismatch '+k)
    for k in ('input_digest','cell','program'): require(proof.get(k)==spec[k],'strict identity mismatch '+k)
    if not ratified_reference:require(proof.get('suite')==spec['suite'],'strict suite mismatch')
    require(proof.get('effective_options')==spec['expected_options'] and len(proof['effective_options'])==270,'effective physics/Hash mismatch')
    for pk,sk in [('CTA','CTA'),('instructions','instructions'),('kernel_count','kernels')]: require(proof.get(pk)==spec['expected'][sk],'strict complete ROI mismatch '+pk)
    if not ratified_reference:require(proof.get('profile')==spec.get('downstream_profile'),'strict profile mismatch')

def choose_reference(original, alternate=None, link=None):
    """Pure deterministic precedence; a rejected apparent original blocks substitution."""
    if original.get('valid'): return dict(selected=original,reason='VALID_ORIGINAL_PRIORITY')
    if original.get('apparent_accepted') or original.get('acceptance_uncertain'): return dict(selected=None,reason='ORIGINAL_ACCEPTANCE_IDENTITY_HOLD_NO_SUBSTITUTION')
    if original.get('identity_verified') is not True:return dict(selected=None,reason='ORIGINAL_IDENTITY_HOLD_NO_SUBSTITUTION')
    if link and alternate and alternate.get('cohort')==link['alternate_cohort'] and alternate.get('scientific_role')==link['alternate_role'] and alternate.get('valid'):
        require(original['cohort']==link['original_cohort'],'wrong original link')
        return dict(selected=alternate,reason='EXACT_PREDECLARED_REFERENCE_ONLY_NAMED_VIEW')
    return dict(selected=None,reason='MISSING_NO_IMPUTATION')

def distribution(rows, population, formal=False):
    ids=[r['input_digest'] for r in rows]
    require(len(set(ids))==len(ids) and set(ids)<=set(population),'duplicate/foreign denominator')
    require(all(type(r['value']) in (int,float) and math.isfinite(r['value']) and r['value']>0 for r in rows),'zero/missing/nonfinite ratio')
    values=[r['value'] for r in rows]
    return dict(n=len(rows),expected_n=len(population),missing_n=len(population)-len(rows),population=ids,
                full35_qualified=len(population)==35 and len(rows)==35,
                GM=math.exp(sum(map(math.log,values))/len(values)) if formal and values else None,
                positive=sum(x>1 for x in values) if formal else None,neutral=sum(x==1 for x in values) if formal else None,
                negative=sum(x<1 for x in values) if formal else None,values=rows if formal else None,
                metric_generation_enabled=formal)

def paired_metric(cells,digest,profile,metric):
    """Always form each ratio from one input, never a ratio of unmatched GMs."""
    need={'DH_speedup':[('DH','P0'),('DH',profile)],'CH_speedup':[('CH','P0'),('CH',profile)],
          'CH_over_DH':[('CH',profile),('DH',profile)],
          'relative_DTC_improvement':[('CH','P0'),('DH','P0'),('CH',profile),('DH',profile)]}[metric]
    refs=[cells.get((digest,c,p)) for c,p in need]
    if not all(refs): return None
    require(all(r['input_digest']==digest and r['cell']==c and r['profile']==p for r,(c,p) in zip(refs,need)),'paired denominator identity mismatch')
    first=refs[0]
    for r in refs:
        require(all(r[k]==first[k] for k in ('input_digest','input_binding_sha256','expected_ROI','core_commit','framework_commit','binary_sha256')),'paired build/ROI denominator mismatch')
    x=[r['cycles'] for r in refs]
    if metric=='relative_DTC_improvement': value=(x[1]/x[3])/(x[0]/x[2])
    else:value=x[0]/x[1]
    return dict(input_digest=digest,value=value,source_cohorts=[r['cohort'] for r in refs],source_roles=[r['scientific_role'] for r in refs],RESULT_sha256=[r['RESULT_sha256'] for r in refs])

def summarize(points, selections, profiles, formal=False):
    programs={}
    for p in points:
        pg={k:p[k] for k in ('input_digest','program','suite')}
        require(programs.setdefault(p['input_digest'],pg)==pg,'duplicate input program identity')
    require(len(programs)==35,'wrong frozen population')
    cells={};rowkeys=set()
    for row in selections:
        k=key(row['key']);require(k not in rowkeys,'duplicate slot');rowkeys.add(k)
        if row['selected'] is not None:cells[k]=row['selected']
    require(rowkeys=={key(p) for p in points},'scope cell coverage mismatch')
    ids=sorted(programs); suites=sorted({p['suite']for p in programs.values()})
    metrics={d:{p:{m:paired_metric(cells,d,p,m) for m in METRICS}for p in profiles}for d in ids}
    all_profile_common={m:[d for d in ids if all(metrics[d][p][m] is not None for p in profiles)]for m in METRICS}
    aggregates={}
    for p in profiles:
        aggregates[p]={}
        for suite in ['ALL']+suites:
            population=[d for d in ids if suite=='ALL' or programs[d]['suite']==suite]
            quad=[d for d in population if metrics[d][p]['relative_DTC_improvement'] is not None]
            aggregates[p][suite]={}
            for m in METRICS:
                available=[metrics[d][p][m] for d in population if metrics[d][p][m] is not None]
                common=[metrics[d][p][m] for d in population if d in all_profile_common[m]]
                fourway=[metrics[d][p][m] for d in quad]
                aggregates[p][suite][m]=dict(available=distribution(available,population,formal),all_profile_common=distribution(common,population,formal),same_profile_fourway=distribution(fourway,population,formal))
    return dict(analysis_namespace='DTC_L2_MLP_DERIVED35_SAME_PHYSICS_V1',formal_GM_generated=formal,
                no_ledger_union=True,no_runtime_parent_or_adoption=True,no_role_mutation=True,no_missing_imputation=True,
                expected_inputs=35,expected_original_slots=350,selected_measurement_references=len(cells),
                missing_slots=350-len(cells),programs=programs,all_profile_common=all_profile_common,aggregates=aggregates,
                per_input=metrics if formal else None)

def publication_gate(receipt_path, qualification_path):
    """Explicit public provenance is a release gate, never an acceptance replacement."""
    require(receipt_path is not None and qualification_path is not None,'formal metrics require public receipt and CPU qualification')
    qa=read(qualification_path); back=read(receipt_path); require(qa.get('status')=='PASS','CPU qualification absent')
    require(qa.get('consumer_sha256')==sha(__file__) and qa.get('contract_sha256')==CONTRACT_SHA,'CPU source binding mismatch')
    require(back.get('schema')=='DTC_DERIVED35_PUBLICATION_RECEIPT_V1' and back.get('verified') is True,'wrong publication receipt')
    require(re.fullmatch('[0-9a-f]{40}',back.get('commit','')) is not None,'no immutable commit')
    expected={str(CONTRACT):CONTRACT_SHA,str(P(__file__).resolve()):sha(__file__),str(P(qualification_path).resolve()):sha(qualification_path)}
    require(all(back.get('files',{}).get(k)==v for k,v in expected.items()),'published contract/consumer/QA mismatch')
    require(back.get('qualification_only') is False,'CPU fixture publication cannot release formal data')
    return back

class ReadonlyConsumer:
    def __init__(self):
        require(sha(CONTRACT)==CONTRACT_SHA,'contract SHA changed');self.contract=read(CONTRACT)
        c=self.contract;require(c['status']=='MAIN_APPROVED_NAMED_ANALYSIS_ONLY_RUNTIME_ADOPTION_NOT_AUTHORIZED','contract not Main approved')
        require(c['statistics']['ledger_union'] is False and c['statistics']['role_mutation'] is False,'wrong contract boundary')
        require(sha(c['frozen_scope_path'])==SCOPE_SHA==c['frozen_scope_sha256'],'scope SHA changed')
        require(sha(c['predeclared_mapping_snapshot_path'])==MAP_SHA==c['predeclared_mapping_snapshot_sha256'],'mapping SHA changed')
        self.scope=read(c['frozen_scope_path']);self.snapshot=read(c['predeclared_mapping_snapshot_path']);self.frozen={r['original_cohort']:r for r in self.snapshot['rows']}
        self.links={r['original_cohort']:r for r in c['predeclared_reference_links']};require(len(self.links)==12,'wrong alternate count')
        require(len({r['alternate_cohort']for r in self.links.values()})==12,'duplicate alternate source')
        irpath=A/'agents/B/incident11_recovery_trials_plan_v1/DRAFT_PLAN.json';require(sha(irpath)==IR_PLAN_SHA,'IR lineage plan changed');self.ir=read(irpath);self.science_keys=self.ir['science_projection_keys']
        exact={r['original_cohort']:r['new_cohort']for r in self.ir['rows']};exact['E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V1']='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V2'
        require(exact=={o:r['alternate_cohort']for o,r in self.links.items()},'nonpredeclared alternate')
        require(len(self.scope['points'])==350 and {p['input_digest']for p in self.scope['points']}==set(c['program_input_digests']),'wrong scope')
        self.old=load('derived35_pinned_original_consumer',R/'tools/l2_results.py',OLD_CONSUMER_SHA)
        self.generator=load('derived35_pinned_generator',R/'tools/l2_config_generator.py',GENERATOR_SHA)
        engine=load('derived35_readonly_engine',R/'tools/l2_native.py','e8276aadbb243b29166d89e5e937de260e6017061b475b62ac9c6c6f3dc3825a');self.q=engine.registered()[2]
        self.pins={};self.specs={};self.cache={}
        self.pin(CONTRACT);self.pin(c['frozen_scope_path']);self.pin(c['predeclared_mapping_snapshot_path']);self.pin(irpath);self.pin(self.old.__file__);self.pin(self.generator.__file__);self.pin(engine.__file__)

    def pin(self,path):
        path=P(path);value=sha(path);prior=self.pins.setdefault(str(path),value);require(prior==value,'source changed during snapshot '+str(path));return value
    def get(self,path):
        path=P(path);raw=path.read_bytes();value=hashlib.sha256(raw).hexdigest();prior=self.pins.setdefault(str(path),value);require(prior==value,'source changed during snapshot '+str(path));return json.loads(raw)
    def spec(self,c):
        if c not in self.specs:self.specs[c]=self.get(R/'control/specs'/(c+'.json'))
        return self.specs[c]

    def proof_and_small_archive(self,c,result,spec,root):
        """Reuse ratified full archive/native receipt; rejoin small critical records.
        No rehash of raw logs, tar chunks, or large trace assets is performed.
        """
        proof=result['proof'];assert_proof(proof,spec,result['cycles'])
        ip=root/'control/qualification_ledger'/(c+'.INTENT.json');intent=self.get(ip);done=self.get(ip.with_name(c+'.DONE.json'));out=P(intent['output'])
        require(done==self.get(out/'NATIVE_EXIT.json'),'DONE/EXIT mismatch')
        require(done.get('stop_reason') is None and done.get('launcher_wait_returncode')==0 and done.get('native_simulator_observed') is True,'not natural completion')
        require(intent['uuid']==done['uuid']==result['uuid']==proof['uuid'],'UUID mismatch')
        if root==R:
            qr=self.q.get('consumed',{}).get(c,{});require(qr.get('uuid')==done['uuid'] and qr.get('execution_receipt')==done,'authority execution receipt mismatch')
            require(qr.get('intent_sha256')==self.pin(ip),'authority INTENT SHA mismatch')
        strict=self.get(out/'L2_STRICT.json');require(strict==proof,'RESULT/strict sidecar mismatch')
        require(proof['raw_gzip_sha256']==done['raw_sha256'] and proof['raw_uncompressed_sha256']==done['raw_uncompressed_sha256'],'raw receipt mismatch')
        frozen=self.get(out/'DOWNSTREAM_FROZEN_SPEC.json');assert_identity(frozen,spec,self.science_keys)
        dbp=out/'DISPATCH_BINDING.json';db=self.get(dbp)
        require(self.pin(dbp)==proof['dispatch_binding_sha256']==intent['dispatch_binding_sha256'],'dispatch binding mismatch')
        require(db['cohort']==c and db['canonical_spec_sha256']==self.pin(out/'DOWNSTREAM_FROZEN_SPEC.json'),'frozen canonical mismatch')
        for fn in ('NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json'):
            doc=self.get(out/fn);require(doc['dispatch_binding_sha256']==self.pin(dbp),'launch/PID dispatch mismatch')
            for field in [k for k in intent if k.startswith('additional_') and k.endswith('_binding')]:require(doc.get(field)==intent[field],'operational generation three-way binding mismatch')
        for k,side in proof.items():
            if k.startswith('additional_') and k.endswith('_strict'):
                require(isinstance(side,dict) and side.get('status','').startswith('PASS'),'nonpass additional strict')
                sp=P(side['sidecar_path']);require(sp.parent==out and self.pin(sp)==side['sidecar_sha256'],'additional strict sidecar mismatch')
        archive=result['archive'];receipt=archive['receipt'];require(receipt==self.get(root/'control'/(c+'_ARCHIVE_RECEIPT.json')),'archive receipt mismatch')
        require(receipt.get('status')==ARCHIVE_PASS and receipt['cohort']==c and receipt.get('source_disposition')=='SOURCE_KEEP','archive/native not qualified')
        require(archive.get('independently_verified_entries',0)>0 and receipt.get('true164_root','').startswith('/home/shared/'),'true164 receipt missing')
        bundle=P(receipt['target_mount_path']);manifest=self.get(bundle/'SOURCE_MANIFEST.json');require(self.pin(bundle/'SOURCE_MANIFEST.json')==receipt['manifest_sha256'],'archive manifest SHA mismatch')
        require(self.get(bundle/'RECEIPT.json')==receipt,'archive receipt file mismatch')
        restore=self.get(bundle/'RESTORE_VERIFIED_NATIVE_TARGET.json');entries={e['path']:e for e in manifest['entries']};restored={e['path']:e for e in restore['rows']}
        require(len(entries)==len(manifest['entries']) and len(restored)==len(restore['rows']),'duplicate archive entry')
        require(len(entries)==len(restored)==archive['independently_verified_entries'],'archive population mismatch')
        critical=['DISPATCH_BINDING.json','DOWNSTREAM_FROZEN_SPEC.json','DOWNSTREAM_INTENT.json','L2_STRICT.json','NATIVE_EXIT.json','NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']
        critical += [P(v['sidecar_path']).name for k,v in proof.items()if k.startswith('additional_') and k.endswith('_strict')]
        for fn in critical:
            require(fn in entries and fn in restored and entries[fn].get('sha256')==restored[fn].get('sha256')==self.pin(out/fn),'archive critical SHA mismatch '+fn)
            rp=P(receipt['native_restore'])/fn;require(self.pin(rp)==entries[fn]['sha256'],'restored critical SHA mismatch '+fn)
        require(entries.get('raw.log.gz',{}).get('sha256')==done['raw_sha256'],'archived raw receipt mismatch')
        return dict(out=str(out),uuid=done['uuid'],DONE_sha256=self.pin(ip.with_name(c+'.DONE.json')),strict_sha256=self.pin(out/'L2_STRICT.json'),archive_receipt_sha256=self.pin(root/'control'/(c+'_ARCHIVE_RECEIPT.json')),archive_sha256=receipt['archive_sha256'],manifest_sha256=receipt['manifest_sha256'],receipt_reuse='SOURCE_BOUND_PREVIOUS_FULL_STRICT_AND_FULL_ARCHIVE_NATIVE_RESTORE_NO_LARGE_RAW_REPLAY')

    def measure(self,c,target,role):
        if c in self.cache:return self.cache[c]
        result_path=R/'analysis'/(c+'.RESULT.json');spec=self.spec(c)
        row=dict(cohort=c,scientific_role=role,valid=False,apparent_accepted=False,acceptance_uncertain=True,identity_verified=False,raw_state='PENDING_NO_RESULT',cycles=None,RESULT_path=str(result_path),RESULT_sha256=None,reasons=[])
        self.cache[c]=row
        try:
            # Read possible acceptance before any identity/role failure. An
            # unreadable/racing RESULT stays uncertain and cannot authorize a
            # substitute. Only a genuinely absent or known nonaccepted result
            # may proceed to the fixed, independently verified negative link.
            value=None
            if result_path.exists():
                value=self.get(result_path)
                require(isinstance(value,dict),'RESULT object required')
                row.update(raw_state=value.get('state'),RESULT_sha256=self.pin(result_path),uuid=value.get('uuid'),apparent_accepted=value.get('state') in (PASS,REUSE),acceptance_uncertain=value.get('state') not in (PASS,REUSE,'FAIL_L2MLP_ARCHIVED_NO_RETRY'))
            else:row['acceptance_uncertain']=False
            assert_identity(spec,target,self.science_keys)
            require(spec.get('scientific_role','ORIGINAL_PRIMARY_SLOT')==role or role=='ORIGINAL_PRIMARY_SLOT' and 'scientific_role'not in spec,'source role mismatch')
            row['identity_verified']=True
            if role!='ORIGINAL_PRIMARY_SLOT':
                lineage=spec.get('incident_recovery_trial_lineage',spec.get('supplemental_trial_lineage',{}))
                require(lineage.get('primary_statistics_excluded') is True and lineage.get('validated_union_authorized') is False,'old exclusion flags changed')
            if value is None:row['reasons'].append('NO_RESULT_PENDING_OR_UNSTARTED');return row
            if not self.old.accepted(value):row['reasons'].append('NOT_STRICT_ACCEPTED');return row
            require(value['cohort']==c,'RESULT cohort mismatch')
            if role=='ORIGINAL_PRIMARY_SLOT':
                old=self.frozen[c]['original_measurement']
                if old['accepted_existing_receipt']:require(row['RESULT_sha256']==old['RESULT_sha256'],'previously accepted original changed')
            else:
                require(value.get('validated_union_authorized',False) is False,'new trial union mutation')
                original=next(o for o,link in self.links.items()if link['alternate_cohort']==c)
                prior=self.frozen[original]['predeclared_alternate']['measurement']
                if prior['accepted_existing_receipt']:require(row['RESULT_sha256']==prior['RESULT_sha256'],'previously accepted alternate changed')
                if role=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL':
                    require(value.get('scientific_role')==role and value.get('primary_statistics_excluded') is True,'IR RESULT exclusion mismatch')
                    require(self.get(R/'analysis/incident_recovery_results'/(c+'.RESULT.json'))==value,'IR mirror mismatch')
            if value['state']==REUSE:
                require(role=='ORIGINAL_PRIMARY_SLOT' and spec['downstream_profile']=='P0','reference only ratified original P0')
                frozen=self.frozen[c]['original_measurement'];require(frozen['matched_P0_reference'] and frozen['RESULT_sha256']==row['RESULT_sha256'],'unratified P0 reference')
                sourcepath=P(value['reference_result_path']);require(self.pin(sourcepath)==value['reference_result_sha256'],'ratified reference source changed')
                source=self.get(sourcepath);require(source['cycles']==value['cycles'] and source['uuid']==value['uuid'] and source['proof']==value['proof'] and source['archive']==value['archive'],'ratified source mismatch')
                assert_proof(value['proof'],spec,value['cycles'],ratified_reference=True)
                evidence=dict(ratified_P0_reference=True,reference_result_path=str(sourcepath),reference_result_sha256=self.pin(sourcepath),reuse_verification=value['reuse_verification'],no_new_start=True,source_suite_display=value['proof'].get('suite'),frozen35_suite_display=spec['suite'],source_profile_display=value['proof'].get('profile'),frozen35_profile='P0',profile_established_by_full270_equality_and_frozen_reuse_SHA=True,suite_is_frozen35_display_group_not_physics=True,receipt_reuse='IMMUTABLE_MATCHED_P0_SOURCE_SHA_AND_RATIFIED_FULL_STRICT_NATURAL_ARCHIVE_FLAGS')
            else:evidence=self.proof_and_small_archive(c,value,spec,R)
            row.update(valid=True,cycles=value['cycles'],evidence=evidence,**{k:spec[k] for k in ('input_digest','input_binding_sha256','core_commit','framework_commit','binary_sha256','cell')},profile=spec['downstream_profile'],expected_ROI=spec['expected'],spec_sha256=self.pin(R/'control/specs'/(c+'.json')),options_sha256=jsonsha(spec['expected_options']))
        except (EvidenceHold,OSError,ValueError,KeyError,TypeError) as error:row['reasons'].append(type(error).__name__+': '+str(error))
        return row

    def alternate_lineage(self,link):
        c=link['alternate_cohort'];old=link['original_cohort'];spec=self.spec(c)
        if link['alternate_role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL':
            plan=next(r for r in self.ir['rows']if r['new_cohort']==c);record=self.q.get('authorized_incident_recovery_trials',{});record=record.get(c)if isinstance(record,dict)else next((r for r in record if r['cohort']==c),None)
            require(record is not None,'IR not officially registered');require(record['original_cohort']==old and record['original_uuid']==plan['original_uuid'],'IR registered lineage mismatch')
            for k in ('original_negative_RESULT_sha256','original_DONE_sha256','science_projection_sha256'):
                require(record[k]==plan[k],'IR plan/authority lineage mismatch '+k)
                require(spec['incident_recovery_trial_lineage'][k]==plan[k],'IR spec lineage mismatch '+k)
            lineage=spec['incident_recovery_trial_lineage']
            require(lineage['original_cohort']==old and lineage['original_uuid']==plan['original_uuid'],'IR spec original UUID mismatch')
            require(lineage['automatic_retry'] is False and lineage['reuse_old_UUID'] is False and lineage['refunds']==0 and lineage['new_grants']==1,'IR independent-trial lineage mismatch')
            require(record['primary_statistics_excluded'] is True and record['validated_union_authorized'] is False,'IR authority exclusion changed')
            require(self.pin(R/'analysis'/(old+'.RESULT.json'))==plan['original_negative_RESULT_sha256'],'original negative changed')
            require(self.pin(R/'control/qualification_ledger'/(old+'.DONE.json'))==plan['original_DONE_sha256'],'original negative DONE changed')
            require(compactsha({k:spec[k] for k in self.science_keys})==plan['science_projection_sha256'],'IR frozen scientific projection mismatch')
        else:
            frozen=self.frozen[old]['original_measurement'];require(self.pin(frozen['typed_certificate_path'])==frozen['typed_certificate_sha256'],'original scan negative changed')
            lineage=spec['supplemental_trial_lineage']
            require(lineage['negative_certificate_path']==frozen['typed_certificate_path'] and lineage['negative_certificate_sha256']==frozen['typed_certificate_sha256'],'R2 negative lineage mismatch')
        return True

    def run(self,publication_receipt=None,qualification=None):
        formal=False
        if publication_receipt is not None:
            publication_gate(publication_receipt,qualification);self.pin(publication_receipt);self.pin(qualification);formal=True
        selections=[]
        for point in self.scope['points']:
            c=point['cohort'];target=self.spec(c);frozen=self.frozen[c]['original_measurement']
            for field in ('input_digest','input_binding_sha256','core_commit','framework_commit','binary_sha256'):
                require(target[field]==frozen[field],'frozen original declaration changed '+field)
            require(target['expected']==frozen['expected_ROI'] and jsonsha(target['expected_options'])==frozen['expected_options_sha256'],'frozen original ROI/options changed')
            require(self.pin(target['input_binding_path'])==target['input_binding_sha256'],'frozen input binding bytes changed')
            # Expected vectors are regenerated from the same-design P0 by the
            # already qualified generator; exactly 2 target options may change.
            baseline_cohort=next(p['cohort']for p in self.scope['points']if p['input_digest']==point['input_digest'] and p['cell']==point['cell'] and p['profile']=='P0')
            flatten=lambda opts:{k:' '.join(v) if isinstance(v,list) else v for k,v in opts.items()}
            baseline=flatten(self.spec(baseline_cohort)['expected_options']);text=''.join(k+' '+v+'\n'for k,v in sorted(baseline.items()))
            _,generated=self.generator.generate([text],point['profile']);require(generated['effective_options']==flatten(target['expected_options']),'uniform qualified parameter family mismatch')
            original=self.measure(c,target,'ORIGINAL_PRIMARY_SLOT');alternate=None;link=self.links.get(c)
            if link:
                require(key(link['key'])==key(point),'predeclared key mismatch')
                try:self.alternate_lineage(link);alternate=self.measure(link['alternate_cohort'],target,link['alternate_role'])
                except (EvidenceHold,OSError,ValueError,KeyError,TypeError)as error:alternate=dict(cohort=link['alternate_cohort'],scientific_role=link['alternate_role'],valid=False,cycles=None,reasons=[str(error)])
            selected=choose_reference(original,alternate,link)
            selections.append(dict(key={k:point[k]for k in ('input_digest','program','suite','cell','profile')},original_cohort=c,original=original,alternate=alternate,**selected))
        summary=summarize(self.scope['points'],selections,self.contract['profiles'],formal)
        return dict(schema='DTC_DERIVED35_SOURCE_BOUND_ANALYSIS_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),contract_sha256=CONTRACT_SHA,consumer_sha256=sha(__file__),formal_metric_release='PUBLIC_IMMUTABLE_VERSION_AND_CPU_QA_VERIFIED'if formal else'DRY_COVERAGE_ONLY_NO_FORMAL_GM',rows=selections,summary=summary,source_pins=[dict(path=p,sha256=h)for p,h in sorted(self.pins.items())],original_roles_unchanged=True,ledger_union=False,runtime_adoption_authorized=False,new_models_started=0,new_grants=0,production_changes=0)
