// Mechanism-study B: port of historical TVD consumers; public hook patch is
// reviewed/applied by A. Compile/production qualification is separate.
unsigned long long l2_cache::m_gpu_cycle_for_tvd() const {
  return ft_physical_cycle();
}

bool l2_cache::tvd_install_victim(new_addr_type address, ep_l2::PayloadHandle h,
    unsigned valid, unsigned dirty, bool wb, unsigned long long now,
    tvd_directory::ticket *installed) {
  auto plan = m_tvd->preview_install(address, wb, true);
  if (plan.status != tvd_directory::OK) return false;
  tvd_directory::ticket ticket;
  if (m_tvd->commit_install(plan, address, h, valid, dirty, 0, wb, now, ticket) != tvd_directory::OK)
    return false;
  ++m_tvd_native_installs;
  if (installed) *installed = ticket;
  if (plan.displaced.valid()) {
    assert(m_ep_l2_payload.inspect(plan.displaced).pins == 0);
    m_ep_l2_payload.release(plan.displaced);
  }
  return true;
}

void l2_cache::tvd_selector_cancel(unsigned uid) {
  if(m_selector.active&&m_selector.uid==uid) {
    m_quota_row_port.cancel_owner(13,uid);m_selector=quota_selector();
  }
}

bool l2_cache::tvd_selector_step(unsigned uid,unsigned purpose,new_addr_type line,
    bool dirty,unsigned bank) {
  if(!m_selector.active) {
    m_selector=quota_selector();m_selector.active=true;m_selector.uid=uid;
    m_selector.purpose=purpose;m_selector.line=line;m_selector.dirty=dirty;
    m_selector.bank=bank;m_selector.clean_count=m_tvd->clean_occupancy();
  }
  auto&c=m_selector;
  if(c.uid!=uid||c.purpose!=purpose||c.line!=line||c.dirty!=dirty||c.bank!=bank)
    throw std::logic_error("overlapping serialized frontend selector");
  if(c.done)return true;
  if(c.clean_count!=m_tvd->clean_occupancy()) {
    tvd_selector_cancel(uid);return false;
  }
  const auto&e=m_tvd->at(c.cursor);
  const ep_l2_quota_row_port::key key(13,uid,c.cursor,e.incarnation,
      e.payload.payload_id,e.payload.generation,unsigned(e.status));
  if(!quota_ready(key))return false;
  const auto service=m_quota_row_port.token(key,m_quota_l2_tick);
  if(!service.valid)throw std::logic_error("selector without paid indexed READ");
  ++m_selector_probes;
  const bool limited=!dirty&&c.clean_count>=m_tvd->clean_limit();
  if(purpose==1&&e.status==tvd_directory::EMPTY&&(!limited||dirty)) {
    c.best=c.cursor;c.done=true;
  } else {
    bool candidate=e.reclaimable();
    if(purpose==1&&limited&&e.status!=tvd_directory::CLEAN)candidate=false;
    if(purpose==2&&(!e.payload.valid()||
        (bank!=~0u&&e.payload.payload_id%4!=bank)))candidate=false;
    if(candidate) {
      const bool prefer_clean=dirty||purpose==2;
      if(c.best==128||
         (prefer_clean&&e.status==tvd_directory::CLEAN&&c.best_state!=unsigned(tvd_directory::CLEAN))||
         ((!prefer_clean||unsigned(e.status)==c.best_state)&&e.age<c.best_age)) {
        c.best=c.cursor;c.best_age=e.age;c.best_state=unsigned(e.status);
      }
    }
  }
  m_quota_row_port.commit(key,m_quota_l2_tick);
  ++c.cursor;if(c.cursor==m_tvd->capacity())c.done=true;
  return c.done;
}

bool l2_cache::tvd_select_install(mem_fetch*mf,new_addr_type line,bool dirty,
    tvd_directory::install_plan&plan) {
  if(!quota_timed()){plan=m_tvd->preview_install(line,dirty,true);return true;}
  if(!dirty&&!m_tvd->clean_limit()){plan=tvd_directory::install_plan();plan.status=tvd_directory::DISABLED;return true;}
  if(!tvd_selector_step(mf->get_request_uid(),1,line,dirty,~0u))return false;
  if(m_selector.best>=m_tvd->capacity()) {
    tvd_selector_cancel(mf->get_request_uid());return false;
  }
  plan=m_tvd->selected_install(line,dirty,m_selector.best,true);
  if(plan.status!=tvd_directory::OK){tvd_selector_cancel(mf->get_request_uid());return false;}
  return true;
}

