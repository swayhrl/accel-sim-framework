"""New-root/true164 namespace overlay over pinned COPY/restore primitives."""
import pathlib,json,hashlib,importlib.util,os,subprocess
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1/validation_storage_recovery12_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');G=1024**3
NAS=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261026_dtc_recovery12_failure_repair_validation_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def adapted(cell):
 engine=load('recovery12_archive_engine',R/'tools/recovery12_native_v1.py');reg,epoch,q,p=engine.registered();assert cell in q['admitted_specs'] and q['outbox_sha256']==sha(__file__);base=load('recovery12_private_original_outbox',T/'tools/sweep_outbox.py');assert sha(T/'tools/sweep_outbox.py')==read(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')['outbox_sha256'];base.ROOT=R;base.NAS=NAS;base.COHORTS={c:'DTC' for c in q['admitted_specs']}
 overlay=p['copy_gate_overlay'];assert sha(overlay['path'])==overlay['sha256'];adapter=load('recovery12_exact_copy_gate',overlay['path']);return adapter.install_private_outbox(base,engine.REQ,cohort=cell)
def archive(cell):return adapted(cell).archive(cell)
def verify(cell):
 base=adapted(cell);receipt=read(R/'control'/(cell+'_ARCHIVE_RECEIPT.json'));bundle=P(receipt['target_mount_path']);manifest=base.manifest_for(cell);assert manifest==read(bundle/'SOURCE_MANIFEST.json');f,v=base.libraries(bundle);index=f.verify_archive(bundle,manifest);proof=f.check_native(P(receipt['native_restore']),manifest);assert index['archive_sha256']==receipt['archive_sha256'] and len(proof)==len(manifest['entries']);return {'receipt':receipt,'independently_verified_restored_entries':len(proof),'archive_overlay_sha256':sha(__file__)}
