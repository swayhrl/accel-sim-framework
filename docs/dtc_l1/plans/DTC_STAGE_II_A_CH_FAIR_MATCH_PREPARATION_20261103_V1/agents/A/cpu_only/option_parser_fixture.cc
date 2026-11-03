// CPU ONLY: links ONLY Core src/option_parser.cc; no simulator/model object.
#include "option_parser.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <climits>
int main(int argc, char **argv) {
  char *cache=0,*clocks=0,*fifos=0;
  int fr=64,ret=192,nmem=20,nsub=2,split=0,sched=1;
  option_parser_t p=option_parser_create();
  option_parser_register(p,"-gpgpu_cache:dl2",OPT_CSTR,&cache,"L2","");
  option_parser_register(p,"-gpgpu_frfcfs_dram_sched_queue_size",OPT_INT32,&fr,"FRFCFS","64");
  option_parser_register(p,"-gpgpu_dram_return_queue_size",OPT_INT32,&ret,"return","192");
  option_parser_register(p,"-gpgpu_clock_domains",OPT_CSTR,&clocks,"clocks","");
  option_parser_register(p,"-gpgpu_dram_partition_queues",OPT_CSTR,&fifos,"FIFO","");
  option_parser_register(p,"-gpgpu_n_mem",OPT_INT32,&nmem,"controllers","20");
  option_parser_register(p,"-gpgpu_n_sub_partition_per_mchannel",OPT_INT32,&nsub,"subpartitions","2");
  option_parser_register(p,"-dram_seperate_write_queue_enable",OPT_BOOL,&split,"write split","0");
  option_parser_register(p,"-gpgpu_dram_scheduler",OPT_INT32,&sched,"scheduler","1");
  for (int i=1;i<argc;i++) option_parser_cfgfile(p,argv[i]);
  char ct,rp,wp,ap,wap,sif,mshr_type;
  unsigned sets,line,ways,entries,merge,mq,res,width;
  // Exact sscanf format/order from pinned gpu-cache.h cache_config::init.
  int ntok=sscanf(cache,"%c:%u:%u:%u,%c:%c:%c:%c:%c,%c:%u:%u,%u:%u,%u",
     &ct,&sets,&line,&ways,&rp,&wp,&ap,&wap,&sif,&mshr_type,&entries,&merge,&mq,&res,&width);
  assert(ntok==15 && ct=='S' && sets==128 && line==128 && ways==16);
  assert(rp=='L' && wp=='B' && ap=='m' && wap=='L' && sif=='L' && mshr_type=='A');
  assert(entries>0 && merge>0 && mq>0 && res==0 && width==32);
  assert(line%width==0 && line/32==4 && line%32==0);
  assert(fr>0 && ret==192 && nmem==20 && nsub==2 && split==0 && sched==1);
  assert(!strcmp(clocks,"1410.0:1410.0:1410.0:850.0"));
  assert(!strcmp(fifos,"64:64:64:64"));
  printf("{\"ntok\":%d,\"entries\":%u,\"merge\":%u,\"miss_queue\":%u,\"frfcfs\":%d,\"shared_credit\":%d,\"cache_bytes\":%u,\"model_cycles\":0}\n",ntok,entries,merge,mq,fr,fr+ret-(nsub-1),nmem*nsub*sets*line*ways);
  option_parser_destroy(p);
}
