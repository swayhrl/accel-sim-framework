#include "ag7_policyb_progress.h"
#include <cstdlib>
#include <unistd.h>
int main(int argc,char**argv){
 const int n=argc==2?std::atoi(argv[1]):0;
 if(n<8193||n>20000)return 41;
 dtc_ag7::ProgressProducer producer;
 if(!producer.enabled())return 42;
 for(int i=0;i<n;++i){
  const bool end=i==n-1;
  producer.observe(i==0?"INIT":end?"BOUNDARY":"SIMULATE",i,true,true,end?"NATURAL":"NONE");
  if(!producer.enabled())return 43;
  char ack=0;if(read(0,&ack,1)!=1||ack!='A')return 44;
 }
 return 0;
}