bool l2_cache::tvd_prepare_dirty_install(mem_fetch*mf) {
  auto&p=m_ft_pending;
  if(p.request!=mf||!p.dirty||p.wad||p.bound)
    throw std::logic_error("invalid deferred DIRTY install state");
  p.dirty_plan_ready=false;
  if(!m_ep_l2_payload.handle_live(p.victim)||
     !m_ep_l2_payload.handle_owner_matches(p.victim,p.saved.owner)||
     !m_ep_l2_payload.handle_owner_matches(p.landing,m_config.block_addr(mf->get_addr())))
    throw std::logic_error("DIRTY source/landing identity changed");
  const auto&source=m_ep_l2_payload.inspect(p.victim);
  if(source.pins||source.pending_sector_mask.any())return false;
  if(source.versions!=p.saved.versions||source.generation!=p.saved.generation)
    throw std::logic_error("DIRTY data identity changed before enqueue");
  if(!tvd_select_install(mf,p.victim_address,true,p.dirty_plan))return false;
  const auto&old=m_tvd->at(p.dirty_plan.index);
  if(p.dirty_plan.displaced.valid()) {
    if(!m_ep_l2_payload.handle_owner_matches(p.dirty_plan.displaced,old.line))
      throw std::logic_error("DIRTY displaced identity changed");
    const auto&slot=m_ep_l2_payload.inspect(p.dirty_plan.displaced);
    if(slot.pins||slot.pending_sector_mask.any())return false;
    if(slot.generation==std::numeric_limits<unsigned>::max())
      throw std::overflow_error("DIRTY displaced generation exhausted");
  }
  const unsigned ready=p.saved.ready_sector_mask.to_ulong();
  const bool retain=m_config.m_ep_l2_tvd_dirty&&(p.dirty_mask&~ready)==0;
  const auto valid=m_tvd->validate_install(p.dirty_plan,p.victim_address,
      retain?p.victim:ep_l2::PayloadHandle(),retain?ready:p.dirty_mask,p.dirty_mask,0,true);
  if(valid!=tvd_directory::OK)return false;
  p.dirty_key=ep_l2_quota_row_port::key(5,mf->get_request_uid(),p.dirty_plan.index,
      old.incarnation,old.payload.payload_id,old.payload.generation,unsigned(old.status));
  if(!quota_ready(p.dirty_key))return false;
  p.dirty_plan_ready=true;return true;
}

bool l2_cache::tvd_prepare_clean_install(mem_fetch *mf,tvd_directory::install_plan&plan,
    ep_l2_quota_row_port::key&key,bool&can_install) {
  auto&p=m_ft_pending;const unsigned uid=mf->get_request_uid();
  can_install=false;
  if(!p.request||p.request!=mf||p.dirty||!p.retain_clean||!p.landing_reserved)
    throw std::logic_error("clean install not fully reserved before metadata READ");
  auto refuse=[&](){m_quota_row_port.cancel_owner(4,uid);return false;};
  if(!m_ep_l2_payload.handle_live(p.victim)||
     !m_ep_l2_payload.handle_owner_matches(p.victim,p.saved.owner)||
     !m_ep_l2_payload.handle_owner_matches(p.landing,m_config.block_addr(mf->get_addr())))
    throw std::logic_error("clean source/landing identity changed before Native commit");
  const auto&land=m_ep_l2_payload.inspect(p.landing);
  if(land.allocation_role!=ep_l2_payload_store::RESIDENT || land.pins || land.pending_sector_mask.any())
    throw std::logic_error("clean landing reservation changed before Native commit");
  const auto&src=m_ep_l2_payload.inspect(p.victim);
  if(src.generation==std::numeric_limits<unsigned>::max())
    throw std::overflow_error("clean victim generation exhausted before Native commit");
  if(src.pins||src.pending_sector_mask.any())return refuse();
  if(src.generation!=p.saved.generation||src.versions!=p.saved.versions||
     src.ready_sector_mask!=p.saved.ready_sector_mask)
    throw std::logic_error("clean victim data identity changed before Native commit");
  if(tag_payload_handle(p.tag_index)!=p.victim||
     m_tag_array->get_block(p.tag_index)->m_block_addr!=p.saved.owner ||
     m_tag_array->get_block(p.tag_index)->is_modified_line() ||
     m_tag_array->get_block(p.tag_index)->is_reserved_line())
    throw std::logic_error("clean native tag identity changed before metadata commit");
  // Serialized frontend already holds landing/control and its issue capacity.
  // Recheck dynamic lower/MSHR availability before any old row/tag mutation.
  unsigned lower_slots=0;
  const auto line=m_config.mshr_addr(mf->get_addr());
  if(!mf->get_is_write()) {
    if(m_mshrs.full(line))return refuse();
    if(m_mshrs.needs_lower_read(line,mf->get_access_sector_mask()))++lower_slots;
  }
  if(!miss_queue_has_slots(lower_slots))return refuse();
  if(!tvd_select_install(mf,p.saved.owner,false,plan))return false;
  if(plan.status!=tvd_directory::OK)return refuse();
  const auto&row=m_tvd->at(plan.index);
  if(plan.displaced.valid()) {
    if(!m_ep_l2_payload.handle_owner_matches(plan.displaced,row.line))
      throw std::logic_error("displaced CLEAN/WB_COMPLETE identity changed");
    const auto&old=m_ep_l2_payload.inspect(plan.displaced);
    if(old.allocation_role!=ep_l2_payload_store::TVD)
      throw std::logic_error("displaced directory payload role changed");
    if(old.pins||old.pending_sector_mask.any())return refuse();
    if(old.generation==std::numeric_limits<unsigned>::max())
      throw std::overflow_error("displaced generation exhausted before Native commit");
  }
  const auto valid=m_tvd->validate_install(plan,p.saved.owner,p.victim,
      p.saved.ready_sector_mask.to_ulong(),0,0,false);
  if(valid!=tvd_directory::OK)return refuse();
  key=ep_l2_quota_row_port::key(4,uid,plan.index,row.incarnation,
      row.payload.payload_id,row.payload.generation,unsigned(row.status));
  if(!m_quota_row_port.owns(key))m_quota_row_port.cancel_owner(4,uid);
  if(m_quota_row_port.lanes()!=m_config.m_ep_l2_quota_row_lanes)
    m_quota_row_port.configure(m_config.m_ep_l2_quota_row_lanes);
  if(!m_quota_row_port.ready(key,m_quota_l2_tick))return false;
  can_install=true;return true;
}

