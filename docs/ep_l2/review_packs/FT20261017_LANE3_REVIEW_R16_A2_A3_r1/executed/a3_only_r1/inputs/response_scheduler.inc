bool scheduler_cache::ft_response_ready(unsigned long long cycle) {
  if(m_ro && m_ro->has_response() && (m_ro->reply.transaction.valid() || m_ro->prefer_ro || !native_queue_facade::access_ready()))return m_ro->prepare(cycle);
  if (!ft_enabled()) return true;
  mem_fetch *mf = native_queue_facade::peek_next_access();
  std::map<mem_fetch *,ep_l2::PayloadHandle>::const_iterator it = m_ft_read_refs.find(mf);
  assert(it != m_ft_read_refs.end());
  return m_ep_l2_payload.request(it->second, false, cycle,
      (unsigned long long)-1, ep_l2_payload_store::RESIDENT_HIT_READ) == ep_l2_payload_store::GRANTED;
}
