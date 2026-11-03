from pathlib import Path
import subprocess,json,hashlib
G=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_preparation_20261103_v1/planning-isolated.git');O=G.parent/'agents/C'
pre='docs/dtc_l1/plans/DTC_STAGE2_CH_MATCH_AND_PHASE_ATTRIBUTION_20261103_V1/'
names=['README.md','ANALYSIS_AND_DECISION_RULES.md','BASELINE_COVERAGE_GATE.tsv','GOAL_FOR_DTC_MAIN.md','WORKLOAD_PHASE_HYPOTHESES.tsv','VALIDATION.json'];receipts=[]
for n in names:
 b=subprocess.check_output(['git','-c','safe.directory='+str(G),'--git-dir='+str(G),'show','5ba029e60c2e7523b193043b345990c7ae52531c:'+pre+n]);receipts.append({'commit':'5ba029e60c2e7523b193043b345990c7ae52531c','path':pre+n,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
 if n in names[3:]:print(n,b.decode()[:13000])
atlas=['README.md','SOURCE_AUTHORITY.md','EVIDENCE_SCHEMA_V1R1.md','PROJECT_SCOPE_ADVISORIES_V1R1.md','project_views/DTC_L1.md','programs/cuda_samples/convolutionSeparable.md','programs/cuda_samples/scan.md','programs/cuda_samples/vectorAdd.md','programs/rodinia/hybridsort.md','programs/rodinia/particlefilter_naive.md']+[f'programs/polybench_gpu/{x}.md' for x in ['2DCONV','ATAX','MVT','BICG','GEMM','3MM']]
for n in atlas:
 b=subprocess.check_output(['git','-c','safe.directory='+str(G),'--git-dir='+str(G),'show','47a097aad4406893a07f8d230e1e0a850609bf39:docs/workload_atlas/'+n]);receipts.append({'commit':'47a097aad4406893a07f8d230e1e0a850609bf39','path':'docs/workload_atlas/'+n,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(O/'AUTHORITY_READ_RECEIPTS.json').write_text(json.dumps({'files':receipts,'limitations':'Read-only inspected byte anchors. Prior plan was snapshot330; final361fa331 supersedes status only, not historical evidence. Atlas source candidate is not capture ELF or numeric input certification.'},indent=2)+'\n')
