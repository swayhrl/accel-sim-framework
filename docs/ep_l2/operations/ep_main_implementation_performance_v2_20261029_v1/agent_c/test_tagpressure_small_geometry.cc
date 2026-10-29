#include "ep-l2-tagpressure-diag.h"
#include "ep-l2-detach-diag.h"
#include <cassert>
#include <memory>
#include <cstdio>
using namespace ep_l2_tagpressure;
void check(unsigned sets,unsigned ways,bool expected){
 int cache=1;snapshot s;s.cache_identity=&cache;s.slice=2;s.physical_cycle=11;s.request_uid=99;s.sets=sets;s.assoc=ways;s.raw=s.raw_r4=3;s.requester=NONRO_NATIVE_PATH;s.ro_runtime=true;s.T=false;
 for(unsigned i=0;i<ways;++i){s.ways[i].kind=RESERVED_WAY;s.ways[i].live=true;s.ways[i].attached=true;s.ways[i].required=1;}
 auto p=std::unique_ptr<phase_counts>(new phase_counts);p->observe(s,&cache,2,11,99);
 if(!expected){assert(p->invalid&&!p->basic_closure());return;}
 assert(!p->invalid&&p->basic_closure()&&p->heads_raw_reserved_eligible[(3*W+ways)*W+ways]==1);
 auto table=std::unique_ptr<route_joint_table>(new route_joint_table);table->record(2,1,&cache,11,99,s,NOT_CONSULTED,false,0);assert(!table->invalid&&table->rows==1);
 // Same T-independent captured state, T=true, same joint cell/count.
 s.T=true;table->record(2,1,&cache,11,99,s,NOT_CONSULTED,false,0);assert(table->rows==1);
 bool found=false;for(const auto&v:table->slots)if(v.key){auto a=route_joint_table::decode(v.key);assert(a[0]==2&&a[1]==1&&a[2]==3&&a[3]==ways&&a[4]==NONRO_NATIVE_PATH&&a[5]==2&&v.count==2);found=true;}assert(found);
 for(unsigned r=ways+1;r<W;++r)for(unsigned raw=0;raw<RAW;++raw)assert(p->heads_raw_reserved[raw*W+r]==0);
 // Repeated snapshot/preview does not write a ledger; actual callback gates once.
 ep_l2_detach_diag::ledger ledger;unsigned committed=0;for(unsigned i=0;i<4;++i)if(ledger.once(11,99))++committed;assert(committed==1);assert(ledger.once(12,99));
 auto mismatch=std::unique_ptr<phase_counts>(new phase_counts);mismatch->observe(s,&cache,2,11,98);assert(mismatch->invalid);
 // Positive predicate population excludes ready-only, reused, detached, and nonlive.
 s.ways[0].ready=1;if(ways>1)s.ways[1].reuse=true;if(ways>2)s.ways[2].attached=false;if(ways>3)s.ways[3].live=false;
 auto negative=std::unique_ptr<phase_counts>(new phase_counts);negative->observe(s,&cache,2,11,99);assert(negative->basic_closure());assert(negative->heads_raw_reserved_eligible[(3*W+ways)*W+(ways-4)]==1);
 auto reg=std::unique_ptr<registry>(new registry);legacy_view view;view.sets=sets;view.assoc=ways;view.runtime=true;FILE*f=std::tmpfile();assert(f);writer wire(f);reg->serialize(wire,"SLICE",2,-1,*p,view,11,1,true,true);assert(!wire.invalid);std::rewind(f);char prefix[2048]={};assert(std::fread(prefix,1,sizeof(prefix)-1,f)>0);std::fclose(f);
#ifdef ORIGINAL_SCOPE
 if(!(sets==64&&ways==16))assert(std::strstr(prefix,"EPL2_TAGPRESSURE_GEOMETRY_V1"));
#else
 if(!(sets==64&&ways==16))assert(std::strstr(prefix,"EPL2_TAGPRESSURE_GEOMETRY_V2_CANDIDATE"));
#endif
 std::printf("TP_GEOMETRY_PASS|sets=%u|ways=%u|T0_structural=1|T1_same_joint=1|once_headcycle=1|predicate_negative=1|snapshot_context_reject=1\n",sets,ways);
}
int main(){
#ifdef ORIGINAL_SCOPE
 check(16,8,false);check(32,4,false);check(32,8,true);check(64,16,true);
 std::puts("ORIGINAL_UNSUPPORTED16X8_32X4_CONFIRMED");
#else
 check(16,8,true);check(32,4,true);check(32,8,true);check(64,16,true);
 check(16,4,false);check(16,16,false);
#endif
 std::printf("TP_COUNTS_SIZE|phase=%zu|joint=%zu|registry=%zu|production_capture_hook_tested=0|application_NI=0\n",sizeof(phase_counts),sizeof(route_joint_table),sizeof(registry));
}
