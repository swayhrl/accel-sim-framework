#include "/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core/tests/ep_l2/potential_fixture.h"
#include <iostream>
int main(int argc,char **argv){assert(argc==8);setvbuf(stdout,NULL,_IOLBF,0);fixture f(argv,"512:2:64:64","S:32:128:8,L:B:m:L:P,A:128:1,128:0,32");
 assert(f.cache->tvd_enabled()&&!f.cache->ro_enabled());assert(f.cache->mshr_entry_capacity()==128&&f.cache->ep_l2_descriptor_pool_capacity()==512&&f.cache->ep_l2_wad_capacity()==128);assert(f.cache->ep_l2_payload_for_test().physical_slots()==1168);
 std::vector<new_addr_type> a;for(new_addr_type x=0;x<(1ull<<23)&&a.size()<110;x+=128)if(f.gpu->getMemoryConfig()->m_L2_config.set_index(x)==0)a.push_back(x);assert(a.size()==110);
 auto done=[&](mem_fetch *r){auto uid=r->get_request_uid();auto addr=r->get_addr();f.send(r);for(unsigned n=0;n<3000&&!f.replies.count(uid);n++){f.step();if(f.reads.count(addr)){f.return_read(addr);f.step();}}assert(f.replies.count(uid));};
 for(unsigned i=0;i<80;i++)done(f.make(a[i],false));
#ifdef NEW_CAP
 const auto *dir=f.cache->tvd_for_test();assert(dir->clean_occupancy()<=dir->clean_limit());
#endif
 // Revisit a definitely evicted first line: useful retained service or ordinary refetch are both valid.
 done(f.make(a[0],false));
 auto w=f.make(a[80],true);f.memory[a[80]]=f.expected.at(w->get_request_uid());done(w);
 for(unsigned i=81;i<90;i++)done(f.make(a[i],false));
 for(unsigned n=0;n<1000&&f.wb.empty();n++)f.step();assert(f.wb.size()==1&&f.lower_wb==1);auto old=f.wb[0];assert(f.cache->ep_l2_wad_contains(old->get_addr()));
 // Hold the real completion for multiple cycles; mandatory ownership remains, no optional reclaim can drop it.
 for(unsigned n=0;n<32;n++)f.step();assert(f.cache->ep_l2_wad_contains(old->get_addr()));f.sp->set_done(old);delete old;f.wb.clear();++f.completed_wb;
 for(unsigned n=0;n<1000&&f.part->busy();n++)f.step();assert(!f.part->busy()&&f.cache->ft_drained()&&f.sp->l2_char_no_resource_leak());assert(f.cache->ep_l2_wad_occupancy()==0&&f.cache->ep_l2_payload_pending_operations()==0);assert(f.replies.size()==f.expected.size());
 unsigned long long hash=1469598103934665603ull;for(auto &v:f.expected){hash=(hash^v.first)*1099511628211ull;for(auto z:v.second)hash=(hash^z)*1099511628211ull;}
 unsigned long long grants=0;for(unsigned b=0;b<4;b++)grants+=f.cache->ep_l2_payload_bank_grants(b);
 std::cout<<"CLEAN_CAP_PRODUCTION|cycles="<<f.gpu->gpu_sim_cycle<<"|replies="<<f.replies.size()<<"|lowerWB="<<f.completed_wb<<"|digest="<<hash<<"|grants="<<grants<<"|bankmax="<<f.bank_max<<"|drain=1\n";
#ifdef NEW_CAP
 std::cout<<"CLEAN_CAP_STATE|limit="<<dir->clean_limit()<<"|clean="<<dir->clean_occupancy()<<"|live="<<dir->occupied()<<"|mandatory="<<dir->mandatory()<<"\n";
#endif
}
