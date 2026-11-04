"""Private exact namespace; original COPY/restore primitives and source kept."""
import pathlib,json,hashlib,importlib.util,os,subprocess
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');NAS=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/results');G=1024**3;M=1024**2
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def adapted(c):
 e=load('ds18_archive_engine',R/'tools/l2_native.py');reg,ep,q,p=e.registered();assert q['outbox_sha256']==sha(__file__)and c in q['consumed'];row=q['consumed'][c];out=R/'DTC/run/results'/row['uuid'];ip=R/'control/qualification_ledger'/(c+'.INTENT.json');dp=ip.with_name(c+'.DONE.json');assert row['intent_sha256']==sha(ip)and read(dp)==row['execution_receipt']==read(out/'NATIVE_EXIT.json')
 assert not load('ds18_archive_r20_resource',p['six_scope_resource_source']['path']).rss(R,row)[1];base=load('ds18_unchanged_outbox',T/'tools/sweep_outbox.py');assert sha(base.__file__)==read(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')['outbox_sha256'];base.ROOT=R;base.NAS=NAS;base.COHORTS={c:'DTC'for c in q['admitted_specs']}
 def gate(reservation=0,other_reservation=None):
  assert other_reservation is None and type(reservation)is int and 0<=reservation<=sum(x.stat().st_size for x in out.rglob('*')if x.is_file())+16*M
  assert R.stat().st_dev==2128 and os.uname().nodename=='huangrulin-sshfs-174';parent=NAS
  while not parent.exists():parent=parent.parent
  fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(parent)],text=True))['filesystems'][0];assert fs['fstype']=='fuse.sshfs'and fs['source']=='admin-wcx@10.208.130.164:/home/shared'
  v=e.resources({'request':e.REQ,'cohort':'DS18_CLOSED_COPY'},False)
  if not(v['physical_RAM_pass']and v['physical_disk_pass']and v['native_free_bytes']>v['required_free_bytes']+8*M):raise RuntimeError('RESOURCE_HOLD_COPY_NO_SOURCE_RELEASE')
  return dict(v,new_native_restore_reserved_bytes=reservation,copy_metadata_bound_bytes=8*M,true164_mount=fs,new_model_starts=0)
 base.gate=gate;return base
def archive(c):return adapted(c).archive(c)
def verify(c):
 b=adapted(c);a=read(R/'control'/(c+'_ARCHIVE_RECEIPT.json'));m=b.manifest_for(c);root=P(a['target_mount_path']);assert read(root/'SOURCE_MANIFEST.json')==m;f,v=b.libraries(root);idx=f.verify_archive(root,m);proof=f.check_native(P(a['native_restore']),m);assert idx['archive_sha256']==a['archive_sha256']and len(proof)==len(m['entries']);return dict(receipt=a,independently_verified_entries=len(proof),archive_overlay_sha256=sha(__file__))
