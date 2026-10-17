/*
Extracted portions of gpu-cache.h / gpu-cache.cc retain the following notice:

Copyright (c) 2009-2021, Tor M. Aamodt, Tayler Hetherington,
Vijay Kandiah, Nikos Hardavellas, Mahmoud Khairy, Junrui Pan,
Timothy G. Rogers
The University of British Columbia, Northwestern University, Purdue
University All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer;
2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution;
3. Neither the names of The University of British Columbia, Northwestern
University nor the names of their contributors may be used to
endorse or promote products derived from this software without specific
prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
*/
// Audit harness: exact request() body extracted from Lane3 gpu-cache.h.
// Containers, roles and counters below are a minimal surrounding fixture;
// this is NOT a compiled full GPGPU-Sim or application result.
#include <array>
#include <bitset>
#include <cassert>
#include <iostream>
#include <vector>
struct Arbiter {
  enum role {RESIDENT, BYPASS, WB, RO};
  enum request_result {GRANTED, LEGACY_PORT_BUSY, BANK_TRUE_CONTENTION};
  enum operation_class {RESIDENT_HIT_READ, RESIDENT_WRITE, FILL_WRITE,
    WB_READOUT, BYPASS_FILL, BYPASS_READ, RO_FILL_WRITE, RO_RESPONSE_READ};
  static const unsigned k_resident_slots=1024;
  struct pending_op {
    pending_op(role r_,unsigned id_,bool w,unsigned long long seq,
        unsigned long long arrival=0):r(r_),id(id_),write(w),sequence(seq),
        true_conflict(false),first_conflict_cycle(arrival){}
    role r; unsigned id; bool write; unsigned long long sequence;
    bool true_conflict; unsigned long long first_conflict_cycle;
  };
  unsigned m_mode=2,m_ft_mode=2;
  unsigned long long m_cycle=~0ULL;
  unsigned m_resident_reads=0,m_resident_writes=0,m_bypass_reads=0,m_bypass_writes=0;
  unsigned long long m_bank_attempts=0,m_bank_retry_attempts=0,m_bank_grants=0,
    m_bank_wait_cycles=0,m_bank_true_conflict_ops=0,m_bank_true_conflict_events=0,m_next_sequence=0;
  std::array<unsigned long long,4> m_bank_grants_by_bank{},m_bank_wait_cycles_by_bank{},
    m_bank_true_conflict_ops_by_bank{},m_bank_true_conflict_events_by_bank{};
  std::vector<int> m_slots=std::vector<int>(1168);
  std::bitset<4> m_bank_granted;
  std::vector<pending_op> m_pending[4],m_granted[4];
  bool enabled() const{return m_mode!=0;}
  bool banked() const{return m_mode==2;}
  void record_logical_operation(unsigned,operation_class){} // no control effect
  request_result request(role r, unsigned id, bool write, unsigned long long cycle,
                         unsigned long long sequence = (unsigned long long)-1,
                         operation_class op_class = RESIDENT_HIT_READ) {
    if (!enabled()) return GRANTED;
    if (m_ft_mode && m_cycle != (unsigned long long)-1)
      assert(cycle >= m_cycle && "FT bank clock must be physical and monotonic");
    if (m_cycle != cycle) {
      m_cycle = cycle;
      m_resident_reads = m_resident_writes = m_bypass_reads = m_bypass_writes = 0;
      m_bank_granted.reset();
      if (banked()) {
        for (unsigned b = 0; b < 4; ++b) {
          // A production retry need not return in the single cycle after it
          // was selected.  Retain an unconsumed oldest grant until its owner
          // actually retries; clearing it here loses the request.  Two
          // interleaved same-bank retries would otherwise select-and-discard
          // each other forever, eventually deadlocking the memory system.
          if (!m_granted[b].empty()) continue;
          if (m_pending[b].empty()) continue;
          unsigned best = 0;
          for (unsigned i = 1; i < m_pending[b].size(); ++i)
            if (m_pending[b][i].sequence < m_pending[b][best].sequence) best = i;
          m_granted[b].push_back(m_pending[b][best]);
          m_pending[b].erase(m_pending[b].begin() + best);
        }
      }
    }
    if (m_mode == 1) {
      unsigned &used_port = r == RESIDENT ?
          (write ? m_resident_writes : m_resident_reads) :
          (write ? m_bypass_writes : m_bypass_reads);
      if (used_port) return LEGACY_PORT_BUSY;
      ++used_port; return GRANTED;
    }
    const unsigned global_id = r == BYPASS ? k_resident_slots + id : id;
    assert(global_id < m_slots.size());
    const unsigned bank = global_id % 4;
    ++m_bank_attempts;
    if (!m_granted[bank].empty()) {
      const pending_op op = m_granted[bank].front();
      if (op.r == r && op.id == id && op.write == write) {
        // Its first call was accounted as the logical operation.  This call
        // is the retry that finally consumes an oldest-ready grant.
        ++m_bank_retry_attempts;
        m_granted[bank].clear(); m_bank_granted.set(bank); ++m_bank_grants;
        ++m_bank_grants_by_bank[bank];
        if (op.true_conflict) {
          const unsigned long long waited = cycle - op.first_conflict_cycle;
          m_bank_wait_cycles += waited;
          m_bank_wait_cycles_by_bank[bank] += waited;
        }
        return GRANTED;
      }
    }
    // A matching queued op is a retry. A new op is a new logical payload RAM
    // operation, even if it must wait behind older work or this cycle's grant.
    int pending_index = -1;
    for (unsigned i = 0; i < m_pending[bank].size(); ++i)
      if (m_pending[bank][i].r == r && m_pending[bank][i].id == id &&
          m_pending[bank][i].write == write) pending_index = i;
    if (pending_index >= 0) ++m_bank_retry_attempts;

    // No selected older op, no queued older op, and no operation consumed on
    // this bank this cycle: the first ready op uses an idle bank immediately.
    // There is no reason to stage it until N+1 merely to wait for hypothetical
    // later arrivals in the same cycle.
    if (m_granted[bank].empty() && m_pending[bank].empty() &&
        !m_bank_granted.test(bank)) {
      assert(pending_index < 0);
      record_logical_operation(bank, op_class);
      m_bank_granted.set(bank); ++m_bank_grants; ++m_bank_grants_by_bank[bank];
      return GRANTED;
    }

    if (pending_index < 0) {
      record_logical_operation(bank, op_class);
      m_pending[bank].push_back(pending_op(
          r, id, write,
          sequence == (unsigned long long)-1 ? m_next_sequence++ : sequence,
          cycle));
      pending_index = m_pending[bank].size() - 1;
    }
    // This denial has a real physical reason: an older selected/pending op,
    // or an operation already consumed this cycle.  It is no longer used for
    // first-idle-op staging bookkeeping.
    pending_op &denied = m_pending[bank][pending_index];
    if (!denied.true_conflict) {
      denied.true_conflict = true;
      denied.first_conflict_cycle = cycle;
      ++m_bank_true_conflict_ops;
      ++m_bank_true_conflict_ops_by_bank[bank];
    }
    ++m_bank_true_conflict_events;
    ++m_bank_true_conflict_events_by_bank[bank];
    return BANK_TRUE_CONTENTION;
  }

};
int main(){
 using A=Arbiter;
 {A a;
  assert(a.request(A::RESIDENT,8,false,0)==A::GRANTED);
  assert(a.request(A::RO,4,false,0)==A::BANK_TRUE_CONTENTION);
  assert(a.request(A::RO,4,false,1)==A::GRANTED);
  std::cout<<"CONTROL stable role and selected requester: grant at next cycle\n";
 }
 {A a;
  // RO last-sector fill is waiting behind another bank operation.
  assert(a.request(A::RESIDENT,8,false,0)==A::GRANTED);
  assert(a.request(A::RO,4,true,0,~0ULL,A::RO_FILL_WRITE)==A::BANK_TRUE_CONTENTION);
  // Next cache cycle: responses are examined before lower returns. A ready
  // earlier sector requests RO response read, but the older fill is selected.
  assert(a.request(A::RO,4,false,1,~0ULL,A::RO_RESPONSE_READ)==A::BANK_TRUE_CONTENTION);
  assert(a.request(A::RO,4,true,1,~0ULL,A::RO_FILL_WRITE)==A::GRANTED);
  // Actual store_port::tag_ready(complete) now transfers RO -> RESIDENT.
  unsigned successes=0;
  for(unsigned t=2;t<1002;++t)successes+=a.request(A::RESIDENT,4,false,t,~0ULL,A::RO_RESPONSE_READ)==A::GRANTED;
  assert(successes==0&&a.m_granted[0].size()==1&&a.m_granted[0][0].r==A::RO);
  std::cout<<"REPRO role transition: 1000 consecutive denied retries; selected old RO read remains parked\n";
 }
 {A a;
  // Slot0 fill first waits for bank service, while only slot4 has a response.
  assert(a.request(A::RESIDENT,8,false,0)==A::GRANTED);
  assert(a.request(A::RO,0,true,0,~0ULL,A::RO_FILL_WRITE)==A::BANK_TRUE_CONTENTION);
  assert(a.request(A::RESIDENT,4,false,1,~0ULL,A::RO_RESPONSE_READ)==A::BANK_TRUE_CONTENTION);
  assert(a.request(A::RO,0,true,1,~0ULL,A::RO_FILL_WRITE)==A::GRANTED);
  // Newly ready slot0 wins ready_response(cursor=0) before the retry of slot4.
  unsigned successes=0;
  for(unsigned t=2;t<1002;++t)successes+=a.request(A::RESIDENT,0,false,t,~0ULL,A::RO_RESPONSE_READ)==A::GRANTED;
  assert(successes==0&&a.m_granted[0][0].id==4);
  // Retrying the original candidate immediately makes progress; no bank reset.
  assert(a.request(A::RESIDENT,4,false,1002,~0ULL,A::RO_RESPONSE_READ)==A::GRANTED);
  std::cout<<"REPRO candidate switch: 1000 denied retries of new slot0; retry of original slot4 releases grant\n";
 }
 {A a;unsigned max_grants=0;
  for(unsigned t=0;t<1000;++t){unsigned n=0;
   for(unsigned id: {0U,4U,8U,12U})n+=a.request(A::RESIDENT,id,false,t)==A::GRANTED;
   max_grants=std::max(max_grants,n);assert(n<=1);
  }
  std::cout<<"CONTROL stable requesters: max bank grants in any physical cycle="<<max_grants<<"\n";
 }
}
