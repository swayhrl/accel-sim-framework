"""Create reviewable A-owned hook patch; never edit a Core public file."""
import argparse,difflib,hashlib,json,subprocess
from pathlib import Path
BASE='84359d4ba492acb639a2092fa271e9169038bf7d'
OLD='30c2920a3754bdaae09511f93d91873959c09f15'

def prepare(core,out):
 def git(ref,file):return subprocess.check_output(['git','-C',str(core),'show',ref+':'+file],text=True)
 before={};after={}
 def load(file):
  if file not in before:before[file]=git(BASE,file);after[file]=before[file]
  return after[file]
 def replace(file,old,new):
  s=load(file);assert s.count(old)==1,(file,old,s.count(old));after[file]=s.replace(old,new,1)
 h='src/gpgpu-sim/gpu-cache.h';cc='src/gpgpu-sim/gpu-cache.cc';ft='src/gpgpu-sim/ep-l2-ft-cache.inc'
 oldh=git(OLD,h);oldft=git(OLD,ft)
 # Same allocator, same line table, persistent generations. No new pool.
 decl=oldh[oldh.index('  // Lane 3\'s completion objects'):oldh.index('  void sector_masks(',oldh.index('  // Lane 3\'s completion objects'))]
 decl+='  mem_fetch *ro_descriptor_request(const ro_descriptor_handle &) const;\n  mem_access_sector_mask_t ro_descriptor_sectors(const ro_descriptor_handle &) const;\n'
 replace(h,'  void sector_masks(new_addr_type block_addr,',decl+'  void sector_masks(new_addr_type block_addr,')
 replace(h,'        m_ideal_meta(ideal_meta)','        m_ideal_meta(ideal_meta), m_ro_descriptor_count(0)')
 replace(h,'  const bool m_ideal_meta;','  const bool m_ideal_meta;\n  unsigned m_ro_descriptor_count;')
 replace(h,'    bool m_response_queued;\n    ep_l2_descriptor() : m_mf(NULL), m_response_queued(false) {',
  '    bool m_response_queued;\n    bool m_ro_external;\n    new_addr_type m_ro_line;\n    unsigned long long m_ro_generation;\n    ep_l2_descriptor() : m_mf(NULL), m_response_queued(false), m_ro_external(false), m_ro_line(0), m_ro_generation(0) {')
 replace(h,'    bool m_has_atomic;','    bool m_has_atomic;\n    bool m_ro_line_owner;\n    ep_l2::PayloadHandle m_ro_handle;')
 replace(h,'    mshr_entry() : m_has_atomic(false) {','    mshr_entry() : m_has_atomic(false), m_ro_line_owner(false) {')
 replace(cc,'void mshr_table::ensure_descriptor_available() {','#include "ep-l2-ro-mshr.inc"\n\nvoid mshr_table::ensure_descriptor_available() {')
 replace(cc,'  table::const_iterator i = m_data.find(block_addr);\n  if (i != m_data.end()) {',
  '  table::const_iterator i = m_data.find(block_addr);\n  if (m_descriptor_pool_size && ro_targets_on_line(block_addr)+(i==m_data.end()?0:i->second.m_list.size())>=m_descriptor_per_line_cap) return EP_L2_BLOCK_PER_ADDRESS_CAP;\n  if (i != m_data.end()) {')
 replace(cc,'    descriptor = ep_l2_descriptor();','    const auto generation=descriptor.m_ro_generation;\n    descriptor = ep_l2_descriptor();descriptor.m_ro_generation=generation;')
 replace(cc,'    if (entry->second.m_list.empty()) m_data.erase(entry);','    if (entry->second.m_list.empty() && !entry->second.m_ro_line_owner) m_data.erase(entry);')
 # Fields/callbacks only. Old feature_ro_pending_state guard is untouched.
 replace(h,'    m_ep_l2_feature_ro_pending_state = false;',
  '    m_ro_tag_detach=m_ro_line_mshr_bypass=false;\n    m_ro_ranges=m_ro_ranges_sha256=m_ro_manifest_sha256=m_ro_scope=m_ro_manifest=nullptr;\n    m_ep_l2_feature_ro_pending_state = false;')
 replace(h,'  bool m_ep_l2_feature_ro_pending_state;',
  '  bool m_ro_tag_detach,m_ro_line_mshr_bypass;\n  char *m_ro_ranges,*m_ro_ranges_sha256,*m_ro_manifest_sha256,*m_ro_scope,*m_ro_manifest;\n  bool m_ep_l2_feature_ro_pending_state;')
 replace(h,'  unsigned ep_l2_ft_mode() const { return m_ep_l2_ft_mode; }',
  '  bool ro_requested() const { return m_ro_tag_detach||m_ro_line_mshr_bypass; }\n  unsigned ep_l2_ft_mode() const { return m_ep_l2_ft_mode; }')
 replace(h,'class cache_config {','class cache_config {\n  friend class ep_l2_ro_runtime;')
 replace(h,'class l2_cache : public data_cache {','class ep_l2_ro_runtime;\nclass l2_cache : public data_cache {\n  friend class ep_l2_ro_runtime;\n  friend struct ep_l2_ms_c_ro_probe;')
 replace(h,'    validate_ep_l2_mode_config();','    validate_ep_l2_mode_config();\n    ro_init();')
 replace(h,'  bool ft_enabled() const {',
  '  ~l2_cache();\n  bool ro_enabled() const {return m_ro!=nullptr;}\n  bool access_ready() const;\n  void ro_frontend_cycle(mem_fetch *);\n  void ro_bind_commandlist(const char *);\n  void ro_begin_epoch();\n  void ro_end_epoch();\n  bool ro_drained() const;\n  bool ro_return(mem_fetch *,unsigned long long);\n  void ro_print(FILE *,unsigned) const;\n  bool ft_enabled() const {')
 replace(h,'  void validate_ep_l2_mode_config() const {',
  '  ep_l2_ro_runtime *m_ro;\n  void ro_init();\n  void validate_ep_l2_mode_config() const {\n    if(m_config.ro_requested() && (m_config.m_ep_l2_ft_mode!=2 || m_config.m_ep_l2_wbuf_entries!=16 || m_config.m_ep_l2_payload_mode!=2 || m_config.m_ep_l2_descriptor_pool_size!=512 || m_config.m_ep_l2_descriptor_per_line_cap!=32 || m_config.m_mshr_entries!=128 || m_config.m_ep_l2_wad_entries!=128 || m_config.m_ep_l2_bank_ops!=1 || m_config.m_ep_l2_static_s64 || m_config.m_ep_l2_wb_local_cap || m_config.m_ep_l2_mq2 || m_config.m_ep_l2_rg1 || m_config.m_ep_l2_ideal_wb || m_config.m_ep_l2_ideal_meta || m_config.m_ep_l2_ideal_read_hit)) {fprintf(stderr,"RO requires standalone U16 P1 D512/line128/WAD128\\n");abort();}\n')
 replace(h,'bool ft_drained() const { return ', 'bool ft_drained() const { return ro_drained() && (')
 replace(h,'!m_ft_quota.reserved && !m_ft_quota.live); }','!m_ft_quota.reserved && !m_ft_quota.live)); }')
 replace(h,'              ep_l2_payload_store::RESIDENT)',
  '              ep_l2_payload_store::RESIDENT &&\n          !(m_ep_l2_payload.resident(handle.payload_id).allocation_role==ep_l2_payload_store::RO && m_ep_l2_payload.resident(handle.payload_id).status==ep_l2_payload_store::RO_FILL_ATTACHED))')
 replace(h,'  bool ep_l2_needs_lower_read;','  bool ep_l2_needs_lower_read;\n  bool ep_l2_ro_lookup_wait=false;')
 # Existing paid RAM, role/operation accounting only, never another data RAM.
 replace(h,'enum role { RESIDENT, BYPASS, WB, IDEAL_REFERENCE };','enum role { RESIDENT, BYPASS, WB, IDEAL_REFERENCE, RO };')
 replace(h,'    BYPASS_READ\n','    BYPASS_READ, RO_FILL_WRITE, RO_RESPONSE_READ\n')
 replace(h,'    BYPASS_READY, WB_RESERVED, WB_STAGED','    BYPASS_READY, WB_RESERVED, WB_STAGED, RO_FILL_ATTACHED, RO_FILL_DETACHED')
 replace(h,'  bool banked() const { return m_mode == 2; }','  bool banked() const { return m_mode == 2; }\n  unsigned ft_mode() const {return m_ft_mode;}')
 replace(h,'  payload_handle preview_free(role r, unsigned bank = (unsigned)-1) const {','  payload_handle preview_free(role r, unsigned bank = (unsigned)-1) const {\n    if(r==RO && m_ft_mode!=2)return payload_handle();')
 replace(h,'  unsigned wb_used() const { return used(WB); }',
  '  unsigned wb_used() const { return used(WB); }\n  unsigned ro_used() const {return used(RO);}\n  unsigned long long bank_ro_fill_write() const {return m_bank_ro_fill_write;}\n  unsigned long long bank_ro_response_read() const {return m_bank_ro_response_read;}\n  unsigned long long m_bank_ro_fill_write=0,m_bank_ro_response_read=0;')
 replace(h,'used(RESIDENT) - used(BYPASS) - used(WB);','used(RESIDENT) - used(BYPASS) - used(WB) - used(RO);')
 replace(h,'      case BYPASS_READ: ++m_bank_bypass_read; break;',
  '      case BYPASS_READ: ++m_bank_bypass_read; break;\n      case RO_FILL_WRITE: ++m_bank_ro_fill_write;break;\n      case RO_RESPONSE_READ: ++m_bank_ro_response_read;break;')
 replace(h,'      } else if (s.allocation_role == WB) {',
  '      } else if (s.allocation_role == RO) {\n        if(m_ft_mode!=2 || (s.status!=RO_FILL_ATTACHED && s.status!=RO_FILL_DETACHED)) return false;\n      } else if (s.allocation_role == WB) {')
 # Restore narrow runtime hooks without replacing the current FT implementation.
 replace(cc,'#include "ep-l2-ft-cache.inc"','#include "ep-l2-ro-runtime.inc"\n#include "ep-l2-ft-cache.inc"')
 replace(cc,'  if (ft_enabled()) return ft_access(addr, mf, time, events);',
  '  if(m_ro)m_ro->check_access(mf);\n  if(ft_enabled()) {if(m_ro && !m_ro->query_admissible(mf))return RESERVATION_FAIL;auto result=ft_access(addr,mf,time,events);if(m_ro && result!=RESERVATION_FAIL)m_ro->record_accepted(mf);return result;}')
 replace(cc,'  plan = l2_access_plan();','  plan = l2_access_plan();\n  if(m_ro && m_ro->preview(mf,plan))return;')
 # Host guards remain native, plus whole-epoch certified-range protection.
 replace(ft,'  if (!ft_enabled()) { baseline_cache::force_tag_access(addr, time, mask); return; }',
  '  if (!ft_enabled()) { baseline_cache::force_tag_access(addr, time, mask); return; }\n  if(m_ro)m_ro->prefill_begin(m_config.block_addr(addr));')
 replace(ft,'  // This is untimed host initialization,',
  '  if(m_ro && !m_ro->prefill_allowed(m_config.block_addr(addr)))return false;\n  // This is untimed host initialization,')
 replace(ft,'  assert(m_ep_l2_payload.ownership_consistent());\n  return true;',
  '  if(m_ro)m_ro->prefill_complete(index,handle,owner,mask);\n  assert(m_ep_l2_payload.ownership_consistent());\n  return true;')
 replace(ft,'  mem_fetch *mf = baseline_cache::peek_next_access();\n  if (ft_enabled()) {',
  '  if(m_ro && m_ro->selected)return m_ro->reply.request;\n  mem_fetch *mf = baseline_cache::peek_next_access();\n  if (ft_enabled()) {')
 replace(ft,'  if (!ft_enabled()) return true;',
  '  if(m_ro && m_ro->has_response() && (m_ro->reply.transaction.valid() || m_ro->prefer_ro || !baseline_cache::access_ready()))return m_ro->prepare(cycle);\n  if (!ft_enabled()) return true;')
 replace(ft,'  if (!ft_enabled()) { baseline_cache::commit_next_access(); return; }',
  '  if(m_ro && m_ro->selected){m_ro->commit(ft_physical_cycle());return;}\n  if (!ft_enabled()) { baseline_cache::commit_next_access(); return; }')
 replace(ft,'  m_ft_read_refs.erase(it);','  m_ft_read_refs.erase(it);\n  if(m_ro)m_ro->prefer_ro=true;')
 merge=oldft[oldft.index('  if(m_ro) {\n    if(m_ro->native_owner_conflict'):oldft.index('  unsigned index = (unsigned)-1;',oldft.index('  if(m_ro) {\n    if(m_ro->native_owner_conflict'))]
 replace(ft,'  m_ep_l2_last_payload_request_result = ep_l2_payload_store::GRANTED;\n  const new_addr_type owner = m_config.block_addr(addr);\n  unsigned index = (unsigned)-1;',
  '  m_ep_l2_last_payload_request_result = ep_l2_payload_store::GRANTED;\n  const new_addr_type owner = m_config.block_addr(addr);\n'+merge+'  unsigned index = (unsigned)-1;')
 replace(ft,'  if (probe == RESERVATION_FAIL) return RESERVATION_FAIL;',
  '  if(probe==RESERVATION_FAIL && m_ro){m_ro->relieve(addr);probe=m_tag_array->probe(owner,index,mf,mf->is_write(),true);}\n  if (probe == RESERVATION_FAIL) return RESERVATION_FAIL;\n  if(ro_new && (!m_ro->capacity(mf,false) || !miss_queue_has_slots(mf->get_access_sector_mask().count()+(probe==MISS && m_tag_array->block_is_modified(index)))))return RESERVATION_FAIL;')
 replace(ft,'    if (read) {\n      if (m_mshrs.full(key))',
  '    if(ro_new) {slots+=mf->get_access_sector_mask().count();}\n    else if (read) {\n      if (m_mshrs.full(key))')
 replace(ft,'const cache_request_status result = data_cache::access(addr, mf, time, events);',
  'const cache_request_status result = ro_new ? m_ro->accept_new(mf,index,probe,time,events) : data_cache::access(addr, mf, time, events);')
 replace(ft,'else if (slot.pending_sector_mask.none()) slot.status =',
  'else if (slot.pending_sector_mask.none() && slot.allocation_role!=ep_l2_payload_store::RO) slot.status =')
 replace(ft,'void l2_cache::lower_accepted(mem_fetch *mf, unsigned long long cycle) {',
  'void l2_cache::lower_accepted(mem_fetch *mf, unsigned long long cycle) {\n  if(mf->ro_lower_packet()) {if(!m_ro)throw std::logic_error("RO packet without runtime");m_ro->tx->lower_accepted(ep_l2::PayloadHandle(mf->get_ep_l2_payload_id(),mf->get_ep_l2_payload_generation()),mf->get_access_sector_mask().to_ulong());return;}')
 mf='src/gpgpu-sim/mem_fetch.h'
 replace(mf,'  bool has_ft_wb_data() const',
  '  bool ro_lower_packet() const {return m_ro_lower_packet;}\n  void set_ro_lower_packet(){m_ro_lower_packet=true;}\n  bool has_ft_wb_data() const')
 replace(mf,'  bool m_ft_wb_data_valid;','  bool m_ft_wb_data_valid;\n  bool m_ro_lower_packet=false;')
 sub='src/gpgpu-sim/l2cache.cc'
 replace(sub,'    if (!m_config->m_L2_config.disabled() && m_L2cache->waiting_for_fill(mf)) {',
  '    if(mf->ro_lower_packet()) {if(m_L2cache->ro_return(mf,m_gpu->gpu_sim_cycle+m_gpu->gpu_tot_sim_cycle)){m_dram_L2_queue->pop();delete mf;}}\n    else if (!m_config->m_L2_config.disabled() && m_L2cache->waiting_for_fill(mf)) {')
 replace(sub,'    mem_fetch *mf = m_icnt_L2_queue->top();','    mem_fetch *mf = m_icnt_L2_queue->top();\n    if(!m_config->m_L2_config.disabled())m_L2cache->ro_frontend_cycle(mf);')
 # Deliberately leave dispatch/options to A's published interface. This patch
 # is a scoped cache/allocator adapter, not a complete runnable release.
 out.mkdir(parents=True,exist_ok=True)
 patch=''
 for f in before:
  bh=subprocess.check_output(['git','-C',str(core),'rev-parse',BASE+':'+f],text=True).strip()
  ah=subprocess.check_output(['git','-C',str(core),'hash-object','--stdin'],input=after[f],text=True).strip()
  patch+='diff --git a/'+f+' b/'+f+'\nindex '+bh+'..'+ah+' 100644\n'
  patch+=''.join(difflib.unified_diff(before[f].splitlines(True),after[f].splitlines(True),fromfile='a/'+f,tofile='b/'+f))
 (out/'CACHE_ALLOCATOR_ADAPTER.patch').write_text(patch)
 (out/'ADAPTER_PREIMAGES.json').write_text(json.dumps(dict(base=BASE,historical=OLD,
  status='SOURCE_ONLY_A_INTEGRATION_REQUIRED_NOT_COMPILED',files={f:dict(before=hashlib.sha256(before[f].encode()).hexdigest(),after=hashlib.sha256(after[f].encode()).hexdigest()) for f in before},
  remaining_A_owned_hooks=['Register new T/M/ranges/manifest options default0; never enable legacy rejected feature flags.',
   'Dispatch whole-commandlist bind/begin/end through GPU/partition from Framework exact commandlist; keep native host memcpy guards.',
   'Print ro_print at final full application terminal; reject unqualified combinations with A diagnostics and B victim.',
   'Add CMake fixture targets; preserve all current atomic/RG1/MQ2/quota/physical-clock repairs.']),indent=2)+'\n')
 return after

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--core',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();prepare(a.core,a.out)
