// Only environmental inputs are fixtures. Production method statements are
// extracted byte-for-byte into production_bodies.inc; no algorithm rewriting.
#include "gpu-cache.h"
#include "dtc-l1-invalidation.h"
#include <memory>
#include <unordered_map>
#include <list>
#include <iostream>
#include <string>
#include <stdexcept>
namespace y2 {
using namespace dtc_l1;
class ordinary_cache : public invalidation_observed_cache<::l1_cache> {
 public:
  // Production protected custom-Tag constructor avoids GPU perf-counter
  // registration; actual cache cycle/invalidate/drain methods are unchanged.
  ordinary_cache(cache_config&config,int sid)
    : invalidation_observed_cache<::l1_cache>("Y2_L1D",config,sid,0,nullptr,nullptr,
        IN_L1D_MISS_QUEUE,new tag_array(config,sid,0),nullptr) {}
  void hold() {m_extra_mf_fields.emplace(nullptr,extra_mf_fields());}
  void drain() {assert(m_extra_mf_fields.erase(nullptr)==1);}
};
struct config_fixture {
  bool dtc_l1_invalidate_on_source_event=true,dtc_l1_finite_service=true;
  unsigned dtc_l1_mode=3,dtc_l1_lower_outstanding_cap=2,n_simt_clusters=2,n_simt_cores_per_cluster=2;
  struct cache_status {FuncCache status=FuncCachePreferNone;FuncCache get_cache_status()const{return status;}} m_L1D_config;
};
struct source_config_fixture {bool gpgpu_flush_l1_cache=false;bool flush_l1()const{return gpgpu_flush_l1_cache;}};
class simt_core_cluster;
class gpgpu_sim {
 public:
  config_fixture *m_shader_config;
  source_config_fixture m_config;
  std::vector<simt_core_cluster*> m_cluster;
  unsigned long long gpu_sim_cycle=1,gpu_tot_sim_cycle=0;
  unsigned m_dtc_l1_lower_outstanding=0,m_dtc_l1_lower_peak=0;
  unsigned long long m_dtc_l1_lower_cap_full_events=0,m_dtc_l1_lower_requests_acquired=0,m_dtc_l1_lower_requests_released=0;
  uint64_t global_cycle()const{return gpu_sim_cycle+gpu_tot_sim_cycle;}
  source_config_fixture&get_config(){return m_config;}
  bool dtc_l1_try_acquire_lower_request();void dtc_l1_complete_lower_request();
  void source_idle();void source_config(FuncCache);
};
struct warp_fixture {bool membar=false;bool get_membar()const{return membar;}void clear_membar(){membar=false;}};
struct scoreboard_fixture {bool pending=false;bool pendingWrites(unsigned)const{return pending;}};
class ldst_unit;
class shader_core_ctx {
 public:
  gpgpu_sim*m_gpu;ldst_unit*m_ldst_unit;scoreboard_fixture*m_scoreboard;
  std::vector<warp_fixture*>m_warp;unsigned not_completed=0;
  gpgpu_sim*get_gpu(){return m_gpu;}
  unsigned get_not_completed()const{return not_completed;}
  void cache_invalidate(invalidation_source source=invalidation_source::UNSPECIFIED);
  bool warp_waiting_at_mem_barrier(unsigned);
};
class simt_core_cluster {
 public:
  config_fixture*m_config;std::vector<shader_core_ctx*>m_core;
  unsigned get_not_completed()const;
  void cache_invalidate(invalidation_source source=invalidation_source::UNSPECIFIED);
};
struct warp_inst_t {
  unsigned uid=0,warp=0;
  unsigned get_uid()const{return uid;}unsigned warp_id()const{return warp;}void clear(){uid=0;}
};
struct packet_fixture {
  unsigned uid;uint64_t address;packet_fixture*original=nullptr;bool write=false;
  static unsigned destructions;
  unsigned get_request_uid()const{return uid;}packet_fixture*get_original_mf()const{return original;}
  uint64_t get_addr()const{return address;}bool get_is_write()const{return write;}
  ~packet_fixture(){++destructions;}
};
using mem_fetch=packet_fixture;
struct wb_fixture {bool allow=false;unsigned calls=0;bool writeback(warp_inst_t&){++calls;return allow;}};
class ldst_unit {
 public:
  enum class dtc_l1_m4_operation:uint8_t{CACHEABLE_LOAD,STORE,ATOMIC,BYPASS_LOAD,PROXY_FENCE};
  struct dtc_l1_oo_pib_entry {warp_inst_t inst;std::vector<line_reference>references;size_t next_reference=0;dtc_l1_m4_operation operation=dtc_l1_m4_operation::CACHEABLE_LOAD;bool source_completed=false;service_entry service;};
  using dtc_l1_io_pib_entry=dtc_l1_oo_pib_entry;
  struct dtc_l1_oo_inflight {physical_identity physical;uint64_t line_address=0;unsigned inst_uid=0;uint8_t expected_sector_mask=15,response_sector_mask=0;};
  config_fixture*m_config;shader_core_ctx*m_core;::l1_cache*m_L1D;
  std::unique_ptr<oo_frontend>m_dtc_l1_oo_frontend;
  std::unique_ptr<io_frontend>m_dtc_l1_io_frontend;
  std::unique_ptr<sector_oo_frontend>m_dtc_l1_sector_frontend;
  source_invalidation_observer m_dtc_invalidation;
  std::list<dtc_l1_oo_pib_entry>m_dtc_l1_oo_pib,m_dtc_l1_io_pib;
  std::unordered_map<unsigned,dtc_l1_oo_inflight>m_dtc_l1_oo_inflight;
  uint64_t m_dtc_l1_oo_lower_responses=0,m_dtc_l1_io_pib_peak=0;
  uint64_t m_dtc_l1_m4_store_admits=0,m_dtc_l1_m4_atomic_admits=0,m_dtc_l1_m4_bypass_load_admits=0,m_dtc_l1_m4_proxy_fence_admits=0,m_dtc_l1_m4_source_completions=0,m_dtc_l1_m4_observation_retires=0;
  uint64_t m_dtc_l1_oo_ready_but_wb_blocked_cycles=0,m_dtc_l1_oo_out_of_order_retires=0;
  service_quota m_dtc_service_collect{4},m_dtc_service_retire{1};
  uint64_t m_dtc_service_collected_sectors=0,m_dtc_service_ready_to_complete_sum=0,m_dtc_service_ready_to_collect_sum=0,m_dtc_service_collection_cycles=0,m_dtc_service_wb_wait=0,m_dtc_service_retired=0;
  uint64_t m_dtc_service_occupancy_sample_cycle=UINT64_MAX,m_dtc_service_samples=0,m_dtc_service_pib_integral=0,m_dtc_service_physical_integral=0;
  warp_inst_t m_next_wb;wb_fixture*m_operand_collector;
  std::map<unsigned,completion_accounting>ledger;unsigned closed=0;
  // Completion register/scoreboard back-end is outside this CPU fixture.
  void dtc_l1_r4c1_record_ready(const warp_inst_t&i,unsigned admitted,unsigned registered,const char*){assert(admitted==registered);ledger.at(i.uid).mark_ready(registered);}
  unsigned dtc_l1_r4c3_registered_dependencies(const warp_inst_t&i){return dtc_l1_oo_find_entry(i.uid)->references.size();}
  void dtc_l1_oo_complete_instruction(const warp_inst_t&i,unsigned n){closed+=ledger.at(i.uid).close_once(n);}
  dtc_l1_oo_pib_entry*dtc_l1_oo_find_entry(unsigned uid){for(auto&e:m_dtc_l1_oo_pib)if(e.inst.uid==uid)return &e;return nullptr;}
  dtc_l1_io_pib_entry*dtc_l1_io_find_entry(unsigned uid){for(auto&e:m_dtc_l1_io_pib)if(e.inst.uid==uid)return &e;return nullptr;}
  bool dtc_l1_paper_io_active()const{return m_dtc_l1_io_frontend!=nullptr;}
  bool dtc_l1_paper_oo_active()const;bool dtc_l1_sector_oo_active()const;bool dtc_l1_finite_service_active()const;
  bool dtc_l1_m4_observe_admit(warp_inst_t&,dtc_l1_m4_operation);void dtc_l1_m4_observe_complete(const warp_inst_t&);
  bool dtc_l1_oo_select_ready(uint64_t*)const;
  bool dtc_l1_service_collect(service_entry&,const std::vector<line_reference>&);void dtc_l1_service_retired(const service_entry&);
  bool dtc_l1_oo_consume_response(mem_fetch*);bool dtc_l1_oo_writeback_ready();
  void dtc_l1_sample_service_occupancy(uint64_t);void invalidate(invalidation_source=invalidation_source::UNSPECIFIED);void frozen_invalidate();
};
unsigned packet_fixture::destructions=0;
#include "production_bodies.inc"
} // namespace y2
