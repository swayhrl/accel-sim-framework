// Mechanism-study B: port of historical TVD consumers; public hook patch is
// reviewed/applied by A. Compile/production qualification is separate.
unsigned long long l2_cache::m_gpu_cycle_for_tvd() const {
  return ft_physical_cycle();
}


// OPTIONAL128 has one shared 128-row query/selector read fabric.  The legacy
// base selector is a 128-way state+age reduction, now explicitly two pipeline
// cycles (127 64-bit age comparisons; physical timing/PPA remains unclosed).
// Ext replacement is one fixed RR row, never a 128-row min scan.
// One additional indexed Ext read view (not an address CAM). Same-row
// fanout can serve read/RCW checks; two different rows in one tick cannot.
bool l2_cache::optional_read_row(unsigned row,unsigned long long now) {
  if(m_optional_read_cycle==now) {
    if(m_optional_read_row!=row || m_optional_read_uid!=m_optional_query_uid ||
       m_optional_read_fanouts>=2)return false;
    ++m_optional_read_fanouts;return true;
  }
  m_optional_read_cycle=now;m_optional_read_row=row;
  m_optional_read_uid=m_optional_query_uid;m_optional_read_fanouts=1;
  ++m_optional_reads;return true;
}
// Paid existing Base bank-compatible reduction, used only for landing pressure.
// No unlimited Ext scan. With <=512 resident tags (<=128/bank), Ext128 alone
// cannot fill292 physical slots/bank. If no reclaimable Base row exists, a full
// bank must include finite mandatory/pinned traffic, whose original completion
// paths remain independent of the frontend and eventually permit this reclaim.
bool l2_cache::optional_bank_reclaim(unsigned bank,unsigned long long now) {
  if(!m_optional_reclaim_live || m_optional_reclaim_bank!=bank ||
     m_optional_reclaim_revision!=m_tvd->revision()) {
    if(m_tvd_query_cycle==now)return false;
    m_tvd_query_cycle=now;++m_optional_selector_reads;
    m_optional_reclaim_row=128;
    for(auto state:{tvd_directory::CLEAN,tvd_directory::WB_COMPLETE}) {
      for(unsigned i=0;i<128;++i) {
        const auto &e=m_tvd->at(i);
        if(e.status!=state || !e.reclaimable() || !e.payload.valid() ||
           e.payload.payload_id%4!=bank)continue;
        if(m_optional_reclaim_row==128 ||
           e.age<m_tvd->at(m_optional_reclaim_row).age)m_optional_reclaim_row=i;
      }
      if(m_optional_reclaim_row!=128)break;
    }
    m_optional_reclaim_bank=bank;m_optional_reclaim_revision=m_tvd->revision();
    m_optional_reclaim_ready=now+2;m_optional_reclaim_live=true;
    if(m_optional_reclaim_row!=128)
      m_optional_reclaim_incarnation=m_tvd->at(m_optional_reclaim_row).incarnation;
    return false;
  }
  if(now<m_optional_reclaim_ready || m_optional_reclaim_row==128 ||
     m_optional_base_front_write==now)return false;
  const auto t=tvd_directory::ticket(m_optional_reclaim_row,m_optional_reclaim_incarnation);
  assert(m_tvd->live(t));
  const auto &e=m_tvd->at(t.index);assert(e.reclaimable() && e.payload.payload_id%4==bank);
  m_optional_base_front_write=now;ep_l2::PayloadHandle h;
  assert(m_tvd->reclaim(t,h,now)==tvd_directory::OK);
  assert(m_ep_l2_payload.inspect(h).pins==0);m_ep_l2_payload.release(h);
  m_optional_reclaim_live=false;++m_optional_reclaims;optional_forget_plan();
  return true;
}
void l2_cache::optional_forget_plan() {
  m_optional_base_plan_live=false;m_optional_spill_phase=0;
}
bool l2_cache::optional_base_selector(mem_fetch *mf,new_addr_type line,
    bool wb,unsigned long long now) {
  if(!m_tvd_optional)return true;
  if(m_optional_base_plan_live && m_optional_base_uid==mf->get_request_uid() &&
     m_optional_base_plan.line==line && m_optional_base_plan.writeback==wb &&
     m_optional_base_plan.revision==m_tvd->revision())
    return now>=m_optional_base_ready;
  optional_forget_plan();
  if(m_tvd_query_cycle==now)return false;
  m_tvd_query_cycle=now;++m_optional_selector_reads;
  m_optional_base_plan=m_tvd->preview_install(line,wb,true);
  m_optional_base_uid=mf->get_request_uid();
  m_optional_base_ready=now+2;m_optional_base_plan_live=true;
  return false;
}
bool l2_cache::optional_absence_current(mem_fetch *mf,unsigned long long now) {
  if(!m_tvd_optional || !m_optional_base_done ||
     m_optional_absence_epoch==m_tvd->creation_epoch())return true;
  // A producer cannot publish another Base owner while this single frontend
  // lease exists.  Do not silently cancel a live reader if violated.
  assert(!m_tvd_read && "unqualified concurrent Base creator with Ext reader");
  m_optional_base_done=false;m_optional_lookup_segment=false;
  m_tvd_lookup_done=false;m_tvd_lookup_cycle=now;
  ++m_optional_replays;optional_forget_plan();
  return false;
}
l2_cache::optional_prepare l2_cache::optional_spill_prepare(mem_fetch *mf,
    unsigned long long now) {
  if(!m_tvd_optional || m_config.m_ep_l2_victim_extension!=2 ||
     !m_optional_base_plan_live ||
     m_optional_base_plan.status!=tvd_directory::OK ||
     !m_optional_base_plan.displaced.valid())return OPTIONAL_FALLBACK;
  const auto &source=m_tvd->at(m_optional_base_plan.index);
  if(source.status!=tvd_directory::CLEAN || !source.reclaimable())
    return OPTIONAL_FALLBACK; // Never migrate WB_COMPLETE or mandatory.
  if(m_optional_spill_phase==0 || m_optional_spill_uid!=mf->get_request_uid()) {
    if(m_tvd_query_cycle==now)return OPTIONAL_WAIT;
    m_tvd_query_cycle=now;++m_optional_selector_reads;
    if(!optional_read_row(m_optional_rr,now))return OPTIONAL_WAIT;
    const auto &target=m_tvd_optional->at(m_optional_rr);
    if(target.status!=tvd_directory::EMPTY &&
       (target.status!=tvd_directory::CLEAN || !target.reclaimable())) {
      ++m_optional_fallback;return OPTIONAL_FALLBACK; // bounded, no scan
    }
    m_optional_target_inc=target.incarnation;
    m_optional_spill_source=source.payload;
    m_optional_spill_cycle=now;m_optional_spill_phase=1;
    m_optional_spill_uid=mf->get_request_uid();
    return OPTIONAL_WAIT;
  }
  if(now<=m_optional_spill_cycle || m_tvd_query_cycle==now)return OPTIONAL_WAIT;
  m_tvd_query_cycle=now;++m_optional_selector_reads; // actual indexed recheck
  if(!optional_read_row(m_optional_rr,now))return OPTIONAL_WAIT;
  const auto &target=m_tvd_optional->at(m_optional_rr);
  if(target.incarnation!=m_optional_target_inc || target.readers ||
     !(source.payload==m_optional_spill_source)) {
    m_optional_spill_phase=0;++m_optional_fallback;return OPTIONAL_FALLBACK;
  }
  m_optional_ext_plan=m_tvd_optional->preview_clean_slot(m_optional_rr,source.line,true);
  if(!m_tvd->spill_ready(m_optional_base_plan,*m_tvd_optional,m_optional_ext_plan,now)) {
    m_optional_spill_phase=0;++m_optional_fallback;return OPTIONAL_FALLBACK;
  }
  if(m_optional_base_front_write==now)return OPTIONAL_WAIT;
  if(!m_optional_write.reserve(m_optional_rr,m_optional_target_inc,
       mf->get_request_uid(),source.payload,ep_l2_optional_segment_port::INSTALL,now))
    return OPTIONAL_WAIT;
  m_optional_base_front_write=now;
  return OPTIONAL_READY;
}
bool l2_cache::optional_commit_spill(mem_fetch *mf,new_addr_type line,
    ep_l2::PayloadHandle h,unsigned valid,unsigned long long now) {
  assert(m_optional_base_front_write==now);
  assert(m_optional_write.reserved(m_optional_rr,m_optional_target_inc,
      mf->get_request_uid(),ep_l2_optional_segment_port::INSTALL,now));
  ep_l2::PayloadHandle displaced;tvd_directory::ticket installed;
  const auto r=m_tvd->commit_clean_spill(m_optional_base_plan,*m_tvd_optional,
       m_optional_ext_plan,line,h,valid,now,installed,displaced);
  assert(r==tvd_directory::OK);
  if(displaced.valid()) {
    assert(m_ep_l2_payload.inspect(displaced).pins==0);
    m_ep_l2_payload.release(displaced);
  }
  ++m_tvd_native_installs;++m_optional_spills;
  m_optional_ever_populated=true;m_optional_rr=(m_optional_rr+1)%128;
  // Sole head evicts Y while allocating X. Y != X by native tag MISS proof.
  assert(line!=m_optional_query_line);
  m_optional_absence_epoch=m_tvd->creation_epoch();
  optional_forget_plan();return true;
}

