// Independent bounded CPU qualification: exact Source78 production classes.
#include "/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core/tests/ep_l2/potential_fixture.h"
int main(int argc,char **argv){
 assert(argc==10);const unsigned ways=std::stoul(argv[8]);assert(ways==8||ways==16);const unsigned sets=std::stoul(argv[9]);assert(sets==32||sets==64);const std::string geo="S:"+std::to_string(sets)+":128:"+std::to_string(ways)+",L:B:m:L:P,A:128:1,128:0,32";setvbuf(stdout,NULL,_IOLBF,0);
 fixture f(argv,"512:2:64:64",geo.c_str());
 const bool unified=std::string(argv[3])=="2";assert(!f.cache->ro_enabled() && f.cache->tvd_enabled()==unified);
 const auto &c=f.gpu->getMemoryConfig()->m_L2_config;
 const auto &ram=f.cache->ep_l2_payload_for_test();
 assert(c.get_num_lines()==sets*ways && c.get_assoc()==ways && c.get_line_sz()==128);
 if(unified)assert(f.cache->tvd_for_test()->capacity()==128);
 assert(ram.physical_slots()==1168 && ram.bank_service_limit()==1 && ram.free_slots()==1168 && ram.ownership_consistent());
 assert(f.cache->mshr_entry_capacity()==128 && f.cache->ep_l2_descriptor_pool_capacity()==512 && f.cache->ep_l2_wad_capacity()==128);
 printf("SYSTEM_SOURCE78_CONSTRUCTOR|sets=%u|ways=%u|FT=%s|Payload=1168|D=512|LineMSHR=128|WAD=128|P1|PASS\n",sets,ways,argv[3]);
 std::vector<new_addr_type> same; for(new_addr_type a=0;a<(1ull<<20) && same.size()<ways+1;a+=128) if(f.gpu->getMemoryConfig()->m_L2_config.set_index(a)==0)same.push_back(a); assert(same.size()==ways+1);
 const new_addr_type victim=same[ways-1], incoming=same[ways];
 for(unsigned i=0;i<ways;i++){
  auto r=f.make(same[i],i==ways-1);
  if(i==ways-1)f.memory[victim]=f.expected.at(r->get_request_uid());
  f.send(r);f.until_frontend_empty();
 }
 assert(f.cache->ft_reserved_ways_for_test(0)==ways-1 && f.reads.size()==ways-1);
 auto r=f.make(incoming,true);auto uid=r->get_request_uid();f.memory[incoming]=f.expected.at(uid);
 f.send(r);for(unsigned n=0;n<1000 && !f.replies.count(uid);n++)f.step();
 assert(f.replies.count(uid));
 for(unsigned n=0;n<1000 && f.wb.empty();n++)f.step();
 assert(f.wb.size()==1 && f.lower_wb==1 && f.cache->ep_l2_wad_contains(victim));
 // Return independent pending sectors in descending address order.
 std::vector<new_addr_type> a;for(auto &x:f.reads)a.push_back(x.first);
 for(auto i=a.rbegin();i!=a.rend();++i){f.return_read(*i);f.step();}
 for(auto w:f.wb){assert(w->get_addr()==victim);f.sp->set_done(w);delete w;++f.completed_wb;}f.wb.clear();
 for(unsigned n=0;n<1000 && f.part->busy();n++)f.step();
 assert(!f.part->busy() && f.sp->l2_char_no_resource_leak() && f.cache->ft_drained());
 assert(f.replies.size()==f.expected.size() && f.completed_wb==1 && f.bank_max==1);
 assert(f.cache->ep_l2_wad_occupancy()==0 && f.cache->ep_l2_payload_pending_operations()==0);
 if(unified)assert(f.cache->tvd_for_test()->occupied()==1u);
 printf("SYSTEM850_SEMANTIC|cycles=%llu|replies=%zu|dirtyWB=%u|reverse_returns=%u|drain=1\n",f.gpu->gpu_sim_cycle,f.replies.size(),f.completed_wb,ways-1);
 f.part->print(stdout);
 printf("SYSTEM_SOURCE78_REAL_REQUESTS|sets=%u|ways=%u|requests=%zu|pending_peak=%u|dirtyWB=1|reverse_returns=%u|bankP1=1|drain=1|PASS\n",sets,ways,f.expected.size(),ways-1,ways-1);
}
