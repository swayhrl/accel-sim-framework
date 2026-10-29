#include "t_joint_counter_reference.h"
#include <cassert>
#include <cstdio>
using namespace ep_t_joint;
int main(){
 key k{7,2,100,3,4};counter off;off.probe(k,true,true,YES);off.preview(k,true);off.detach(k);off.accept(k);off.complete(k);assert(off.get().raw_full_events==0);
 counter c(true);c.probe(k,true,true,YES);c.probe(k,true,true,YES);c.preview(k,true);c.preview(k,true);c.detach(k);c.detach(k);c.accept(k);c.accept(k);c.complete(k);assert(c.get().raw_full_events==1&&c.get().joint_yes_events==1&&c.get().actual_detach_events==1&&c.get().completed==1);
 key unknown{7,2,101,3,4};c.probe(unknown,true,true,UNKNOWN);c.preview(unknown,false);assert(c.get().joint_unknown_events==1&&c.get().preview_deny_events==1);
 key diff=unknown;diff.tick++;c.preview(diff,true);diff=unknown;diff.set++;c.detach(diff);diff=unknown;diff.request_generation++;c.accept(diff);assert(c.get().unmatched==3);
 key nonordinary{99,1,1,1,1};c.probe(nonordinary,false,true,YES);c.probe(nonordinary,true,false,YES);assert(c.get().raw_full_events==2);
 c.abandon(unknown);counter saturated(true);for(unsigned i=0;i<65;++i)saturated.probe(key{i,0,1,0,0},true,true,NO);assert(saturated.get().raw_full_events==64&&saturated.get().overflow==1&&saturated.get().joint_no_events==64);
 std::printf("T_JOINT_REFERENCE_PASS|sizeof=%zu|defaultOFF=1|repeat_idempotent=1|same_uid_generation_tick_set=1|overflow_explicit=1|production_hook=0|application_NI=0\n",sizeof(counter));
}
