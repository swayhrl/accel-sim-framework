#include "gpu-cache.h"
#include "dtc-l1-invalidation.h"
#include <iostream>
#ifdef NDEBUG
#error assertions required
#endif
class api_cache:public dtc_l1::invalidation_observed_cache<l1_cache>{
 public:
  explicit api_cache(cache_config&c):invalidation_observed_cache<l1_cache>("Y2_API",c,0,0,nullptr,nullptr,IN_L1D_MISS_QUEUE,new tag_array(c,0,0),nullptr){}
};
int main(int argc,char**argv){
 if(argc!=2)return 64;bool finite=std::string(argv[1])=="finite1";
 char geo[]="N:8:128:1,L:T:m:L:L,A:4:4,4:0,32";cache_config ordinary_cfg;ordinary_cfg.init(geo,FuncCachePreferNone);api_cache ordinary(ordinary_cfg);
 dtc_l1::config cfg;cfg.selected_mode=dtc_l1::mode::PAPER_OO;cfg.finite_service=finite;cfg.logical_sets=8;cfg.logical_ways=1;cfg.physical_lines=1;
 dtc_l1::oo_frontend f(cfg);dtc_l1::source_invalidation_observer observer;observer.configure(0,0);f.advance_service(1);
 assert(f.admit(1));auto first=f.access(1,1,0).physical;f.complete(first);f.advance_service(2);assert(f.retire_ready_uid(2,1));assert(!f.will_new_miss(0));
 auto a=observer.request(5,dtc_l1::invalidation_source::IDLE_CLUSTER,f,ordinary);assert(a.changed==1&&a.reclaimed==1&&!f.is_allocated(first));
 assert(observer.request(5,dtc_l1::invalidation_source::IDLE_CLUSTER,f,ordinary).changed==0);
 assert(f.admit(2));auto second=f.access(5,2,0).physical;assert(second.id==first.id&&second.generation==first.generation+1);
 assert(f.admit(3));assert(f.access(5,3,0).kind==dtc_l1::io_access_kind::PENDING_HIT);
 auto b=observer.request(5,dtc_l1::invalidation_source::MEMBAR,f,ordinary);assert(b.changed==1&&b.retained==1&&f.ref_count(second)==2);
 assert(f.admit(4));assert(f.access(5,4,0).kind==dtc_l1::io_access_kind::NO_FREE_LINE);
 f.complete(second);f.advance_service(6);assert(f.retire_ready_uid(6,2));assert(f.ref_count(second)==1&&f.is_allocated(second));
 f.advance_service(7);assert(f.retire_ready_uid(7,3)&&!f.is_allocated(second));
 f.advance_service(8);auto third=f.access(8,4,0).physical;assert(third.id==first.id&&third.generation==first.generation+2);
 f.complete(third);f.advance_service(9);assert(f.retire_ready_uid(9,4));auto c=observer.request(9,dtc_l1::invalidation_source::CACHE_CONFIG_CHANGE,f,ordinary);assert(c.reclaimed==1);
 f.assert_shadow_refs();
 std::cout<<"{\"allocated\":"<<f.allocated_lines()<<",\"refs\":"<<f.active_refs()<<",\"pib\":"<<f.occupancy()<<",\"requests\":"<<observer.requests<<",\"changed\":"<<observer.changed<<",\"noops\":"<<observer.no_op_requests<<",\"ordinary_commits\":"<<observer.ordinary_commits<<",\"generation_jump\":"<<third.generation-first.generation<<",\"map_loss_count\":"<<f.map_loss_to_free_count()<<",\"map_loss_sum\":"<<f.map_loss_to_free_sum()<<"}\n";
}
