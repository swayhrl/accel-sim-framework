from pathlib import Path
import re

def require(ok,reason):
    if not ok: raise ValueError(reason)

def runtime_metrics(raw,expected_options):
    normal=False;metrics={};actual={}
    for line in Path(raw).open(errors='replace'):
        normal|='GPGPU-Sim: *** exit detected ***' in line
        match=re.fullmatch(r'gpu_tot_sim_(cycle|insn)\s*=\s*(\d+)\s*',line)
        if match:metrics[match[1]]=int(match[2])
        match=re.match(r'^\s*(-[A-Za-z0-9_:]+)\s+(.*?)\s*$',line)
        if match and match[1] in expected_options:
            value=match[2].rsplit(' # ',1)[0].strip()
            require(match[1] not in actual or actual[match[1]]==value,'conflicting native option dump')
            actual[match[1]]=value
    require(normal and set(metrics)=={'cycle','insn'},'missing actual complete native exit/counters')
    # All L2 research options and frozen geometry must appear in the native dump.
    scoped={k:v for k,v in expected_options.items() if k.startswith('-gpgpu_ep_l2_') or k in ('-gpgpu_cache:dl2','-gpgpu_cache:dl2_texture_only')}
    require(bool(scoped) and all(actual.get(k)==v for k,v in scoped.items()),'effective native L2 options mismatch/missing')
    return metrics
