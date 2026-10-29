// PREPARED ONLY. Real Source78 component objects; no Trace kernel/model execution.
// Link only the exact existing Source78 headers+all matching libraries.
#include "/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core/tests/ep_l2/potential_fixture.h"
int main(int argc,char **argv) {
  // base overlay FTmode WBUF staticS64 WBquota bankOps
  assert(argc==8 && std::stoul(argv[3])==2 && std::stoul(argv[4])==16 &&
         std::stoul(argv[5])==0 && std::stoul(argv[6])==0 && std::stoul(argv[7])==1);
  fixture f(argv,"512:2:64:64","S:32:128:8,L:B:m:L:P,A:128:1,128:0,32");
  const auto &cfg=f.gpu->getMemoryConfig()->m_L2_config;
  const auto &ram=f.cache->ep_l2_payload_for_test();
  assert(cfg.get_num_lines()==256 && cfg.get_assoc()==8 && cfg.get_line_sz()==128);
  assert(f.cache->ft_enabled() && ram.ft_mode()==2 && ram.physical_slots()==1168 &&
         ram.bank_service_limit()==1 && !ram.static_s64());
  assert(!f.cache->tvd_enabled() && !f.cache->ro_enabled());
  assert(f.cache->mshr_entry_capacity()==128 &&
         f.cache->ep_l2_descriptor_pool_capacity()==512 &&
         f.cache->ep_l2_wad_capacity()==128);
  assert(f.cache->mshr_entries_used()==0 &&
         f.cache->ep_l2_descriptor_count_used()==0 &&
         f.cache->ep_l2_wad_occupancy()==0 &&
         f.cache->ep_l2_payload_pending_operations()==0 &&
         ram.free_slots()==1168 && ram.ownership_consistent() &&
         ram.fixed_quota_consistent() && f.cache->ft_drained());
  puts("W_ONLY_SOURCE78_COMPONENT|case=app32x8_constructor|FT=2|TVD=0|RO_runtime=0|RO_metrics=NOT_APPLICABLE|physical=1168|MSHR=128|D=512|WAD=128|bankops=1|model_starts=0|manual_ticks=0|requests=0|PASS");
  return 0;
}
