import pathlib,json,subprocess,shutil
P=pathlib.Path;T=P('/root/data/dtc_main_short3_20261024_v1');F=T/'docs-worktree';D=F/'docs/dtc_l1/review_packs/DTC_AE_MATCHED_HASH_SHORT3_20261024_V1'
code=(T/'tools/short3_controller_r2.py').read_text().replace('CONTROLLER_START_R2.json','CONTROLLER_START_R3.json').replace('short3_strict.py','short3_strict_r2.py').replace('.R2.CLI_EXECUTION.json','.R3.CLI_EXECUTION.json').replace('.R2.PREPARE.json','.R3.PREPARE.json').replace('.R2.ARCHIVE_CLI.json','.R3.ARCHIVE_CLI.json')
old=" for cell in matrix:\n  assert not (T/'control/qualification_ledger'/(cell+'.INTENT.json')).exists(),'consumed cell never restarted'"
new=""" for cell in matrix:
  existing=T/'control/qualification_ledger'/(cell+'.INTENT.json')
  if existing.exists():
   assert cell=='E2-AEF3-NN-DM','only the one closed original point may be consumed before this continuation'
   science=strict.terminal(cell);archive=read(T/'control'/(cell+'_ARCHIVE_RECEIPT.json'))
   assert archive['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
   completed.append({'cell':cell,'cycles':science['cycles'],'uuid':science['uuid'],'archive':archive,'original_spent_run_postprocess_only':True})
   state({'state':'PRESERVED_CONSUMED_CELL_ALREADY_ACCEPTED_ARCHIVED','cell':cell,'completed':completed})
   continue
  assert not existing.exists(),'consumed cell never restarted'"""
assert old in code;code=code.replace(old,new)
with (T/'tools/short3_controller_r3.py').open('x') as f:f.write(code)
shutil.copyfile(T/'tools/short3_controller_r3.py',D/'tools/short3_controller_r3.py')
with (D/'README.md').open('a') as f:f.write('''
## Expected-option metadata correction after first natural completion

NN-DM completed naturally in3.05s with6132cycles,1kernel/168CTA/1,284,872instructions and the original resource decision. The original single-line expected-option generator retained GEMM's trace option and truncated a quoted multiline DRAM timing string; the exact actual argv, input and all config bytes were correct. The first strict pass therefore held, and the finite controller sealed the11 unused starts. A corrected expectation resolver now parses the frozen config using quoted multiline semantics and binds -trace from the frozen argv; exactly these two metadata fields differ for every cell. Original specs, closed raw, launcher, simulator and configuration bytes remain unchanged. The corrected strict parser independently accepts the existing output; no NN-DM model rerun or refund occurs. R3 continues only the11 never-started cells after the original NN-DM archive/native restore is verified. Both stopped metadata controllers and their states are retained.
''')
print('R3_FINITE_UNUSED_ONLY_CONTROLLER_PREPARED')
