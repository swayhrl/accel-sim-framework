// C lifecycle V2: six bounded producer heads, registered arbitration,
// explicit READ then COMMIT, no same-row pair and no cancellation refund.
// This is a timing protocol model, not a physical port/PPA qualification.
#ifndef EP_L2_QUOTA_ROW_PORT_H
#define EP_L2_QUOTA_ROW_PORT_H
#include <array>
#include <cstdint>
#include <stdexcept>
#include <limits>
struct ep_l2_row_service_token {
 bool valid=false;
 unsigned index=128,producer=0,uid=0;
 std::uint64_t incarnation=0,tick=0;
};
class ep_l2_quota_row_port {
 public:
  struct key {
    unsigned producer,uid,row,payload_id,state;
    std::uint64_t incarnation,generation;
    key(unsigned p=0,unsigned u=0,unsigned r=128,std::uint64_t i=0,
        unsigned h=~0u,std::uint64_t g=0,unsigned st=0):
      producer(p),uid(u),row(r),payload_id(h),state(st),incarnation(i),generation(g){}
    bool operator==(const key&o)const{return producer==o.producer&&uid==o.uid&&row==o.row&&
      payload_id==o.payload_id&&state==o.state&&incarnation==o.incarnation&&generation==o.generation;}
  };
  struct counters {
    std::uint64_t read_beats=0,commit_beats=0,acks=0,holds=0,row_conflicts=0,
      port_conflicts=0,cancellations=0,ingress_refusals=0,arbitration_ticks=0,wait_ticks=0;
  };
  explicit ep_l2_quota_row_port(unsigned k=1):lanes_(k) {
    if(k!=1&&k!=2)throw std::invalid_argument("row lanes1/2");
  }
  void configure(unsigned k) {
    if(pending()||queued())throw std::logic_error("configure busy metadata fabric");
    if(k!=1&&k!=2)throw std::invalid_argument("row lanes1/2");lanes_=k;
  }
  static unsigned group(unsigned p) {
    if(p==2)return 0;                     // completion origin
    if(p==1)return 1;                     // lower enqueue
    if(p==3||p==4||p==5||p==6||p==7||p==12||p==13)return 2; // one frontend head
    if(p==8)return 3;                     // read-lease begin
    if(p==9||p==14)return 4;               // response/cancel retirement
    if(p==10||p==11)return 5;              // rollback/terminal cleanup (exclusive)
    throw std::invalid_argument("unknown metadata producer");
  }
  // One call at the real L2 service boundary; callbacks cannot mint a new
  // tick. The six head records are finite, explicit metadata ingress.
  void tick(std::uint64_t now) {
    if(now<observed_tick_)throw std::logic_error("metadata clock regressed");
    if(now==observed_tick_)return;
    if(pending())stats_.wait_ticks+=now-observed_tick_;
    observed_tick_=now;++stats_.arbitration_ticks;
    for(auto&h:heads_)if(h.active)h.eligible=true;
    if(pending()||last_commit_tick_==now||read_tick_==now)return;
    unsigned n=0,last=rr_;
    for(unsigned a=0;a<6&&n<lanes_;++a) {
      unsigned g=(rr_+a)%6;auto&h=heads_[g];
      if(!h.active||!h.eligible||h.selected)continue;
      bool clash=false;for(unsigned i=0;i<n;++i)clash|=slots_[i].identity.row==h.identity.row;
      if(clash){++stats_.row_conflicts;continue;}
      slots_[n].live=true;slots_[n].identity=h.identity;slots_[n].head=g;
      h.selected=true;++n;last=g;
    }
    if(n){read_tick_=now;++stats_.read_beats;rr_=(last+1)%6;}
  }
  bool ready(const key&k,std::uint64_t now) {
    tick(now);
    if(k.row>=128)throw std::invalid_argument("metadata row out of range");
    unsigned g=group(k.producer);auto&h=heads_[g];
    if(!h.active){h.active=true;h.eligible=false;h.selected=false;h.identity=k;}
    else if(!(h.identity==k)){++stats_.ingress_refusals;return false;}
    for(const auto&slot:slots_)if(slot.live&&slot.identity==k) {
      if(now>read_tick_)return true;
      ++stats_.holds;return false;
    }
    ++stats_.holds;return false;
  }
  ep_l2_row_service_token token(const key&k,std::uint64_t now)const {
    ep_l2_row_service_token t;
    if(now!=observed_tick_||now<=read_tick_)return t;
    for(const auto&s:slots_)if(s.live&&s.identity==k) {
      t.valid=true;t.index=k.row;t.incarnation=k.incarnation;t.tick=now;
      t.producer=k.producer;t.uid=k.uid;return t;
    }return t;
  }
  void commit(const key&k,std::uint64_t now) {
    tick(now);
    if(!token(k,now).valid)throw std::logic_error("COMMIT without paid row token");
    for(auto&slot:slots_)if(slot.live&&slot.identity==k) {
      auto&h=heads_[slot.head];
      if(!h.active||!(h.identity==k))throw std::logic_error("metadata ingress identity lost");
      slot.live=false;h.active=false;h.selected=false;h.eligible=false;
      if(last_commit_tick_!=now){++stats_.commit_beats;last_commit_tick_=now;}
      ++stats_.acks;return;
    }throw std::logic_error("unowned metadata commit");
  }
  bool owns(const key&k)const {
    for(const auto&h:heads_)if(h.active&&h.identity==k)return true;return false;
  }
  bool cancel(const key&k) {
    if(!owns(k))return false;cancel_owner(k.producer,k.uid);return true;
  }
  unsigned cancel_owner(unsigned producer,unsigned uid) {
    unsigned n=0;
    for(unsigned g=0;g<6;++g) {
      auto&h=heads_[g];if(!h.active||h.identity.producer!=producer||h.identity.uid!=uid)continue;
      for(auto&s:slots_)if(s.live&&s.head==g)s.live=false;
      h.active=false;h.selected=false;h.eligible=false;++stats_.cancellations;++n;
    }return n;
  }
  unsigned cancel_frontend(unsigned uid) {
    unsigned n=0;for(unsigned p: {3u,4u,5u,6u,7u,12u,13u})n+=cancel_owner(p,uid);return n;
  }
  unsigned pending()const{unsigned n=0;for(const auto&s:slots_)n+=s.live;return n;}
  unsigned queued()const{unsigned n=0;for(const auto&h:heads_)n+=h.active;return n;}
  bool producer_active(unsigned p)const {
    for(const auto&h:heads_)if(h.active&&h.identity.producer==p)return true;return false;
  }
  bool producer_selected(unsigned p)const {
    for(const auto&s:slots_)if(s.live&&s.identity.producer==p)return true;return false;
  }
  unsigned lanes()const{return lanes_;}
  const counters&stats()const{return stats_;}
  static unsigned merged_count(unsigned count,unsigned cap,const int*d,unsigned n,unsigned k) {
    if((k!=1&&k!=2)||n>k||cap>128||count>cap)throw std::invalid_argument("count contract");
    int value=count;for(unsigned i=0;i<n;++i){if(d[i]<-1||d[i]>1)throw std::invalid_argument("delta");
      value+=d[i];if(value<0||value>int(cap))throw std::overflow_error("ordered quota block");}
    return unsigned(value);
  }
 private:
  struct head{bool active=false,eligible=false,selected=false;key identity;};
  struct slot{bool live=false;unsigned head=6;key identity;};
  unsigned lanes_,rr_=0;
  std::array<head,6>heads_;
  std::array<slot,2>slots_;
  std::uint64_t observed_tick_=0,read_tick_=~std::uint64_t(0),last_commit_tick_=~std::uint64_t(0);
  counters stats_;
};
#endif
