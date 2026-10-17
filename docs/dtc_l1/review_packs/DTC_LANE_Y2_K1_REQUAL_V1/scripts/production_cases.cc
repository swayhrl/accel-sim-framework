#include "production_fixture.h"
#ifdef NDEBUG
#error Safety tests require assertions
#endif
using namespace y2;
using fields=std::map<std::string,uint64_t>;
static void check(bool b){if(!b)throw std::runtime_error("independent expectation failed");}
struct world {
  config_fixture cfg;y2::gpgpu_sim gpu;cache_config cache_cfg;
  y2::shader_core_ctx cores[4];y2::simt_core_cluster clusters[2];scoreboard_fixture scores[4];warp_fixture warps[4];wb_fixture wb[4];
  std::vector<std::unique_ptr<ordinary_cache>> caches;std::vector<std::unique_ptr<y2::ldst_unit>> units;
  std::unordered_map<unsigned,packet_fixture*> roots;
  explicit world(bool finite=true,unsigned physical=4,unsigned width=4) {
    cfg.dtc_l1_finite_service=finite;gpu.m_shader_config=&cfg;
    auto parser=option_parser_create();register_source_invalidation_option(parser,&cfg.dtc_l1_invalidate_on_source_event);
    const char*args[]={"Y2","-gpgpu_dtc_l1_invalidate_on_source_event","1"};option_parser_cmdline(parser,3,args);option_parser_destroy(parser);
    char geometry[]="N:8:128:1,L:T:m:L:L,A:4:4,4:0,32";cache_cfg.init(geometry,FuncCachePreferNone);
    for(unsigned i=0;i<4;++i){
      caches.emplace_back(new ordinary_cache(cache_cfg,i));
      units.emplace_back(new y2::ldst_unit());auto&u=*units.back();u.m_config=&cfg;u.m_core=&cores[i];u.m_L1D=caches.back().get();u.m_operand_collector=&wb[i];
      config c;c.selected_mode=mode::PAPER_OO;c.finite_service=finite;c.logical_sets=8;c.logical_ways=1;c.physical_lines=physical;c.allocation_width=width;c.oo_pib_entries=16;
      u.m_dtc_l1_oo_frontend.reset(new oo_frontend(c));u.m_dtc_l1_oo_frontend->advance_service(1);u.m_dtc_invalidation.configure(i,0);
      cores[i].m_gpu=&gpu;cores[i].m_ldst_unit=&u;cores[i].m_scoreboard=&scores[i];cores[i].m_warp={&warps[i]};
    }
    for(unsigned i=0;i<2;++i){clusters[i].m_config=&cfg;clusters[i].m_core={&cores[i*2],&cores[i*2+1]};gpu.m_cluster.push_back(&clusters[i]);}
  }
  y2::ldst_unit&u(unsigned sm=0){return *units[sm];}oo_frontend&f(unsigned sm=0){return *u(sm).m_dtc_l1_oo_frontend;}
  void tick(uint64_t t){gpu.gpu_sim_cycle=t;for(auto&p:units)p->m_dtc_l1_oo_frontend->advance_service(t);}
  physical_identity access(unsigned uid,uint64_t address=0,unsigned sm=0){auto&fe=f(sm);check(fe.admit(uid));return fe.access(gpu.global_cycle(),uid,address).physical;}
  void retained(unsigned sm){auto id=access(1,0,sm);f(sm).complete(id);tick(2);check(f(sm).retire_ready_uid(2,1));}
  void snapshot(const char*phase,unsigned sm=0,fields extra={}){
    auto&fe=f(sm);auto&ld=u(sm);auto&o=ld.m_dtc_invalidation;
    fields m={{"allocated",fe.allocated_lines()},{"refs",fe.active_refs()},{"pib",fe.occupancy()},{"ldst_pib",ld.m_dtc_l1_oo_pib.size()},{"events",o.requests},{"changed",o.changed},{"noops",o.no_op_requests},{"ordinary_commits",o.ordinary_commits},{"ordinary_pending",caches[sm]->invalidation_pending()},{"inflight",ld.m_dtc_l1_oo_inflight.size()},{"credits",gpu.m_dtc_l1_lower_outstanding},{"acquired",gpu.m_dtc_l1_lower_requests_acquired},{"released",gpu.m_dtc_l1_lower_requests_released},{"closed",ld.closed},{"wb_blocked",ld.m_dtc_l1_oo_ready_but_wb_blocked_cycles},{"map_loss_count",fe.map_loss_to_free_count()},{"map_loss_sum",fe.map_loss_to_free_sum()}};
    m.insert(extra.begin(),extra.end());std::cout<<"{\"phase\":\""<<phase<<"\",\"state\":{";bool first=true;for(auto&p:m){if(!first)std::cout<<",";first=false;std::cout<<"\""<<p.first<<"\":"<<p.second;}std::cout<<"}}\n";
    fe.assert_shadow_refs();check(gpu.m_dtc_l1_lower_requests_acquired-gpu.m_dtc_l1_lower_requests_released==gpu.m_dtc_l1_lower_outstanding);
  }
  physical_identity issue(unsigned uid,unsigned request,uint64_t address=0){
    auto id=access(uid,address);check(gpu.dtc_l1_try_acquire_lower_request());
    roots[request]=new packet_fixture{request,address};u().m_dtc_l1_oo_inflight.emplace(request,y2::ldst_unit::dtc_l1_oo_inflight{id,address,uid,15,0});
    u().m_dtc_l1_oo_pib.push_back({{uid,0},{{address,15}},1});u().ledger[uid].register_dependencies(1);u().ledger[uid].own_pib_dependencies(1);return id;
  }
  void join(unsigned uid){check(f().admit(uid));check(f().access(gpu.global_cycle(),uid,0).kind==io_access_kind::PENDING_HIT);u().m_dtc_l1_oo_pib.push_back({{uid,0},{{0,15}},1});u().ledger[uid].register_dependencies(1);u().ledger[uid].own_pib_dependencies(1);}
  void response(unsigned request,unsigned sector,bool write=false,uint64_t offset=0){
    auto*p=new packet_fixture{1000+sector,roots.at(request)->address+sector*32+offset,roots.at(request),write};
    check(u().dtc_l1_oo_consume_response(p));
  }
};
static void source_case(const std::string&name){
  world w;for(unsigned i=0;i<4;++i){auto id=w.access(1,0,i);w.f(i).complete(id);}w.tick(2);for(unsigned i=0;i<4;++i)check(w.f(i).retire_ready_uid(2,1));w.tick(3);
  if(name=="source_negative"||name=="k0_default"||name=="k0_explicit_off"||name=="k0_frozen"){
    if(name!="source_negative"){
      auto parser=option_parser_create();register_source_invalidation_option(parser,&w.cfg.dtc_l1_invalidate_on_source_event);
      if(name=="k0_explicit_off"){const char*args[]={"Y2","-gpgpu_dtc_l1_invalidate_on_source_event","0"};option_parser_cmdline(parser,3,args);}option_parser_destroy(parser);
    }
    w.gpu.m_config.gpgpu_flush_l1_cache=name!="source_negative";
    if(name=="k0_frozen")for(auto&u:w.units)u->frozen_invalidate();else w.gpu.source_idle();w.snapshot("after",0,{{"queryable",!w.f().will_new_miss(0)}});return;
  }
  if(name=="source_idle"){
    w.gpu.m_config.gpgpu_flush_l1_cache=true;w.cores[1].not_completed=1;w.gpu.source_idle();
    w.snapshot("blocked_cluster",0,{{"queryable",!w.f().will_new_miss(0)}});w.snapshot("selected_cluster",2,{{"queryable",!w.f(2).will_new_miss(0)}});
    w.tick(4);w.gpu.source_idle();w.snapshot("repeat",2);return;
  }
  if(name=="source_membar"){
    w.gpu.m_config.gpgpu_flush_l1_cache=true;w.warps[0].membar=true;w.scores[0].pending=true;
    check(w.cores[0].warp_waiting_at_mem_barrier(0));w.snapshot("scoreboard_block");
    w.scores[0].pending=false;check(!w.cores[0].warp_waiting_at_mem_barrier(0));w.snapshot("membar_selected");w.snapshot("other_sm",1);return;
  }
  if(name=="source_config"){
    w.gpu.source_config(FuncCachePreferNone);w.snapshot("same_config");w.gpu.source_config(FuncCachePreferL1);w.snapshot("changed_config");w.snapshot("other_cluster",2);return;
  }
  throw std::runtime_error("unknown source case");
}
int main(int argc,char**argv){try{
  if(argc!=2)return 64;std::string name=argv[1];
  if(name.rfind("source_",0)==0||name.rfind("k0_",0)==0){source_case(name);return 0;}
  if(name=="scope_io"||name=="scope_modern"){check_source_invalidation_mode(true,name=="scope_io"?2:4);return 1;}
  if(name.rfind("same_cycle_",0)==0){
    world w(false);auto id=w.issue(1,100);for(unsigned s:{0u,1u,2u})w.response(100,s);w.tick(2);w.wb[0].allow=true;
    if(name=="same_cycle_ERW")w.u().invalidate(invalidation_source::MEMBAR);
    w.response(100,3);
    if(name=="same_cycle_REW")w.u().invalidate(invalidation_source::MEMBAR);
    check(w.u().dtc_l1_oo_writeback_ready());
    if(name=="same_cycle_RWE")w.u().invalidate(invalidation_source::MEMBAR);
    w.snapshot("ordered",0,{{"old_allocated",w.f().is_allocated(id)},{"event_retained",w.u().m_dtc_invalidation.retained},{"event_reclaimed",w.u().m_dtc_invalidation.reclaimed}});return 0;
  }
  world w(true,name=="stale_generation"?2:4);auto&f=w.f();auto&ld=w.u();
  if(name=="ordinary_deferred"){
    auto id=w.access(1);w.caches[0]->hold();w.tick(3);ld.invalidate(invalidation_source::MEMBAR);w.snapshot("request",0,{{"old_allocated",f.is_allocated(id)},{"old_ref",f.ref_count(id)},{"queryable",!f.will_new_miss(0)}});
    w.tick(4);ld.invalidate(invalidation_source::IDLE_CLUSTER);ld.m_dtc_invalidation.cycle(4,*w.caches[0]);w.snapshot("repeat_pending");
    w.caches[0]->drain();w.tick(5);ld.m_dtc_invalidation.cycle(5,*w.caches[0]);w.snapshot("ordinary_commit",0,{{"request_cycle",ld.m_dtc_invalidation.first_request_cycle},{"commit_cycle",ld.m_dtc_invalidation.first_ordinary_commit_cycle},{"old_ref",f.ref_count(id)}});
  }else if(name=="wb_backpressure"){
    auto id=w.issue(1,100);for(unsigned s:{3u,1u,0u,2u})w.response(100,s);w.tick(2);check(!ld.dtc_l1_oo_writeback_ready());
    w.tick(3);check(!ld.dtc_l1_oo_writeback_ready());ld.invalidate(invalidation_source::MEMBAR);w.snapshot("collection_event",0,{{"ref",f.ref_count(id)}});
    w.tick(4);check(!ld.dtc_l1_oo_writeback_ready());w.tick(5);check(!ld.dtc_l1_oo_writeback_ready());w.snapshot("wb_denied",0,{{"ref",f.ref_count(id)}});
    w.tick(6);w.wb[0].allow=true;check(ld.dtc_l1_oo_writeback_ready());w.snapshot("wb_granted",0,{{"old_allocated",f.is_allocated(id)}});
  }else if(name=="old_new_returns"||name=="duplicate_sector"||name=="wrong_address"||name=="write_reply"||name=="stale_generation"){
    auto old=w.issue(1,100);ld.invalidate(invalidation_source::IDLE_CLUSTER);auto next=w.issue(2,200);
    check(old.id!=next.id);check(!w.gpu.dtc_l1_try_acquire_lower_request());
    w.response(100,3);
    if(name=="duplicate_sector"){w.response(100,3);return 1;}
    if(name=="wrong_address"){w.response(100,1,false,128);return 1;}
    if(name=="write_reply"){w.response(100,1,true);return 1;}
    for(unsigned s:{1u,0u,2u})w.response(200,s);w.response(200,3);w.snapshot("new_return_complete",0,{{"old_ready",f.entry_ready_for(1)},{"new_ready",f.entry_ready_for(2)}});
    for(unsigned s:{0u,2u,1u})w.response(100,s);w.snapshot("old_inflight_erased",0,{{"old_ready",f.entry_ready_for(1)}});
    w.tick(2);w.wb[0].allow=true;for(unsigned t=2;t<=8;++t){w.tick(t);ld.dtc_l1_oo_writeback_ready();}
    w.snapshot("drained",0,{{"old_allocated",f.is_allocated(old)},{"next_allocated",f.is_allocated(next)}});
    if(name=="stale_generation"){auto reused=w.access(3,128);check(reused.id==old.id&&reused.generation>old.generation);f.complete(old);return 1;}
  }else if(name=="late_waiter"){
    auto old=w.issue(1,100);for(unsigned uid=2;uid<=6;++uid)w.join(uid);
    for(unsigned s:{2u,0u,3u,1u})w.response(100,s);w.tick(2);check(f.wakeups()==4);w.join(7);
    ld.invalidate(invalidation_source::MEMBAR);f.advance_service(2);w.snapshot("partial_metadata",0,{{"wakeups",f.wakeups()},{"ref",f.ref_count(old)},{"ready1",f.entry_ready_for(1)}});
    w.tick(3);w.snapshot("metadata_done",0,{{"wakeups",f.wakeups()},{"ready7",f.entry_ready_for(7)}});
    w.wb[0].allow=true;for(unsigned t=4;t<=28;++t){w.tick(t);ld.dtc_l1_oo_writeback_ready();}w.snapshot("last_ref",0,{{"old_allocated",f.is_allocated(old)}});
  }else if(name=="partial_grant"){
    auto old=w.access(1);check(f.try_serve_tag(1,0));service_entry grant;grant.tag_grant_cycle=1;ld.invalidate(invalidation_source::IDLE_CLUSTER);
    check(!grant.tag_can_commit(1));w.tick(2);check(grant.tag_can_commit(2));auto next=w.access(2);check(next.id!=old.id);
    w.snapshot("grant_commit",0,{{"old_ref",f.ref_count(old)},{"new_ref",f.ref_count(next)},{"generation_preserved",f.fill_identity_matches(old)}});
    // A separate width-1 fixture proves accepted partial references survive E.
    world p(true,2,1);auto a=p.access(1);p.u().m_dtc_l1_oo_pib.push_back({{1,0},{{0,15},{128,15}},1});
    check(p.f().access(1,1,128).kind==io_access_kind::NO_FREE_LINE);p.u().invalidate(invalidation_source::MEMBAR);
    check(p.f().access(1,1,128).kind==io_access_kind::NO_FREE_LINE);p.f().complete(a);p.tick(2);uint64_t selected=0;check(p.f().entry_ready_for(1));check(!p.u().dtc_l1_oo_select_ready(&selected));p.snapshot("partial_admission_block",0,{{"ready_frontend",p.f().entry_ready_for(1)},{"selected",0}});
    auto b=p.f().access(2,1,128);check(b.kind==io_access_kind::NEW_MISS);p.snapshot("partial_kept",0,{{"old_ref",p.f().ref_count(a)}});
    p.u().m_dtc_l1_oo_pib.front().next_reference=2;p.u().ledger[1].register_dependencies(2);p.u().ledger[1].own_pib_dependencies(2);p.f().complete(b.physical);p.wb[0].allow=true;
    for(unsigned t=3;t<=7;++t){p.tick(t);p.u().dtc_l1_oo_writeback_ready();}p.snapshot("partial_final",0,{{"old_allocated",p.f().is_allocated(a)}});
  }else if(name=="proxy_same_warp"){
    y2::warp_inst_t proxy{20,0};check(ld.dtc_l1_m4_observe_admit(proxy,y2::ldst_unit::dtc_l1_m4_operation::PROXY_FENCE));auto old=w.issue(21,100);for(unsigned s:{0u,1u,2u,3u})w.response(100,s);w.tick(2);ld.invalidate(invalidation_source::MEMBAR);uint64_t selected=0;check(!ld.dtc_l1_oo_select_ready(&selected));w.snapshot("proxy_blocks",0,{{"old_ref",f.ref_count(old)},{"younger_ready",f.entry_ready_for(21)}});
    ld.dtc_l1_m4_observe_complete(proxy);check(ld.dtc_l1_oo_writeback_ready());w.snapshot("proxy_retired",0,{{"old_ref",f.ref_count(old)}});w.wb[0].allow=true;for(unsigned t=3;t<=6;++t){w.tick(t);ld.dtc_l1_oo_writeback_ready();}w.snapshot("younger_retired",0,{{"old_allocated",f.is_allocated(old)}});
  }else if(name=="slot_reuse"){
    auto old=w.access(1);unsigned slot=f.entry_slot(1);auto gen=f.entry_slot_generation(1);ld.invalidate(invalidation_source::MEMBAR);f.complete(old);w.tick(2);check(f.retire_ready_uid(2,1));
    auto next=w.access(2);check(f.entry_slot(2)==slot&&f.entry_slot_generation(2)>gen);w.snapshot("reused",0,{{"slot_advanced",1},{"new_ready",f.entry_ready_for(2)},{"new_ref",f.ref_count(next)}});
  }else if(name=="same_multi_bank"){
    for(unsigned uid=1;uid<=4;++uid){check(f.admit(uid));check(f.try_serve_tag(1,(uid-1)*128));f.access(1,uid,(uid-1)*128);}
    check(!f.try_serve_tag(1,8*128));ld.invalidate(invalidation_source::MEMBAR);check(!f.try_serve_tag(1,8*128));w.snapshot("banks_hidden",0,{{"tag_requests",f.tag_requests()},{"tag_conflicts",f.tag_conflicts()}});
  }else if(name=="sidecars"){
    auto old=w.access(1);f.complete(old);w.tick(2);check(f.retire_ready_uid(2,1));
    for(unsigned n=1;n<=4;++n){y2::warp_inst_t inst{10+n,n};check(ld.dtc_l1_m4_observe_admit(inst,static_cast<y2::ldst_unit::dtc_l1_m4_operation>(n)));}
    w.snapshot("sidecar_admitted",0,{{"queryable",!f.will_new_miss(0)}});ld.invalidate(invalidation_source::MEMBAR);w.snapshot("sidecar_event");
    for(unsigned n=1;n<=4;++n){y2::warp_inst_t inst{10+n,n};ld.dtc_l1_m4_observe_complete(inst);w.tick(2+n);check(ld.dtc_l1_oo_writeback_ready());}
    w.snapshot("sidecar_retired",0,{{"source_completed",ld.m_dtc_l1_m4_source_completions},{"sidecar_retires",ld.m_dtc_l1_m4_observation_retires}});
  }else if(name=="no_implicit_sidecar_event"){
    auto old=w.access(1);f.complete(old);w.tick(2);check(f.retire_ready_uid(2,1));
    for(unsigned n=1;n<=4;++n){y2::warp_inst_t inst{10+n,n};check(ld.dtc_l1_m4_observe_admit(inst,static_cast<y2::ldst_unit::dtc_l1_m4_operation>(n)));ld.dtc_l1_m4_observe_complete(inst);w.tick(2+n);check(ld.dtc_l1_oo_writeback_ready());}
    w.snapshot("no_implicit_event",0,{{"queryable",!f.will_new_miss(0)}});
  }else return 78;
  return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
