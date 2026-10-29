// Independent bounded CPU qualification: exact Source78 production classes.
#include "/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core/tests/ep_l2/potential_fixture.h"
int main(int argc,char **argv){
 assert(argc==8);setvbuf(stdout,NULL,_IOLBF,0);
 fixture f(argv,"512:2:64:64","S:32:128:8,L:B:m:L:P,A:128:1,128:0,32");
 assert(!f.cache->ro_enabled() && !f.cache->tvd_enabled());
 std::vector<new_addr_type> same; for(new_addr_type a=0;a<(1ull<<20) && same.size()<9;a+=128) if(f.gpu->getMemoryConfig()->m_L2_config.set_index(a)==0)same.push_back(a); assert(same.size()==9);
 const new_addr_type victim=same[7], incoming=same[8];
 for(unsigned i=0;i<8;i++){
  auto r=f.make(same[i],i==7);
  if(i==7)f.memory[victim]=f.expected.at(r->get_request_uid());
  f.send(r);f.until_frontend_empty();
 }
 assert(f.cache->ft_reserved_ways_for_test(0)==7 && f.reads.size()==7);
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
 puts("W_ONLY_SOURCE78_32X8_REAL_REQUESTS|requests=9|pending_peak=7|dirtyWB=1|reverse_returns=7|bankP1=1|drain=1|PASS");
}
