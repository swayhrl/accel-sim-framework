from pathlib import Path
import sys,os,json,datetime,inspect,hashlib
def apply(directory):
 assert os.getpid()==1498278 and int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 main=sys.modules['__main__'];s=main.DTC_MAIN_BROAD_SHARED_CPU_INSTALL_V1;q=s['engine'].registered()[2];leaf=main.DTC_L2_MLP_PADDING_ONLY_OWNER_V1['resource'];path=Path(inspect.getsourcefile(leaf));h=hashlib.sha256(path.read_bytes()).hexdigest()
 assert path==Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/tools/l2_resources.py')and h=='6ad97e35de88ff5876bc0af674324f979f35c211f31d182976d2f66abb9c4854'
 reference={'cohort':next(iter(q['consumed']))};base=leaf(reference,True);assert base['source_module_sha256']==h and'additional_padding_admission_proof'not in base
 assert sum(x['additional_reserved_bytes']for x in base['RAM_reservation_entries']+base['own_ram_forecasts'])==base['total_projected_additional_RAM_bytes']
 v=dict(status='ACTUAL_CAPTURED_PRE_PADDING_ORIGINAL_NOFLAG_FULL_RESOURCE',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner_pid=os.getpid(),owner_start_ticks=977758783,leaf_source_path=str(path),leaf_source_sha256=h,leaf_qualname=leaf.__qualname__,reference_spec=reference,raw_resource=base,NOFLAG_marker_absent=True,full_cost_sum_verified=True,models_started=0,new_grants=0)
 text=json.dumps(v,sort_keys=True,indent=2)+'\n';p=Path(directory)/'ACK.json'
 with p.open('x')as f:f.write(text);f.flush();os.fsync(f.fileno())
 return dict(path=str(p),status=v['status'])
