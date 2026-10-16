#!/usr/bin/env python3
"""Independent fixed-record address witnesses for diagnostic projections."""
import json
from legacy_format_risk_detail_v1 import classify, footprints, projections, shared_service

# Original LUD member1 line104: P=0000fffe, base0x40, stride64.
frozen = list(range(0x40,0x400,64))
execution_first0 = list(range(0x80,0x440,64))
if frozen[0]!=0x40 or execution_first0[0]!=0x80:
    raise ValueError('LUD address witness')
c = projections(frozen,[execution_first0,frozen],4,'SHARED')
if c['records_with_different_active_addresses']!=1 or c['possible_shared_service_change_records']!=0:
    raise ValueError('Address distinction must survive equal shared-service count')
if shared_service(frozen)!=8 or shared_service(execution_first0)!=8:
    raise ValueError('32-bank independent word count')

# Original 2DConvolution member1 line58: firstP1 vs possible firstE0.
frozen = list(range(4,128,4))
execution_first0 = list(range(8,132,4))
if len(footprints(frozen,4,128))!=1 or len(footprints(execution_first0,4,128))!=2:
    raise ValueError('Global line-count counterexample')
if len(footprints(frozen,4,32))!=4 or len(footprints(execution_first0,4,32))!=5:
    raise ValueError('Global sector-count counterexample')

# Original Btree full32 list: lane28 differs; single-request count stays one.
c = projections([0x7f8eed50bc04],[[0x7f8ef0d10f88]],4,'CACHEABLE_GLOBAL_LOAD')
if c['possible_line128_identity_change_records']!=1 or c['possible_line128_count_change_records']!=0:
    raise ValueError('Single-lane tag identity distinction')
if classify('LDG.E.SYS')!='CACHEABLE_GLOBAL_LOAD' or classify('LDG.E.STRONG.GPU')!='BYPASS_GLOBAL_LOAD':
    raise ValueError('Frozen consumer load policy')
print(json.dumps(dict(status='PASS',independent_original_record_witnesses=3,
                      no_simulation=True,no_address_interpretation_selected=True)))