void l2_cache::tvd_commit_clean_install(const tvd_directory::install_plan&plan,
    ep_l2::PayloadHandle incoming,unsigned valid,unsigned long long now,
    const ep_l2_quota_row_port::key&key) {
  // Only the just-qualified clean Native path reaches this. No directory
  // producer callback occurs inside that path between preflight and here.
  tvd_directory::ticket installed;
  const auto service=m_quota_row_port.token(key,m_quota_l2_tick);
  const auto r=m_tvd->commit_install(plan,plan.line,incoming,valid,0,0,false,now,installed,&service);
  if(r!=tvd_directory::OK)
    throw std::logic_error("prepared CLEAN install invalidated after Native commit");
  m_quota_row_port.commit(key,m_quota_l2_tick);
  ++m_tvd_native_installs;
  if(plan.displaced.valid())m_ep_l2_payload.release(plan.displaced);
  m_ep_l2_payload.transfer(incoming,ep_l2_payload_store::TVD,ep_l2_payload_store::TVD_VALID);
  tvd_selector_cancel(key.uid);
}

bool l2_cache::tvd_cached_wad_contains(mem_fetch *mf, new_addr_type address) const {
  assert(m_tvd);
  if (m_tvd_lookup == mf && m_tvd_lookup_done) {
    const auto t = m_tvd_lookup_ticket;
    return m_tvd->live(t) && m_tvd->at(t.index).line == address &&
        m_tvd->at(t.index).mandatory();
  }
  // A normal resident hit/sector miss cannot alias a mandatory WB owner:
  // miss lookup blocks on WAD; promotion waits for completion; host prefill
  // requires quiescence. No new functional address lookup is issued here.
  // Before the query pipeline this is UNKNOWN to an observational preview;
  // it is not an admission proof. ft_access below refuses an unqueried MISS.
  return false;
}

bool l2_cache::tvd_reclaim_one(unsigned bank,unsigned long long now) {
  if(quota_timed()) {
    if(!m_tvd_lookup)throw std::logic_error("general reclaim without serialized frontend owner");
    const unsigned uid=m_tvd_lookup->get_request_uid();
    if(!tvd_selector_step(uid,2,0,false,bank))return false;
    if(m_selector.best>=m_tvd->capacity()){tvd_selector_cancel(uid);return false;}
    const auto index=m_selector.best;const auto&e=m_tvd->at(index);
    const tvd_directory::ticket ticket(index,e.incarnation);
    const auto plan=m_tvd->preview_reserved_reclaim(ticket);
    if(plan.status!=tvd_directory::OK){tvd_selector_cancel(uid);return false;}
    if(!plan.payload.valid()||!m_ep_l2_payload.handle_owner_matches(plan.payload,e.line))
      throw std::logic_error("general reclaim payload identity");
    const auto&slot=m_ep_l2_payload.inspect(plan.payload);
    if(slot.pins||slot.pending_sector_mask.any())return false;
    if(slot.generation==std::numeric_limits<unsigned>::max())
      throw std::overflow_error("general reclaim generation exhausted");
    const auto key=quota_key(12,uid,ticket);
    if(!quota_ready(key))return false;
    const auto service=m_quota_row_port.token(key,m_quota_l2_tick);
    ep_l2::PayloadHandle released;
    const auto r=m_tvd->commit_reserved_reclaim(plan,released,now,&service);
    if(r==tvd_directory::COUNTER_BUSY)return false;
    if(r!=tvd_directory::OK){m_quota_row_port.cancel_owner(12,uid);tvd_selector_cancel(uid);return false;}
    m_quota_row_port.commit(key,m_quota_l2_tick);m_ep_l2_payload.release(released);
    tvd_selector_cancel(uid);return true;
  }
  // Mandatory space first reclaims optional clean, then completed WB data.
  // Pinned reads and pending/inflight WB are never eligible victims.
  for (auto state : {tvd_directory::CLEAN, tvd_directory::WB_COMPLETE}) {
    unsigned best=m_tvd->capacity();
    for (unsigned i=0;i<m_tvd->capacity();++i) {
      const auto &e=m_tvd->at(i);
      if (e.status!=state || !e.reclaimable() || !e.payload.valid() ||
          (bank!=(unsigned)-1 && e.payload.payload_id%4!=bank)) continue;
      if (best==m_tvd->capacity() || e.age<m_tvd->at(best).age) best=i;
    }
    if (best==m_tvd->capacity()) continue;
    const auto token=tvd_directory::ticket(best,m_tvd->at(best).incarnation);
    ep_l2::PayloadHandle h;
    assert(m_tvd->reclaim(token,h,now)==tvd_directory::OK);
    assert(m_ep_l2_payload.inspect(h).pins==0);
    m_ep_l2_payload.release(h);return true;
  }
  return false;
}

