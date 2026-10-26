"""New-root/true164 namespace overlay over pinned COPY/restore primitives."""
import pathlib,json,hashlib,importlib.util,os,subprocess
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1/validation_remaining_failure_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');G=1024**3
NAS=P('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261026_dtc_remaining_failure_repair_validation_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def adapted():
 engine=load('repair_archive_engine',R/'tools/remaining_native_v1.py');reg,epoch,q,p=engine.registered();assert q['outbox_sha256']==sha(__file__);base=load('repair_private_original_outbox',T/'tools/sweep_outbox.py');assert sha(T/'tools/sweep_outbox.py')==read(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')['outbox_sha256'];base.ROOT=R;base.NAS=NAS;base.COHORTS={c:'DTC' for c in q['admitted_specs']}
 def gate(reservation=0,other_reservation=None):
  assert other_reservation is None,'foreign write budgets must come from current native registry';parent=NAS
  while not parent.exists():parent=parent.parent
  fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(parent)],text=True))['filesystems'][0];assert fs['fstype']=='fuse.sshfs' and fs['source']=='admin-wcx@10.208.130.164:/home/shared';sample=engine.resources({'cohort':'REPAIR_COPY_METADATA','request':engine.REQ},False);assert R.stat().st_dev==T.stat().st_dev and sample['physical_disk_pass'] and sample['host_MemAvailable_bytes']>=64*G
  assert sample['native_free_bytes']>sample['required_free_bytes'];return dict(sample,new_native_restore_reserved_bytes=reservation,copy_overlay_sha256=sha(__file__),original_outbox_source_sha256=sha(T/'tools/sweep_outbox.py'),source_disposition='SOURCE_KEEP',scientific_model_starts=0)
 base.gate=gate;return base
def archive(cell):return adapted().archive(cell)
def verify(cell):
 base=adapted();receipt=read(R/'control'/(cell+'_ARCHIVE_RECEIPT.json'));bundle=P(receipt['target_mount_path']);manifest=base.manifest_for(cell);assert manifest==read(bundle/'SOURCE_MANIFEST.json');f,v=base.libraries(bundle);index=f.verify_archive(bundle,manifest);proof=f.check_native(P(receipt['native_restore']),manifest);assert index['archive_sha256']==receipt['archive_sha256'] and len(proof)==len(manifest['entries']);return {'receipt':receipt,'independently_verified_restored_entries':len(proof),'archive_overlay_sha256':sha(__file__)}
