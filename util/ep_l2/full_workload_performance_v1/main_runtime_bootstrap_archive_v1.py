"""Main bounded control/runtime bootstrap archive; not a science launch or ledger restore.

Bulk inputs, RO ranges, raw results and builds retain their separate immutable164
archives. Only a frozen metadata/tools snapshot is copied and restored here.
"""
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import uuid

J = Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
sys.path.insert(0, str(J/'tools'))
from ep_perf_common import *
import main_p64_ni_and_stage_v2 as admission


def main():
    uid = str(uuid.uuid4())
    snapshot_dir = J/'control/runtime_bootstrap_snapshots'/uid
    snapshot_dir.mkdir(parents=True)
    gate_ref = admission.gate()
    gate = exact(gate_ref)
    # C explicitly reports no active/pending build at this start and coordinates
    # this brief copy interval with Main. Its unstarted2.5GiB ceiling is not a
    # second reservation. This COPY_ONLY receipt never authorizes a model.
    added_compile_upper = 0
    child_cap = 64*M
    need(gate['margin_bytes'] >= added_compile_upper + child_cap, 'COPY_ONLY additional compiler+restore CPU headroom HOLD')
    need(gate['snapshot']['native_free_bytes'] >= gate['disk_required_bytes'] + 64*M, 'COPY_ONLY actual64MiB extra native window HOLD')
    own, unused = authority()
    q = own['registered_future_requests'][GOAL]
    publication = J/'control/GITHUB_PUSH_CHECKPOINT_V5_878485c3-eaf4-4652-b21b-89de1340499b.json'
    pub = exact(ref(publication))
    need(pub['latest_publish_verified'], 'published review head not verified')
    head = pub['head']
    snap = dict(schema='EP_NONAUTHORITATIVE_OWN_REGISTRY_SNAPSHOT_V1', goal=GOAL, utc=now(),
        snapshot=q, original_registry_ref_at_snapshot=ref(REG), authoritative=False,
        recovery_rule='Read current native authority. Never overwrite live registry, replay consumed requests, refund or automatically restart models.')
    qp = snapshot_dir/'OWN_SCOPE_SNAPSHOT_NOT_AUTHORITY.json'
    put(qp, snap, True)
    git_tar = snapshot_dir/'published_review_docs_and_tools.tar'
    subprocess.run(['git','-C',str(J/'review'),'archive','--format=tar','--output='+str(git_tar),head,
        'docs/ep_l2/operations/ep_full_workload_performance_20261027_v1',
        'util/ep_l2/full_workload_performance_v1'],check=True,timeout=20)
    selected = {}
    def add(path, member, role):
        path=Path(path)
        need(path.is_file() and not path.is_symlink(), 'only regular bounded control members')
        if member in selected:
            need(selected[member]['original_path']==str(path), 'member collision')
            return
        st=path.stat()
        need(st.st_size<=8*M,'unexpected large control member; no bulk copy')
        selected[member]=dict(member=member,original_path=str(path),role=role,bytes=st.st_size,
            sha256=sha(path),mode=stat.S_IMODE(st.st_mode),uid=st.st_uid,gid=st.st_gid,mtime_ns=st.st_mtime_ns,atime_ns=st.st_atime_ns)
    for p in sorted((J/'tools').rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            add(p, 'runtime_root/'+str(p.relative_to(J)), 'HOST_CODE_OR_CPU_EVIDENCE_NOT_SOURCE_BUILD')
    external_refs={}
    for case, h in q['admitted_specs'].items():
        p=J/'cases'/case/'control/FROZEN_SPEC.json'
        need(sha(p)==h,'exact admitted spec drift')
        s=read(p)
        add(p,'runtime_root/'+str(p.relative_to(J)),'FROZEN_REGISTERED_SPEC')
        for r in s['ordered_configs']:
            need(sha(r['path'])==r['sha256'],'ordered config drift')
            p=Path(r['path']);add(p,'runtime_root/'+str(p.relative_to(J)),'FROZEN_ORDERED_CONFIG')
        for key in ('input_binding_ref','eligibility_ref','ro_qualification_ref','source_qualification_ref','host_qualification_ref'):
            r=s.get(key)
            if not r:continue
            need(sha(r['path'])==r['sha256'],'qualification metadata drift '+key)
            p=Path(r['path'])
            member='runtime_root/'+str(p.relative_to(J)) if p.is_relative_to(J) else 'external_metadata/'+r['sha256']+'.json'
            add(p,member,key)
            external_refs[str(p)]=dict(sha256=r['sha256'],member=member)
    for p in sorted((J/'control').glob('*.json')):
        if p.name.startswith(('STAGE_','SEARCH_PLAN_','HOST_QUALIFICATION','SOURCE_QUALIFICATION','USER_AUTHORIZATION','NATIVE_PEER','MAIN_','P_MS0_','SOURCE92_','RESOURCE_POLICY')):
            add(p,'runtime_root/'+str(p.relative_to(J)),'MAIN_IMMUTABLE_CONTROL_OR_ENGINEERING_RECEIPT')
    add(J/'control/USER_REQUEST.txt','runtime_root/control/USER_REQUEST.txt','USER_REQUEST')
    add(qp,qp.name,'NONAUTHORITATIVE_SNAPSHOT')
    add(git_tar,git_tar.name,'PUBLISHED_GIT_COMMIT_SNAPSHOT')
    add(publication,'PUBLISH_RECEIPT.json','ACTUAL_REMOTE_HEAD_VERIFICATION')
    catalog=dict(schema='EP_RUNTIME_BOOTSTRAP_PATH_CATALOG_V1',goal=GOAL,utc=now(),published_review_head=head,
        complete_science_or_source_build_archive=False,restores_complete_included_population_only=True,
        path_map=external_refs,registered_points=len(q['admitted_specs']),Source_KEEP=True,
        excludes=['Trace and datasets','RO range bodies already archived separately','Scientific raw/results already in per-case164 archives','Source/build releases already archived separately','Mutable live ledgers/claims/controller state'],
        restore_entry='Use tools/ep_perf_archive.py restore on MANIFEST.json into a fresh native target. Inspect RECOVERY.md and the catalog; resolve separately archived immutable dependencies by exactSHA. Do not copy the nonauthoritative ledger snapshot into live authority or automatically launch an ELF.')
    cp=snapshot_dir/'RECOVERY_CATALOG.json';put(cp,catalog,True);add(cp,cp.name,'RECOVERY_PATH_MAP')
    guide=snapshot_dir/'RECOVERY.md'
    guide.write_text('# Bounded runtime/control recovery snapshot\n\nThis archive restores only its explicit manifest population. Published review HEAD: `'+head+'`.\n\nBulk Trace, RO range bodies, scientific results and Source/builds remain in their separate genuine164 archives and SOURCE_KEEP locations. Exact original paths and SHA metadata are retained; resolve those before any current native qualification. No completeness claim applies to external dependency closure.\n\nNever restore the own-scope snapshot over active registry, modify consumed charges, replay a launch, or bypass the current native entry. It is an audit snapshot, not new scientific authority. All existing model results and running processes remain unchanged.\n')
    add(guide,guide.name,'RECOVERY_BOUNDARY')
    members=sorted(selected.values(),key=lambda x:x['member'])
    total=sum(x['bytes']for x in members)
    need(len(members)<=4000 and total<=64*M,'finite bootstrap content bound')
    mount=json.loads(subprocess.check_output(['findmnt','-J','-T','/root/share/mnt164'],text=True))['filesystems'][0]
    need(mount['source']=='admin-wcx@10.208.130.164:/home/shared' and mount['fstype']=='fuse.sshfs','genuine164 required')
    target=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/ep_l2_full_workload_performance_20261027_v1/runtime_bootstrap')/uid
    need(not target.exists(),'new immutable archive target')
    target.mkdir(parents=True)
    with locked(J/'control/ARCHIVE_SHARED_WINDOW.lock'):
        partial=target/'bootstrap.tar.PARTIAL'
        with partial.open('xb')as disk:
            with tarfile.open(fileobj=disk,mode='w|')as out:
                for r in members:
                    p=Path(r['original_path']);st=p.stat()
                    need(st.st_size==r['bytes']and st.st_mtime_ns==r['mtime_ns']and sha(p)==r['sha256'],'frozen included member changed')
                    ti=tarfile.TarInfo(r['member']);ti.size=r['bytes'];ti.mode=r['mode'];ti.uid=r['uid'];ti.gid=r['gid'];ti.mtime=r['mtime_ns']//1000000000
                    with p.open('rb')as f:out.addfile(ti,f)
            disk.flush();os.fsync(disk.fileno())
        archive=target/'bootstrap.tar';partial.rename(archive)
        ah=sha(archive);need(sha(archive)==ah,'closed NAS readback SHA')
        manifest=dict(schema='EP_BOUNDED_RUNTIME_CONTROL_BOOTSTRAP_ARCHIVE_V1',goal=GOAL,uuid=uid,archive_sha256=ah,archive_bytes=archive.stat().st_size,members=members,published_head=head,Source_KEEP=True,complete_external_scientific_asset_closure_claim=False)
        mp=target/'MANIFEST.json';put(mp,manifest,True)
        receipts=[]
        for label in ('FIRST','INDEPENDENT'):
            with tempfile.TemporaryDirectory(prefix='BOOTSTRAP_'+uid+'_'+label+'_',dir=J/'restore_windows')as work:
                dest=Path(work)/'fresh_native_target'
                def limit():
                    resource.setrlimit(resource.RLIMIT_AS,(64*M,64*M));resource.setrlimit(resource.RLIMIT_CPU,(60,60))
                a=subprocess.run([sys.executable,'-B',str(J/'tools/ep_perf_archive.py'),'restore','--archive',str(archive),'--manifest',str(mp),'--target',str(dest),'--max-bytes',str(total)],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,preexec_fn=limit,timeout=90)
                need(a.returncode==0,'independent native restore failed '+a.stderr[-2000:])
                r=json.loads(a.stdout);r.update(restore_label=label,owned_scratch_only_released=True,scientific_Source_deleted=False);receipts.append(r)
        receipt=dict(schema='EP_BOUNDED_RUNTIME_BOOTSTRAP_TWO_RESTORE_RECEIPT_V1',goal=GOAL,utc=now(),uuid=uid,status='GENUINE164_INCLUDED_CONTROL_RUNTIME_POPULATION_FULL_SHA_AND_TWO_NATIVE_RESTORES_PASS',archive_ref=ref(archive),manifest_ref=ref(mp),CPU_gate_ref=gate_ref,conservative_additional_Source_engineering_cap_bytes=added_compile_upper,sequential_restore_child_AS_bytes=child_cap,published_review_head=head,registered_point_snapshot=len(q['admitted_specs']),included_files=len(members),included_logical_bytes=total,native_restores=receipts,Source_KEEP=True,source_release_bytes=0,models_started=0,ledger_writes=0,external_bulk_dependency_closure='SEPARATE_ARCHIVES_NOT_REVERIFIED_HERE')
        rr=put(snapshot_dir/'ARCHIVE_RECEIPT.json',receipt,True);put(target/'ARCHIVE_RECEIPT.json',receipt,True)
        put(target/'COMMIT.json',dict(schema='EP_RUNTIME_BOOTSTRAP_COMMIT_V1',receipt_ref=ref(target/'ARCHIVE_RECEIPT.json'),archive_ref=ref(archive),manifest_ref=ref(mp),commit_last=True,Source_KEEP=True),True)
        print(json.dumps(dict(receipt_ref=rr,status=receipt['status'],archive_ref=ref(archive),logical_bytes=total,files=len(members))))


if __name__=='__main__':main()
