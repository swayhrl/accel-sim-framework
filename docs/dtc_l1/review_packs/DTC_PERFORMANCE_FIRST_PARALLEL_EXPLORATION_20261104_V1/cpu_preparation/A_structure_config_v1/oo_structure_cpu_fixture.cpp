#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>
#include "dtc-l1-common.h"
using namespace dtc_l1;
config base_cfg(unsigned sets=64,unsigned ways=8,unsigned phys=640) {
 config c;c.selected_mode=mode::PAPER_OO;c.finite_service=true;c.progressive_wakeup=false;c.tag_hash_bankrow=true;c.logical_sets=sets;c.logical_ways=ways;c.physical_lines=phys;c.oo_pib_entries=128;c.ref_count_bits=13;c.tag_banks=4;c.tag_requests_per_bank_per_cycle=1;c.tag_requests_per_cycle=4;c.allocation_width=4;return c;
}
void fill_one(oo_frontend &f,uint64_t &cycle,uint64_t uid,uint64_t addr) {
 f.advance_service(cycle);assert(f.admit(uid));assert(f.try_serve_tag(cycle,addr));auto r=f.access(cycle,uid,addr);assert(r.kind==io_access_kind::NEW_MISS);f.complete(r.physical);f.advance_service(cycle+1);assert(f.retire_one_ready(cycle+2));cycle+=4;
}
void progress_case(const char *name,unsigned sets,unsigned ways,unsigned phys,bool expected_block) {
 auto c=base_cfg(sets,ways,phys);oo_frontend f(c);uint64_t cycle=1;
 for(unsigned i=0;i<640;++i)fill_one(f,cycle,i+1,uint64_t(i)*128);
 assert(f.occupancy()==0);assert(f.retires()==640);
 unsigned minset=999,maxset=0;std::vector<unsigned> bucket(sets,0);for(unsigned i=0;i<640;++i)++bucket[logical_tag_set(uint64_t(i)*128,sets,true)];for(auto n:bucket){minset=std::min(minset,n);maxset=std::max(maxset,n);}
 assert(f.admit(10001));unsigned blocked=0;for(unsigned j=0;j<16;++j){f.advance_service(cycle+j);auto r=f.access(cycle+j,10001,uint64_t(640)*128);if(r.kind==io_access_kind::NO_FREE_LINE)++blocked;else{assert(!expected_block);assert(r.kind==io_access_kind::NEW_MISS);break;}}
 if(expected_block){assert(f.allocated_lines()==640);assert(f.tag_evictions()==0);assert(maxset<ways);assert(blocked==16);assert(f.new_misses()==640);assert(f.no_free_physical_events()==16);}else assert(blocked==0);
 std::cout<<"{\"case\":\""<<name<<"\",\"sets\":"<<sets<<",\"ways\":"<<ways<<",\"physical_lines\":"<<phys<<",\"prior_requests_completed_and_retired\":640,\"prior_live_PIB_entries\":0,\"initial_per_set_min\":"<<minset<<",\"initial_per_set_max\":"<<maxset<<",\"repeated_NO_FREE_LINE\":"<<blocked<<",\"new_misses\":"<<f.new_misses()<<",\"allocated_lines\":"<<f.allocated_lines()<<",\"tag_evictions\":"<<f.tag_evictions()<<",\"expected_structural_HOLD\":"<<(expected_block?"true":"false")<<"}\n";
}
void pib_case(){auto c=base_cfg();c.oo_pib_entries=192;oo_frontend f(c);for(unsigned i=0;i<192;++i)assert(f.admit(i));assert(!f.admit(192));assert(f.occupancy()==192);assert(f.retire_one_ready(1));assert(!f.retire_one_ready(1));assert(f.retire_one_ready(2));std::cout<<"{\"case\":\"OO_PIB192_ADMISSION_AND_RETIRE_LIMIT\",\"admitted\":192,\"next_admission_blocked\":true,\"one_retirement_per_cycle_preserved\":true}\n";}
void ports_case(){auto c=base_cfg();c.tag_requests_per_bank_per_cycle=2;c.tag_requests_per_cycle=8;oo_frontend f(c);for(unsigned b=0;b<4;++b){assert(f.try_serve_tag(1,b*128));assert(f.try_serve_tag(1,b*128));}assert(!f.try_serve_tag(1,0));assert(f.try_serve_tag(2,0));assert(f.try_serve_tag(2,0));assert(!f.try_serve_tag(2,0));auto b=base_cfg();oo_frontend g(b);for(unsigned n=0;n<4;++n)assert(g.try_serve_tag(1,n*128));assert(!g.try_serve_tag(1,0));std::cout<<"{\"case\":\"TAG4BANK_2PERBANK_8TOTAL\",\"eight_grants_accepted\":true,\"ninth_total_and_third_samebank_rejected\":true,\"baseline_four_limit_preserved\":true}\n";}
int main(){progress_case("BASE64x8_POOL640",64,8,640,false);progress_case("TAG64x16_POOL640",64,16,640,true);progress_case("TAG128x8_POOL640",128,8,640,true);progress_case("PHYS768_TAG64x8",64,8,768,false);progress_case("PHYS1024_TAG64x8",64,8,1024,false);pib_case();ports_case();}
