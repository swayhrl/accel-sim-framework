"""Independent frozen source + exact ELF + pure CPU sscanf telemetry reachability check."""
from common import *

def uncomment(s):return re.sub(r'//[^\n]*|/\*.*?\*/','',s,flags=re.S)
def function(source,signature):
    start=source.index(signature);pos=source.index('{',start);depth=1;i=pos+1
    while depth:
        if source[i]=='{':depth+=1
        elif source[i]=='}':depth-=1
        i+=1
    return source[start:i]

def main():
    paths=['src/gpgpu-sim/gpu-sim.cc','src/gpgpu-sim/gpu-sim.h','src/gpgpu-sim/shader.cc','src/gpgpu-sim/dtc-l1-invalidation.h']
    source={p:blob(CORE_REPO,CANDIDATE_CORE,p).decode() for p in paths}
    shader=source[paths[2]];gpu=source[paths[0]];header=source[paths[1]]
    functions={
      'normal_kernel_stats':function(gpu,'void gpgpu_sim::gpu_print_stat('),
      'public_aggregate_stats':function(shader,'void gpgpu_sim::shader_print_dtc_l1_stats('),
      'normal_cache_stats':function(shader,'void gpgpu_sim::shader_print_cache_stats('),
      'legacy_l1_stats':function(shader,'void gpgpu_sim::shader_print_l1_miss_stat('),
      'per_SM_cache_stats':function(shader,'void ldst_unit::print_cache_stats('),
      'per_SM_DTC_stats':function(shader,'void ldst_unit::print_dtc_l1_stats(')}
    clean={k:uncomment(v) for k,v in functions.items()}
    checks=dict(normal_stats_calls_public_aggregate='shader_print_dtc_l1_stats(stdout)' in clean['normal_kernel_stats'],normal_stats_calls_cache_stats='shader_print_cache_stats(stdout)' in clean['normal_kernel_stats'],normal_stats_legacy_call_commented_out='shader_print_l1_miss_stat' not in clean['normal_kernel_stats'],aggregate_has_no_event_observer_print='m_dtc_invalidation' not in clean['public_aggregate_stats'] and 'DTC_INVALIDATE_V1_SUMMARY' not in clean['public_aggregate_stats'],normal_cache_stats_does_not_call_legacy_or_per_SM_printer=all(x not in clean['normal_cache_stats'] for x in ['print_dtc_l1_stats','print_cache_stats(','shader_print_l1_miss_stat']),legacy_calls_cluster_cache_stats='m_cluster[i]->print_cache_stats' in clean['legacy_l1_stats'],LDST_cache_stats_calls_event_printer='print_dtc_l1_stats(fp)' in clean['per_SM_cache_stats'],event_print_guarded_K1='if (m_config->dtc_l1_invalidate_on_source_event)' in clean['per_SM_DTC_stats'],runtime_flag_initialized_zero='gpu_runtime_stat_flag = 0;' in header,source_has_legacy_runtime_bit_guard='if (m_config.gpu_runtime_stat_flag & GPU_RSTAT_L1MISS)' in gpu)
    # The function definition name itself includes print_cache_stats; only inspect its body.
    checks['normal_cache_stats_does_not_call_legacy_or_per_SM_printer']=all(x not in clean['normal_cache_stats'].split('{',1)[1] for x in ['print_dtc_l1_stats','print_cache_stats(','shader_print_l1_miss_stat'])
    all_sources=git(CORE_REPO,'grep','-n','shader_print_l1_miss_stat(',CANDIDATE_CORE,'--','src')
    trace=subprocess.run(['git','-C',str(FW_REPO),'grep','-n','-E','shader_print_l1_miss_stat|print_cache_stats|print_dtc_l1_stats|gpu_print_stat','0c8fcb571977303f3e87ecb0cac6cf7bd25d3cfc','--','gpu-simulator'],capture_output=True,text=True)
    assert trace.returncode==1 and not trace.stdout
    library=Path('/workspace/builds/dtc-lane-x-k1-release-c0a5e2c3-174-v1/libcudart.so');assert sha(library)=='06957c897f8248fa2b08a5c18823207db8dda954c218337ba399ba70e7f97b56'
    disassembly=[]
    for name,symbol in [('terminal','_ZN9gpgpu_sim14gpu_print_statEy'),('aggregate','_ZNK9gpgpu_sim25shader_print_dtc_l1_statsEP8_IO_FILE'),('legacy','_ZNK9gpgpu_sim25shader_print_l1_miss_statEP8_IO_FILE')]:
        r=subprocess.run(['/usr/bin/objdump','-d','-C','--disassemble='+symbol,str(library)],capture_output=True,text=True)
        # GNU objdump --disassemble matches mangled symbol without -C.
        if not re.search(r'^\s*[0-9a-f]+:',r.stdout,re.M):r=subprocess.run(['/usr/bin/objdump','-d','--disassemble='+symbol,str(library)],capture_output=True,text=True)
        assert r.returncode==0 and re.search(r'^\s*[0-9a-f]+:',r.stdout,re.M)
        p=ROOT/(name+'_ELF_disassembly.txt');p.write_text(r.stdout);disassembly.append(dict(function=name,symbol=symbol,sha256=sha(p),calls=[line.strip() for line in r.stdout.splitlines() if re.search(r'\bcall',line)]))
    terminal=(ROOT/'terminal_ELF_disassembly.txt').read_text()
    checks['exact_ELF_terminal_calls_public_stats']='shader_print_dtc_l1_stats' in terminal
    checks['exact_ELF_terminal_no_legacy_call']='shader_print_l1_miss_stat' not in terminal
    config=blob(FW_REPO,'dab43027467d577291aabd6a5d2812d601219188','docs/dtc_l1/review_packs/DTC_LANE_AA3_GAUSSIAN_V1/config/FAST64_OO.config').decode()
    matches=re.findall(r'^-gpgpu_runtime_stat\s+(\S+)',config,re.M);assert matches[-1]=='500000'
    assert '#define GPU_RSTAT_L1MISS 0x10' in header
    # Exact production initialization statements, no GPU/Core construction, no trace.
    init=re.search(r'gpu_stat_sample_freq = 10000;\s*gpu_runtime_stat_flag = 0;\s*sscanf\(gpgpu_runtime_stat, "%d:%x", &gpu_stat_sample_freq,\s*&gpu_runtime_stat_flag\);',header).group(0)
    fixture='#include <cstdio>\n#include <cassert>\nint main(){ const char *gpgpu_runtime_stat="500000"; int gpu_stat_sample_freq; unsigned gpu_runtime_stat_flag;\n'+init+'\nstd::printf("freq=%d flag=%u L1MISS_enabled=%u\\n",gpu_stat_sample_freq,gpu_runtime_stat_flag,(gpu_runtime_stat_flag&0x10)!=0);assert(gpu_stat_sample_freq==500000 && gpu_runtime_stat_flag==0);return 0;}\n'
    cpp=PACK/'scripts/runtime_stat_flag_cpu.cc';cpp.write_text(fixture)
    exe=ROOT/'runtime_stat_flag_cpu';build=subprocess.run(['/usr/bin/g++','-std=c++11','-Wall','-Wextra','-O0',str(cpp),'-o',str(exe)],capture_output=True,text=True);assert build.returncode==0,build.stderr
    run=subprocess.run([str(exe)],capture_output=True,text=True);assert run.returncode==0 and run.stdout=='freq=500000 flag=0 L1MISS_enabled=0\n'
    checks['frozen_effective_runtime_L1MISS_flag_zero']=True
    assert all(checks.values()),checks
    write(PACK/'TELEMETRY_SOURCE_AND_ELF_AUDIT.json',dict(status='FAIL_CLOSED_NORMAL_REPLAY_K1_EVENT_TELEMETRY_UNAVAILABLE',Core=CANDIDATE_CORE,library_sha256=sha(library),checks=checks,source_SHA256={p:hashlib.sha256(s.encode()).hexdigest() for p,s in source.items()},functions=functions,all_legacy_call_sites=all_sources,Framework_build_source='0c8fcb571977303f3e87ecb0cac6cf7bd25d3cfc',Framework_no_direct_print_calls=True,ELF_disassembly=disassembly,CPU_fixture=dict(compile_argv=['/usr/bin/g++','-std=c++11','-Wall','-Wextra','-O0',str(cpp),'-o',str(exe)],source_sha256=sha(cpp),binary_sha256=sha(exe),returncode=run.returncode,stdout=run.stdout,no_GPU_or_trace=True),frozen_effective_runtime_stat='500000',debug_event_limit=0,diagnostic_parity='AA3 K1-only noncomparative acceptance preserved; issue is absence of normal replay output, not K0/K1 parity',full_simulations_started=0))
    print('CONFIRMED SCIENTIFIC STOP: frozen normal replay does not emit required K1 event summaries; no Core/config modification or simulator invocation.')

if __name__=='__main__':main()
