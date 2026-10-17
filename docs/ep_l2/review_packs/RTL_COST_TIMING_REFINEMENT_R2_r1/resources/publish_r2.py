from pathlib import Path
import json,hashlib,gzip,shutil,csv,subprocess,datetime,collections,re
repo=Path('/workspace/worktrees/accel-sim-ep-l2-rtl-cost-r2');art=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_TIMING_REFINEMENT_R2_lane2');book=Path('/workspace/ep_l2_rtl_cost_timing_r2');pack=art/'PUBLIC_REVIEW_PACK_R2';canonical='ed1c6ea12f8e0b7249bf5ef21229861bdc1afadd';frozen='09de19579c0708f6542dfd65e1f3aae8a9a8b841'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def copy(f,to):to.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(f,to)
def save_source(f,to):
 f=Path(f)
 if f.exists():
  if f.suffix=='.gz':copy(f,to);return
  if f.stat().st_size>512*1024:
   to=to.with_name(to.name+'.gz');to.parent.mkdir(parents=True,exist_ok=True)
   with f.open('rb') as x,to.open('wb') as y,gzip.GzipFile(fileobj=y,mode='wb',mtime=0,filename='') as z:shutil.copyfileobj(x,z)
   with gzip.open(to,'rb') as z:assert hashlib.file_digest(z,'sha256').hexdigest()==sha(f)
  else:copy(f,to)
 elif f.with_name(f.name+'.gz').exists():copy(f.with_name(f.name+'.gz'),to.with_name(to.name+'.gz'))
 else:raise FileNotFoundError(f)
summary=json.loads((art/'FINAL_SUMMARY_v2/COST_SUMMARY.json').read_text());assert {x['mode'] for x in summary}=={'B16','S64','UNIFIED'}
functional=json.loads((art/'functional-v6/FUNCTIONAL_RECEIPT.json').read_text());last=json.loads((art/'unified-last-physical-v2/FUNCTIONAL_RECEIPT.json').read_text());bytes_ref=json.loads((art/'lane3-bytes-v2/LANE3_BYTE_RECEIPT.json').read_text());diag=json.loads((art/'DATA_PATHS_R2/DATA_PATHS_RECEIPT.json').read_text());assert len(functional)==4 and len(last)==1 and len(bytes_ref['rows'])==3 and len(diag['rows'])==3
for row in functional+last:assert row['returncode']==0 and row['full_synthesizable_top']
for row in bytes_ref['rows']:assert row['status']=='ACTUAL_RTL_BYTE_COMPARISON_PASS' and row['comparisons']==13 and row['full_line_final_comparisons']==10
for row in diag['rows']:assert row['same_primary_WNS_TNS'] and row['reset_timed']
# Explicit terminal completion proof; no early process exit can qualify a suite.
trace=[]
for mode in ('B16','UNIFIED','S64'):
 new=(art/f'functional-v6/{mode}-run.log').read_text();old=(repo/f'docs/ep_l2/review_packs/RTL_COST_OPEN_FLOW_V1_r1/functional/pin_admission_r1/new-{mode}-run.log').read_text();a=next(x for x in new.splitlines() if x.startswith('RTL_RESULT'));b=next(x for x in old.splitlines() if x.startswith('RTL_RESULT'));assert a==b,(mode,a,b);trace.append({'mode':mode,'exact_R1_terminal_counts_and_cycles':True,'actual':a})
a=next(x for x in (art/'unified-last-physical-v2/UNIFIED_LAST_PHYSICAL-run.log').read_text().splitlines() if x.startswith('UNIFIED_LAST_PHYSICAL_BOUNDARY'));b=next(x for x in (repo/'docs/ep_l2/review_packs/RTL_COST_OPEN_FLOW_V1_r1/functional/unified_last_physical_r1/UNIFIED_LAST_PHYSICAL-run.log').read_text().splitlines() if x.startswith('UNIFIED_LAST_PHYSICAL_BOUNDARY'));assert a==b;trace.append({'mode':'UNIFIED_LAST_PHYSICAL','exact_R1_terminal_counts_and_cycles':True,'actual':a})
for n in ('first-292','first-128','first-16','first-64'):assert 'SUCCESS!' in (art/f'select-proof-v2/{n}.log').read_text()
assert json.loads((art/'select-mux-proof-v3/SELECT_EQ_RECEIPT.json').read_text())['status']=='ACTUAL_FINAL_RTL_ALL_BINARY_INPUTS_COMBINATIONAL_EQ_PASS'
for n in ('0-0','1-0','1-1'):assert 'Induction step proven: SUCCESS!' in (art/f'word-induction-v2/proof-{n}.log').read_text()
pack.mkdir(exist_ok=False)
for folder in ('FINAL_SUMMARY_v2','FINAL_COMPARISON_v2'):
 for p in (art/folder).iterdir():copy(p,pack/p.name)
