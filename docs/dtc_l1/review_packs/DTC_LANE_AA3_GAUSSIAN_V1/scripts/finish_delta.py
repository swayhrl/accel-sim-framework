from common import *
profiles={p:json.loads((PACK/'specs'/f'{p}.json').read_text())['expected_full_default_and_config_echo'] for p,*_ in POINTS}
deltas=[]
for key in sorted(profiles['K0_32x4']):
    values=[profiles[p][key] for p,*_ in POINTS]
    if len({json.dumps(v) for v in values})>1:
        assert key in [K_OPTION,'-gpgpu_dtc_l1_logical_sets','-gpgpu_dtc_l1_logical_ways'],key
        deltas.append(dict(option=key,**{p:json.dumps(profiles[p][key]) for p,*_ in POINTS}))
assert len(deltas)==3
table(PACK/'CONTROLLED_DELTA.tsv',deltas)
write(PACK/'ENGINEERING_CORRECTIONS.json',dict(failed_CPU_preparation='prepare_stop_evidence.py final whitelist incorrectly spelled logical Tag option names as tag_sets/tag_ways',affected_data='No source/config/input/option values changed; source/input hashes and all CPU parser checks had completed before whitelist assertion',repair='Use actual production logical_sets/logical_ways names and complete only the deterministic delta table from existing checked profiles; fresh preparation script corrected',failed_stderr_sha256=sha(ROOT/'prepare_cpu.stderr'),actual_simulator_starts=0,corrected_script_sha256=sha(PACK/'scripts/prepare_stop_evidence.py'),completion_script_sha256=sha(Path(__file__))))
print('PASS: exactly K option, logical sets and logical ways differ across 267-field profiles.')
