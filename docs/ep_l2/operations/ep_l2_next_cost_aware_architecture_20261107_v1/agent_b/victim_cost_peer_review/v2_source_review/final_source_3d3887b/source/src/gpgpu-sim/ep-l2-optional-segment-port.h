#pragma once
#include <cstdint>
#include <limits>
#include "ep-l2-ft-interface.h"
struct ep_l2_optional_segment_port {
 enum op { BEGIN_READ=1, END_READ=2, CANCEL_READ=4, INSTALL=8, DROP=16 };
 std::uint64_t cycle=std::numeric_limits<std::uint64_t>::max(),incarnation=0;
 unsigned row=128,uid=0,mask=0,count=0;
 ep_l2::PayloadHandle payload;
 std::uint64_t grants=0,merges=0,busy=0;
 bool reserve(unsigned r,std::uint64_t g,unsigned u,ep_l2::PayloadHandle h,
              op operation,std::uint64_t now) {
  if(now!=cycle){cycle=now;row=r;incarnation=g;uid=u;payload=h;
   mask=operation;count=1;++grants;return true;}
  const bool pair=count==1 && mask==BEGIN_READ &&
      (operation==END_READ || operation==CANCEL_READ);
  if(pair && row==r && incarnation==g && uid==u && payload==h) {
   mask|=operation;++count;++merges;return true;
  }
  ++busy;return false;
 }
 bool reserved(unsigned r,std::uint64_t g,unsigned u,op operation,
               std::uint64_t now)const {
  return cycle==now && row==r && incarnation==g && uid==u && (mask&operation);
 }
 // No release/refund API. One clock consumed even after cancellation.
};
