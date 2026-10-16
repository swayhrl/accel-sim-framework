#!/usr/bin/env python3
"""Audit overlays and emit 18 non-executable R1.1 placeholders. No admission."""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
from run_ft_lane4_diagnostic import B16_MODES, ROOT


def grid():
    rows=[]
    modes={'OFF':dict(wb=False,meta=False,read_hit=False),**B16_MODES}
    for workload in ['convolutionSeparable','FWT_7_21','vectorAdd_4M','sad']:
        for mode,vector in modes.items():
            if mode=='I_WB_META' and workload not in {'convolutionSeparable','FWT_7_21'}:continue
            path=ROOT/'tests/ep_l2/ft_lane4/b16'/(mode.lower()+'.config')
            tokens=shlex.split(path.read_text(),comments=True)
            expected={'-gpgpu_ep_l2_ideal_'+k:str(int(v)) for k,v in vector.items()}
            if len(tokens)!=6 or dict(zip(tokens[::2],tokens[1::2]))!=expected:
                raise ValueError('overlay not restricted to expected ideal bits: '+str(path))
            conditions=['native_normal_exit','64_slice_resource_and_requester_closure',
                        'copy_lines_equals_staging_reads_equals_wb_lower_accept',
                        'unchanged_physical_bank_limit_and_real_response_path']
            if vector['wb']:conditions+=['wb_data_full=0','wbuf_full=0']
            if vector['meta']:conditions+=['line_mshr_full=0','descriptor_full=0','per_address_full=0']
            if vector['read_hit']:conditions+=['reads_served>0','reference_responses_live=0','reference_arrivals_live=0']
            rows.append(dict(workload=workload,mode=mode,expected_ideal_vector=vector,
                owner='lane5' if mode=='OFF' else 'lane4',status='NOT_RUN',
                core_source_commit=None,framework_source_commit=None,binary_sha256=None,
                runtime_config_sha256=None,trace_content_sha256=None,run_key=None,
                cycles=None,instructions=None,matched_baseline_run_key=None,
                qualified_release_sha256=None,scientific_acceptance='NOT_RUN',
                overlay_path=str(path.relative_to(ROOT)),overlay_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                required_observations=conditions))
    assert len(rows)==18
    return dict(schema='EPL2_LANE4_R1_1_PREPARATION_V1',executable=False,
        note='Source adaptation and overlays only; no compiled R1.1 identity is populated.',
        prerequisites=['official Lane1 R1.1 runtime',
            'current Lane5 repair gates and per-mode ideal gates',
            'current Lane5 OFF and ideal launch authorizations',
            'same-binary Lane5 B16 baseline on identical trace/epoch/features/termination',
            'original shared registry deduplication and live production admission; R0.1 priority'],
        preserved_identity_fields=['core_source_commit','framework_source_commit','binary_sha256',
            'trace_content_sha256','workload','epoch_range','feature_vector','termination_contract'],
        change_rule='Append only the hashed ideal overlay; recompute runtime_config_sha256 and run_key.',
        science='Conditional ideal diagnostic, not realizable speedup or a complete mathematical ceiling.',rows=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    with a.out.open('x') as f:json.dump(grid(),f,indent=2);f.write('\n')
    print('18 overlays/modes checked; 18 NOT_RUN; no registry admission or simulator invoked')
