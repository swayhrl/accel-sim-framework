  bool has_response() const {handle h;return tx->ready_response(h,cursor);}
  bool prepare(uint64_t cycle) {
    if(cycle!=physical_cycle())throw std::logic_error("RO response bank cycle must be physical GPU time");
    if(selected && response_cycle==cycle)return true;
    if(selected){tx->commit_response(reply.transaction,false,response_cycle);selected=false;}
    handle h;if(!tx->ready_response(h,cursor))return false;
    if(!tx->prepare_response(h,cycle,reply))return false;
    selected=true;response_cycle=cycle;
    reply.request->set_ft_wb_data(c.m_ep_l2_payload.inspect(h).versions);return true;
  }
  void commit(uint64_t cycle) {
    if(!selected)throw std::logic_error("RO response commit without grant");
    tx->commit_response(reply.transaction,true,cycle);cursor=(reply.transaction.payload_id+1)%c.m_ep_l2_payload.physical_slots();selected=false;prefer_ro=false;
  }