bool l2_cache::tvd_frontend_reclaim(mem_fetch *mf,tvd_directory::ticket t,
    unsigned long long now) {
  const unsigned producer=3,uid=mf->get_request_uid();
  auto cancel=[&](){m_quota_row_port.cancel_owner(producer,uid);};
  if(!m_tvd->live(t)){cancel();return false;}
  const auto plan=m_tvd->preview_reserved_reclaim(t);
  if(plan.status==tvd_directory::PINNED){cancel();return false;}
  if(plan.status!=tvd_directory::OK){cancel();return false;}
  const auto h=plan.payload;
  // All allocator release refusals precede directory/count mutation.
  if(!h.valid()||!m_ep_l2_payload.handle_live(h)||
     !m_ep_l2_payload.handle_owner_matches(h,m_config.block_addr(mf->get_addr()))) {
    cancel();throw std::logic_error("frontend reclaim payload identity changed before COMMIT");
  }
  const auto&slot=m_ep_l2_payload.inspect(h);
  if(slot.pins||slot.pending_sector_mask.any()){cancel();return false;}
  if(slot.generation==std::numeric_limits<unsigned>::max()) {
    cancel();throw std::overflow_error("frontend reclaim payload generation exhausted before COMMIT");
  }
  const bool timed=m_config.m_ep_l2_quota_row_lanes!=0;
  const auto key=quota_key(producer,uid,t);
  if(timed) {
    if(m_quota_row_port.lanes()!=m_config.m_ep_l2_quota_row_lanes)
      m_quota_row_port.configure(m_config.m_ep_l2_quota_row_lanes);
    if(!m_quota_row_port.ready(key,m_quota_l2_tick))return false;
  }
  ep_l2::PayloadHandle released;
  const auto service=m_quota_row_port.token(key,m_quota_l2_tick);
  const auto result=m_tvd->commit_reserved_reclaim(plan,released,now,timed?&service:NULL);
  if(result==tvd_directory::COUNTER_BUSY)return false;
  if(result!=tvd_directory::OK) {cancel();return false;}
  if(timed)m_quota_row_port.commit(key,m_quota_l2_tick);
  if(released!=h)throw std::logic_error("frontend reclaim release identity mismatch");
  m_ep_l2_payload.release(released);
  return true;
}

