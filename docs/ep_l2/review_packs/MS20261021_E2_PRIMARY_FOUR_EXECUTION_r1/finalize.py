"""Publish completed authorized evidence only; never execute an application."""
from pathlib import Path
import sys,json,time,contextlib,io,importlib.util
P=Path(__file__).resolve().parent;ROOT=P.parents[3];sys.path.insert(0,str(P));sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c
from final_audit import audit

def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(Path(p).resolve()),sha256=c.digest(p))
def main():
 with contextlib.redirect_stdout(io.StringIO()):r=audit()
 s=c.Coordinator().snapshot();plan=read(P/'PLAN.json');hand=ROOT/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/e';receipt=read(hand/'RECEIPT.json')
 assert receipt['event']=='PRIMARY_FOUR_TERMINAL' and s['controller']['state']=='STOPPED'
 deliveries=[]
 for row in plan['profiles']:
  path=P/(row['pair_id']+'_D_DELIVERY_RECEIPT.json')
  if path.exists():deliveries.append(dict(delivery=ref(path),receipt=read(path)))
 assert len(deliveries)==sum(x.get('accepted',False) for x in r['rows'])
 c.write_json(P/'D_DELIVERY_INDEX.json',dict(status='DELIVERED_ACCEPTED_POINTS_AFTER_E_REMOTE_READBACK',at_unix=time.time(),deliveries=deliveries,pending_D_analysis_is_not_execution_blocker=True))
 receipt.update(event='PRIMARY_FOUR_FINAL_CLOSED',at_unix=time.time(),independent_terminal_audit=ref(P/'FINAL_INDEPENDENT_TERMINAL_AUDIT.json'),result_allocated_bytes_including_directories=r['result_allocated_bytes_including_directories'],result_growth_logical_bytes=r['result_growth_logical_bytes'],D_delivery_index=ref(P/'D_DELIVERY_INDEX.json'),next_conditions=[],next_batch=r['next_batch'])
 c.write_json(hand/'RECEIPT.json',receipt);c.write_json(P/'FINAL_RECEIPT.json',receipt)
 text='# Lane E2 — PRIMARY FOUR closed\n\n'+f"{r['status']}. Original174;originalT0={r['T0']};actual{r['actual_starts']}/40,remaining{r['remaining']};contingency8/8 consumed. Original controllerSTOPPED,owned activeapplications/leases0. main61/Core d010/Framework9dd/vendorf90 unchanged;no native/build,secondcontroller ornewGoal.\n\n"
 text+='| Authorized condition | New attempt | State | cycles | real exit/wait | instructions |\n|---|---|---|---:|---|---:|\n'
 for row in r['rows']:text+=f"| {row['condition']} | {row.get('attempt_id','NONE')} | {row['state']} | {row.get('cycles','UNKNOWN')} | {row.get('exit_code','UNKNOWN')}/{row.get('wait_status','UNKNOWN')} | {row.get('instructions','UNKNOWN')} |\n"
 text+='\nAccepted endpoints require normal real nativeexit0/wait0,completeinput and exactinstruction count,64slice/source/version/ownership/resourceclosure. Native process PID/startticks/boot and actualparentcollector are bound in the ready/exit/receipt SHA chain; processabsence/rawtext never establishesPASS. Exactqualifications and F full_data_free_finite_residual_service gate are retained.\n\n'
 text+=f"MAIN S/F pairs CURRENT_ACCEPTED:{r['accepted_MAIN_pairs']};controls:{r['accepted_controls']}. Original mainpairs unchanged. Vector reuses E013S73696 and freshE033F75039,ratio0.982102639961;the oldE014 RESOURCE_LIMIT/exit−15 remains invalid andcharged. DWT F_MINUS_R166718 versus W_ONLY166792/F167643 gives−74/+925 conditionalcyclecontrasts;sum851,notuniqueadditivecriticalstallattribution.\n\n"
 text+='L2_DATA_FREE is a diagnostic service exemption retaining finite residual resources,real metadata/ROP/copy-latch/completion and exactoracle scope. It is never a hardwareP1 throughput endpoint or replacement for acceptedmainF/S. All old32attempts/raw/failure/INCOMPLETE/HOLD receipts remain byte-identical. Only FWT F_MINUS_W→DWT F_MINUS_R andBtreeF→VectorF retry changedmatrixrows;other30rows,original32+8 buckets,T0 and40cap remain. BtreeS staysHOLD,FWT recovery/WB64/sensitivity were not run.\n\n'
 text+=f"Batch growth:{r['result_growth_logical_bytes']}B logical,{r['result_allocated_bytes_including_directories']}B allocatedincludingdirectories. Cumulative new:{r['output_usage']['new_bytes']}B/6GiB;old+new:{r['output_usage']['total_bytes']}B/20GiB. Remaining generation:new{r['remaining_new_generation_bytes']}B,total{r['remaining_total_generation_bytes']}B. Every actualendpoint<=384MiB,four<=1.5GiB;collector/metadata accounted,no migration refund. Workspacefree{r['resources']['disk_free_bytes']}B,Sharefree{r['resources']['share_disk_free_bytes']}B,MemAvailable{r['resources']['available_memory_bytes']}B atfinalaudit.\n\n"
 text+='Each acceptedpoint was pushed andremote-readbefore D inbox/events/shared delivery; seeD_DELIVERY_INDEX.json. No waitingforDanalysis. NextbatchNONE_AUTHORIZED: only thisPRIMARY FOUR,neithersecondary norautomaticreplacement/retry. OriginalOct21BJT18:00start/22:00intake,perendpoint10800s,workspace5GiBfloor+2GiBmonitor,CPU/RAM/Share andallscientific gates remain. Seven-inputGMUNKNOWN.\n'
 (hand/'STATUS.md').write_text(text);(P/'FINAL_STATUS.md').write_text(text)
 spec=importlib.util.spec_from_file_location('pub',P.parent/'MS20261020_E2_TAKEOVER_r1/publish.py');pub=importlib.util.module_from_spec(spec);spec.loader.exec_module(pub)
 paths=[p for p in P.rglob('*') if p.is_file() and p.suffix in ['.json','.md','.py','.csv'] and '__pycache__' not in p.parts]+[hand/'STATUS.md',hand/'RECEIPT.json']
 with contextlib.redirect_stdout(io.StringIO()):rb=pub.publish('docs(ep-l2-e2): close only PRIMARY FOUR with independent terminal and charged history',paths)
 c.write_json(P/'FINAL_REMOTE_READBACK.json',rb)
 notice=dict(status=r['status'],E_publication=rb['remote_commit'],report='docs/ep_l2/review_packs/MS20261021_E2_PRIMARY_FOUR_EXECUTION_r1/FINAL_STATUS.md',audit=ref(P/'FINAL_INDEPENDENT_TERMINAL_AUDIT.json'),actual=r['actual_starts'],remaining=r['remaining'],MAIN_pairs=r['accepted_MAIN_pairs'],accepted_controls=r['accepted_controls'],results=[{k:x.get(k) for k in ['condition','attempt_id','state','accepted','cycles','instructions','exit_code','wait_status','result_directory','receipt']} for x in r['rows']],output_usage=r['output_usage'],growth_bytes=r['result_growth_logical_bytes'],allocated_bytes=r['result_allocated_bytes_including_directories'],D_deliveries=deliveries,interpretation=r['interpretation'],next_batch=r['next_batch'],controller='STOPPED',old_failures_HOLD_charges_preserved=True,only_two_exact_rows_changed=True)
 for channel in [c.HANDOFF/'events',c.HANDOFF/'inbox',Path('/workspace/ep_l2_ms20261019_shared')]:c.write_json(channel/'E2_TO_A2_D_PRIMARY_FOUR_FINAL_CLOSED.json',notice)
 print(json.dumps(dict(status=r['status'],remote_commit=rb['remote_commit'],verified_files=len(rb['verified_paths']),actual=r['actual_starts'],remaining=r['remaining'],MAIN_pairs=r['accepted_MAIN_pairs'],accepted_controls=r['accepted_controls'],results=notice['results'],growth_bytes=r['result_growth_logical_bytes'],allocated_bytes=r['result_allocated_bytes_including_directories'],controller='STOPPED')),flush=True)
if __name__=='__main__':main()
