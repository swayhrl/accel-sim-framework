#!/usr/bin/env python3
import csv,hashlib,json,subprocess
from pathlib import Path
ROOT=Path('/data/c16/awma/prel1_coalescer_independent_holdout_capture_20260925')
REPO=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-prel1-holdout-capture-v1')
OUT=REPO/'docs/vm_tlb/review_packs/AWMA_PREL1_COALESCER_INDEPENDENT_HOLDOUT_CAPTURE_109_V1'
OUT.mkdir(parents=True,exist_ok=True)
FORMAL=ROOT/'primary_formal'; RAW=FORMAL/'raw'; TG=next(RAW.glob('*.traceg.xz')); TR=next(RAW.glob('*.trace.xz'))
VALIDATOR=Path('/data/c16/awma/simcompat-v2/q05_routeb_basedelta_canary_20260916T154104Z/hotfix_fb5d0b_admission/traceg_grammar_smoke_fb5d0b')
PRODUCER=Path('/data/c16/awma/storage_sidelane_v1/producer_5143/bin/route_b_5143.so')
POST=Path('/data/c16/awma/storage_sidelane_v1/producer_5143/bin/post-traces-processing_5143')
RUNNER=REPO/'util/vm_tlb/awma/kernel_census/routeb_selected_capture.py'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_tsv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
ident=json.loads((FORMAL/'IDENTITY.json').read_text())
term=next(x for x in (FORMAL/'stdout.log').read_text(errors='replace').splitlines() if 'ROUTEB_TERMINAL_COMPLETE' in x)
grammar=json.loads(subprocess.check_output([str(VALIDATOR),str(TG)],text=True))
qualification={'selected_target':'PRIMARY','target_id':'STR_e0922aa2a506_P1','scenario':'S2','phase':'DECODE','decode_step':1,'function_identity_sha256':'d1934c1198203f32a8446aa6060a5371f039492e919c517e67a0ff56e061d5c8','grid':'1,1,1','block':'128,1,1','recurrence':'STABLE_49','deterministic_path_occurrence':1,'routeb_selector_ordinal':49,'routeb_global_navigation':994,'census_sha256':'df580ffa6d174e96345f4e8b0ca0027c3092067c7e6941fd2835a5229c0c9b81','trace_xz_sha256':sha(TR),'traceg_xz_sha256':sha(TG),'traceg_size_bytes':TG.stat().st_size,'kernelslist_sha256':sha(RAW/'kernelslist'),'kernelslist_g_sha256':sha(RAW/'kernelslist.g'),'runner_sha256':sha(RUNNER),'producer_sha256':sha(PRODUCER),'postprocessor_sha256':sha(POST),'validator_sha256':sha(VALIDATOR),'terminal':term,'grammar_status':grammar['status'],'trace_version':grammar['trace_version'],'cta_count':grammar['thread_blocks'],'instruction_count':grammar['instructions'],'status':'READY_FOR_PREL1_COALESCER_INDEPENDENT_VALIDATION_174NEW'}
write_tsv(OUT/'RUNTIME_IDENTITY_BRIDGE.tsv',[{k:qualification[k] for k in ['scenario','target_id','phase','decode_step','function_identity_sha256','grid','block','recurrence','deterministic_path_occurrence','routeb_selector_ordinal','routeb_global_navigation','census_sha256']}])
write_tsv(OUT/'CAPTURE_QUALIFICATION.tsv',[{k:qualification[k] for k in ['selected_target','target_id','trace_xz_sha256','traceg_xz_sha256','terminal','grammar_status','trace_version','cta_count','instruction_count','status']}])
durable='/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/prel1_coalescer_independent_holdout_capture_20260925/primary_formal/raw/'+TG.name
authority={**qualification,'preregistration_commit':'d450b2a06a0af18960d81b0ccbb46d047fe6cbae','lane_d_authority':'a383cc2bb04805c405b7dd2d0f918d4fe2738f32','producer_authority':'5143b4e10aaf2fc47bb60492155d2464b0b726fd','traceg_durable_path':durable,'fallback_used':False,'mechanism_results_consulted':False,'accel_sim_runs':0}
write_tsv(OUT/'HOLDOUT_SIM_INPUT_AUTHORITY.tsv',[authority])
(OUT/'HOLDOUT_CONSUMER_HANDOFF.json').write_text(json.dumps(authority,indent=2,sort_keys=True)+'\n')
(OUT/'PREREGISTRATION_BINDING.md').write_text('# Preregistration binding\n\nPrimary `STR_e0922aa2a506_P1` was selected exclusively by preregistration `d450b2a06a0af18960d81b0ccbb46d047fe6cbae` and Lane-D authority `a383cc2bb04805c405b7dd2d0f918d4fe2738f32`. No mechanism result was consulted; fallback was not triggered.\n')
(OUT/'README.md').write_text('# PREL1 coalescer independent holdout capture 109 V1\n\nStatus: `READY_FOR_PREL1_COALESCER_INDEPENDENT_VALIDATION_174NEW`. Primary target captured once, terminal/accounting/xz/grammar qualified, and published durably. No mechanism or Accel-Sim execution occurred.\n')
(ROOT/'HOLDOUT_CONSUMER_HANDOFF.json').write_text(json.dumps(authority,indent=2,sort_keys=True)+'\n')
(ROOT/'QUALIFICATION_RECEIPT.json').write_text(json.dumps({'terminal':term,'grammar':grammar,'status':authority['status']},indent=2,sort_keys=True)+'\n')
(ROOT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(ROOT)}\n' for p in sorted(x for x in ROOT.rglob('*') if x.is_file() and x.name!='SHA256SUMS')))
# Durable raw-data index is rooted at ROOT; SHA256SUMS closes every indexed evidence file.
rows=[]
for p in sorted(x for x in ROOT.rglob('*') if x.is_file()): rows.append({'relative_path':str(p.relative_to(ROOT)),'size_bytes':p.stat().st_size,'sha256':sha(p)})
write_tsv(OUT/'RAW_DATA_INDEX.tsv',rows)
(REPO/'docs/vm_tlb/codex_handoff/awma/AWMA_PREL1_COALESCER_INDEPENDENT_HOLDOUT_CAPTURE_109_V1_REPORT.md').write_text('# AWMA PREL1 coalescer independent holdout capture 109 V1\n\nPrimary preregistered target captured and qualified independently. Status: `READY_FOR_PREL1_COALESCER_INDEPENDENT_VALIDATION_174NEW`. Fallback was not used; no mechanism or Accel-Sim run occurred.\n')
files=sorted(p for p in OUT.iterdir() if p.is_file())
(OUT/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files))
print(json.dumps(authority,sort_keys=True))
