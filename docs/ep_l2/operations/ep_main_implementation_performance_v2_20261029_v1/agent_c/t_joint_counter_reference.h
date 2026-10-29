// Notification-only engineering reference. NOT wired into simulator; default OFF.
#ifndef EP_T_JOINT_COUNTER_REFERENCE_H
#define EP_T_JOINT_COUNTER_REFERENCE_H
#include <array>
#include <cstdint>
namespace ep_t_joint {
enum eligibility { UNKNOWN=0, NO=1, YES=2 };
struct key { uint64_t uid,request_generation,tick;unsigned slice,set;bool operator==(const key&o)const{return uid==o.uid&&request_generation==o.request_generation&&tick==o.tick&&slice==o.slice&&set==o.set;} };
struct stats { uint64_t raw_full_events=0,joint_yes_events=0,joint_no_events=0,joint_unknown_events=0,preview_allow_events=0,preview_deny_events=0,actual_detach_events=0,accepted=0,completed=0,unmatched=0,overflow=0; };
struct slot { key k{};bool live=false,raw_full=false,preview_seen=false,detached=false,accepted=false;eligibility structural=UNKNOWN; };
class counter {
 bool enabled_;std::array<slot,64>slots_{};stats st_{};
 slot* find(key k){for(auto&s:slots_)if(s.live&&s.k==k)return &s;return nullptr;}
 public:
 explicit counter(bool enabled=false):enabled_(enabled){}
 const stats& get()const{return st_;}
 void probe(key k,bool ordinary,bool raw_full,eligibility e){
  if(!enabled_||!ordinary||!raw_full)return;
  // Production must pass an already-computed condition; no probes/scans here.
  // One slot per exact request-attempt tick. Repeated preview is idempotent.
  if(find(k))return;
  slot*p=nullptr;for(auto&s:slots_)if(!s.live){p=&s;break;}
  if(!p){++st_.overflow;return;}*p=slot{};p->live=true;p->k=k;p->raw_full=true;p->structural=e;
  ++st_.raw_full_events;if(e==YES)++st_.joint_yes_events;else if(e==NO)++st_.joint_no_events;else ++st_.joint_unknown_events;
 }
 void preview(key k,bool allow){if(!enabled_)return;auto*p=find(k);if(!p){++st_.unmatched;return;}if(p->preview_seen)return;p->preview_seen=true;if(allow)++st_.preview_allow_events;else ++st_.preview_deny_events;}
 void detach(key k){if(!enabled_)return;auto*p=find(k);if(!p){++st_.unmatched;return;}if(!p->detached){p->detached=true;++st_.actual_detach_events;}}
 void accept(key k){if(!enabled_)return;auto*p=find(k);if(!p){++st_.unmatched;return;}if(!p->accepted){p->accepted=true;++st_.accepted;}}
 void complete(key k){if(!enabled_)return;auto*p=find(k);if(!p||!p->accepted){++st_.unmatched;return;}++st_.completed;p->live=false;}
 void abandon(key k){if(!enabled_)return;auto*p=find(k);if(p)p->live=false;}
};
}
#endif
