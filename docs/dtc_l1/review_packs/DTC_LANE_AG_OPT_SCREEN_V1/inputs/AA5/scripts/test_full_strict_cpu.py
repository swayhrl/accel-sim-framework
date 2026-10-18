"""Actual historical full-output strict parser negative tests; never invokes simulator."""
from strict_matrix import *
text=BASELINES[32].read_text();tests={
 'truncated_last_kernel':text[:text.rindex('kernel_name =')],
 'missing_exit':text.replace('GPGPU-Sim: *** exit detected ***',''),
 'wrong_instruction':text.replace('gpu_sim_insn = 11484','gpu_sim_insn = 11483',1),
 'wrong_CTA':text.replace('gpu_tot_issued_cta = 2\n','gpu_tot_issued_cta = 1\n',1),
 'wrong_member':text.replace('Processing kernel '+json.loads((PACK/'ORDERED_KERNELS.json').read_text())[0]['member_path'],'Processing kernel /wrong.traceg',1),
 'physical_balance':re.sub(r'(DTC_L1_oo_physical_allocated = )(\d+)',lambda m:m[1]+str(int(m[2])+1),text,count=1),
 'finite_population':text.replace('DTC_SERVICE_V1_samples = 398272\n','DTC_SERVICE_V1_samples = 398271\n',1),
 'terminal_live_Ref':text.replace('DTC_L1_oo_active_refs = 0\n','DTC_L1_oo_active_refs = 1\n',1),
}
rows=[]
for n,t in tests.items():
 require(t!=text,'negative_not_applied:'+n)
 try:parse(t,0,True)
 except Exception as exc:rows.append(dict(test=n,status='REJECTED',reason=repr(exc)))
 else:raise AssertionError('NEGATIVE_ACCEPTED:'+n)
write(PACK/'FULL_STRICT_CPU_NEGATIVES.json',dict(status='PASS_REJECTED_ALL_ACTUAL_HISTORICAL_OUTPUT_MUTATIONS',tests=rows,full_sim_starts=0));print(rows)
