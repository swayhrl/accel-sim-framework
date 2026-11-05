#include <cassert>
#include <cstdio>
#include "../../src/gpgpu-sim/ep-l2-quota-row-port.h"
using P=ep_l2_quota_row_port;
int main(){
  P::key a(1,5,0,1,5,7,2),b(2,6,1,2,6,8,3),c(1,7,2,3,7,9,2);
  for(unsigned k=1;k<=2;++k){
    P p(k);assert(!p.ready(a,1));assert(!p.ready(a,1));
    assert(p.stats().read_beats==1&&p.pending()==1);
    assert(!p.ready(b,1));
    if(k==2)assert(p.pending()==2);else assert(p.pending()==1);
    assert(!p.ready(c,1));assert(p.pending()==k);
    assert(p.ready(a,2));p.commit(a,2);
    if(k==2){assert(p.ready(b,2));p.commit(b,2);}
    assert(!p.ready(c,2));assert(p.pending()==0);
    assert(p.stats().commit_beats==1&&p.stats().acks==k);
    assert(!p.ready(c,3));assert(p.ready(c,7));p.commit(c,7);
    assert(p.pending()==0&&p.stats().read_beats==2&&p.stats().commit_beats==2);
    bool bad=false;try{p.commit(c,7);}catch(const std::logic_error&){bad=true;}assert(bad);
    printf("PASS K%u fixed_port_batch read=%llu commit=%llu acks=%llu\n",k,
      (unsigned long long)p.stats().read_beats,(unsigned long long)p.stats().commit_beats,
      (unsigned long long)p.stats().acks);
  }
  P p(2);assert(!p.ready(a,1));
  auto same=a;same.uid=9;assert(!p.ready(same,1));
  assert(p.stats().row_conflicts==1&&p.pending()==1);
  assert(p.cancel(a));assert(!p.ready(b,1)&&p.pending()==0);
  assert(!p.ready(b,2)&&p.pending()==1);
  assert(p.ready(b,3));assert(p.ready(b,3));assert(p.pending()==1);
  p.commit(b,3);assert(p.pending()==0);
  int d[2]={-1,1};assert(P::merged_count(64,64,d,2,2)==64);
  int z[2]={0,0};assert(P::merged_count(64,64,z,2,2)==64);
  int up[2]={1,1};bool bad=false;try{P::merged_count(63,64,up,2,2);}catch(...){bad=true;}assert(bad);
  bad=false;int rev[2]={1,-1};try{P::merged_count(64,64,rev,2,2);}catch(...){bad=true;}assert(bad);
  auto other=b;other.generation++;bad=false;try{p.commit(other,3);}catch(...){bad=true;}assert(bad);
  puts("PASS same_row_conflict cancel_no_refund repeated_DRAM_poll delta_order identity_no_steal");
}
