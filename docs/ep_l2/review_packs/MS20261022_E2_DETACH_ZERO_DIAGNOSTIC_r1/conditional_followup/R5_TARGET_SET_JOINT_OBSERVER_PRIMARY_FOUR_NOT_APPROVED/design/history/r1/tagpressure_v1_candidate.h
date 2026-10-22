#ifndef EPL2_TAGPRESSURE_V1_CANDIDATE_H
#define EPL2_TAGPRESSURE_V1_CANDIDATE_H
// DESIGN CANDIDATE ONLY. Not compiled, deployed, or production-qualified.
// All inputs below must be captured before preview/admission at the SAME
// pre-existing r4 observer probe. This reducer cannot query/mutate the model.
#include <array>
#include <cstdint>
#include <limits>
namespace epl2_tagpressure_v1 {
constexpr unsigned RAW=8, W=17, MASK=32, PRED=8;
enum way_kind { RESERVED_WAY, INVALID_WAY, REPLACEABLE_CLEAN, REPLACEABLE_DIRTY };
// Original raw enum 0..WRITE_ALLOCATED maps identically; all other -> UNKNOWN.
// Wire schema supplies explicit raw labels; no integer enum inference by consumer.
enum reason_bit { HAS_ELIGIBLE=1, HAS_NOT_ATTACHED=2, HAS_REUSE=4,
                  HAS_NO_MISSING=8, HAS_NO_LIVE=16 };
struct way {way_kind kind=INVALID_WAY;bool live=false,attached=false,reuse=false;
            unsigned required=0,ready=0;};
struct snapshot {
 unsigned assoc=0,raw=RAW-1,raw_r4=RAW-1;
 bool ro_runtime=false,T=false; // per slice config; never changes a decision
 std::array<way,16> ways{};
};
enum route { PROD_NOT_REACHED, NOT_CONSULTED, CONSULTED_MISS, CONSULTED_FAIL, EXISTING_HIT_RESERVED, ROUTE_OTHER };
struct phase_counts {
 // Keep PHASE counters only; SLICE/GLOBAL totals are exact reductions of these.
 uint64_t covered=0, skipped[4]={}, absent=0, ro_observed=0,ro_na=0;
 bool invalid=false;
 std::array<uint64_t,RAW*W> heads_raw_reserved{};
 std::array<uint64_t,RAW*W*W> heads_raw_reserved_eligible{};
 std::array<uint64_t,RAW*W*MASK> heads_raw_reserved_reasonmask{};
 std::array<uint64_t,RAW*W*PRED> ways_raw_reserved_predmask{};
 std::array<uint64_t,RAW*W*4> ways_raw_reserved_class{};
 std::array<uint64_t,RAW*W*W> heads_raw_reserved_invalid{};
 // Real same-head route/admission capture, runtime present only.
 std::array<uint64_t,RAW*W*2*6*2> heads_raw_reserved_eligible_route_admit{};
 std::array<uint64_t,RAW*W*2*6> heads_raw_reserved_eligible_early{};
 // Live predicate masks are (attached?1:0)|(reuse?2:0)|(missing?4:0).
 // They describe physical state even when T=false; operational eligibility
 // is separately T && structural mask==5. Runtime-off is NA, NOT no-live.
 static void checked(uint64_t&v,uint64_t n,bool&bad){
  if(n>std::numeric_limits<uint64_t>::max()-v){bad=true;return;}v+=n;
 }
 void add(uint64_t&v,uint64_t n=1){checked(v,n,invalid);}
 void observe(const snapshot&s,unsigned production_route,bool admitted,unsigned early){
  if(s.assoc!=16||s.raw>=RAW||s.raw!=s.raw_r4||production_route>=6||early>=6){invalid=true;return;}
  unsigned r=0,ni=0,eligible=0,reasons=0;
  for(unsigned i=0;i<s.assoc;++i){
   const auto&w=s.ways[i]; if(unsigned(w.kind)>3){invalid=true;return;}
   r+=w.kind==RESERVED_WAY;ni+=w.kind==INVALID_WAY;
   if(!s.ro_runtime)continue;
   if(!w.live){reasons|=HAS_NO_LIVE;continue;}
   // Keep reasons independently, not priority masked: reuse+noMissing coexists.
   if(!w.attached)reasons|=HAS_NOT_ATTACHED;
   if(w.reuse)reasons|=HAS_REUSE;
   if(!(w.required&~w.ready))reasons|=HAS_NO_MISSING;
   if(w.attached&&!w.reuse&&(w.required&~w.ready)){
    reasons|=HAS_ELIGIBLE;++eligible;
   }
  }
  add(covered);const unsigned k=s.raw*W+r;
  add(heads_raw_reserved[k]);add(heads_raw_reserved_invalid[k*W+ni]);
  if(s.ro_runtime){add(ro_observed);add(heads_raw_reserved_eligible[k*W+eligible]);
   add(heads_raw_reserved_reasonmask[k*MASK+reasons]);
   add(heads_raw_reserved_eligible_route_admit[((k*2+bool(eligible))*6+production_route)*2+admitted]);
   add(heads_raw_reserved_eligible_early[(k*2+bool(eligible))*6+early]);
  }else add(ro_na);
  for(unsigned i=0;i<s.assoc;++i){const auto&w=s.ways[i];
   add(ways_raw_reserved_class[k*4+unsigned(w.kind)]);
   if(s.ro_runtime&&w.live){unsigned m=(w.attached?1:0)|(w.reuse?2:0)|((w.required&~w.ready)?4:0);
    add(ways_raw_reserved_predmask[k*PRED+m]);}
  }
 }
 bool basic_closure()const{
  uint64_t h=0,e=0,m=0,cl=0,iv=0;
  for(auto n:heads_raw_reserved)h+=n;
  for(auto n:heads_raw_reserved_eligible)e+=n;
  for(auto n:heads_raw_reserved_reasonmask)m+=n;
  for(auto n:ways_raw_reserved_class)cl+=n;
  for(auto n:heads_raw_reserved_invalid)iv+=n;
  return !invalid&&h==covered&&covered==ro_observed+ro_na&&e==ro_observed&&m==ro_observed&&cl==covered*16&&iv==covered;
 }
};
// No static instance/global allocation in this design header. Producer must
// bind lifecycle/64-slice/18-phase registry to existing r4 ledger, reject overflow,
// and implement full wire-schema equations, not just basic_closure().
}
#endif