bool l2_cache::tvd_install_victim(new_addr_type address, ep_l2::PayloadHandle h,
    unsigned valid, unsigned dirty, bool wb, unsigned long long now,
    tvd_directory::ticket *installed) {
  auto plan = m_tvd_optional ? m_optional_base_plan :
      m_tvd->preview_install(address, wb, true);
  if(m_tvd_optional) {
    assert(m_optional_base_plan_live && plan.line==address && plan.writeback==wb);
    assert(now>=m_optional_base_ready && plan.revision==m_tvd->revision());
    assert(m_optional_base_front_write!=now);
    m_optional_base_front_write=now;
  }
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
  if(m_tvd_optional) {
    assert(address!=m_optional_query_line);
    m_optional_absence_epoch=m_tvd->creation_epoch();optional_forget_plan();
  }
  return true;
}

bool l2_cache::tvd_cached_wad_contains(mem_fetch *mf, new_addr_type address) const {
  assert(m_tvd);
  if (m_tvd_lookup == mf && m_tvd_lookup_done && !m_optional_lookup_segment) {
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

bool l2_cache::tvd_reclaim_one(unsigned bank, unsigned long long now) {
  // The segmented candidate pays the same shared reduction fabric for a
  // bank-compatible Base reclaim. No unpriced all-row fallback is used.
  if(m_tvd_optional)return optional_bank_reclaim(bank,now);
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
  if (m_tvd_lookup != mf || (m_tvd_optional && m_optional_query_uid!=mf->get_request_uid())) {
    assert(!m_tvd_read);
    m_tvd_lookup = mf; m_tvd_lookup_cycle = now;
    m_tvd_lookup_done = false;
    m_optional_base_done=false;m_optional_lookup_segment=false;
    m_optional_query_uid=mf->get_request_uid();m_optional_query_line=address;
    optional_forget_plan();
    ++m_tvd_lookup_wait; return wait(M::VICTIM_LOOKUP);
  }
  if (now <= m_tvd_lookup_cycle) return wait(M::VICTIM_LOOKUP);
  if(!optional_absence_current(mf,now))return wait(M::VICTIM_LOOKUP);
  if (!m_tvd_lookup_done) {
    if (m_tvd_query_cycle == now) return wait(M::VICTIM_LOOKUP);
    m_tvd_query_cycle = now;
    if(!m_tvd_optional || !m_optional_base_done) {
      ++m_tvd_lookup_queries;m_tvd_lookup_ticket=m_tvd->find(address);
      if(m_tvd_optional && !m_tvd->live(m_tvd_lookup_ticket)) {
        m_optional_base_done=true;m_optional_absence_epoch=m_tvd->creation_epoch();
        return wait(M::VICTIM_LOOKUP);
      }
    } else {
      ++m_optional_queries;m_optional_lookup_segment=true;
      m_tvd_lookup_ticket=m_tvd_optional->find(address);
    }
    m_tvd_lookup_done = true;
  }
  tvd_directory *directory=m_optional_lookup_segment?m_tvd_optional.get():m_tvd.get();
  const auto ticket = m_tvd_lookup_ticket;
  if(m_optional_lookup_segment && ticket.index<128 &&
     !optional_read_row(ticket.index,now))return wait(M::VICTIM_LOOKUP);
  if (!directory->live(ticket)) return TVD_NORMAL;
  // Dirty pending/inflight reads use a distinct client+UID+generation key
  // in the existing bank scoreboard. The public r2 adapter delays WB->TVD
  // role transitions while the reader is pinned. CLEAN_ONLY WAD records have
  // no retained handle and still return WAIT_WRITEBACK below.
  auto op = mf->isatomic() ? tvd_directory::ATOMIC_OP :
            mf->get_is_write() ? tvd_directory::WRITE_OP : tvd_directory::READ_OP;
  auto observation = directory->preview_ticket(ticket, mf->get_access_sector_mask().to_ulong(), op);
  known |= 1ULL << M::SAME_ADDRESS_WB;
  if (observation.status == tvd_directory::WAIT_WRITEBACK) {
    ++m_tvd_wb_wait; return wait(M::SAME_ADDRESS_WB);
  }
  // A mandatory-WB refusal above can mask the later reader/pin predicate.
  known |= 1ULL << M::PINNED_PAYLOAD;
  if (observation.status == tvd_directory::PINNED) {
    ++m_tvd_wb_wait; return wait(M::PINNED_PAYLOAD);
  }
  if(m_optional_lookup_segment &&
     (op!=tvd_directory::READ_OP || observation.status==tvd_directory::MISSING_SECTOR)) {
    // No ext->dirty promotion. Destroy the clean alias before Native fill/write.
    const auto &e=directory->at(ticket.index);
    if(e.readers || m_ep_l2_payload.inspect(e.payload).pins)
      return wait(M::PINNED_PAYLOAD);
    if(!m_optional_write.reserve(ticket.index,ticket.incarnation,mf->get_request_uid(),
         e.payload,ep_l2_optional_segment_port::DROP,now))return wait(M::VICTIM_LOOKUP);
    ep_l2::PayloadHandle released;
    assert(directory->reclaim(ticket,released,now)==tvd_directory::OK);
    m_ep_l2_payload.release(released);++m_optional_invalidations;
    // This head paid the address query and its own DROP just proved absence.
    // Keep the Base epoch proof, but retire the dead row token. Re-reading that
    // old row on every retry would monopolize the sole Ext indexed view and
    // starve a different RR row required by Native replacement.
    m_tvd_lookup_ticket=tvd_directory::ticket();
    return TVD_NORMAL;
  }
  if (op != tvd_directory::READ_OP) return TVD_NORMAL; // base promotion
  if (observation.status == tvd_directory::MISSING_SECTOR) {
    ep_l2::PayloadHandle released;
    if (directory->reclaim(ticket, released, now) == tvd_directory::PINNED)
      return wait(M::PINNED_PAYLOAD);
    m_ep_l2_payload.release(released); return TVD_NORMAL;
  }
  if (observation.status != tvd_directory::READ_READY) return TVD_NORMAL;
  known |= 1ULL << M::RESPONSE_QUEUE_FULL;
  if (!response_space) { ++m_tvd_resp_wait; return wait(M::RESPONSE_QUEUE_FULL); }
  if(m_optional_lookup_segment && !m_tvd_read &&
     !m_optional_write.reserve(ticket.index,ticket.incarnation,mf->get_request_uid(),
        observation.payload,ep_l2_optional_segment_port::BEGIN_READ,now))
    return wait(M::VICTIM_LOOKUP);
  if (!m_tvd_read) {
    assert(m_ep_l2_payload.handle_owner_matches(observation.payload, address));
    m_tvd_read.reset(new tvd_directory::read_lease());
    assert(directory->begin_read(observation, mf->get_access_sector_mask().to_ulong(), *m_tvd_read) == tvd_directory::OK);
    m_ep_l2_payload.pin(observation.payload);
  }
  const auto h = m_tvd_read->handle();
  // Reserve retire metadata before bank service and response enqueue. A failed
  // bank grant consumes the port cycle, but retains the single exact lease.
  if(m_optional_lookup_segment &&
     !m_optional_write.reserve(ticket.index,ticket.incarnation,mf->get_request_uid(),
       h,ep_l2_optional_segment_port::END_READ,now))return wait(M::VICTIM_LOOKUP);
  if (m_ep_l2_payload.request(h, false, now, (unsigned long long)-1,
      ep_l2_payload_store::TVD_READ, ep_l2_payload_store::FRONTEND, mf->get_request_uid()) != ep_l2_payload_store::GRANTED) {
    ++m_tvd_bank_wait; return wait(M::DATA_SERVICE);
  }
  mf->set_ep_l2_payload_identity(h.payload_id, h.generation);
  mf->set_ft_wb_data(m_ep_l2_payload.inspect(h).versions);
  return TVD_RESPONSE;
}

void l2_cache::tvd_response_commit(mem_fetch *mf, unsigned long long now) {
  assert(m_tvd_read && mf == m_tvd_lookup);
  const auto h = m_tvd_read->handle();
  tvd_directory *directory=m_optional_lookup_segment?m_tvd_optional.get():m_tvd.get();
  if(m_optional_lookup_segment)assert(m_optional_write.reserved(m_tvd_lookup_ticket.index,
      m_tvd_lookup_ticket.incarnation,mf->get_request_uid(),ep_l2_optional_segment_port::END_READ,now));
  assert(directory->response_commit(*m_tvd_read, now) == tvd_directory::OK);
  m_ep_l2_payload.unpin(h);
  const auto ticket=m_tvd_lookup_ticket;
  assert(directory->live(ticket) && directory->at(ticket.index).payload==h);
  const auto &e=directory->at(ticket.index);
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
  m_optional_base_done=false;m_optional_lookup_segment=false;optional_forget_plan();
  if(m_ro)m_ro->record_accepted(mf);
  ++m_ft_stats.accepted;
  ms_observe_frontend(mf, now, 0, true, 0); // Actual response enqueue, exactly once.
}

bool l2_cache::tvd_promote(mem_fetch *mf, unsigned time, std::list<cache_event> &events) {
  const auto physical_cycle = m_gpu_cycle_for_tvd();
  const auto address = m_config.block_addr(mf->get_addr());
  assert(m_tvd_lookup == mf && m_tvd_lookup_done && !m_optional_lookup_segment);
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
    assert(m_tvd->commit_dirty_promotion(plan, physical_cycle, promoted, wb_ticket) == tvd_directory::OK);
    ++m_tvd_native_promotions;
    assert(m_ep_l2_wad_birth_cycle.insert(std::make_pair(evicted.m_block_addr, physical_cycle)).second);
    m_ep_l2_payload.transfer(victim, ep_l2_payload_store::WB, ep_l2_payload_store::WB_STAGED);
    auto &p = m_ft_pending; p.request = mf; p.dirty = p.wad = true;
    p.tag_index = index; p.victim = p.staging = victim;
    p.victim_address = evicted.m_block_addr; p.born = physical_cycle;
    p.wad_ticket = wb_ticket;
    mem_fetch *packet = m_memfetch_creator->alloc(evicted.m_block_addr, L2_WRBK_ACC,
        mf->get_access_warp_mask(), evicted.m_byte_mask, evicted.m_sector_mask,
        evicted.m_modified_size, true, time, -1, -1, -1, NULL, mf->get_streamID());
    packet->set_chip(mf->get_tlx_addr().chip); packet->set_partition(mf->get_tlx_addr().sub_partition);
    send_write_request(packet, cache_event(WRITE_BACK_REQUEST_SENT, evicted), time, events);
    assert(p.bound); p = ft_replacement();
  } else {
    assert(m_tvd->promote(t, promoted, physical_cycle) == tvd_directory::OK);
    ++m_tvd_native_promotions;
    if (live) m_ep_l2_payload.release(victim);
  }
  m_ep_l2_payload.transfer(promoted, ep_l2_payload_store::RESIDENT, ep_l2_payload_store::RESIDENT_VALID);
  m_tag_array->tvd_bind(index, address, time, old.valid_sectors);
  set_tag_payload_handle(index, promoted);
  assert(m_ep_l2_payload.ownership_consistent());
  return true;
}

void l2_cache::tvd_epoch_cleanup(unsigned long long now) {
  if (!m_tvd) return;
  if(m_tvd_optional && m_optional_ever_populated)
    throw std::logic_error("OPTIONAL128 runtime cleanup profile is not qualified");
  assert(m_tvd->epoch_ready() && !m_tvd_read);
  while (tvd_reclaim_one((unsigned)-1, now)) {}
  assert(m_tvd->occupied() == 0); m_tvd_lookup = NULL;
}

void l2_cache::tvd_print(FILE *fp, unsigned slice) {
  m_tvd->advance(m_gpu_cycle_for_tvd()); const auto &s = m_tvd->stats();
  if(m_tvd_optional) {
    m_tvd_optional->advance(m_gpu_cycle_for_tvd());
    fprintf(fp,"EPL2TVDX1|SEGMENT|slice=%u|mode=%u|base_capacity=128|ext_capacity=128|base_live=%u|ext_live=%u|mandatory=%u|ext_mandatory=%u|ext_queries=%llu|base_replays=%llu|spills=%llu|fallback=%llu|invalidations=%llu|selector_reads=%llu|ext_write_grants=%llu|ext_write_merges=%llu|shared_query_ports=1|base_selector_cycles=2|indexed_ext_read_recheck_cycles=2|ext_write_ports=1|ext_indexed_read_views=1|base_reclaim_cycles=2|payload_slots=1168|bank_count=4|bank_ports=1|PPA=UNKNOWN\n",
      slice,m_config.m_ep_l2_victim_extension,m_tvd->occupied(),m_tvd_optional->occupied(),
      m_tvd->mandatory(),m_tvd_optional->mandatory(),m_optional_queries,m_optional_replays,
      m_optional_spills,m_optional_fallback,m_optional_invalidations,m_optional_selector_reads,
      (unsigned long long)m_optional_write.grants,(unsigned long long)m_optional_write.merges);
  }
  if(m_tvd_optional) {
    const auto &x=m_tvd_optional->stats();
    fprintf(fp,"EPL2TVDX1|CONTROL|slice=%u|ext_indexed_reads=%llu|paid_base_bank_reclaims=%llu|old_indexed_read_views=3|added_ext_indexed_read_views=1|old_update_lanes=3|added_ext_update_lanes=1|ext_read_responses=%llu|ext_served_sectors=%llu|ext_served_sector_bytes=%llu|ext_clean_installs=%llu|ext_reclaimed=%llu|ext_clean_slot_cycles=%llu|unexported_ext_waits=UNKNOWN\n",
      slice,m_optional_reads,m_optional_reclaims,
      (unsigned long long)x.read_responses,(unsigned long long)x.served_sectors,
      (unsigned long long)x.served_sector_bytes,(unsigned long long)x.clean_installs,
      (unsigned long long)x.reclaimed,(unsigned long long)x.clean_retention_slot_cycles);
  }
  fprintf(fp,"EPL2TVDV3|METADATA_COST|slice=%u|frontend_cam_queries=%llu|frontend_cam_ports=1|completion_cam_queries=%llu|completion_cam_ports=1|indexed_wb_accept=%llu|indexed_rollback=%llu|native_install_commits=%llu|native_promotion_commits=%llu|extra_packet_identity_bits=0|directory_bound_wb_uid_bits=32|indexed_control_read_views=3|indexed_control_update_lanes=3|metadata_PPA=UNKNOWN|metadata_clock_closure=UNKNOWN\n",
      slice,m_tvd_lookup_queries,m_tvd_indexed_completions,m_tvd_indexed_accepts,
      m_tvd_indexed_rollbacks,m_tvd_native_installs,m_tvd_native_promotions);
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
