#!/usr/bin/env python3
"""Bounded preparation from saved proofs and two small commandlists only.

Never opens a trace body, runs native_fallback.build/verify, creates a registry,
or launches a compiler/native test/simulator. Outputs are proposals, not gates.
Run from the original C Framework root. Existing output bytes are immutable.
"""
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import time

resource.setrlimit(resource.RLIMIT_AS, (256 * 2**20, 256 * 2**20))
START = time.monotonic()
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
CORE_ROOT = Path('/workspace/worktrees/gpgpu-sim-ep-l2-ms20261019-c-ro-v1')
D = '6825d1cd0c87d8b0122e03a9dff5253c873b747b'
C = '06cf7fd7d5dd7d0f0815345d4c692ee01bc3e025'
CORE = 'd010911e3174a3764791183cd108fe4664ba8731'
FW = '9dd1ee57a83d83b56b7874bc7c716185ab52c8f7'
BINARY = '61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5'
PACK = 'docs/ep_l2/review_packs/MS20261021_D_WORKLOAD_PREFREEZE_r1/'
DP = 'docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/input_suitability_20261020_r1/'
EMPTY = b'first_line,last_line_inclusive\n'
PREP = 'PREPARED_NOT_E_QUALIFIED_NOT_ADOPTED'
reads, checks = [], []


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check(name, condition):
    if not condition:
        raise ValueError(name)
    checks.append(name)


def blob(commit, path, core=False):
    repo = CORE_ROOT if core else ROOT
    size = int(subprocess.check_output(['git', '-C', str(repo), 'cat-file', '-s', commit + ':' + path]))
    if size > 1024 * 1024 or sum(x['bytes'] for x in reads) + size > 4 * 1024 * 1024:
        raise ValueError('metadata read bound')
    data = subprocess.check_output(['git', '-C', str(repo), 'show', commit + ':' + path])
    reads.append(dict(repo='swayhrl/gpgpu-sim' if core else 'swayhrl/accel-sim-framework',
                      commit=commit, path=path, bytes=len(data), sha256=sha(data)))
    return data


def small_command(path, expected):
    p = Path(path)
    check('commandlist <=64KiB: ' + p.parent.parent.name, p.stat().st_size <= 65536)
    data = p.read_bytes()
    check('commandlist exact saved SHA: ' + expected, sha(data) == expected)
    reads.append(dict(path=str(p), bytes=len(data), sha256=sha(data), kind='CURRENT_SMALL_COMMANDLIST'))
    return data