l2_cache::tvd_frontend_result l2_cache::tvd_frontend(mem_fetch *mf,
    unsigned long long now, bool response_space) {
  if (!m_tvd) return TVD_NORMAL;
  // Guard the path that can complete before l2_cache::access. A certificate
  // contradiction must fail before lookup, promotion, pin or enqueue mutation.
  if(m_ro) {
    m_ro->check_access(mf);
  }
  unsigned index = (unsigned)-1;
  const auto address = m_config.block_addr(mf->get_addr());
  const auto tag = m_tag_array->probe(address, index, mf, mf->is_write(), true);
  if (tag == HIT || tag == SECTOR_MISS || tag == HIT_RESERVED) return TVD_NORMAL;
  namespace M = ep_l2::mechanism_v1;
  unsigned long long known = 1ULL << M::VICTIM_LOOKUP;
  // Observation only: preserve all controller predicates, paid lookup cycles,
  // response/lower backpressure and bank arbitration below. Unknown native
  // resources are not reported as free while this shortcut owns the head.
  auto wait = [&](M::WaitReason reason) {
    ms_observe_frontend(mf, now, 1ULL << reason, false, known | (1ULL << reason));
    return TVD_WAIT;
  };
  if (m_tvd_lookup != mf) {
    assert(!m_tvd_read);
    m_tvd_lookup = mf; m_tvd_lookup_cycle = now;
    m_tvd_lookup_done = false;
    ++m_tvd_lookup_wait; return wait(M::VICTIM_LOOKUP);
  }
  if (now <= m_tvd_lookup_cycle) return wait(M::VICTIM_LOOKUP);
  if (!m_tvd_lookup_done) {
    if (m_tvd_query_cycle == now) return wait(M::VICTIM_LOOKUP);
    m_tvd_query_cycle = now; ++m_tvd_lookup_queries;
    m_tvd_lookup_ticket = m_tvd->find(address);
    m_tvd_lookup_done = true;
  }
  const auto ticket = m_tvd_lookup_ticket;
  if (!m_tvd->live(ticket)) {
    m_quota_row_port.cancel_owner(3,mf->get_request_uid());
    return TVD_NORMAL;
  }
  // Dirty pending/inflight reads use a distinct client+UID+generation key
  // in the existing bank scoreboard. The public r2 adapter delays WB->TVD
  // role transitions while the reader is pinned. CLEAN_ONLY WAD records have
  // no retained handle and still return WAIT_WRITEBACK below.
  auto op = mf->isatomic() ? tvd_directory::ATOMIC_OP :
            mf->get_is_write() ? tvd_directory::WRITE_OP : tvd_directory::READ_OP;
  auto observation = m_tvd->preview_ticket(ticket, mf->get_access_sector_mask().to_ulong(), op);
  known |= 1ULL << M::SAME_ADDRESS_WB;
  if (observation.status == tvd_directory::WAIT_WRITEBACK) {
    ++m_tvd_wb_wait; return wait(M::SAME_ADDRESS_WB);
  }
  // A mandatory-WB refusal above can mask the later reader/pin predicate.
  known |= 1ULL << M::PINNED_PAYLOAD;
  if (observation.status == tvd_directory::PINNED) {
    ++m_tvd_wb_wait; return wait(M::PINNED_PAYLOAD);
  }
  if (op != tvd_directory::READ_OP) return TVD_NORMAL; // ft_access commits promotion
  if (observation.status == tvd_directory::MISSING_SECTOR) {
    if(!tvd_frontend_reclaim(mf,ticket,now))return wait(M::VICTIM_LOOKUP);
    return TVD_NORMAL;
  }
  // If a previously prepared reclaim is no longer selected, cancel only this
  // frontend owner's reservation. No beat refund or stale-handle release.
  m_quota_row_port.cancel_owner(3,mf->get_request_uid());
  if (observation.status != tvd_directory::READ_READY) return TVD_NORMAL;
  known |= 1ULL << M::RESPONSE_QUEUE_FULL;
  if (!response_space) {
    if(quota_timed()) {
      m_quota_row_port.cancel_owner(8,mf->get_request_uid());
      m_quota_row_port.cancel_owner(9,mf->get_request_uid());
    }
    ++m_tvd_resp_wait;return wait(M::RESPONSE_QUEUE_FULL);
  }
  if (!m_tvd_read) {
    if(!m_ep_l2_payload.handle_owner_matches(observation.payload,address))
      throw std::logic_error("reader payload identity before begin");
    if(m_ep_l2_payload.inspect(observation.payload).pins==std::numeric_limits<unsigned>::max())
      throw std::overflow_error("reader pin exhausted before lifetime begin");
    const auto key=quota_key(8,mf->get_request_uid(),ticket);
    if(quota_timed()&&!quota_ready(key))return wait(M::VICTIM_LOOKUP);
    const auto service=m_quota_row_port.token(key,m_quota_l2_tick);
    std::unique_ptr<tvd_directory::read_lease> lease(new tvd_directory::read_lease());
    const auto begin=m_tvd->begin_read(observation,mf->get_access_sector_mask().to_ulong(),
        *lease,quota_timed()?&service:NULL);
    if(begin!=tvd_directory::OK) {
      if(quota_timed())m_quota_row_port.cancel_owner(8,mf->get_request_uid());
      return wait(M::VICTIM_LOOKUP);
    }
    if(quota_timed())m_quota_row_port.commit(key,m_quota_l2_tick);
    m_ep_l2_payload.pin(observation.payload);m_tvd_read=std::move(lease);
  }
  const auto h = m_tvd_read->handle();
  if (m_ep_l2_payload.request(h, false, now, (unsigned long long)-1,
      ep_l2_payload_store::TVD_READ, ep_l2_payload_store::FRONTEND, mf->get_request_uid()) != ep_l2_payload_store::GRANTED) {
    ++m_tvd_bank_wait; return wait(M::DATA_SERVICE);
  }
  mf->set_ep_l2_payload_identity(h.payload_id, h.generation);
  mf->set_ft_wb_data(m_ep_l2_payload.inspect(h).versions);
  // The response/cancel head is prepaid BEFORE ICNT enqueue. Payload and
  // reader lifetime remain pinned until the successful enqueue callback.
  if(quota_timed()) {
    const auto key=quota_key(9,mf->get_request_uid(),ticket);
    if(!quota_ready(key))return wait(M::VICTIM_LOOKUP);
  }
  return TVD_RESPONSE;
}

void l2_cache::tvd_response_commit(mem_fetch *mf, unsigned long long now) {
  assert(m_tvd_read && mf == m_tvd_lookup);
  const auto h = m_tvd_read->handle();
  const auto ticket=m_tvd_lookup_ticket;
  const auto key=quota_key(9,mf->get_request_uid(),ticket);
  const auto service=m_quota_row_port.token(key,m_quota_l2_tick);
  const auto retired=m_tvd->response_commit(*m_tvd_read,now,quota_timed()?&service:NULL);
  if(retired!=tvd_directory::OK)throw std::logic_error("response enqueue without paid retirement");
  if(quota_timed())m_quota_row_port.commit(key,m_quota_l2_tick);
  m_ep_l2_payload.unpin(h);
  assert(m_tvd->live(ticket) && m_tvd->at(ticket.index).payload==h);
  const auto &e=m_tvd->at(ticket.index);
  const auto &slot=m_ep_l2_payload.inspect(h);
  // A reader may pin either a WB-role pending victim OR a TVD-role already
  // accepted victim. Completion while either is pinned must eventually
  // publish TVD_VALID; restricting this to roleWB strands TVD_INFLIGHT state.
  if (!slot.pins &&
      (e.status==tvd_directory::WB_INFLIGHT || e.status==tvd_directory::WB_COMPLETE)) {
    assert(slot.allocation_role==ep_l2_payload_store::WB ||
           slot.allocation_role==ep_l2_payload_store::TVD);
    m_ep_l2_payload.transfer(h,ep_l2_payload_store::TVD,
        e.status==tvd_directory::WB_COMPLETE?ep_l2_payload_store::TVD_VALID:ep_l2_payload_store::TVD_INFLIGHT);
  }
  m_tvd_read.reset(); m_tvd_lookup = NULL;
  if(m_ro)m_ro->record_accepted(mf);
  ++m_ft_stats.accepted;
  ms_observe_frontend(mf, now, 0, true, 0); // Actual response enqueue, exactly once.
}

