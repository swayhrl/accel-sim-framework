#define main original_ro_module_tests_main
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/observation_guided_20261029_v1/round2/agent_c/ro_module_fixture_source78.cc"
#undef main
#include "mt_sector_counter_candidate.h"
#include <limits>
using ep_l2_mt_candidate::counters;
static admission observed_merge(transactions &t,identity h,mem_fetch *q,unsigned mask,counters *c) {
  auto s=t.diagnostic_state(h); // TEST adapter only. Production design forwards existing scalars.
  auto a=t.merge(h,q,mask,21,true,GLOBAL_DEMAND_READ);
  if(a==ACCEPTED)ep_l2_mt_candidate::observe(c,mask,s.required,s.issued,s.ready,s.reuse);
  return a;
}
static void strict_sector(bool enabled,bool T) {
 mshr_table shared(128,32,512,32);reference_port p;
 transactions t(shared,p,1168,certificate(),switches(T,true));t.begin_epoch(21,hash());
 auto h=p.reserve(0,0x1000,0);counters c;auto *o=enabled?&c:nullptr;
 assert(t.admit(21,0x1000,h,p.binding(0),request(2000),1,true,GLOBAL_DEMAND_READ)==ACCEPTED);
 assert(shared.num_entries_used()==0 && shared.descriptor_count_used()==1);
 assert(t.can_detach(h)==T);
 assert(observed_merge(t,h,request(2001),2,o)==ACCEPTED); // New sector, not previously required.
 t.lower_accepted(h,3);assert(t.fill(h,1,1));
 assert(observed_merge(t,h,request(2002),1,o)==ACCEPTED); // Ready request while OTHER sector pending.
 assert(observed_merge(t,h,request(2003),2,o)==ACCEPTED); // Strict requested-sector pre-ready revisit.
 assert(t.fill(h,2,2));
 assert(observed_merge(t,h,request(2004),1,o)==ACCEPTED); // Entire required set ready, response drain only.
 assert(observed_merge(t,h,request(2004),1,o)==DESCRIPTOR_OR_ADDRESS_FULL); // Duplicate UID no count.
 assert(!t.can_detach(h)); // Reuse protection persists, T does not bypass it.
 if(enabled){assert(c.exact && c.accepted_live_merge==4 && c.requested_not_ready==2 && c.previously_required_not_ready==1 && c.newly_required_not_ready==1 && c.requested_issued_not_ready==1 && c.all_requested_ready==2 && c.ready_with_other_required_pending==1 && c.ready_only_draining==1 && c.reuse_first==1 && c.reuse_first_without_strict_pending_revisit==1);}
 else assert(c.accepted_live_merge==0);
 response out;for(unsigned i=0;i<5;++i){assert(t.prepare_response(h,3+i,out));t.commit_response(h,true,3+i);}
 assert(t.drained() && t.end_epoch() && shared.descriptor_count_used()==0 && shared.num_entries_used()==0 && p.slots[0].pins==0);
 printf("MT_CPU|mode=M1T%u|observer=%u|semantic=admits1,merge4,lower2,responses5,descriptors0,line0,ready3,pins0|strict_pending=%llu|new_sector=%llu|ready_other_pending=%llu|ready_only_drain=%llu|reuse_first_without_strict=%llu|counter_bytes=%zu|PASS\n",T,enabled,(unsigned long long)c.previously_required_not_ready,(unsigned long long)c.newly_required_not_ready,(unsigned long long)c.ready_with_other_required_pending,(unsigned long long)c.ready_only_draining,(unsigned long long)c.reuse_first_without_strict_pending_revisit,sizeof(c));
}
static void ready_reuse_suppresses_detach(bool enabled,bool T) {
 mshr_table shared(128,32,512,32);reference_port p;transactions t(shared,p,1168,certificate(),switches(T,true));t.begin_epoch(21,hash());
 auto h=p.reserve(0,0x2000,0);assert(t.admit(21,0x2000,h,p.binding(0),request(2100),3,true,GLOBAL_DEMAND_READ)==ACCEPTED);t.lower_accepted(h,3);assert(t.fill(h,1,1));assert(t.can_detach(h)==T);
 counters c;assert(observed_merge(t,h,request(2101),1,enabled?&c:nullptr)==ACCEPTED);assert(!t.can_detach(h));
 assert(!t.detach(h));assert(t.fill(h,2,2));response out;for(unsigned i=0;i<2;++i){assert(t.prepare_response(h,3+i,out));t.commit_response(h,true,3+i);}assert(t.end_epoch());
 if(enabled)assert(c.previously_required_not_ready==0 && c.ready_with_other_required_pending==1 && c.reuse_first_without_strict_pending_revisit==1);
 printf("MT_CPU|case=ready_reuse_guard|mode=M1T%u|observer=%u|semantic=merge1,detach0,responses2,descriptors0|PASS\n",T,enabled);
}
int main(int argc,char **argv){
 assert(argc==3);bool enabled=std::string(argv[1])=="ON",T=std::string(argv[2])=="T1";
 original_ro_module_tests_main();strict_sector(enabled,T);ready_reuse_suppresses_detach(enabled,T);
 counters c;c.accepted_live_merge=std::numeric_limits<uint64_t>::max();c.accepted(1,1,1,0,false);assert(!c.exact);counters invalid;invalid.accepted(0,0,0,0,false);assert(!invalid.exact);
 puts("MT_CPU|overflow_and_invalid_mask_fail_closed=1|PASS");return 0;
}
