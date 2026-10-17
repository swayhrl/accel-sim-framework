  bool has_response() const {handle h;return reply.transaction.valid() || tx->ready_response(h,cursor);}
  bool prepare(uint64_t cycle) {
    if(cycle!=physical_cycle())throw std::logic_error("RO response bank cycle must be physical GPU time");
    if(selected && response_cycle==cycle)return true;
    if(selected){tx->commit_response(reply.transaction,false,response_cycle);selected=false;}
    // The existing reply identity also holds a denied candidate, but selected
    // means a real Bank grant in response_cycle. No data is read or exposed
    // while only waiting. Keep that identity until enqueue, including across
    // ICNT backpressure and a same-bank lower-index transaction becoming ready.
    if(!reply.transaction.valid()) {
      handle h;if(!tx->ready_response(h,cursor))return false;
      reply.transaction=h;
    }
    if(!tx->prepare_response(reply.transaction,cycle,reply))return false;
    selected=true;response_cycle=cycle;
    reply.request->set_ft_wb_data(c.m_ep_l2_payload.inspect(reply.transaction).versions);return true;
  }
  void commit(uint64_t cycle) {
    if(!selected)throw std::logic_error("RO response commit without grant");
    tx->commit_response(reply.transaction,true,cycle);cursor=(reply.transaction.payload_id+1)%c.m_ep_l2_payload.physical_slots();
    reply.transaction=handle();selected=false;prefer_ro=false;
  }