bool l2_cache::tvd_cancel_frontend_read(mem_fetch*mf,unsigned long long now) {
  if(!m_tvd_read||m_tvd_lookup!=mf)return false;
  const auto ticket=m_tvd_lookup_ticket;const auto h=m_tvd_read->handle();
  if(!m_tvd->live(ticket)||!m_ep_l2_payload.handle_live(h)||
      m_tvd->at(ticket.index).payload!=h)
    throw std::logic_error("cancel reader identity");
  const auto key=quota_key(14,mf->get_request_uid(),ticket);
  if(quota_timed()) {
    m_quota_row_port.cancel_owner(9,mf->get_request_uid());
    if(!quota_ready(key))return false;
  }
  const auto service=m_quota_row_port.token(key,m_quota_l2_tick);
  const auto result=m_tvd->cancel_read(*m_tvd_read,quota_timed()?&service:NULL);
  if(result!=tvd_directory::OK)return false;
  if(quota_timed())m_quota_row_port.commit(key,m_quota_l2_tick);
  m_ep_l2_payload.unpin(h);
  const auto&e=m_tvd->at(ticket.index);const auto&slot=m_ep_l2_payload.inspect(h);
  if(!slot.pins&&(e.status==tvd_directory::WB_INFLIGHT||e.status==tvd_directory::WB_COMPLETE))
    m_ep_l2_payload.transfer(h,ep_l2_payload_store::TVD,
      e.status==tvd_directory::WB_COMPLETE?ep_l2_payload_store::TVD_VALID:ep_l2_payload_store::TVD_INFLIGHT);
  m_tvd_read.reset();m_tvd_lookup=NULL;return true;
}

bool l2_cache::tvd_promote(mem_fetch *mf, unsigned time, std::list<cache_event> &events) {
  const auto physical_cycle = m_gpu_cycle_for_tvd();
  const auto address = m_config.block_addr(mf->get_addr());
  assert(m_tvd_lookup == mf && m_tvd_lookup_done);
  auto t = m_tvd_lookup_ticket;
  if (!m_tvd->live(t)) return true;
  const auto old = m_tvd->at(t.index);
  if (old.mandatory() || old.readers) return false;
  // Preserve payload bank class. Select the oldest eligible resident way of
  // that class in the address's set; invalid ways take priority.
  unsigned index = (unsigned)-1;
  const unsigned first = m_config.set_index(address) * m_config.get_assoc();
  for (unsigned i = first; i < first + m_config.get_assoc(); ++i) {
    if (i % 4 != old.payload.payload_id % 4) continue;
    auto b = m_tag_array->get_block(i); auto h = tag_payload_handle(i);
    if (b->is_reserved_line()) continue;
    if (m_ep_l2_payload.handle_live(h) && (m_ep_l2_payload.inspect(h).pins ||
        m_ep_l2_payload.inspect(h).pending_sector_mask.any())) continue;
    if (index == (unsigned)-1 || b->is_invalid_line() ||
        b->get_last_access_time() < m_tag_array->get_block(index)->get_last_access_time()) index = i;
    if (b->is_invalid_line()) break;
  }
  if (index == (unsigned)-1 || m_ft_pending.request) return false;
  auto block = m_tag_array->get_block(index);
  const auto victim = tag_payload_handle(index);
  const bool live = m_ep_l2_payload.handle_live(victim);
  const bool dirty = block->is_modified_line();
  // Fixed control withholds64 slots even when empty. A clean replaced
  // resident gives back one same-bank non-victim credit; a dirty WB does not.
  if(!m_ep_l2_payload.fixed_promotion_room(old.payload,
      live&&!dirty?victim:ep_l2::PayloadHandle()))return false;
  ep_l2::PayloadHandle promoted; tvd_directory::ticket wb_ticket;
  if (dirty) {
    if (!miss_queue_has_slots(1)) return false;
    // This first adapter rejects local-WB-cap combinations at construction;
    // do not bypass the parent quota for an unqualified combined mode.
    assert(!m_config.m_ep_l2_wb_local_cap);
    assert(live);
    const auto saved = m_ep_l2_payload.inspect(victim);
    const unsigned dirty_mask = block->get_dirty_sector_mask().to_ulong();
    const unsigned ready_mask = saved.ready_sector_mask.to_ulong();
    const bool retain = m_config.m_ep_l2_tvd_dirty && (dirty_mask & ~ready_mask) == 0;
    auto plan = m_tvd->preview_dirty_promotion(t, block->m_block_addr, victim,
        retain ? ready_mask : dirty_mask, dirty_mask,
        saved.pending_sector_mask.to_ulong(), retain, true);
    if (plan.status != tvd_directory::OK) return false;
    evicted_block_info evicted;
    evicted.set_info(block->m_block_addr, block->get_modified_size(),
        block->get_dirty_byte_mask(), block->get_dirty_sector_mask());
    const auto key=quota_key(7,mf->get_request_uid(),t);
    if(quota_timed()&&!quota_ready(key))return false;
    mem_fetch *packet=m_memfetch_creator->alloc(evicted.m_block_addr,L2_WRBK_ACC,
        mf->get_access_warp_mask(),evicted.m_byte_mask,evicted.m_sector_mask,
        evicted.m_modified_size,true,time,-1,-1,-1,NULL,mf->get_streamID());
    const auto service=m_quota_row_port.token(key,m_quota_l2_tick);
    const auto result=m_tvd->commit_dirty_promotion(plan,physical_cycle,promoted,wb_ticket,
        quota_timed()?&service:NULL,packet->get_request_uid(),quota_timed());
    if(result!=tvd_directory::OK) {
      delete packet;
      if(quota_timed())m_quota_row_port.cancel_owner(7,mf->get_request_uid());
      return false;
    }
    if(quota_timed())m_quota_row_port.commit(key,m_quota_l2_tick);
    ++m_tvd_native_promotions;
    if(!m_ep_l2_wad_birth_cycle.insert(std::make_pair(evicted.m_block_addr,physical_cycle)).second)
      throw std::logic_error("promotion WAD birth duplicate");
    m_ep_l2_payload.transfer(victim,ep_l2_payload_store::WB,ep_l2_payload_store::WB_STAGED);
    auto&p=m_ft_pending;p.request=mf;p.dirty=p.wad=true;
    p.tag_index=index;p.victim=p.staging=victim;p.victim_address=evicted.m_block_addr;
    p.born=physical_cycle;p.wad_ticket=wb_ticket;
    packet->set_chip(mf->get_tlx_addr().chip);packet->set_partition(mf->get_tlx_addr().sub_partition);
    send_write_request(packet,cache_event(WRITE_BACK_REQUEST_SENT,evicted),time,events);
    if(!p.bound)throw std::logic_error("promotion packet not bound");
    p=ft_replacement();
  } else {
    if(live&&m_ep_l2_payload.inspect(victim).generation==std::numeric_limits<unsigned>::max())
      throw std::overflow_error("promotion native victim generation exhausted");
    const auto key=quota_key(6,mf->get_request_uid(),t);
    if(quota_timed()&&!quota_ready(key))return false;
    const auto service=m_quota_row_port.token(key,m_quota_l2_tick);
    const auto result=m_tvd->promote(t,promoted,physical_cycle,quota_timed()?&service:NULL);
    if(result!=tvd_directory::OK)return false;
    if(quota_timed())m_quota_row_port.commit(key,m_quota_l2_tick);
    ++m_tvd_native_promotions;
    if(live)m_ep_l2_payload.release(victim);
  }
  m_ep_l2_payload.transfer(promoted, ep_l2_payload_store::RESIDENT, ep_l2_payload_store::RESIDENT_VALID);
  m_tag_array->tvd_bind(index, address, time, old.valid_sectors);
  set_tag_payload_handle(index, promoted);
  assert(m_ep_l2_payload.ownership_consistent());
  return true;
}

