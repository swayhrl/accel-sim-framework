// New private V5 production prototype: bounded metadata reservation only.
// This does not complete frontend/cleanup integration; see Track C README.
#ifndef EP_L2_QUOTA_ROW_PORT_H
#define EP_L2_QUOTA_ROW_PORT_H
#include <array>
#include <cstdint>
#include <stdexcept>
#include <limits>
class ep_l2_quota_row_port {
 public:
  struct key {
    unsigned producer, uid, row, payload_id, state;
    std::uint64_t incarnation, generation;
    key(unsigned p=0,unsigned u=0,unsigned r=128,std::uint64_t i=0,
        unsigned h=~0u,std::uint64_t g=0,unsigned st=0):
      producer(p),uid(u),row(r),payload_id(h),state(st),incarnation(i),generation(g){}
    bool operator==(const key&o)const{return producer==o.producer&&uid==o.uid&&row==o.row&&
      payload_id==o.payload_id&&state==o.state&&incarnation==o.incarnation&&generation==o.generation;}
  };
  struct counters {
    std::uint64_t read_beats=0,commit_beats=0,acks=0,holds=0,row_conflicts=0,
      port_conflicts=0,cancellations=0;
  };
  explicit ep_l2_quota_row_port(unsigned k=2): lanes_(k) {
    if(k!=1&&k!=2)throw std::invalid_argument("row lanes must be1 or2");
  }
  void configure(unsigned k) {
    if(pending())throw std::logic_error("configure busy row port");
    if(k!=1&&k!=2)throw std::invalid_argument("row lanes must be1 or2");lanes_=k;
  }
  // Time is an explicit L2 service tick, not core-cycle or DRAM-call count.
  // First same-tick requests form READ; subsequent ticks expose COMMIT.
  // No new READ while any prepared entry remains. All repeated polls are free
  // of new mutation, but each failed poll is diagnostic only, not a clock.
  bool ready(const key&k,std::uint64_t tick) {
    monotonic(tick);
    for(unsigned i=0;i<2;++i)if(slots_[i].live&&slots_[i].identity==k) {
      if(tick<=read_tick_){++stats_.holds;return false;}
      commit_tick_=tick;return true;
    }
    if(pending()&&tick!=read_tick_){++stats_.port_conflicts;return false;}
    if(!pending()&&(commit_tick_==tick || (stats_.read_beats&&read_tick_==tick))) {
      ++stats_.port_conflicts;return false;
    }
    for(unsigned i=0;i<2;++i)if(slots_[i].live&&slots_[i].identity.row==k.row) {
      ++stats_.row_conflicts;return false;
    }
    unsigned n=pending();if(n>=lanes_){++stats_.port_conflicts;return false;}
    // Retained identity marks a physical READ claim even after cancellation.
    // No extra register/slot is added, and no third row may reuse a cancelled
    // K2 lane during the same READ beat.
    if(n) {
      unsigned claims=0;for(const auto&s:slots_)claims+=s.identity.row<128;
      if(claims>=lanes_){++stats_.port_conflicts;return false;}
    }
    if(!n) {
      read_tick_=tick;commit_tick_=unset();++stats_.read_beats;
      for(auto&s:slots_)s.identity=key();
    }
    for(unsigned i=0;i<2;++i)if(!slots_[i].live && slots_[i].identity.row==128) {
      slots_[i].live=true;slots_[i].identity=k;break;
    }
    ++stats_.holds;return false;
  }
  void commit(const key&k,std::uint64_t tick) {
    monotonic(tick);
    if(commit_tick_!=tick||tick<=read_tick_)throw std::logic_error("commit without paid reservation");
    for(unsigned i=0;i<2;++i)if(slots_[i].live&&slots_[i].identity==k) {
      if(last_count_commit_!=tick){++stats_.commit_beats;last_count_commit_=tick;}
      slots_[i].live=false;++stats_.acks;return;
    }
    throw std::logic_error("unowned row commit");
  }
  // Reservation cancellation never refunds an occupied READ/COMMIT beat.
  // No allocator, packet, row or count has changed at this preflight stage.
  bool cancel(const key&k) {
    for(auto&slot:slots_)if(slot.live&&slot.identity==k){slot.live=false;++stats_.cancellations;return true;}
    return false;
  }
  // Bounded owner cancellation before any visible row/payload mutation.
  // Cancelling cannot refund the paid READ beat or steal another producer.
  unsigned cancel_owner(unsigned producer,unsigned uid) {
    unsigned n=0;for(auto&slot:slots_)if(slot.live&&slot.identity.producer==producer&&slot.identity.uid==uid) {
      slot.live=false;++stats_.cancellations;++n;
    }return n;
  }
  unsigned pending()const{unsigned n=0;for(const auto&s:slots_)n+=s.live;return n;}
  unsigned lanes()const{return lanes_;}
  const counters&stats()const{return stats_;}
  // Explicit one-count-write arithmetic helper. Caller must preflight all row
  // transitions and publish atomically; production count mutations are not yet
  // routed here. This helper is NOT a claim of completed quota integration.
  static unsigned merged_count(unsigned count,unsigned cap,const int*delta,unsigned n,unsigned k) {
    if(k!=1&&k!=2)throw std::invalid_argument("row lanes");
    if(n>k||cap>128||count>cap)throw std::invalid_argument("count contract");
    int projected=count;
    for(unsigned i=0;i<n;++i){if(delta[i]<-1||delta[i]>1)throw std::invalid_argument("row delta");
      projected+=delta[i];if(projected<0||projected>int(cap))throw std::overflow_error("ordered quota block");}
    return unsigned(projected);
  }
 private:
  struct slot{bool live=false;key identity;};
  static std::uint64_t unset(){return std::numeric_limits<std::uint64_t>::max();}
  void monotonic(std::uint64_t tick){if(tick<observed_tick_)throw std::logic_error("row clock regressed");observed_tick_=tick;}
  unsigned lanes_;std::array<slot,2>slots_;
  std::uint64_t observed_tick_=0,read_tick_=0,commit_tick_=unset(),last_count_commit_=unset();
  counters stats_;
};
#endif
