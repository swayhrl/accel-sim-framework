"""Mechanism-study extension of the original node registry, never a second quota authority.

All state transactions use the original permanent REGISTRY.lock. Old scientific
records, loaders and client hashes are read-only. RUN_LEDGER.json is a projection;
its canonical state is the new field in the original central JSON.
"""
from __future__ import annotations
import argparse
import datetime
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import time
import uuid
import subprocess
import policy_v2

OLD_TOOLS = Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1/util/ep_l2/ft_lane5')
sys.path.insert(0, str(OLD_TOOLS))
from registry import (Registry, ACTIVE, canonical, local_resources, retained_tree_bytes,
                      write_json, process_identity, run_key, validate_hash)

AUTHORITY = policy_v2.AUTHORITY
CAMPAIGN = 'EPL2_MECHANISM_STUDY_20261019_V1'
FIELD = 'mechanism_study_20261019_v1'
SHARED = Path('/workspace/ep_l2_ft20261016_shared')
HANDOFF = SHARED / FIELD
OUTPUT = Path('/workspace/ep_l2_ms20261019_e_results')
OLD_OUTPUTS = (Path('/workspace/ep_l2_potential20261017_lane5_results'),
               Path('/workspace/results/ep_l2_ft20261016'))
GIB = 2**30
FULL_GROWTH = 2*GIB + 128*2**20
START_DEADLINE = 1792576800  # 2026-10-21 18:00 Asia/Shanghai
INTAKE_DEADLINE = 1792591200
REUSED_TOOL_PINS = {'registry.py': '81a31c347bd3c5531eb959569ae7baffbecd5f75c6142a65e1aedbfd05a8808d', 'run.py': '43f65cf89fdbdf81e8786e8b00d2d9be1dfc521c41e386f01ed00fc7708c9060', 'validate.py': '08a7396a6e11893dbbcb982725765a6c9b12194b1e01e3f0dc70d337f85dd500', 'acceptance.py': '459675b32fba1cb76526e26be00956fb16a5c6ed2677ed7aada9bf2c7af19d75', 'headroom_config.py': '43e1b577a81b75863fa5821cd1da6d9a634f7ae0848adfa0f276922294582f69', 'feature_schema.py': '26353fa1724d69cc63ab0bc8ac0d13650210a6824b05b49ea44499e785aad6e7', 'parse_unified_terminal.py': '536d1a8d55452b7aee5b84168648b228eb35cc5e82b523e81b59634c51db352b'}
NATIVE_GATES = {'old_all_off_equivalence', 'finite_wbuf', 'requester_exact_once',
 'sector_reference_data', 'stale_fill', 'resource_closure', 'wb_lifecycle',
 'bank_service', 'physical_bank_clock', 'memcpy_payload_identity', 'mode_legality'}


def require(condition, message):
    if not condition: raise ValueError(message)


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(4*2**20), b''): h.update(block)
    return h.hexdigest()


def tooling_binding():
    for name,sha in REUSED_TOOL_PINS.items():
        require(digest(OLD_TOOLS/name)==sha,'reused source changed; compatibility audit required: '+name)
    client=json.loads((SHARED/'CLIENT_CONTRACT.json').read_text())
    for name in ('registry_client','runner','acceptance_module'):
        require(digest(client[name])==client[name+'_sha256'], 'original tooling changed: '+name)
    verify_extension_binding(HANDOFF/'CLIENT_CONTRACT.json')
    return {k:client[k] for k in ('registry_client_sha256','registry_source_commit',
                                'runner_sha256','runner_source_commit','acceptance_module_sha256')}


def verify_extension_binding(path):
    client=json.loads(Path(path).read_text())
    require(client['authority_commit']==AUTHORITY,'E client authority not yet published')
    require(client['resource_lease_api_sha256']==digest(__file__),'E resource API checksum mismatch')
    source_commit=client['source_publication_commit'];validate_hash(source_commit,40)
    root=Path(client['execution_worktree'])
    require(bool(client['source_files']),'E source publication manifest missing')
    expected={p.relative_to(root).as_posix() for p in Path(__file__).parent.glob('*.py')
              if not p.name.startswith('test_')}
    require(set(client['source_files'])==expected,'E runtime source manifest incomplete')
    for name,sha in client['source_files'].items():
        require(digest(root/name)==sha,'E runtime checksum mismatch: '+name)
        blob=subprocess.check_output(['git','show',source_commit+':'+name],cwd=root)
        require(hashlib.sha256(blob).hexdigest()==sha,'E source publication mismatch: '+name)
    return source_commit