void l2_cache::quota_request_epoch_cleanup() {
  if(!quota_timed()||!m_tvd||m_cleanup_requested)return;
  if(m_cleanup_epoch==std::numeric_limits<unsigned long long>::max())
    throw std::overflow_error("cleanup epoch exhausted");
  ++m_cleanup_epoch;m_cleanup_requested=true;m_cleanup_done=false;
  m_cleanup_cursor=0;m_cleanup_requested_at=ft_physical_cycle();
}

void l2_cache::quota_cleanup_tick(bool origins_empty) {
  if(!quota_timed()||!m_tvd||!m_cleanup_requested||m_cleanup_done||!origins_empty)return;
  if(m_ft_pending.request||!m_ft_wb.empty()||!m_ft_read_refs.empty()||m_tvd_read||
     !m_ep_l2_wad_birth_cycle.empty())return;
  if(m_selector.active)throw std::logic_error("stale frontend selector at terminal cleanup");
  if(m_cleanup_cursor>=m_tvd->capacity())throw std::logic_error("cleanup cursor");
  const auto&e=m_tvd->at(m_cleanup_cursor);
  const ep_l2_quota_row_port::key key(11,unsigned(m_cleanup_epoch),m_cleanup_cursor,
      e.incarnation,e.payload.payload_id,e.payload.generation,unsigned(e.status));
  if(!quota_ready(key))return;
  const auto service=m_quota_row_port.token(key,m_quota_l2_tick);
  if(e.status!=tvd_directory::EMPTY) {
    const tvd_directory::ticket ticket(m_cleanup_cursor,e.incarnation);
    const auto plan=m_tvd->preview_reserved_reclaim(ticket);
    if(plan.status!=tvd_directory::OK)throw std::logic_error("terminal mandatory/reader ownership not drained");
    if(!plan.payload.valid()||!m_ep_l2_payload.handle_owner_matches(plan.payload,e.line))
      throw std::logic_error("cleanup payload identity");
    const auto&slot=m_ep_l2_payload.inspect(plan.payload);
    if(slot.pins||slot.pending_sector_mask.any())throw std::logic_error("cleanup pin/pending ownership");
    if(slot.generation==std::numeric_limits<unsigned>::max())
      throw std::overflow_error("cleanup payload generation exhausted");
    ep_l2::PayloadHandle released;
    const auto r=m_tvd->commit_reserved_reclaim(plan,released,ft_physical_cycle(),&service);
    if(r==tvd_directory::COUNTER_BUSY)return;
    if(r!=tvd_directory::OK)throw std::logic_error("cleanup row grant invalid");
    m_ep_l2_payload.release(released);
  }
  m_quota_row_port.commit(key,m_quota_l2_tick);++m_cleanup_cursor;
  if(m_cleanup_cursor==m_tvd->capacity()) {
    if(m_tvd->occupied()||m_quota_row_port.queued())throw std::logic_error("cleanup terminal ownership leak");
    m_cleanup_done=true;m_cleanup_done_at=ft_physical_cycle();m_tvd_lookup=NULL;
  }
}