def write(name, value):
    data = value if isinstance(value, bytes) else (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError('immutable output already exists: ' + name)
    else:
        with path.open('xb') as f:
            f.write(data)
    return dict(path=str(path.relative_to(ROOT)), sha256=sha(data), bytes=len(data))


selection = json.loads(blob(D, PACK + 'INPUT_SELECTION_FROZEN.json'))
rodinia = json.loads(blob(D, PACK + 'RODINIA_LOCAL_METADATA.json'))
proof_bytes = blob(D, DP + 'CANDIDATE_AUDIT.json')
check('saved D complete-input proof SHA', sha(proof_bytes) == 'be9074886c6a91a760d3df48e9fddf1b4b114728ea12cb1a1d44d573db906532')
proof = json.loads(proof_bytes)
proposal = json.loads(blob(D, DP + 'SGEMM_PROPOSAL_TO_E.json'))
fallback_schema = blob(C, 'util/ep_l2/mechanism_study_c/native_fallback.py')
runtime = blob(CORE, 'src/gpgpu-sim/ep-l2-ro-runtime.inc', core=True).decode()
oracle = blob(CORE, 'src/gpgpu-sim/ep-l2-ro-oracle.h', core=True).decode()
check('source has explicit empty fallback scope', 'SAFE_FALLBACK_NO_CERTIFIED_LINES' in runtime and 'NO_READONLY_CERTIFICATION' in runtime)
check('source rejects nonempty fallback ranges', 'fallback cannot enable any RO line' in runtime and 'native fallback must certify zero lines' in oracle)
check('source binds manifest/ranges SHA', 'RO manifest SHA256 mismatch' in runtime and 'RO range SHA256 mismatch' in runtime)

sg = next(x for x in selection['rows'] if x['workload'] == 'sgemm')
bf = next(x for x in selection['rows'] if x['candidate_id'] == 'D_WL_PREFREEZE_BFS_GRAPH65536_r1')
sg_proof = next(x for x in proof['results'] if x['workload'] == 'sgemm')
bf_saved = next(x for x in rodinia['inputs'] if x['variant'] == '__data_graph65536_txt')
sg_cmd = small_command(sg['entry'], sg['commandlist_sha256'])
bf_cmd = small_command(bf['entry'], bf['commandlist_sha256'])
check('SGEMM complete commandlist matches original saved proposal', sg_cmd.decode() == proposal['full_commandlist'])
check('BFS complete commandlist matches saved D literal', bf_cmd.decode() == bf_saved['commandlist_literal'])
check('SGEMM one full saved native body', len(sg_proof['files']) == 1 and sg_proof['files'][0]['status'] == 'COMPLETE_NATIVE_OPCODE_COVERAGE')
check('SGEMM inherited composite matches frozen selection', sg_proof['trace_content_sha256'] == sg['trace_content_sha256'] == proposal['trace_content_sha256'])
check('SGEMM inherited instructions match', sg_proof['full_active_lane_instruction_records'] == sg['full_lane_instructions'] == 1658916864)
check('SGEMM saved non-atomic result only, no new proof', sg_proof['files'][0]['global_atomic_records'] == 0 and not sg_proof['E_scientific_acceptance'])
sg_names = [s for s in sg_cmd.decode().splitlines() if s.startswith('kernel')]
check('SGEMM ordered kernels exactly saved full proof', sg_names == [x['name'] for x in sg_proof['files']])
body = sg_proof['files'][0]
body_path = Path(sg['entry']).parent / body['name']
check('SGEMM current stat size matches saved body (no content read)', body_path.stat().st_size == body['bytes'] == 2216170035)

artifacts = []
artifacts.append(write('SGEMM_COMMANDLIST.txt', sg_cmd))
artifacts.append(write('BFS_COMMANDLIST.txt', bf_cmd))
artifacts.append(write('sgemm_empty_fallback/certified_ranges.csv', EMPTY))
manifest = dict(
    schema='EP_L2_RO_ORACLE_V1', status='SAFE_FALLBACK_NO_CERTIFIED_LINES',
    scope='NO_READONLY_CERTIFICATION', epoch='whole_commandlist',
    framework_source_commit=C,
    address_domain='CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS',
    commandlist=sg['entry'], commandlist_sha256=sha(sg_cmd),
    kernels=[dict(path=str(body_path), sha256=body['sha256'], bytes=body['bytes'])],
    kernel_count=1, unresolved_opcodes={'NO_READONLY_CERTIFICATION': 1},
    assumptions=[],
    fallback_reason='SGEMM full-epoch RO opportunity UNKNOWN; explicitly certify no lines on its own saved complete frozen input. Not a measured zero-RO proof.',
    counts={'CERTIFIED_RO_lines': 0, 'CERTIFIED_RO_read_lane_references': 0},
    artifacts={'certified_ranges.csv': sha(EMPTY)}, runtime_qualification=False,
    preparation_status=PREP,
    identity_lineage='Metadata candidate assembled from exact saved D full-input proof; body SHA inherited, not freshly rehashed. framework_source_commit pins existing C schema baseline, not runtime or a claim native_fallback.build executed.',
    policy='Fixed F T/M stay ON; empty certificate admits no RO transaction. All addresses retain ordinary W/V/native routing and real capacity/order/drain guards. E must independently bind full input, manifest/ranges, exact source/main/config/profile and qualification before any separately authorized use.')
check('candidate empty ranges exact native grammar', EMPTY == b'first_line,last_line_inclusive\n')
check('candidate certifies no lines and is not runtime qualified', not manifest['runtime_qualification'] and manifest['counts']['CERTIFIED_RO_lines'] == 0)
manifest_ref = write('sgemm_empty_fallback/manifest.candidate.json', manifest)
artifacts.append(manifest_ref)

commands, hosts, kernels = [], [], []
for line_no, raw in enumerate(bf_cmd.decode().splitlines(), 1):
    if not raw:
        continue
    if raw.startswith('kernel'):
        kernels.append(raw)
        commands.append(dict(command_line=line_no, kind='KERNEL', kernel=raw, ordinal=len(kernels)))
    else:
        fields = raw.split(',')
        check('BFS host command grammar at line ' + str(line_no), len(fields) == 3 and fields[0] == 'MemcpyHtoD')
        a, n = int(fields[1], 16), int(fields[2])
        check('BFS host range valid at line ' + str(line_no), 0 <= a < 2**64 and 0 < n <= 2**64-a)
        first, last = a & ~127, (a+n-1) & ~127
        host = dict(command_line=line_no, kind=fields[0], address=f'{a:016x}', bytes=n,
                    after_kernel_count=len(kernels), before_kernel_ordinal=len(kernels)+1,
                    phase='INITIAL_PREFIX' if not kernels else 'POST_INITIALIZATION_UPDATE',
                    first_affected_line=f'{first:016x}', last_affected_line_inclusive=f'{last:016x}',
                    affected_line_count=(last-first)//128+1,
                    affected_byte_begin=f'{first:016x}', affected_byte_end_exclusive=f'{last+128:016x}')
        hosts.append(host); commands.append(host)
initial = [x for x in hosts if x['phase'] == 'INITIAL_PREFIX']
later = [x for x in hosts if x['phase'] != 'INITIAL_PREFIX']
check('BFS all twenty launches ordered, no ROI/substitution', kernels == [f'kernel-{i}.traceg' for i in range(1,21)])
check('BFS 36 commands: 20 kernels +16 HtoD', len(commands) == 36 and len(hosts) == 16)
check('BFS initial seven and later nine copies retained', len(initial) == 7 and len(later) == 9)
check('BFS later updates after exact two-kernel boundaries', [x['after_kernel_count'] for x in later] == list(range(2,20,2)))
check('BFS all nine later writes affect same whole128B line', all(x['address'] == '00007fb5155f0000' and x['bytes'] == 1 and x['affected_line_count'] == 1 for x in later))
check('BFS initial prefix includes one-byte flag', initial[-1]['address'] == later[0]['address'] and initial[-1]['bytes'] == 1)
check('BFS true initial total includes flag byte', sum(x['bytes'] for x in initial) == 2555905)
check('BFS all copy bytes include ten one-byte writes', sum(x['bytes'] for x in hosts) == 2555914)
exclusions = [dict(first_line='00007fb5155f0000', last_line_inclusive='00007fb5155f0000',
                   byte_begin='00007fb5155f0000', byte_end_exclusive='00007fb5155f0080',
                   reason='Nine post-initialization HtoD writes, every affected sector/neighbor byte on this128B line excluded for the entire epoch',
                   command_lines=[x['command_line'] for x in later])]
bfs = dict(schema='C_BFS_FULL_COMMAND_HOST_BOUNDARIES_V1', status='DONE_HOST_BOUNDARIES_ONLY_NOT_RO_CERTIFICATE',
           preparation_status=PREP, commandlist=bf['entry'], commandlist_sha256=sha(bf_cmd),
           kernel_count=20, host_command_count=16, initial_HtoD_bytes=2555905,
           initial_nonflag_HtoD_bytes=2555904, later_HtoD_bytes=9, all_HtoD_bytes=2555914,
           commands=commands, whole_epoch_required_host_line_exclusions=exclusions,
           scope='Every byte of the complete small commandlist freshly checked. No kernel body, graph payload or new whole-epoch proof read/generated.',
           command_limits='No DtoH/payload values are represented here. This does not prove absence of real host reads, copies or external writers; source/capture contract remains unresolved. Do not synthesize/drop stop-flag commands or guess payload values.',
           ordinary_path='Later excluded uncovered updates may use ordinary clean/quiescent prefill only after actual native ownership/drain/version guards; not initial-only. A certified-line contradiction refuses before mutation. Empty coverage grants no waiver of host ordering or input validity.',
           unresolved=['Complete20-kernel byte/native grammar/instruction and global-atomic evidence absent in reused D metadata; no fresh scan authorized.',
                       'Graph/source-node/source/build/capture identities and host numeric/payload/stop semantics require F packet or exact MISSING; upstream reference is not captured-source proof.',
                       'Canonical VA, no hidden aliases/external writers/MMIO and complete-visible-agent domain require explicit input contract; unresolved memory opcodes/agents prevent positive RO certification.',
                       'A full whole-epoch GPU read/write/atomic plus later-host exclusion proof is absent; all candidate RO opportunity UNKNOWN, no load-only/kernel-only inference.',
                       'Any new input/profile/runtime/execution eligibility remains independent E review; no native/application approval in this packet.'])
artifacts.append(write('BFS_HOST_BOUNDARIES.json', bfs))

packet = dict(schema='C_SGEMM_FALLBACK_BFS_HOST_PACKET_V1', task_id='C-SGEMM-FALLBACK-BFS-HOST-r1',
              batch_id='EPL2_WORKLOAD_PREPARATION_BATCH_r2', owner='C', status=PREP,
              assigned_preparation='DONE_BOTH_ASSIGNED_METADATA_GAPS',
              SGEMM=dict(candidate_manifest=manifest_ref,
                         trace_content_sha256=sg_proof['trace_content_sha256'],
                         saved_full_input_proof=dict(repo='swayhrl/accel-sim-framework',commit=D,path=DP+'CANDIDATE_AUDIT.json',sha256=sha(proof_bytes)),
                         body_identity='INHERITED_SAVED_FULL_BYTE_PROOF_NO_CURRENT_BODY_HASH',
                         underlying_RO_opportunity='UNKNOWN_NOT_MEASURED_ZERO',
                         proposed_certified_lines=0,
                         registration='E2_EXP_SGEMM_MEDIUM_20261020_r1 / REGISTERED_EXPLORATORY_HOLD_NOT_LAUNCHABLE',
                         cohort='SEPARATE_MAIN61_SGEMM_EXPLORATION_NOT_ORIGINAL_SEVEN_OR_BTREE_REPLACEMENT',
                         proposed_runtime=dict(core_source_commit=CORE,framework_source_commit=FW,binary_sha256=BINARY),
                         required_fixed_F_options={'-gpgpu_ep_l2_ro_tag_detach':'1','-gpgpu_ep_l2_ro_line_mshr_bypass':'1','-gpgpu_ep_l2_ro_scope':'NO_READONLY_CERTIFICATION'},
                         required_invariants='W/V/T/M ON, finite1168 payload, physicalP1, original Tag/MSHR/D512/directory capacity and all ideal/data-free/copy-free/capacity shortcuts OFF. A2 owns full exact S/F option map; this is no launch spec.',
                         oracle_binding_options={'-gpgpu_ep_l2_ro_manifest':manifest_ref['path'],
                                                 '-gpgpu_ep_l2_ro_manifest_sha256':manifest_ref['sha256'],
                                                 '-gpgpu_ep_l2_ro_ranges':str((OUT/'sgemm_empty_fallback/certified_ranges.csv').relative_to(ROOT)),
                                                 '-gpgpu_ep_l2_ro_ranges_sha256':sha(EMPTY)},
                         remaining_gates=['A2 exact common main61 S/F config and independently reviewable bindings, no placeholder READY.',
                                          'E independently rechecks actual complete input identity/native grammar/non-atomic proof and source-specific finite-F input/profile acceptance; existing generic native evidence is only reusable within exact scope.',
                                          'E independent explicit empty fallback review/adoption and manifest/range/hash/commandlist binding; missing/mismatch remains fatal, never silently fallback.',
                                          'Original source/capture/numeric provenance UNKNOWN remains a separate recapture/numeric limitation, not an invented universal veto of trace-model scope.',
                                          'Separate explicit execution/start/resource authorization and original registry entrypoint required after actual qualification.']),
              BFS=dict(host_boundary_artifact='BFS_HOST_BOUNDARIES.json', positive_RO_certificate='MISSING_NOT_CREATED',
                       underlying_RO_opportunity='UNKNOWN', required_excluded_line=exclusions[0],
                       remaining_gates=bfs['unresolved']),
              reused_unchanged=dict(prior_C_review_commit='8a32cd0078b4aa602ccfce7c7320a09077a617d8',
                                    FWT='Existing exact whole-epoch zero-RO proof/main61 Q retained; no Q revoked by missing recapture/numeric assets; old endpoints INCOMPLETE unchanged.',
                                    native='Exact main61 existing empty-fallback/host-update/late-response controls referenced in prior C review, NOT rerun, no new native PASS.',
                                    R35='FAIL_FROZEN; later full-joint replacements remain UNRUN; original Conv certificate and all HOLD/withdrawal boundaries unchanged.'),
              artifacts=artifacts,
              no_new_simulations_native_builds=True)
write('CANDIDATE_PACKET.json', packet)
write('SOURCE_AND_READ_BINDINGS.json', dict(inputs=reads, preparer_path=str(Path(__file__).relative_to(ROOT)),
                                          preparer_sha256=sha(Path(__file__).read_bytes()),
                                          full_trace_body_bytes_read=0, large_body_stat_only=str(body_path),
                                          native_fallback_build_or_verify_invoked=False))
write('METADATA_CHECKS.json', dict(status='PASS_METADATA_ONLY_NOT_NATIVE_OR_E_QUALIFICATION', checks=checks,
                                   check_count=len(checks), bytes_read=sum(x['bytes'] for x in reads),
                                   full_trace_body_bytes_read=0, native_tests=0, simulator_starts=0, main_binary_builds=0,
                                   elapsed_seconds=time.monotonic()-START,
                                   self_maxrss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024))
print(json.dumps(dict(status=PREP, checks=len(checks), metadata_bytes_read=sum(x['bytes'] for x in reads),
                      full_trace_body_bytes_read=0, output=str(OUT)), indent=2))
