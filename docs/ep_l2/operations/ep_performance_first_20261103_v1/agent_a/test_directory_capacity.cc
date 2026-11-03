#include "ep-l2-tvd-directory.h"
#include <iostream>
#include <vector>
using H=ep_l2::PayloadHandle;
using D=ep_l2_tvd_directory<>;
int main(){
 D d(2,true,true); D::ticket a,b,c; auto pa=d.preview_install(128,false);
 assert(pa.status==D::OK);assert(d.occupied()==0);
 assert(d.commit_install(pa,128,H(0,1),15,0,0,false,1,a)==D::OK);
 auto pb=d.preview_install(256,true);assert(d.commit_install(pb,256,H(1,1),15,15,0,true,2,b)==D::OK);
 assert(d.mandatory()==1); H h;
 assert(d.reclaim(b,h,3)==D::WAIT_WRITEBACK);
 auto obs=d.preview_ticket(a,1,D::READ_OP);D::read_lease lease;
 assert(d.begin_read(obs,1,lease)==D::OK);
 auto full=d.preview_install(384,true);assert(full.status==D::DIRECTORY_FULL);
 assert(d.reclaim(a,h,3)==D::PINNED);
 assert(d.cancel_read(lease)==D::OK);
 auto pc=d.preview_install(384,true);assert(pc.status==D::OK);
 auto again=d.preview_install(384,true);assert(pc.index==again.index&&pc.revision==again.revision);
 assert(d.bind_writeback(b,7)==D::OK);assert(d.lower_accept(b,false,3)==D::DATA_TRANSFER_UNPROVEN);
 assert(d.lower_accept(b,true,3)==D::OK);assert(d.set_done(b,4)==D::OK);
 assert(d.commit_install(pc,384,H(2,1),15,15,0,true,4,c)==D::STALE);
 pc=d.preview_install(384,true);assert(pc.status==D::OK&&pc.displaced==H(0,1));
 assert(d.commit_install(pc,384,H(2,1),15,15,0,true,4,c)==D::OK);
 assert(!d.live(a)&&d.reclaim(a,h,5)==D::STALE);
 assert(d.rollback_staged(c,5)==D::OK);assert(d.reclaim(b,h,5)==D::OK);assert(d.occupied()==0&&d.epoch_ready());
 std::cout<<"BASELINE_SEQUENCE_PASS cap=2 clean=1 dirty=2 cancelled=1 complete=1 stale_protected=1 drain=1\n";
#ifdef EXTENDED
 using E=ep_l2_tvd_directory<H,256>;E e(256,true,true,128);std::vector<E::ticket> ws,cs;
 for(unsigned i=0;i<128;i++){auto q=e.preview_install((i+1)*128,true);E::ticket t;assert(q.status==E::OK);assert(e.commit_install(q,(i+1)*128,H(i,1),15,15,0,true,i,t)==E::OK);ws.push_back(t);}
 assert(e.mandatory()==128&&e.occupied()==128);
 assert(e.preview_install(129*128,true).status==E::DIRECTORY_FULL);
 for(unsigned i=128;i<256;i++){auto q=e.preview_install((i+1)*128,false);E::ticket t;assert(q.status==E::OK);assert(e.commit_install(q,(i+1)*128,H(i,1),15,0,0,false,i,t)==E::OK);cs.push_back(t);}
 assert(e.occupied()==256&&e.mandatory()==128);
 assert(e.preview_install(257*128,true).status==E::DIRECTORY_FULL);
 assert(e.bind_writeback(ws[0],99)==E::OK);assert(e.lower_accept(ws[0],true,300)==E::OK);assert(e.set_done(ws[0],301)==E::OK);
 auto q=e.preview_install(257*128,true);E::ticket last;assert(q.status==E::OK);assert(q.index>=128);
 assert(e.commit_install(q,257*128,H(256,1),15,15,0,true,302,last)==E::OK);assert(e.mandatory()==128);
 assert(e.preview_dirty_promotion(cs[1],258*128,H(257,1),15,15,0).status==E::DIRECTORY_FULL);
 assert(e.rollback_staged(last,303)==E::OK);
 for(unsigned i=1;i<ws.size();i++)assert(e.rollback_staged(ws[i],303)==E::OK);
 assert(e.reclaim(ws[0],h,303)==E::OK);
 for(unsigned i=1;i<cs.size();i++)assert(e.reclaim(cs[i],h,303)==E::OK);
 assert(e.occupied()==0&&e.epoch_ready());
 bool threw=false;try{E invalid(256,true,true,257);}catch(const std::invalid_argument&){threw=true;}assert(threw);
 std::cout<<"EXTENDED_SEQUENCE_PASS entries=256 mandatory_max=128 optional_extra=128 generation=1 preview_pure=1 promotion_cap=1 drain=1 sizeof_entry="<<sizeof(E::entry)<<"\n";
#endif
}