void l2_cache::quota_print_terminal(FILE*fp,unsigned slice,unsigned long long app_cycles)const {
  if(!quota_timed())return;
  fprintf(fp,"EPL2CLEANV2|EPOCH_END|slice=%u|complete=%u|cleanup_requested_at=%llu|cleanup_done_at=%llu|app_after_cleanup_cycles=%llu|cleanup_rows=%u|row_pending=%u|ingress_pending=%u|clean_live=%u\n",
      slice,m_cleanup_done?1u:0u,m_cleanup_requested_at,m_cleanup_done_at,app_cycles,
      m_cleanup_cursor,m_quota_row_port.pending(),m_quota_row_port.queued(),m_tvd->clean_occupancy());
}

void l2_cache::tvd_epoch_cleanup(unsigned long long now) {
  if (!m_tvd) return;
  assert(m_tvd->epoch_ready() && !m_tvd_read);
  if(quota_timed()) {
    if(!m_cleanup_done||m_tvd->occupied()||m_quota_row_port.queued())
      throw std::logic_error("timed flush before clocked terminal cleanup");
    m_tvd_lookup=NULL;return;
  }
  while (tvd_reclaim_one((unsigned)-1, now)) {}
  assert(m_tvd->occupied() == 0); m_tvd_lookup = NULL;
}

void l2_cache::tvd_print(FILE *fp, unsigned slice) {
  m_tvd->advance(m_gpu_cycle_for_tvd()); const auto &s = m_tvd->stats();
  if(quota_timed()) {
    const auto&p=m_quota_row_port.stats();
    fprintf(fp,"EPL2CLEANV2|METADATA_COST|slice=%u|logical_control_read_views=3|update_execution=SHARED_TOKEN_GATED|row_service_lanes=%u|count_commit_lanes=1|registered_ingress_heads=6|ingress_depth_per_head=1|selector=indexed_paid_scan|selection_probes=%llu|row_read_beats=%llu|row_commit_beats=%llu|row_acks=%llu|counter_writes=%llu|clean_limit=%u|clean_live=%u|PPA=UNKNOWN|metadata_clock_closure=UNKNOWN\n",
      slice,m_config.m_ep_l2_quota_row_lanes,m_selector_probes,p.read_beats,p.commit_beats,
      p.acks,m_tvd->counter_writes(),m_tvd->clean_limit(),m_tvd->clean_occupancy());
  } else {
  fprintf(fp,"EPL2TVDV3|METADATA_COST|slice=%u|frontend_cam_queries=%llu|frontend_cam_ports=1|completion_cam_queries=%llu|completion_cam_ports=1|indexed_wb_accept=%llu|indexed_rollback=%llu|native_install_commits=%llu|native_promotion_commits=%llu|extra_packet_identity_bits=0|directory_bound_wb_uid_bits=32|indexed_control_read_views=3|indexed_control_update_lanes=3|clean_limit=%u|clean_live=%u|clean_limit_counter_bits=8|metadata_PPA=UNKNOWN|metadata_clock_closure=UNKNOWN\n",
      slice,m_tvd_lookup_queries,m_tvd_indexed_completions,m_tvd_indexed_accepts,
      m_tvd_indexed_rollbacks,m_tvd_native_installs,m_tvd_native_promotions,
      m_tvd->clean_limit(),m_tvd->clean_occupancy());
  }
  fprintf(fp, "EPL2TVDV2|SUMMARY|slice=%u|clean_installs=%llu|dirty_installs=%llu|"
      "read_responses=%llu|dirty_forward_responses=%llu|served_sectors=%llu|served_sector_bytes=%llu|"
      "promotions=%llu|live=%u|mandatory=%u|role_tvd=%u|retention_slot_cycles=%llu|"
      "clean_retention_slot_cycles=%llu|total_retention_slot_cycles=%llu|"
      "lookup_wait_cycles=%llu|wb_wait_cycles=%llu|bank_wait_cycles=%llu|icnt_wait_cycles=%llu|directory_queries=%llu\n", slice,
      (unsigned long long)s.clean_installs, (unsigned long long)s.dirty_installs,
      (unsigned long long)s.read_responses, (unsigned long long)s.dirty_forward_responses,
      (unsigned long long)s.served_sectors, (unsigned long long)s.served_sector_bytes,
      (unsigned long long)s.promotions, m_tvd->occupied(), m_tvd->mandatory(),
      m_ep_l2_payload.tvd_used(), (unsigned long long)s.tvd_extra_retention_slot_cycles,
      (unsigned long long)s.clean_retention_slot_cycles,
      (unsigned long long)(s.clean_retention_slot_cycles + s.tvd_extra_retention_slot_cycles),
      m_tvd_lookup_wait, m_tvd_wb_wait, m_tvd_bank_wait, m_tvd_resp_wait, m_tvd_lookup_queries);
}
