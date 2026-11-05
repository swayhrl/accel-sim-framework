#pragma once
#include <cstdint>
#include <limits>
// Accurate bounded serial row-read engineering schedule around actual directory.
// Not wired into frontend/allocator. One row inspect/comparator per cycle,
// capacity cycles to scan, then one distinct update-lane commit cycle.
template<class Directory> class reclaim_scheduler {
 public:
  enum result { IDLE, BUSY, WAIT_SELECTION, WAIT_PORT, STALE, PINNED, DONE };
  typedef typename Directory::ticket ticket;
  ticket selected;
  unsigned bank=4,cursor=0;
  std::uint64_t last_port=std::numeric_limits<std::uint64_t>::max(),selected_age=0;
  bool pending=false,scanning=false,unified=true,selected_clean=false;
  result issue(const Directory &,unsigned b,std::uint64_t now,bool unified_lru) {
    if(pending)return BUSY;
    if(last_port==now)return WAIT_PORT;
    selected=ticket();bank=b;cursor=0;pending=scanning=true;unified=unified_lru;
    last_port=now;return WAIT_SELECTION;
  }
  result scan(const Directory &d,std::uint64_t now,bool row_read_lane_free) {
    if(!pending)return IDLE;
    if(!scanning)return WAIT_SELECTION;
    if(!row_read_lane_free || last_port==now)return WAIT_PORT;
    last_port=now;const auto &e=d.at(cursor);
    if(e.reclaimable() && e.payload.valid() &&
        (bank==4 || e.payload.payload_id%4==bank)) {
      const bool clean=e.status==Directory::CLEAN;
      if(selected.index==128 || (!unified && clean && !selected_clean) ||
          ((unified || clean==selected_clean) && e.age<selected_age)) {
        selected=ticket(cursor,e.incarnation);selected_age=e.age;selected_clean=clean;
      }
    }
    if(++cursor==d.capacity()) {
      scanning=false;
      if(selected.index==128){pending=false;return IDLE;}
    }
    return WAIT_SELECTION;
  }
  template<class Handle> result commit_to(Directory &d,std::uint64_t now,
                       bool update_port_free,Handle &released) {
    if(!pending)return IDLE;
    if(scanning)return WAIT_SELECTION;
    if(!update_port_free || last_port==now)return WAIT_PORT;
    last_port=now;
    if(!d.live(selected)){pending=false;return STALE;}
    const auto &e=d.at(selected.index);
    if(!e.reclaimable() || !e.payload.valid() ||
        (bank!=4 && e.payload.payload_id%4!=bank)){pending=false;return PINNED;}
    if(e.age!=selected_age){pending=false;return STALE;}
    const auto r=d.reclaim(selected,released,now);pending=false;
    return r==Directory::OK?DONE:STALE;
  }
};
