#include "ep-l2-quota-row-port.h"
#include <cstdio>
int main(){
 ep_l2_quota_row_port p(2);
 using K=ep_l2_quota_row_port::key;
 K a(3,11,0,1,4,1,1),b(2,22,1,1,8,1,3),c(3,33,2,1,12,1,1);
 p.ready(a,1);p.ready(b,1);
 if(p.pending()!=2)return 10;
 if(p.cancel_owner(3,999)!=0||p.pending()!=2)return 11;
 if(p.cancel_owner(3,11)!=1||p.pending()!=1)return 12;
 if(p.stats().read_beats!=1)return 13;
 // K2 has already read two distinct rows in this READ beat. Cancellation
 // cannot manufacture a third physical directory read in the same beat.
 p.ready(c,1);
 if(p.pending()!=1)return 23;
 if(!p.ready(b,2))return 14;p.commit(b,2);
 if(p.pending()!=0)return 15;
 p.ready(c,2);if(p.pending()!=0)return 16;
 p.ready(c,3);if(p.pending()!=1||p.stats().read_beats!=2)return 17;
 if(!p.ready(c,4))return 18;p.commit(c,4);
 puts("PASS bounded_owner_cancel_peer_preserved_no_third_READ_no_beat_refund");
}
