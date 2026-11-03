#include "ep-l2-tvd-directory.h"
#include <cassert>
#include <vector>
#include <iostream>
using D=ep_l2_tvd_directory<>;using H=ep_l2::PayloadHandle;
D::ticket put(D &d,unsigned line,unsigned id,bool dirty,unsigned now){auto p=d.preview_install(line*128ull,dirty);assert(p.status==D::OK);D::ticket t;assert(d.commit_install(p,line*128ull,H(id,1),15,dirty?15:0,0,dirty,now,t)==D::OK);return t;}
void audit(const D &d){unsigned clean=0;for(unsigned i=0;i<d.capacity();i++)clean+=d.at(i).status==D::CLEAN;assert(clean==d.clean_occupancy()&&clean<=d.clean_limit());}
int main(){
 for(unsigned limit: {0u,1u,2u,3u}){
  D d(3,true,true,limit);auto w=put(d,1,1,true,1);assert(d.bind_writeback(w,99)==D::OK);assert(d.lower_accept(w,false,2)==D::DATA_TRANSFER_UNPROVEN);assert(d.lower_accept(w,true,2)==D::OK);assert(d.set_done(w,3)==D::OK);audit(d);
  if(!limit){assert(d.preview_install(256,false).status==D::DISABLED);H h;assert(d.reclaim(w,h,4)==D::OK);assert(d.epoch_ready());continue;}
  auto c=put(d,2,2,false,4);auto plan=d.preview_install(384,false);auto again=d.preview_install(384,false);assert(plan.index==again.index&&plan.revision==again.revision);assert(d.clean_occupancy()==1);
  if(limit==1){assert(plan.index==c.index&&plan.displaced==H(2,1));assert(d.occupied()==2);D::read_lease pin;auto o=d.preview_ticket(c,1,D::READ_OP);assert(d.begin_read(o,1,pin)==D::OK);assert(d.preview_install(384,false).status==D::DIRECTORY_FULL);auto m=put(d,4,4,true,5);assert(d.mandatory()==1);assert(d.reclaim(m,plan.displaced,5)==D::WAIT_WRITEBACK);assert(d.rollback_staged(m,5)==D::OK);assert(d.cancel_read(pin)==D::OK);auto z=put(d,3,3,false,6);assert(z.index==c.index&&!d.live(c)&&d.live(w));audit(d);H h;assert(d.reclaim(z,h,7)==D::OK);assert(d.reclaim(w,h,7)==D::OK);assert(d.epoch_ready()&&!d.occupied());}
  else{auto c2=put(d,3,3,false,5);audit(d);auto pp=d.preview_dirty_promotion(c,4*128ull,H(4,1),15,15,0);assert(pp.status==D::OK);H moved;D::ticket ww;assert(d.commit_dirty_promotion(pp,6,moved,ww)==D::OK&&moved==H(2,1));assert(!d.live(c)&&d.clean_occupancy()==1);audit(d);assert(d.rollback_staged(ww,7)==D::OK);H h;assert(d.reclaim(c2,h,7)==D::OK);assert(d.reclaim(w,h,7)==D::OK);assert(d.epoch_ready()&&!d.occupied());}
 }
 for(unsigned limit:{0u,32u,64u,96u,128u}){D d(128,true,true,limit);std::vector<D::ticket> w;for(unsigned i=0;i<128;i++)w.push_back(put(d,i+1,i,true,i+1));assert(d.mandatory()==128&&d.preview_install(129*128ull,true).status==D::DIRECTORY_FULL);audit(d);for(auto t:w)assert(d.rollback_staged(t,129)==D::OK);assert(d.epoch_ready()&&!d.occupied());}
 bool bad=false;try{D d(128,true,true,129);}catch(const std::invalid_argument&){bad=true;}assert(bad);
 std::cout<<"CLEAN_QUOTA_COMPONENT|limits=0,1,2,3,32,64,96,128|mandatory128=PASS|pin=PASS|generation=PASS|promotion_count=PASS|preview_pure=PASS|full_drain=PASS\n";
}
