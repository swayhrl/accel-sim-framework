"""Prepared reviewed exception entry. Fails closed without explicit user approval.
Does not edit global policy; real resources recorded, original API releases.
"""
from resource_accounting_r3 import *
import copy,time,uuid,hashlib
HARD_DEADLINE=1792312529

def scoped_lease(r,cpu,memory,growth):
 auth_path=BASE/'EXACT_EDA_SPACE_EXCEPTION_AUTHORIZATION_r1.json'
 assert auth_path.exists(),'exception not authorized'
 auth=json.loads(auth_path.read_text());assert auth['approved'] is True and auth['scope']=='ONLY_CURRENT_LANE2_R3_RTL'
 proposal=BASE/'EXACT_EDA_SPACE_EXCEPTION_PROPOSAL_r1.json';assert hashlib.sha256(proposal.read_bytes()).hexdigest()==auth['proposal_sha256']
 assert auth['remote_readback']=='EXACT_AUTHORIZATION_BYTES_PASS' and len(auth['publication_commit'])==40
 assert time.time()<HARD_DEADLINE and cpu==1 and memory<=8*2**30 and growth<=160*2**20
 cwd=Path.cwd().resolve();candidates=json.loads((BASE/'SOURCE_CANDIDATES.json').read_text());candidate=next((candidates[k] for k in ('R3A','R3B_FINAL') if Path(candidates[k]['worktree']).resolve()==cwd),None);assert candidate is not None
 assert candidate['five_RTL_files']=={p:hashlib.sha256((cwd/p).read_bytes()).hexdigest() for p in candidate['five_RTL_files']}
 commands=json.loads(os.environ['LANE2_COMMAND_JSON']);assert any(Path(s).name in ('run_functional.py','run_lane3_bytes_r2.py','run_cost_B_final.sh','run_B_final_remaining_r2.sh','run_U_STA_resume_r2.sh') for s in commands),'outside approved finite validation/PPA entry'
 phase=Path(os.environ['LANE2_MONITOR_ROOT']).resolve();central=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_R3_METADATA_AND_COST_OPT_lane2').resolve();assert central in phase.parents
 with r.locked() as state:
  host=socket.gethostname();assert state['hosts'][host]['min_disk_free_bytes']==48*2**30
  assert not any(x['owner']=='lane2' and x['status'] in reg.ACTIVE for x in state['resource_leases'].values()),'exception phases must be serial'
  resources=reg.local_resources();private=copy.deepcopy(state);private['hosts'][host]['min_disk_free_bytes']=int(47.5*2**30)
  assert resources['disk_free_bytes']-growth>=int(47.5*2**30)
  r.admission(private,host,cpu,memory,False,'build',resources)
  key=uuid.uuid4().hex;state['resource_leases'][key]={'host':host,'owner':'lane2','cpu_units':cpu,'memory_bytes':memory,'status':'RESERVED','created_at':reg.now(),'kind':'R3_RTL_EXACT_SPACE_EXCEPTION','authorization_publication':auth['publication_commit'],'authorization_sha256':hashlib.sha256(auth_path.read_bytes()).hexdigest(),'real_resources_at_admission':resources,'effective_only_this_lease_workspace_floor_bytes':int(47.5*2**30),'global_workspace_floor_unchanged_bytes':48*2**30,'deadline_unix':HARD_DEADLINE,'source_five_RTL_sha256':candidate['five_RTL_files'],'command':commands,'output_forecast_bytes':growth}
 return key
