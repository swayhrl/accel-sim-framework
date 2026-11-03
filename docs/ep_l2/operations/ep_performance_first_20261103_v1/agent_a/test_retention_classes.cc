#include "ep-l2-tvd-directory.h"
#include <iostream>
using H=ep_l2::PayloadHandle;using D=ep_l2_tvd_directory<>;
int main(){for(unsigned clean=0;clean<2;clean++)for(unsigned dirty=0;dirty<2;dirty++){
 D d(2,clean,dirty);D::ticket c,w;auto q=d.preview_install(128,false);
 if(clean){assert(q.status==D::OK);assert(d.commit_install(q,128,H(0,1),15,0,0,false,1,c)==D::OK);}else assert(q.status==D::DISABLED);
 q=d.preview_install(256,true);assert(q.status==D::OK);H retained=dirty?H(1,1):H();
 assert(d.commit_install(q,256,retained,15,15,0,true,2,w)==D::OK);assert(d.mandatory()==1);
 H h;assert(d.reclaim(w,h,2)==D::WAIT_WRITEBACK);assert(d.bind_writeback(w,9)==D::OK);assert(d.lower_accept(w,true,3)==D::OK);assert(d.set_done(w,4)==D::OK);
 if(dirty){assert(d.live(w)&&d.at(w.index).status==D::WB_COMPLETE);assert(d.reclaim(w,h,4)==D::OK&&h==retained);}else assert(!d.live(w));
 if(clean)assert(d.reclaim(c,h,4)==D::OK&&h==H(0,1));
 assert(d.occupied()==0&&d.mandatory()==0&&d.epoch_ready());
 std::cout<<"RETENTION_CLASS_PASS clean="<<clean<<" dirty="<<dirty<<" mandatory_preserved=1 drain=1\n";
}}
