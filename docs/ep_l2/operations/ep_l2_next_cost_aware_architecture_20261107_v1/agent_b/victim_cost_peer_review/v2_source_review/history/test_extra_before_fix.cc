
#define main included_optional128_main
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/next_cost_aware_architecture_20261107_v1/agent_a/core/tests/ep_l2/test_optional128.cc"
#undef main
int main(int argc,char**argv) {
 setvbuf(stdout,nullptr,_IONBF,0);assert(argc==3);scenario f(argv[1],argv[2],true,true,false,1,2,1,16,false,2);
 for(unsigned i=0;i<257;++i){auto u=f.push(i*128ULL);f.await(u);}f.drain();
 auto x=const_cast<l2_cache::tvd_directory*>(f.cache()->optional_for_test());
 auto t=l2_cache::tvd_directory::ticket(0,x->at(0).incarnation);
 auto old=x->at(0);auto obs=x->preview_ticket(t,1,l2_cache::tvd_directory::READ_OP);
 l2_cache::tvd_directory::read_lease lease;
 assert(x->begin_read(obs,1,lease)==l2_cache::tvd_directory::OK);
 auto &store=const_cast<ep_l2_payload_store&>(f.cache()->ep_l2_payload_for_test());
 store.pin(old.payload);
 auto before=f.cache()->optional_spills_for_test();
 puts("STEP pinned fallback native");auto u=f.push(257*128ULL);f.await(u);
 assert(f.cache()->optional_spills_for_test()==before);
 assert(x->live(t) && x->at(0).payload==old.payload && x->at(0).readers==1);
 assert(x->cancel_read(lease)==l2_cache::tvd_directory::OK);store.unpin(old.payload);
 puts("PASS optional_pinned_fixed_RR_falls_back_no_scan_no_generation_loss");
 // Exercise the distinct Ext atomic fallback, then an actual Native Tag hit
 // write/read. We do not assert an independent atomic numerical oracle.
 const auto line=x->at(1).line;puts("STEP ext atomic native");auto atomic=f.push_atomic(line);
 for(unsigned n=0;n<10000 && !f.responses.count(atomic);++n)f.step();
 if(!f.responses.count(atomic)){f.cache()->tvd_print(stdout,0);f.cache()->display_state(stdout);printf("ATOMIC_HOLD|uid=%u|line=%llu|owners=%u\\n",atomic,line,owners(f,line));}
 assert(f.responses.count(atomic));
 assert(!x->live(x->find(line)) && owners(f,line)==1);
 puts("STEP postatomic write");auto w=f.push(line,true);f.await(w);u=f.push(line);f.await(u);
 assert(f.responses.at(u)==(unsigned long long)w+1 && owners(f,line)==1);
 f.drain();assert(store.ownership_consistent());
 puts("PASS optional_Ext_atomic_drop_then_Native_write_unique_new_value");
 const auto nonrr_write=x->at(3).line;
 auto nonrr_w=f.push(nonrr_write,true);f.await(nonrr_w);
 auto nonrr_r=f.push(nonrr_write);f.await(nonrr_r);
 assert(f.responses.at(nonrr_r)==(unsigned long long)nonrr_w+1 &&
        !x->live(x->find(nonrr_write)) && owners(f,nonrr_write)==1);
 puts("PASS optional_nonRR_Ext_fullwrite_drop_then_Native_progress");
 const auto nonrr_partial=x->at(4).line;
 nonrr_r=f.push(nonrr_partial+32);f.await(nonrr_r);
 assert(!x->live(x->find(nonrr_partial)) && owners(f,nonrr_partial)==1);
 puts("PASS optional_nonRR_Ext_missingsector_drop_then_Native_progress");

 const auto line5=x->at(5).line,line6=x->at(6).line;
 const auto before_responses=x->stats().read_responses;
 auto first=f.push(line5);
 for(unsigned n=0;n<1000 && !f.sp->top();++n)f.step(false);
 assert(f.sp->top() && f.sp->top()->get_request_uid()==first);
 auto second=f.push(line6);
 for(unsigned n=0;n<8;++n)f.step(false);
 assert(x->stats().read_responses==before_responses+1 && x->at(6).readers==0);
 f.collect();f.await(second);f.drain();
 assert(x->stats().read_responses==before_responses+2 && x->at(6).readers==0);
 puts("PASS optional_ICNT_full_no_early_reader_then_real_enqueue_exact_once");
 const auto line7=x->at(7).line;const auto h7=x->at(7).payload;
 const auto reader_responses=x->stats().read_responses;
 auto held=f.push(line7);bool blocked=false;
 const auto holder=f.cache()->ep_l2_tag_payload_handle_for_test(0);
 for(unsigned n=0;n<20 && !blocked;++n) {
   const auto grant=store.request(holder,false,f.gpu->gpu_sim_cycle,(unsigned long long)-1,
       ep_l2_payload_store::RESIDENT_HIT_READ,ep_l2_payload_store::COPY_READ,0xfffffffeu);
   assert(grant==ep_l2_payload_store::GRANTED);
   f.step(false);
   if(x->at(7).readers) {
     assert(x->at(7).readers==1 && store.inspect(h7).pins==1);
     assert(x->stats().read_responses==reader_responses);
     blocked=true;
   }
 }
 assert(blocked);f.await(held);f.drain();
 assert(x->at(7).readers==0 && store.inspect(h7).pins==0 &&
        x->stats().read_responses==reader_responses+1);
 puts("PASS optional_bank_denied_live_lease_then_reserved_retire_exact_once");
}
