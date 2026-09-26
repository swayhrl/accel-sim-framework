#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path('/data/c16/awma/p1_p2_native_qualification_20260926');H=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-p1-p2-native-qualification-v1/util/vm_tlb/awma/p1_p2_native/p1_p2_native_harness.py')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((ROOT/'PREREGISTRATION.json').read_text());new=sha(H);old=p['source_sha256']['harness']
a={'status':'PREREGISTRATION_ENGINEERING_AMENDMENT_2','preregistration_sha256':sha(ROOT/'PREREGISTRATION.json'),'previous_amendment_sha256':sha(ROOT/'PREREGISTRATION_AMENDMENT_1.json'),'old_harness_sha256':sha(H) if False else '0d247e8348dddf8999c8aaff7dcd151ad9cf770c970804883bcd7c236ab15743','new_harness_sha256':new,'reason':'Conditional Triton diagnostic stage2 used tl.arange(0,NS) with NS=9 although Triton requires a power-of-two range. Use BLOCK_S=next_power_of_2(NS) with explicit s<NS masks. Target, fixed split size/order, arithmetic, thresholds and formal repetitions are unchanged. First diagnostic canary failed before a formal receipt; this is the second and final surgical attempt for this optional diagnostic.','affected_point':'P1_FIXED_SPLIT_TRITON_256_B1','formal_science_entered_before_fix':False}
(ROOT/'PREREGISTRATION_AMENDMENT_2.json').write_text(json.dumps(a,indent=2,sort_keys=True)+'\n');print(json.dumps(a,sort_keys=True))