module_rows=[];netlists=[];critical=[]
for item in summary:
 mode=item['mode'];d=art/(mode+'-map-v2');r=json.loads((d/'FLOW_RECEIPT.json').read_text());sta=Path(r['STA_root']);dest=pack/'raw_reports'/mode
 assert not item['standard_cell_totals']['unmapped'] and item['standard_cell_totals']['latch_cells']==0 and item['flow_complete']
 assert r['library_sha256']=='2efd0b32eb580e4e60e72fc0575bb3bc69aac907c91d908442e4ae6d7fe55895' and r['sdc_sha256']=='de89d1bdbeaefbbeeb316bfa00525e18e0c9fc013555796f75cc158a1641cbb2' and r['mapping_effort']=='fast-clean'
 for f in r['RTL_files']:assert hashlib.sha256(subprocess.check_output(['git','show',canonical+':'+f['path']],cwd=repo)).hexdigest()==f['sha256']
 for row in functional+last:assert all(row['RTL_sha256'][f['path']]==f['sha256'] for f in r['RTL_files'])
 assert all(bytes_ref['RTL_sha256'][f['path']]==f['sha256'] for f in r['RTL_files'])
 for name in ('stat.json','FLOW_RECEIPT.json','SOURCE_IDENTITY_START.json','synth.ys','abc.constr','yosys.log','mapped.v'):save_source(d/name,dest/name)
 for name in ('NETLIST_FORMAT_RECEIPT.json','STA_PHASE_IDENTITY.json','STA_netlist.v'):save_source(sta/name,dest/name)
 for p in sta.glob('*/*'):
  if p.is_file() and (p.suffix in ('.log','.rpt','.gz')):save_source(p,dest/p.parent.name/p.name)
 for name,expected in [('mapped.v',r['raw_mapped_netlist_sha256']),('STA_netlist.v',r['netlist_sha256'])]:
  base=d if name=='mapped.v' else sta;p=base/name;p=p if p.exists() else p.with_name(p.name+'.gz');blob=gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes();assert hashlib.sha256(blob).hexdigest()==expected;netlists.append({'mode':mode,'source_path':str(p),'decoded_sha256':expected,'archive_sha256':sha(p),'public_path':str((dest/name).relative_to(pack))+'.gz'})
 count=collections.Counter()
 def visit(n,f=1):
  count[n]+=f
  for child,k in item['per_module'][n]['children'].items():visit(child,f*k)
 top=next(n for n in item['per_module'] if n.endswith('\\ep_l2_slice_ctrl'));visit(top)
 for n,v in item['per_module'].items():module_rows.append([mode,n,count[n],v['own_standard_cells'],v['own_area'],v['own_combinational_area'],v['own_sequential_area'],count[n]*v['own_area']])
 path=sta/'target_1132MHz/critical_paths.rpt';text=path.read_text() if path.exists() else gzip.decompress(path.with_suffix('.rpt.gz').read_bytes()).decode();block=text.split('\n\nStartpoint:')[0];critical.append({'mode':mode,'actual_first_primary_path':block,'WNS':item['timing']['target_1132MHz']['wns_ns'],'TNS':item['timing']['target_1132MHz']['tns_ns']})
with (pack/'PER_MODULE_AREA.csv').open('w') as f:w=csv.writer(f);w.writerow(['mode','module','instances','cells_per_instance','own_area','own_comb_area','own_seq_area','aggregate_own_area']);w.writerows(module_rows)
for label in ('functional-v6','unified-last-physical-v2','lane3-bytes-v2','word-induction-v2','select-proof-v2','select-mux-proof-v3','DATA_PATHS_R2'):
 for p in (art/label).rglob('*'):
  if not p.is_file():continue
  # Failed optional full-mux2GiB SAT log remains, explicitly classified by resource receipt.
  if p.name in ('EXACT_STA_INPUT.v.gz',):continue
  save_source(p,pack/'functional_and_diagnosis'/label/p.relative_to(art/label))
