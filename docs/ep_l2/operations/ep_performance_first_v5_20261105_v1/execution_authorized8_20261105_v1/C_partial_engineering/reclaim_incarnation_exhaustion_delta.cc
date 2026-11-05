#include "ep-l2-tvd-directory.h"
#include <limits>
#include <cstdio>
int main() {
 using D=ep_l2_tvd_directory<>;D d(2,true,true,2);D::ticket t;
 auto install=d.preview_install(0,false);
 auto result=d.commit_install(install,0,ep_l2::PayloadHandle(4,7),1,0,0,false,0,t);
 if(result!=D::OK)return 10;
 auto prepared=d.preview_reserved_reclaim(t);
 // Test-only force the boundary reached after UINT64_MAX row incarnations.
 auto&e=const_cast<D::entry&>(d.at(t.index));e.incarnation=std::numeric_limits<unsigned long long>::max();
 D::ticket exhausted(t.index,e.incarnation);
 bool read_refused=false;try{d.preview_reserved_reclaim(exhausted);}catch(const std::overflow_error&){read_refused=true;}
 if(!read_refused||d.clean_occupancy()!=1||d.at(t.index).status!=D::CLEAN)return 11;
 prepared.source=exhausted;ep_l2::PayloadHandle released;
 bool commit_refused=false;try{d.commit_reserved_reclaim(prepared,released,1);}catch(const std::overflow_error&){commit_refused=true;}
 if(!commit_refused||d.clean_occupancy()!=1||d.at(t.index).status!=D::CLEAN||released.valid())return 12;
 puts("PASS incarnation_exhaustion_before_READ_and_COMMIT_no_partial_count_drop");
}
