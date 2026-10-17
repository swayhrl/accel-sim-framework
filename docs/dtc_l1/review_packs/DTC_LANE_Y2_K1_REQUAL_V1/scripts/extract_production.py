#!/usr/bin/env python3
"""Extract exact published method bodies into a namespace-isolated CPU fixture.
No production files are edited. This is source-body testing, not ABI integration.
"""
import argparse, hashlib, json, subprocess
from pathlib import Path

def braced(text,start):
    first=text.index('{',start);depth=0
    # Reviewed methods contain no brace characters in string literals/comments.
    for i in range(first,len(text)):
        depth += (text[i]=='{')-(text[i]=='}')
        if not depth:return text[start:i+1],i+1
    raise ValueError('unclosed brace')

def generate(source,out):
    shader=(source/'src/gpgpu-sim/shader.cc').read_text();gpu=(source/'src/gpgpu-sim/gpu-sim.cc').read_text()
    declarations=[
      ('shader.cc','void ldst_unit::invalidate('),
      ('shader.cc','bool ldst_unit::dtc_l1_finite_service_active() const'),
      ('shader.cc','bool ldst_unit::dtc_l1_paper_oo_active() const'),
      ('shader.cc','bool ldst_unit::dtc_l1_sector_oo_active() const'),
      ('shader.cc','bool ldst_unit::dtc_l1_m4_observe_admit('),
      ('shader.cc','void ldst_unit::dtc_l1_m4_observe_complete('),
      ('shader.cc','bool ldst_unit::dtc_l1_oo_select_ready('),
      ('shader.cc','bool ldst_unit::dtc_l1_service_collect('),
      ('shader.cc','void ldst_unit::dtc_l1_service_retired('),
      ('shader.cc','bool ldst_unit::dtc_l1_oo_consume_response('),
      ('shader.cc','bool ldst_unit::dtc_l1_oo_writeback_ready()'),
      ('shader.cc','void ldst_unit::dtc_l1_sample_service_occupancy('),
      ('shader.cc','void shader_core_ctx::cache_invalidate('),
      ('shader.cc','bool shader_core_ctx::warp_waiting_at_mem_barrier('),
      ('shader.cc','void simt_core_cluster::cache_invalidate('),
      ('shader.cc','unsigned simt_core_cluster::get_not_completed() const'),
      ('gpu-sim.cc','bool gpgpu_sim::dtc_l1_try_acquire_lower_request()'),
      ('gpu-sim.cc','void gpgpu_sim::dtc_l1_complete_lower_request()')]
    chunks=[];manifest=[]
    for file,needle in declarations:
        text=shader if file=='shader.cc' else gpu
        start=text.index(needle);body,end=braced(text,start)
        chunks.append(body)
        manifest.append(dict(source='src/gpgpu-sim/'+file,symbol=needle,first_line=text.count('\n',0,start)+1,last_line=text.count('\n',0,end)+1,sha256=hashlib.sha256(body.encode()).hexdigest(),transformation='none; enclosing test namespace only'))
    for name,needle in [('source_idle','int all_threads_complete = 1;'),('source_config','if (cache_config != m_shader_config->m_L1D_config.get_cache_status())')]:
        if name=='source_idle':
            start=gpu.index(needle,gpu.index('void gpgpu_sim::cycle()'))
            _,end=braced(gpu,gpu.index('if (m_config.gpgpu_flush_l1_cache)',start))
            body=gpu[start:end];wrapper='void gpgpu_sim::source_idle() {\n'+body+'\n(void)all_threads_complete;\n}'
        else:
            start=gpu.index(needle,gpu.index('void gpgpu_sim::change_cache_config('));body,end=braced(gpu,start)
            wrapper='void gpgpu_sim::source_config(FuncCache cache_config) {\n'+body+'\n}'
        chunks.append(wrapper)
        manifest.append(dict(source='src/gpgpu-sim/gpu-sim.cc',symbol=name,first_line=gpu.count('\n',0,start)+1,last_line=gpu.count('\n',0,end)+1,sha256=hashlib.sha256(body.encode()).hexdigest(),transformation='exact source-selected block wrapped as callable; cache reconfiguration aftermath omitted'))
    frozen=subprocess.check_output(['git','-C',str(source),'show','6fba0136f8465b59fe5858a950fa39efb265f654:src/gpgpu-sim/shader.cc'],text=True)
    begin=frozen.index('void ldst_unit::invalidate()');body,end=braced(frozen,begin)
    chunks.append(body.replace('ldst_unit::invalidate()', 'ldst_unit::frozen_invalidate()'))
    manifest.append(dict(source='src/gpgpu-sim/shader.cc',commit='6fba0136f8465b59fe5858a950fa39efb265f654',symbol='frozen ldst_unit::invalidate',sha256=hashlib.sha256(body.encode()).hexdigest(),transformation='method name only changed to frozen_invalidate for coexistence; body unchanged'))
    (out/'production_bodies.inc').write_text('\n\n'.join(chunks)+'\n')
    (out/'EXTRACTED_BODY_BINDING.json').write_text(json.dumps(dict(methods=manifest,scope='exact source statements with explicit clock/scoreboard/packet/operand-collector fixtures; real production OO frontend, service, observer and ordinary L1D cache; not a full GPU simulation'),indent=2)+'\n')
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(exist_ok=True,parents=True);generate(a.source,a.out)
