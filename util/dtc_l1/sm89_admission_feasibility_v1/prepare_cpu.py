#!/usr/bin/env python3
"""Pin source-only probes. Never patches an execution worktree or accepts SM89."""
import difflib,hashlib,json,pathlib,re,subprocess
repo=pathlib.Path(__file__).resolve().parents[3];root=pathlib.Path('/data/c16/dtc_sm89_admission_feasibility_109_v1');pack=repo/'docs/dtc_l1/review_packs/DTC_SM89_ADMISSION_FEASIBILITY_V1';build=root/'build';build.mkdir(exist_ok=True)
pin='18a68dcccd795f1b6cda75504e9450d00c9cee02'
def blob(ref,path):return subprocess.check_output(['git','show',ref+':'+path],cwd=repo)
paths=['gpu-simulator/trace-driven/trace_driven.cc','gpu-simulator/trace-parser/trace_parser.cc','gpu-simulator/trace-parser/trace_parser.h','gpu-simulator/trace-parser/warp_trace_stream.h','util/tracer_nvbit/tracer_tool/tracez_format.h','gpu-simulator/ISA_Def/ampere_opcode.h']
sourceids=[]
for path in paths:
 data=blob(pin,path);assert data==(repo/path).read_bytes();sourceids.append(dict(commit=pin,path=path,sha256=hashlib.sha256(data).hexdigest()))
s=blob(pin,paths[0]).decode();start=s.index('  // resolve the binary version');end=s.index('\n}\n',start);fragment=s[start:end]
assert fragment.count('exit(0);')==1
# This is only failure-status hardening. It does not add binary89 or alias a table.
patched_fragment=fragment.replace('    exit(0);','    fprintf(stderr, "TRACE_ADMISSION_REJECTED_NOT_EXECUTED\\n");\n    exit(EXIT_FAILURE);')
patched=s[:start]+patched_fragment+s[end:]
patch=''.join(difflib.unified_diff(s.splitlines(True),patched.splitlines(True),fromfile='a/gpu-simulator/trace-driven/trace_driven.cc',tofile='b/gpu-simulator/trace-driven/trace_driven.cc'))
(pack/'candidate_fail_closed.patch').write_text(patch)
macros={}
for p in ['kepler_opcode.h','pascal_opcode.h','volta_opcode.h','turing_opcode.h','ampere_opcode.h','hopper_opcode.h']:
 for name,value in re.findall(r'#define\s+(\w*BINART_VERSION)\s+(\d+)',blob(pin,'gpu-simulator/ISA_Def/'+p).decode()):macros[name]=int(value)
prefix='#include <cstdio>\n#include <cstdlib>\n'+''.join(f'#define {k} {v}\n' for k,v in macros.items())+'\nint Hopper_OpcodeMap=90,Ampere_OpcodeMap=80,Volta_OpcodeMap=70,Pascal_OpcodeMap=60,Kepler_OpcodeMap=35,Turing_OpcodeMap=75;\nint main(int argc,char**argv){ if(argc!=2)return 2;struct K{int binary_verion;} k{std::atoi(argv[1])};auto* kernel_trace_info=&k;const int* OpcodeMap=nullptr;\n'
suffix='\nstd::printf("CPU_DISPATCH_SENTINEL_ONLY version=%d table=%d; NO_SIMULATOR_EXECUTION\\n",k.binary_verion,*OpcodeMap);return 0;}\n'
(build/'dispatch_original.cc').write_text(prefix+fragment+suffix);(build/'dispatch_fail_closed.cc').write_text(prefix+patched_fragment+suffix)
# Exact frozen register-conversion body, wrapped for host-only observation.
a=s.index('  auto convert_reg_num =');b=s.index('\n  };',a)+5;lam=s[a:b].strip()
(build/'frozen_register_conversion.h').write_text(lam+'\n')
(pack/'FROZEN_CPU_SOURCE_IDENTITIES.json').write_text(json.dumps(dict(source_files=sourceids,probe_scope='Unmodified parser plus literal dispatcher/register-conversion fragments with CPU sentinels; no simulator execution, no ISA support expansion',dispatch_macros=macros),indent=2)+'\n')
print('Prepared frozen source probes and failure-only candidate; binary89 remains unsupported')