def ledger(data):
    item=data[FIELD]
    require(item['campaign_id']==CAMPAIGN and item['authority_commit'] in
            (AUTHORITY,policy_v2.PRIOR_AUTHORITY), 'campaign authority mismatch')
    expected=40 if item['authority_commit']==AUTHORITY else 24
    require(item['maximum_actual_starts']==expected and item['start_deadline_unix']==START_DEADLINE,
            'budget/deadline changed')
    require(item['additional_results_max_bytes']==6*GIB and item['old_plus_new_results_max_bytes']==20*GIB,
            'output budget changed')
    require(item['host']==socket.gethostname() and item['boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'different host/boot: explicit reconciliation required')
    return item


def counts(item):
    actual=sum(a.get('actual_start') is True for a in item['attempts'])
    uncertain=sum(a['state']=='START_INTENT_UNRECONCILED' for a in item['attempts'])
    pending=sum(a['state']=='RESERVED' for a in item['attempts'])
    item.update(actual_starts=actual,uncertain_start_intents=uncertain,
                remaining_start_capacity=item['maximum_actual_starts']-actual-uncertain-pending)
    require(item['remaining_start_capacity']>=0,str(item['maximum_actual_starts'])+' actual-start budget exhausted')
    return actual,uncertain,pending


def output_usage():
    roots={p.resolve(strict=True) for p in OLD_OUTPUTS}
    old=sum(retained_tree_bytes(p) for p in roots)
    new=retained_tree_bytes(OUTPUT) if OUTPUT.exists() else 0
    return {'old_bytes':old,'new_bytes':new,'total_bytes':old+new}


def pending_growth(data):
    rows=[r for r in data['runs'].values() if r['status'] in ACTIVE and r['host']==socket.gethostname()]
    result=0
    for r in rows:
        reserve=r.get('disk_growth_bytes',FULL_GROWTH)
        result+=max(0,reserve-retained_tree_bytes(Path(r['result_directory'])))
    for r in data['resource_leases'].values():
        if r['status'] in ACTIVE and r['host']==socket.gethostname():
            # Build/test output outside result directories still consumes workspace.
            result+=r.get('disk_growth_bytes',0)
    return result


def resource_gate(data, kind, cpu, memory, growth, resources, usage=None, scan=False, result_growth_bytes=None,
                  disk_floor_bytes=48*GIB, monitor_reserve_bytes=0):
    item=ledger(data)
    require(type(cpu) is int and cpu>=1 and type(memory) is int and memory>0,
            'positive integer CPU/RAM required')
    require(type(growth) is int and growth>0,'conservative positive output-growth reserve required')
    require(kind in ('build','test','simulation','screen'),'unknown resource class')
    if kind=='build':require(cpu<=2,'A build max -j2')
    require((48*GIB-7*GIB//2)<=disk_floor_bytes<=48*GIB and type(monitor_reserve_bytes) is int
            and monitor_reserve_bytes>=0,'bounded task disk floor/monitor reserve required')
    require(disk_floor_bytes==48*GIB or kind=='build','slight-under48 exception only selected A build')
    if disk_floor_bytes!=48*GIB:
        require(growth<=7*GIB//2 and disk_floor_bytes==48*GIB-growth,
                'task floor must derive from exact one-build growth, max3.5GiB; no arbitrary lower floor')
    policy_v2.global_gate(data,kind,cpu,memory)
    # Reuse the production global CPU/RAM/scan/disk guards and permanent lock.
    # Override only this reviewed transaction's policy view. Actual resources
    # stay untouched; ordinary Registry.build_lease and global host policy stay48.
    view=data
    if disk_floor_bytes!=48*GIB:
        view=json.loads(json.dumps(data));view['hosts'][socket.gethostname()]['min_disk_free_bytes']=disk_floor_bytes
    Registry.admission(view,socket.gethostname(),cpu,memory,scan,
                       'simulation' if kind in ('simulation','screen') else 'build',resources)
    active=[r for r in data['runs'].values() if r['status'] in ACTIVE]
    leases=[r for r in data['resource_leases'].values() if r['status'] in ACTIVE]
    require(resources['available_memory_bytes']-memory-sum(r['memory_bytes'] for r in active+leases)>=64*GIB,
            '64GiB memory floor after existing and proposed reservations')
    require(resources['disk_free_bytes']-pending_growth(data)-growth-monitor_reserve_bytes>=disk_floor_bytes,
            '48GiB workspace floor or exact authorized task floor plus existing/proposed output growth and monitor reserve')
    if kind in ('simulation','screen'):
        ours=[r for r in active if r.get('experiment_id')==CAMPAIGN]
        target=item.get('target_simulators',2)
        require(type(target) is int and 1<=target<=3,'E concurrency must be 1..3')
        require(len(ours)<target,'E campaign simulator quota full')
        if target==3:require(not any(r.get('kind')=='MECHANISM_BUILD' for r in leases),
                             'third simulator requires public build completed')
    if usage is not None:
        pending=sum(max(0,r.get('disk_growth_bytes',FULL_GROWTH)-retained_tree_bytes(Path(r['result_directory'])))
                    for r in active if r.get('experiment_id')==CAMPAIGN)
        pending+=sum(r.get('result_growth_bytes',0) for r in leases if r.get('experiment_id')==CAMPAIGN)
        addition=(0 if kind=='build' else growth) if result_growth_bytes is None else result_growth_bytes
        require(type(addition) is int and 0<=addition<=growth,'result growth must fit physical reservation')
        require(usage['new_bytes']+pending+addition<=6*GIB,'new-study 6GiB result ceiling')
        require(usage['total_bytes']+pending+addition<=20*GIB,'old+new 20GiB result ceiling')


class Coordinator:
    def __init__(self, root=SHARED):
        self.registry=Registry(root)
        self.handoff=Path(root)/FIELD

    @contextmanager
    def locked(self):
        # Imported A/B/C clients must enforce helper publication too; checking
        # only the CLI entry would leave their direct reserve_work calls open.
        if self.registry.root.resolve()==SHARED.resolve():tooling_binding()
        with self.registry.locked() as data:
            item=ledger(data)
            yield data,item
            counts(item)
            write_json(self.handoff/'RUN_LEDGER.json',item)

    def snapshot(self):
        # Truly read-only: no updated_at rewrite and no implicit second authority.
        if self.registry.root.resolve()==SHARED.resolve():tooling_binding()
        data=json.loads((self.registry.root/'RUN_REGISTRY.json').read_text())
        return ledger(data)

    def adopt_v2(self):
        with self.locked() as (data,item):
            counts(item)
            changed=policy_v2.amend(item,time.time())
            counts(item)
            return {'changed':changed,'actual_starts':item['actual_starts'],
                    'maximum_actual_starts':item['maximum_actual_starts'],
                    'remaining_start_capacity':item['remaining_start_capacity'],'t0_unix':item['t0_unix']}

    def review_environment(self,candidate_path,review_path,original_physical_storage_identity):
        candidate=json.loads(Path(candidate_path).read_text());review=json.loads(Path(review_path).read_text())
        result=policy_v2.environment_review(candidate,review,original_physical_storage_identity,time.time(),digest)
        with self.locked() as (data,item):
            require(item['authority_commit']==AUTHORITY,'adopt V2 before environment intake')
            key=digest(candidate_path)
            item.setdefault('environment_reviews',{})[key]={**result,
                'candidate_path':str(Path(candidate_path).resolve()),'candidate_sha256':key,
                'review_path':str(Path(review_path).resolve()),'review_sha256':digest(review_path),
                'central_dispatcher_host':data['authority_host'],'resource_lease_granted':False,
                'remote_execution_enabled':False}
            # Actual dispatcher transport/process monitor must be bound after a
            # usable target entry is delivered. No copied registry or implicit
            # remote client is activated by accepting an environment report.
            return item['environment_reviews'][key]

    def reserve_work(self, role, kind, cpu, memory, growth, output_directory, result_growth_bytes=None,
                     disk_authorization_id=None,build_identity=None):
        require(role in ('A','B','C','E') and kind in ('build','test'),'only bounded build/test leases here')
        require(kind!='build' or role=='A','A is sole formal build owner')
        directory=Path(output_directory).resolve()
        require(directory.is_relative_to(Path('/workspace')) and directory.parent.exists(), 'use existing workspace parent')
        require(directory.parent.stat().st_dev==Path('/workspace').stat().st_dev,'output must be physical workspace')
        if kind=='test':require(directory.is_relative_to(OUTPUT),'new test results must be accounted in new result root')
        with self.locked() as (data,item):
            result_growth=(growth if kind=='test' else 0) if result_growth_bytes is None else result_growth_bytes
            require(kind!='test' or result_growth==growth,'all native test output must count toward new results')
            authorization=None;floor=48*GIB;monitor=0
            if disk_authorization_id is not None:
                require(role=='A' and kind=='build','disk exception only named A build')
                authorization=item['disk_authorizations'][disk_authorization_id]
                require(authorization['status']=='READY' and time.time()<authorization['expires_unix'],
                        'disk authorization expired/used/not ready')
                require(authorization['campaign_id']==CAMPAIGN and authorization['host']==socket.gethostname()
                        and authorization['boot_id']==item['boot_id'],'wrong disk authorization campaign/host/boot')
                require(authorization['user_instruction'] and authorization['source_identity']==build_identity,
                        'wrong build source/entry identity for disk authorization')
                require(authorization['api_sha256']==digest(__file__),'disk authorization uses stale E API')
                require(authorization['output_directory']==str(directory) and authorization['cpu_units']==cpu
                        and authorization['memory_bytes']==memory and authorization['growth_bytes']==growth
                        and authorization['result_growth_bytes']==result_growth,'wrong disk authorization paths/resources')
                require(not any(r['status'] in ACTIVE for group in ('runs','resource_leases') for r in data[group].values()),
                        'task-scoped build exception requires no competing heavy lease')
                floor=authorization['disk_floor_bytes'];monitor=authorization['monitor_reserve_bytes']
                require(monitor>=128*2**20,'explicit128MiB minimum monitor/stop overshoot reserve')
            resource_gate(data,kind,cpu,memory,growth,local_resources(),output_usage(),
                          result_growth_bytes=result_growth,disk_floor_bytes=floor,monitor_reserve_bytes=monitor)
            key=uuid.uuid4().hex
            row={'host':socket.gethostname(),'owner':'mechanism_'+role,'role':role,'kind':'MECHANISM_'+kind.upper(),
                 'execution_host_identity':{'hostname':socket.gethostname(),
                     'boot_id':item['boot_id']},'central_dispatcher_host':data['authority_host'],
                 'execution_environment':'original174','source_authority_commit':item['authority_commit'],
                 'build_owner':'A' if kind=='build' else None,'executor_role':role,
                 'experiment_id':CAMPAIGN,'cpu_units':cpu,'memory_bytes':memory,'disk_growth_bytes':growth,
                 'result_growth_bytes':result_growth,'status':'RESERVED','created_at':time.time(),
                 'owner_process':process_identity(os.getpid()),'output_directory':str(directory)}
            if authorization is not None:
                row.update(disk_authorization_id=disk_authorization_id,disk_floor_bytes=floor,
                           monitor_reserve_bytes=monitor,build_identity=build_identity)
                authorization.update(status='CONSUMED',lease_id=key,consumed_unix=time.time())
            data['resource_leases'][key]=row
            return {'lease_id':key,**row}

    def bind_work_process(self, key, role, pid):
        identity=process_identity(pid)
        with self.locked() as (data,item):
            row=data['resource_leases'][key]
            require(row.get('experiment_id')==CAMPAIGN and row['owner']=='mechanism_'+role
                    and row['status']=='RESERVED','wrong lease owner/state')
            previous=row.get('process')
            if previous is not None:
                try:still_same=process_identity(previous['pid'])==previous
                except (FileNotFoundError,ProcessLookupError):still_same=False
                require(not still_same,'previous work child still alive; do not rebind')
                row.setdefault('process_history',[]).append(previous)
            row.update(process=identity,process_bound_unix=time.time())
            return identity

    def release_work(self, key, role, detail, no_child_started=False):
        require(bool(detail),'release detail required')
        with self.locked() as (data,item):
            row=data['resource_leases'][key]
            require(row.get('experiment_id')==CAMPAIGN and row['owner']=='mechanism_'+role
                    and row['status'] in ACTIVE,'wrong lease owner or terminal lease')
            process=row.get('process')
            require(process is not None or no_child_started,'bind actual child or explicitly record no-child-started')
            if process is not None:
                try:still_same=process_identity(process['pid'])==process
                except (FileNotFoundError,ProcessLookupError):still_same=False
                require(not still_same,'work child still alive; keep its resource lease')
            # No auto-expiry and no killing another project.
            row.update(status='RELEASED',released_at=time.time(),detail=detail)

    def register_selection(self, selection_path):
        raw=Path(selection_path).read_bytes();selection=json.loads(raw)
        require(selection['campaign_id']==CAMPAIGN and selection['selected_by']=='D', 'D input preregistration required')
        selected_unix=selection.get('selection_unix')
        if selected_unix is None:
            stamp=datetime.datetime.fromisoformat(selection['selection_utc'].replace('Z','+00:00'))
            require(stamp.tzinfo is not None,'D selection UTC needs explicit timezone')
            selected_unix=stamp.timestamp()
        require(selected_unix<START_DEADLINE,'selection after start deadline')
        require(bool(selection['rationale']) and bool(selection['full_input_identity']), 'complete input selection required')
        for field in ('trace_content_sha256','runtime_independent_input_source','expected_full_instructions','comparison_groups'):
            require(selection['full_input_identity'].get(field) is not None,'missing input field: '+field)
        name=selection['selection_id']
        with self.locked() as (data,item):
            row={'path':str(Path(selection_path).resolve()),'sha256':hashlib.sha256(raw).hexdigest(),'selection':selection}
            old=item['input_selections'].get(name)
            require(old is None or old==row,'input selection cannot be rebound')
            require(not item['attempts'] or old is not None or selected_unix<=min(a['reserved_unix'] for a in item['attempts']),
                    'new selection must precede candidate results; explicit D scope review needed')
            item['input_selections'][name]=row
            return row

    def register_qualification(self, qualification_path):
        raw=Path(qualification_path).read_bytes();q=json.loads(raw)
        require(q['campaign_id']==CAMPAIGN and q['qualified_by']=='E' and q['status']=='INDEPENDENTLY_QUALIFIED',
                'new E independent qualification required')
        for field in ('core_source_commit','framework_source_commit','vendor_pybind11_commit','binary_sha256'):
            validate_hash(q['source_identity'][field],64 if field=='binary_sha256' else 40)
        require(digest(q['binary_path'])==q['source_identity']['binary_sha256'],'binary changed')
        for name in NATIVE_GATES|set(q['affected_additional_gates']):
            g=q['gates'][name]
            require(g['status']=='PASS' and g['production_driven'] is True,'failed/missing gate: '+name)
            require(digest(g['evidence_path'])==g['evidence_sha256'],'gate evidence changed: '+name)
        require(bool(q['supported_profiles']),'independently qualified profiles required')
        policy_v2.combination_qualification(q,digest)
        producer=q['producer_release'];validate_hash(producer['publication_commit'],40)
        require(producer['source_identity']==q['source_identity'],'A release identity mismatch')
        require(digest(producer['path'])==producer['sha256'],'A published release artifact changed')
        require(q['source_identity']['framework_source_commit'] not in
                (AUTHORITY,policy_v2.PRIOR_AUTHORITY),'control HEAD is not runtime Framework')
        for evidence_name in ('build_log','producer_test_manifest'):
            evidence=q[evidence_name]
            require(Path(evidence['path']).stat().st_size>0 and digest(evidence['path'])==evidence['sha256'],
                    'missing/changed '+evidence_name)
        require(q['scope_note'] and q['default_off_equivalence'],'version-specific scope/default OFF evidence required')
        key=hashlib.sha256(raw).hexdigest()
        with self.locked() as (data,item):
            old=item['qualifications'].get(key)
            row={'path':str(Path(qualification_path).resolve()),'sha256':hashlib.sha256(raw).hexdigest(),'qualification':q}
            require(old is None or old==row,'qualification revision must be explicit; never silently replace')
            item['qualifications'][key]=row
            return key

    def place_scientific_hold(self, qualification_id, attempt_id, reason, evidence):
        """Pause affected new-version work; retain all raw and acceptance history."""
        require(bool(reason) and bool(evidence),'hold needs a concrete reason/evidence path')
        with self.locked() as (data,item):
            require(qualification_id in item['qualifications'],'unknown qualification scope')
            key='qualification:'+qualification_id
            entry={'scope':'qualification','qualification_id':qualification_id,'attempt_id':attempt_id,
                'reason':reason,'evidence':str(evidence),'at_unix':time.time(),'status':'REVIEW_REQUIRED',
                'effect':'no new starts or new pair acceptance for this exact qualification; other versions independent'}
            item.setdefault('scientific_hold_history',[]).append(entry)
            item.setdefault('scientific_holds',{})[key]=entry
            affected=[]
            for pair_id,pair in item['accepted_pairs'].items():
                endpoints=[item['accepted_results'][pair[n]] for n in ('baseline_attempt_id','variant_attempt_id')]
                source=item['qualifications'][qualification_id]['qualification']['source_identity']
                matches=[]
                for endpoint in endpoints:
                    if 'qualification_id' in endpoint:matches.append(endpoint['qualification_id']==qualification_id)
                    else:
                        try:matches.append(json.loads(Path(endpoint['path']).read_text())['qualification_id']==qualification_id)
                        except (OSError,KeyError,ValueError):
                            matches.append(all(endpoint['identity'].get(n)==source[n] for n in ('core_source_commit','framework_source_commit','binary_sha256')))
                if any(matches):
                    item.setdefault('pair_status_history',[]).append({'pair_id':pair_id,'previous':pair,'hold':entry})
                    replacement=dict(pair,status='WITHDRAWN_SCIENTIFIC_HOLD',hold=entry)
                    item['accepted_pairs'][pair_id]=replacement;affected.append(pair_id)
                    write_json(self.handoff/'events'/('E_TO_D_PAIR_'+pair_id+'_HOLD.json'),replacement)
            write_json(self.handoff/'events'/('E_TO_A_D_QUALIFICATION_HOLD_'+qualification_id+'.json'),
                       dict(entry,affected_pairs=affected))
            return entry

    def resolve_scientific_hold(self,qualification_id,review_path):
        review=json.loads(Path(review_path).read_text())
        require(review['reviewed_by']=='E' and review['qualification_id']==qualification_id and
                review['status']=='RESOLVED_WITH_EXPLICIT_EVIDENCE','explicit E resolution required')
        require(review['reason'] and review['evidence'],'resolution evidence required')
        for artifact in review['evidence']:
            require(digest(artifact['path'])==artifact['sha256'],'resolution evidence changed')
        with self.locked() as (data,item):
            key='qualification:'+qualification_id
            require(key in item.get('scientific_holds',{}),'no matching active hold')
            require(review['hold_at_unix']==item['scientific_holds'][key]['at_unix'],'resolution targets a stale hold')
            item.setdefault('scientific_hold_resolution_history',[]).append({
               'qualification_id':qualification_id,'review_path':str(Path(review_path).resolve()),
               'review_sha256':digest(review_path),'at_unix':time.time()})
            del item['scientific_holds'][key]
            # Old failed/withdrawn results never become accepted from this alone.

    @staticmethod
    def require_no_hold(item,qualification_id):
        require('qualification:'+qualification_id not in item.get('scientific_holds',{}),
                'scientific review hold on this exact qualification')

    def reserve_application(self, spec):
        identity=spec['identity'];key=run_key(identity)
        growth=spec.get('maximum_result_bytes',FULL_GROWTH)
        require(type(growth) is int and 128*2**20<=growth<=FULL_GROWTH,'bounded hard per-attempt result limit required')
        require(spec['campaign_id']==CAMPAIGN and spec['launch_owner']=='E','E is sole full-application owner')
        require(identity['epoch_range'].get('scope')=='full_application','full input only')
        require(time.time()<START_DEADLINE,'full-application start deadline closed')
        with self.locked() as (data,item):
            counts(item)
            require(item['uncertain_start_intents']==0,'ambiguous previous start requires explicit reconciliation')
            require(item['remaining_start_capacity']>0,str(item['maximum_actual_starts'])+' actual-start budget exhausted')
            # No legacy key is overwritten or silently adopted as this campaign's result.
            previous=data['runs'].get(key)
            if previous is not None and previous.get('experiment_id')!=CAMPAIGN:
                raise ValueError('existing historical key: audit exact reuse, do not relaunch')
            history=[a for a in item['attempts'] if a['run_key']==key]
            require(not any(a['state'] in ('RESERVED','START_INTENT_UNRECONCILED','RUNNING','COMPLETE_VALID') for a in history),
                    'duplicate active or completed run-key')
            if history:require(spec.get('retry_previous_attempt')==history[-1]['attempt_id'] and spec.get('retry_reason'),
                               'same-key retry requires previous attempt and engineering reason')
            selected=item['input_selections'][spec['selection_id']]
            require(digest(selected['path'])==selected['sha256'],'D preregistration changed')
            chosen=selected['selection']['full_input_identity']
            require(chosen['trace_content_sha256']==identity['trace_content_sha256'],'D input mismatch')
            require(policy_v2.comparison_allowed(item,chosen,spec,digest),'unregistered comparison group')
            self.require_no_hold(item,spec['qualification_id'])
            qualified=item['qualifications'][spec['qualification_id']]
            require(digest(qualified['path'])==qualified['sha256'],'independent qualification changed')
            q=qualified['qualification'];source=q['source_identity']
            require(all(identity[n]==source[n] for n in ('core_source_commit','framework_source_commit','binary_sha256')),
                    'cross-binary or wrong production source')
            require(spec['profile'] in q['supported_profiles'],'profile not independently qualified')
            require(spec['profile_semantics']==q['supported_profiles'][spec['profile']], 'profile semantics changed')
            require(spec['labels'].keys()>={'diagnostic','subset','oracle'},'diagnostic/subset/oracle labels explicit')
            bucket=spec['budget_bucket'];require(bucket in item['reservations'],'unknown reserved budget bucket')
            used=sum(policy_v2.charged_bucket(a,item['reservations'])==bucket and
                     (a.get('actual_start') or a['state'] in ('RESERVED','START_INTENT_UNRECONCILED')) for a in item['attempts'])
            require(used<item['reservations'][bucket],'reserved matrix budget exhausted; preserve other controls')
            require(digest(spec['binary'])==identity['binary_sha256'],'binary changed before reservation')
            # Full asset hashing/config closure is performed by the reused runner inspector,
            # before this transaction and again before real Popen; its audit must be attached.
            require(spec.get('input_audit',{}).get('identity')==identity,'content-closed input audit required')
            resource_gate(data,'simulation',1,spec.get('memory_bytes',8*GIB),growth,local_resources(),output_usage(),identity['workload']=='scan')
            attempt_id=f'E{len(item["attempts"])+1:03d}_{uuid.uuid4().hex[:8]}'
            directory=OUTPUT/attempt_id
            row={'attempt_id':attempt_id,'run_key':key,'identity':identity,'selection_id':spec['selection_id'],
                 'qualification_id':spec['qualification_id'],'profile':spec['profile'],'comparison_group':spec['comparison_group'],
                 'budget_bucket':bucket,'labels':spec['labels'],'state':'RESERVED','actual_start':False,
                 'reserved_unix':time.time(),'result_directory':str(directory),'retry_reason':spec.get('retry_reason'),
                 'prior_attempts':[a['attempt_id'] for a in history],'maximum_result_bytes':growth}
            item['attempts'].append(row)
            data['runs'][key]={'run_key':key,'identity':identity,'owner':'mechanism_E','host':socket.gethostname(),
                'boot_id':item['boot_id'],'lease_id':attempt_id,'status':'RESERVED','created_at':time.time(),
                'cpu_units':1,'memory_bytes':spec.get('memory_bytes',8*GIB),'scan':identity['workload']=='scan',
                'result_directory':str(directory),'disk_growth_bytes':growth,'experiment_id':CAMPAIGN,'process':None}
            return row

    def start_application(self, attempt_id, command, cwd, environment, log_stream, popen):
        """Durable intent before Popen; success charges exactly one actual start.

        A crash in the intent/Popen interval is conservatively UNKNOWN, blocking
        further dispatch until PID/raw evidence reconciles it. Never silently
        refund or replay an ambiguous start. OS-level spawn failure is not an
        actual simulator start, and retains its failed attempt directory.
        """
        require(time.time()<START_DEADLINE,'full-application start deadline closed')
        with self.locked() as (data,item):
            attempt=next(a for a in item['attempts'] if a['attempt_id']==attempt_id)
            self.require_no_hold(item,attempt['qualification_id'])
            require(attempt['state']=='RESERVED','attempt is already started or terminal')
            require(not any(a['state']=='START_INTENT_UNRECONCILED' for a in item['attempts']),
                    'ambiguous previous start requires explicit reconciliation')
            require(Path(cwd).resolve()==Path(attempt['result_directory']).resolve(),'wrong output attempt directory')
            require(Path(command[0]).resolve()==Path(cwd).resolve()/'accel-sim.out' and
                    digest(command[0])==attempt['identity']['binary_sha256'],'wrong snapshotted executable')
            # Recheck resource pressure under the same global lock immediately
            # before spawn. Exclude only this already-held reservation, then
            # charge it back once, preserving all other projects and leases.
            view=json.loads(json.dumps(data));view['runs'].pop(attempt['run_key'])
            row=data['runs'][attempt['run_key']]
            resource_gate(view,'simulation',row['cpu_units'],row['memory_bytes'],row['disk_growth_bytes'],
                          local_resources(),output_usage(),row['scan'])
            require(item.get('controller',{}).get('process')==process_identity(os.getpid()) and
                    item['controller']['state']=='ACTIVE','only singleton E controller may start')
            attempt.update(state='START_INTENT_UNRECONCILED',start_intent_unix=time.time())
            counts(item)
            write_json(self.registry.root/'RUN_REGISTRY.json',data)
            write_json(self.handoff/'RUN_LEDGER.json',item)
            try:
                process=popen(command,cwd=cwd,stdout=log_stream,stderr=-2,env=environment,start_new_session=True)
            except OSError as error:
                attempt.update(state='FAILED_SPAWN',spawn_error=str(error))
                row.update(status='FAILED',detail='OS spawn failed before simulator execution')
                return None
            identity=process_identity(process.pid)
            attempt.update(state='RUNNING',actual_start=True,started_unix=time.time(),process=identity)
            row.update(status='RUNNING',process=identity,started_unix=attempt['started_unix'])
            counts(item)
            write_json(self.registry.root/'RUN_REGISTRY.json',data)
            write_json(self.handoff/'RUN_LEDGER.json',item)
            return process

    def finish_application(self, attempt_id, status, receipt_path):
        require(status in ('COMPLETE_VALID','FAILED','TIMEOUT','RESOURCE_LIMIT','INCOMPLETE'), 'invalid terminal status')
        receipt=json.loads(Path(receipt_path).read_text())
        with self.locked() as (data,item):
            attempt=next(a for a in item['attempts'] if a['attempt_id']==attempt_id)
            require(attempt['state']=='RUNNING' and attempt['actual_start'] is True,'no real active start to finish')
            try:still_same=process_identity(attempt['process']['pid'])==attempt['process']
            except (FileNotFoundError,ProcessLookupError):still_same=False
            require(not still_same,'child still alive; keep its lease')
            require(receipt['attempt_id']==attempt_id and receipt['run_key']==attempt['run_key'] and
                    receipt['identity']==attempt['identity'] and receipt['status']==status,'terminal receipt identity mismatch')
            require(receipt['raw_log_sha256']==digest(Path(attempt['result_directory'])/'raw.log'),'raw evidence changed')
            if status=='COMPLETE_VALID':
                require(receipt['independent_acceptance']=='PASS' and receipt['complete_input_verified'] is True,
                        'terminal is not independently accepted')
                require(receipt['validation']['status']=='PASS','summary closure failed')
                item['accepted_results'][attempt_id]={'path':str(Path(receipt_path).resolve()),'sha256':digest(receipt_path),
                    'run_key':attempt['run_key'],'identity':attempt['identity'],'qualification_id':attempt['qualification_id']}
            attempt.update(state=status,finished_unix=time.time(),receipt_path=str(Path(receipt_path).resolve()),
                           receipt_sha256=digest(receipt_path))
            row=data['runs'][attempt['run_key']]
            require(row['lease_id']==attempt_id,'attempt/lease mismatch')
            row.update(status=status,detail=receipt['detail'],raw_log_sha256=receipt['raw_log_sha256'],
                       result_receipt_sha256=digest(receipt_path),finished_unix=time.time())

    @contextmanager
    def unique_controller(self):
        path=self.handoff/'CONTROLLER.lock'
        with path.open('a+') as lock:
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise ValueError('E controller already active')
            with self.locked() as (data,item):
                old=item.get('controller')
                require(not old or old.get('state')=='STOPPED','previous controller needs PID/start_ticks reconciliation')
                item['controller']={'state':'ACTIVE','process':process_identity(os.getpid())}
            try:yield
            finally:
                with self.locked() as (data,item):
                    item['controller']={'state':'STOPPED','process':process_identity(os.getpid()),'stopped_unix':time.time()}


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    sub.add_parser('status')
    c=sub.add_parser('reserve-work');c.add_argument('--role',choices=['A','B','C','E'],required=True)
    c.add_argument('--kind',choices=['build','test'],required=True);c.add_argument('--cpu',type=int,required=True)
    c.add_argument('--memory-bytes',type=int,required=True);c.add_argument('--growth-bytes',type=int,required=True)
    c.add_argument('--output-directory',required=True);c.add_argument('--result-growth-bytes',type=int)
    b=sub.add_parser('bind-work-process');b.add_argument('--role',required=True);b.add_argument('--lease',required=True);b.add_argument('--pid',type=int,required=True)
    r=sub.add_parser('release-work');r.add_argument('--role',required=True);r.add_argument('--lease',required=True);r.add_argument('--detail',required=True);r.add_argument('--no-child-started',action='store_true')
    args=p.parse_args();tooling_binding();coord=Coordinator()
    if args.action=='status':result=coord.snapshot()
    elif args.action=='reserve-work':result=coord.reserve_work(args.role,args.kind,args.cpu,args.memory_bytes,args.growth_bytes,args.output_directory,args.result_growth_bytes)
    elif args.action=='bind-work-process':result=coord.bind_work_process(args.lease,args.role,args.pid)
    else:coord.release_work(args.lease,args.role,args.detail,args.no_child_started);result={'released':args.lease}
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