for p in (repo/'rtl/ep_l2/r2').glob('*'):
 if p.is_file():copy(p,pack/'contracts_and_proofs'/p.name)
copy(repo/'docs/ep_l2/review_packs/RTL_COST_OPEN_FLOW_V1_r1/BLACKBOX_INVENTORY.json',pack/'BLACKBOX_INVENTORY.json')
resources=pack/'resources';resources.mkdir()
for p in book.glob('*'):
 if p.is_file() and (p.suffix in ('.py','.json','.md','.sh') or p.name.endswith('-guard.log')):save_source(p,resources/p.name)
for p in art.glob('*ARCHIVE*.json'):copy(p,resources/p.name)
(pack/'NETLIST_ARCHIVE_INDEX.json').write_text(json.dumps(netlists,indent=2)+'\n');(pack/'CRITICAL_PATHS.json').write_text(json.dumps(critical,indent=2)+'\n');(pack/'EXACT_R1_TRACE_COUNTER_COMPARISON.json').write_text(json.dumps(trace,indent=2)+'\n')
# Raw helper receipt initially used a broad control label; actual static wrapper ties
# unsupported inputs0. Preserve raw and state the accurate scope separately.
(pack/'WORD_EQ_SCOPE_R2.json').write_text(json.dumps({'dynamic_WB_classes':'all coincident controls unconstrained','static_resident_class':'reserve_resident,reserve_wb,become_wb,rollback_release,lower_release tied0 in BOTH actual R1/R2 wrappers','owner':'DYNAMIC_OWNER1 word proof; static hardwire is separately guarded by role/mapping induction','raw_scripts':'functional_and_diagnosis/word-induction-v2','global_controller_formal_equivalence':False},indent=2)+'\n')
comparison=json.loads((art/'FINAL_COMPARISON_v2/R1_R2_COMPARISON.json').read_text());rows=comparison['modes'];now=datetime.datetime.now(datetime.timezone.utc).isoformat();receipt={'schema':'RTL_COST_R2_RECEIPT','Goal':'EPL2_RTL_COST_TIMING_REFINEMENT_R2_BOUNDED','status':'FUNCTIONAL_THREE_MODE_MAP_STA_COMPLETE_TIMING_UNCLOSED','authority':'f2a2fec3ee5e1bb42aa298c84d25bdd9bd70e13e','canonical_RTL_commit':canonical,'source_files':json.loads((art/'B16-map-v2/FLOW_RECEIPT.json').read_text())['RTL_files'],'R1_frozen_publication':frozen,'T0_UTC':'2026-10-17T17:30:58Z','checkpoint4h_UTC':'2026-10-17T21:30:58Z','hard6h_stop_UTC':'2026-10-17T23:30:58Z','reports_collected_UTC':now,'finite_SIM_spec_Core':'9bd30ed913c5058b5d952fbeb2e67cb5e4644b3f','formal_SIM_changed':False,'Lane5_app_runs_started':0,'new_pipeline_or_throughput_changes':False,'R1_SIM_RTL_gaps_remain':True,'same_library_SDC_mapping_effort_RTL_all_modes':True,'all_modes_timing_unclosed':all(x['R2_target_WNS_ns']<0 for x in rows),'SRAM_macro_area':None,'SRAM_macro_delay':None,'whole_slice_PPA':False,'paper_performance_pairing_eligible':False,'DC':'UNRUN_NO_DC_SHELL_PRECISE_SCRIPTS_FILELIST_CONSTRAINTS_ENV_DELIVERED','power_postlayout':'UNRUN','qualification':'actual full-size base+pin/capacity/WAD/stale/backpressure/GEN3+Unified1167; Lane3 actual10vectors per mode; actual source helper SAT; no whole-GPU/late dynamic rollback/post-map proof','source_binary_trace_identity':'per-run RTL/config/VVP/netlist/SDC/Lib/tool/stimulus hashes, all bound to canonical RTL blobs','artifact_root':str(art),'modes':rows,'TVD_three_tests':'NOT_COMPILED_NOT_RUN','preserved_Core_candidates':{'TVD':'be5dcbe1fa5b9a501e81a77a6c399e6f6530e536','common':'099aeb5ac002ddc03ab8dc295caa1333d9aa50e1','structural':'26ed1da60249727870802c84f52fabe72274c541'}}
(pack/'RTL_COST_R2_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');(pack/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
lines=['# EP-L2 RTL R2 bounded refinement','','Actual finite full-capacity controller/access cut; all three modes have unclosed timing.','No whole-L2 area/Fmax, target-GPU PPA or current-SIM-performance coupling.','','|Mode|R1 area|R2 area|Change|R1 WNS ns|R2 WNS ns|R2 WNS2ns|','|---|---:|---:|---:|---:|---:|---:|']
for r in rows:lines.append(f'|{r["mode"]}|{r["R1_area"]:.3f}|{r["R2_area"]:.3f}|{r["area_change_percent"]:.3f}%|{r["R1_target_WNS_ns"]:.6f}|{r["R2_target_WNS_ns"]:.6f}|{r["R2_2ns_WNS_ns"]:.6f}|')
lines+=['','All areas are actual Nangate typical1.1V25C Liberty reference units. Same library','hash2efd0b32, SDCde89d1bd, fast-clean ABC883ps, IO/load/PVT/units/widths and','GEN32/full1024/1168/128/4x292/P1. No false/multicycle/reset exception.2ns is a','separate STA of the same mapped netlist. Both raw and normalized mapped netlists','are included as lossless gzip; original and archive hashes are indexed.','','Balanced per-bank first-free,16-word metadata distribution, local shared increment','and proven static map/owner/role hardwires preserve finite capacities, grant/service','and lifecycle events. The exact R1 base terminal counts AND cycles match for all','three modes; Unified last slot/bank3 drain also matches. This is bounded functional','evidence, not global/post-map equivalence or whole-app numerical proof.','','R1 is immutable. Its known pin old-red artifact is reused, not rerun. New-green pin','cases run against R2. Lane3 numeric10cases/13snapshot-read+10final-lines per mode','consume actual RTL output. Abstract observe strings are covered separately by the','base fixture; they are not automatically proved by the byte reference. Metadata','word induction has explicit static-input restrictions; read WORD_EQ_SCOPE_R2.','','Full helper first-free SAT covers every binary mask at292/128/16/64. Full1168x32','read mux SAT passed after an appropriately admitted8GiB phase; the2GiB stop and','the shared-monitor false output stop are preserved. The corrected optional proof','monitors only its own output directory; global12GiB/floors never changed.','','Read the actual primary critical paths, module cost breakdown, and additional','register/control paths. Additional path filters retain exact primary WNS/TNS and','keep reset timed; no path exception improves the table. High fanout/reset, metadata','and interface timing/DRC remain; no physical buffer/CTS/layout closure is claimed.','','SRAM four292x1024 1RW/128byte-enable boundaries total146KiB; actual macro area/delay','remain UNKNOWN, not DFF data-array estimates. Native full-address Tag/LRU/dirty-byte','MSHR/NoC/lower queues remain external UNKNOWN costs. Control metadata and1024-bit','copy/request/response/WB holding registers are actually standard-cell charged.','','SIM/RTL frontend II4/II3, static copy, return/arbitration/native approval differences','from R1 remain. No R2 cycle/register stage was added; no official simulator patch or','Lane5 app was launched. A later timing model needs Lane1 review after real buffering,','macro binding and throughput matching. No blanket extra hit cycle is authorized.','','DC entrance rtl/ep_l2/flow/run_dc_r2.sh uses same RTL/filelist/common SDC and explicit','actual DB/PVT/operating condition/units/drive/load. dc_shell absent: DC UNRUN. Power','and post-layout UNRUN. See DC_HANDOFF_R2; no made-up target library or macro result.','','Resources: central leases; own cap stays12GiB despite a later shared16GiB policy;','workspace48GiB/Share40GiB/availableRAM64GiB/global CPU and memory protections remain.','All R1 reports/netlists/tests and old review packs preserved; only own new R2 copies','were losslessly archived. No other project process/data/quota changed.','','Local canonical artifact root: '+str(art),'Source canonical RTL: '+canonical,'Read RTL_COST_R2_RECEIPT.json and attached evidence; unpublished/premature attempts','are retained engineering history, not additional accepted performance evidence.']
(pack/'README.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'pack':str(pack),'files':len([p for p in pack.rglob('*') if p.is_file()]),'bytes':sum(p.stat().st_size for p in pack.rglob('*') if p.is_file())}))
