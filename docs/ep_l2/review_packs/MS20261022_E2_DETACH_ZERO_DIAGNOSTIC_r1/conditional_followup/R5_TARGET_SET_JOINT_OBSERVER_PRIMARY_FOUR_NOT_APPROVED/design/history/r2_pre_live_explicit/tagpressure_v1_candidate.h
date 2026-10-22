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
enum requester_kind { CERTIFIED_RO_CANDIDATE, NONRO_NATIVE_PATH, RUNTIME_OFF };
enum way_kind { RESERVED_WAY, INVALID_WAY, REPLACEABLE_CLEAN, REPLACEABLE_DIRTY };
// Original raw enum 0..WRITE_ALLOCATED maps identically; all other -> UNKNOWN.
// Wire schema supplies explicit raw labels; no integer enum inference by consumer.
enum reason_bit { HAS_ELIGIBLE=1, HAS_NOT_ATTACHED=2, HAS_REUSE=4,
                  HAS_NO_MISSING=8, HAS_NO_LIVE=16 };
struct way {way_kind kind=INVALID_WAY;bool live=false,attached=false,reuse=false;
            unsigned required=0,ready=0;};
struct snapshot {
 const void*cache_identity=nullptr;unsigned slice=~0U;
 uint64_t physical_cycle=~uint64_t(0),request_uid=~uint64_t(0);
 unsigned assoc=0,raw=RAW-1,raw_r4=RAW-1;
 unsigned requester=RUNTIME_OFF; // copy existing r4 runtime/candidate booleans
 bool ro_runtime=false,T=false; // per slice config; never changes a decision
 std::array<way,16> ways{};
};
inline bool context_matches(const snapshot&s,const void*cache,unsigned slice,
                            uint64_t cycle,uint64_t uid){
 return cache&&s.cache_identity==cache&&s.slice==slice&&
        s.physical_cycle==cycle&&s.request_uid==uid;
}
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
 // Live predicate masks are (attached?1:0)|(reuse?2:0)|(missing?4:0).
 // They describe physical state even when T=false; operational eligibility
 // is separately T && structural mask==5. Runtime-off is NA, NOT no-live.
 static void checked(uint64_t&v,uint64_t n,bool&bad){
  if(n>std::numeric_limits<uint64_t>::max()-v){bad=true;return;}v+=n;
 }
 void add(uint64_t&v,uint64_t n=1){checked(v,n,invalid);}
 void observe(const snapshot&s,const void*cache,unsigned slice,uint64_t cycle,uint64_t uid){
  if(!context_matches(s,cache,slice,cycle,uid)||s.assoc!=16||s.raw>=RAW||s.raw!=s.raw_r4||s.requester>RUNTIME_OFF||(!s.ro_runtime)!=(s.requester==RUNTIME_OFF)){invalid=true;return;}
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
  }else add(ro_na);
  for(unsigned i=0;i<s.assoc;++i){const auto&w=s.ways[i];
   add(ways_raw_reserved_class[k*4+unsigned(w.kind)]);
   if(s.ro_runtime&&w.live){unsigned m=(w.attached?1:0)|(w.reuse?2:0)|((w.required&~w.ready)?4:0);
    add(ways_raw_reserved_predmask[k*PRED+m]);}
  }
 }
 bool basic_closure()const{
  uint64_t h=0,e=0,m=0,cl=0,iv=0,ro=0;bool bad=invalid;
  for(auto n:heads_raw_reserved)checked(h,n,bad);
  for(auto n:heads_raw_reserved_eligible)checked(e,n,bad);
  for(auto n:heads_raw_reserved_reasonmask)checked(m,n,bad);
  for(auto n:ways_raw_reserved_class)checked(cl,n,bad);
  for(auto n:heads_raw_reserved_invalid)checked(iv,n,bad);
  checked(ro,ro_observed,bad);checked(ro,ro_na,bad);
  if(covered>std::numeric_limits<uint64_t>::max()/16)bad=true;
  return !bad&&h==covered&&covered==ro&&e==ro_observed&&m==ro_observed&&cl==covered*16&&iv==covered;
 }
};
// One bounded, exact sparse joint shared by ALL64 slices/18 phases. This is
// observer metadata, not a second controller/authority/model port. No request log.
// Empty slot key0; nonempty stores packed key+1 and a checked uint64 head count.
// Key has slice6|phase5|raw3|reserved5|requester2|eligibility2|route3|admit1|early3.
// eligibility:0=NA(runtime off),1=no structural eligible,2=has eligible.
// Full tuple is preserved; no marginals are used to assign requester or gate.
struct route_joint_table {
 static constexpr unsigned SLOTS=131072, MAX_ROWS=65536;
 struct slot {uint64_t key=0,count=0;};
 std::array<slot,SLOTS> slots{};unsigned rows=0;bool invalid=false;
 void record(unsigned slice,unsigned phase,const void*cache,uint64_t cycle,
             uint64_t uid,const snapshot&s,unsigned production_route,bool admitted,unsigned early){
  if(!context_matches(s,cache,slice,cycle,uid)||slice>=64||phase>=18||s.assoc!=16||s.raw>=RAW||s.raw!=s.raw_r4||
     s.requester>RUNTIME_OFF||(!s.ro_runtime)!=(s.requester==RUNTIME_OFF)||
     production_route>=6||early>=6){invalid=true;return;}
  unsigned r=0;bool eligible=false;
  for(unsigned i=0;i<16;++i){const auto&w=s.ways[i];
   if(unsigned(w.kind)>3){invalid=true;return;}
   r+=w.kind==RESERVED_WAY;
   eligible|=w.live&&w.attached&&!w.reuse&&(w.required&~w.ready);
  }
  unsigned e=!s.ro_runtime?0:eligible?2:1;
  uint64_t key=slice;
  key=(key<<5)|phase;key=(key<<3)|s.raw;key=(key<<5)|r;
  key=(key<<2)|s.requester;key=(key<<2)|e;
  key=(key<<3)|production_route;key=(key<<1)|unsigned(admitted);
  key=(key<<3)|early;++key;
  unsigned at=unsigned((key*11400714819323198485ull)>>(64-17));
  for(unsigned n=0;n<SLOTS;++n,at=(at+1)&(SLOTS-1)){
   auto&v=slots[at];
   if(v.key==key){phase_counts::checked(v.count,1,invalid);return;}
   if(!v.key){if(rows==MAX_ROWS){invalid=true;return;}
    v.key=key;v.count=1;++rows;return;}
  }
  invalid=true; // capacity/overflow is explicit invalid, never sampling/drop-zero
 }
};
// No static instance/global allocation in this design header. Producer must
// bind lifecycle/64-slice/18-phase registry to existing r4 ledger, reject overflow,
// and implement full wire-schema equations, not just basic_closure().
// The route_joint_table must be called in the SAME once-admitted frontend hook.
// Its row-cap/overflow invalid flag is included in every final r5 acceptance.
}
#endif
