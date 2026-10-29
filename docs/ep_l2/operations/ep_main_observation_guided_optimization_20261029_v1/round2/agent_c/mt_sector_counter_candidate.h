#ifndef EP_L2_MT_SECTOR_COUNTER_CANDIDATE_H
#define EP_L2_MT_SECTOR_COUNTER_CANDIDATE_H
#include <cstdint>
#include <limits>
// Engineering candidate only. No production hook or allocator. The caller
// passes the PRE-successful-merge snapshot after descriptor admission succeeds.
// A null pointer means OFF; no map, queue, Tag probe or address lookup exists.
namespace ep_l2_mt_candidate {
struct counters {
  uint64_t accepted_live_merge=0, requested_not_ready=0;
  uint64_t previously_required_not_ready=0, newly_required_not_ready=0;
  uint64_t requested_issued_not_ready=0, all_requested_ready=0;
  uint64_t ready_with_other_required_pending=0, ready_only_draining=0;
  uint64_t reuse_first=0, reuse_first_without_strict_pending_revisit=0;
  bool exact=true;
  void inc(uint64_t &v) { if(v==std::numeric_limits<uint64_t>::max())exact=false;else ++v; }
  void accepted(unsigned mask,unsigned required,unsigned issued,unsigned ready,bool reuse) {
    if(!mask || ((mask|required|issued|ready)&~15U)) { exact=false;return; }
    inc(accepted_live_merge);
    const unsigned pending=mask&~ready;
    const bool strict=(mask&required&~ready)!=0;
    if(pending)inc(requested_not_ready);
    if(strict)inc(previously_required_not_ready);
    if(mask&~required&~ready)inc(newly_required_not_ready);
    if(mask&issued&~ready)inc(requested_issued_not_ready);
    if(!pending){inc(all_requested_ready);if(required&~ready)inc(ready_with_other_required_pending);else inc(ready_only_draining);}
    if(!reuse){inc(reuse_first);if(!strict)inc(reuse_first_without_strict_pending_revisit);}
  }
};
inline void observe(counters *p,unsigned mask,unsigned required,unsigned issued,unsigned ready,bool reuse) {
  if(p)p->accepted(mask,required,issued,ready,reuse);
}
static_assert(sizeof(counters)<=128,"bounded scalar-only collector");
}
#endif
