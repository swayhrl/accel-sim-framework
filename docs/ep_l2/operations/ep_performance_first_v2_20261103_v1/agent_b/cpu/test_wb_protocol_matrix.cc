// Bounded directed CPU fixture; private access is observation/stimulus only.
#include <bits/stdc++.h>
#include <unistd.h>
#define private public
#define protected public
#include "gpgpu_context.h"
#include "gpu-sim.h"
#include "icnt_wrapper.h"
#include "l2cache.h"
#include "dram.h"
#include "mem_latency_stat.h"
#include "option_parser.h"
#include "trace_driven.h"
#undef protected
#undef private
static memory_partition_unit *watch_part=nullptr;
static int watch_credit=-1;
static l2_cache *watch_cache=nullptr;
static new_addr_type watch_address=0;
static bool negative_armed=false;
static int credit(memory_partition_unit*p){auto&a=p->m_arbitration_metadata;return std::accumulate(a.m_private_credit.begin(),a.m_private_credit.end(),0)+a.m_shared_credit+a.m_wb_progress_credit;}
extern "C" __attribute__((noreturn)) void __assert_fail(const char*expr,const char*file,unsigned line,const char*fn)noexcept{
 bool pass=negative_armed&&watch_part&&credit(watch_part)==watch_credit&&watch_cache->ep_l2_wad_contains(watch_address)&&strstr(expr,"writeback_matches");
 fprintf(stderr,"CPU_ASSERT_INTERCEPT|expr=%s|file=%s|line=%u|credit_before=%d|credit_after=%d|WAD_retained=%u|expected_identity_rejection=%u\n",expr,file,line,watch_credit,watch_part?credit(watch_part):-1,watch_cache?watch_cache->ep_l2_wad_contains(watch_address):0,pass);
 _Exit(pass?86:87);
}
struct calendar{double c=0,i=0,d=0,l=0,cp,ip,dp,lp;int next(){double t=std::min(c,std::min(i,d));int m=0;if(l<=t){t=l;m|=8;l+=lp;}if(i<=t){m|=2;i+=ip;}if(d<=t){m|=4;d+=dp;}if(c<=t){m|=1;c+=cp;}return m;}};
int main(int argc,char**argv){assert(argc==5);setvbuf(stdout,nullptr,_IONBF,0);unsigned mhz=std::stoul(argv[2]),writes=std::stoul(argv[3]);std::string scenario=argv[4];bool dual=scenario=="dual",pressure=scenario=="queue_full",pin=scenario=="pinned",ret=scenario=="return_full";
 gpgpu_context ctx;gpgpu_sim_config cfg(&ctx);option_parser_t opt=option_parser_create();ctx.ptx_reg_options(opt);ctx.func_sim->ptx_opcocde_latency_options(opt);icnt_reg_options(opt);cfg.reg_options(opt);trace_config tc;tc.reg_options(opt);option_parser_cfgfile(opt,argv[1]);cfg.init();option_parser_destroy(opt);exec_gpgpu_sim gpu(cfg,&ctx);gpu.gpu_sim_cycle=1;auto mc=gpu.getMemoryConfig();memory_stats_t stats(cfg.num_shader(),gpu.getShaderCoreConfig(),mc,&gpu);memory_partition_unit part(0,mc,&stats,&gpu);partition_mf_allocator alloc(mc);memory_sub_partition*sp[2]={part.get_sub_partition(0),part.get_sub_partition(1)};l2_cache*cache[2]={sp[0]->ft_cache_for_test(),sp[1]->ft_cache_for_test()};uint64_t signature=1469598103934665603ULL;auto hash_event=[&](uint64_t v){signature^=v;signature*=1099511628211ULL;};unsigned responses=0,read_responses=0;std::set<unsigned> seen;
 auto collect=[&](){for(auto s:sp)while(auto mf=s->pop()){assert(seen.insert(mf->get_request_uid()).second);hash_event(mf->get_request_uid());hash_event(mf->get_addr());hash_event(gpu.gpu_sim_cycle);if(!mf->get_is_write())++read_responses;++responses;delete mf;}};
 auto make=[&](new_addr_type a,bool write){active_mask_t act;act.set(0);mem_access_byte_mask_t bytes;for(unsigned b=0;b<32;++b)bytes.set(b);mem_access_sector_mask_t sec;sec.set(0);return alloc.alloc(a,write?GLOBAL_ACC_W:GLOBAL_ACC_R,act,bytes,sec,32,write,gpu.gpu_sim_cycle,0,0,0,nullptr,0);};
 auto step_cache=[&](){part.cache_cycle(gpu.gpu_sim_cycle);collect();++gpu.gpu_sim_cycle;};
 unsigned num_slices=dual?2:1;
 for(unsigned sid=0;sid<num_slices;++sid){new_addr_type addr=0;for(unsigned n=0;n<writes;){addrdec_t dec;mc->m_address_mapping.addrdec_tlx(addr,&dec);if(dec.sub_partition!=sid){addr+=128;continue;}auto mf=make(addr,true);assert(mf->get_sub_partition_id()==sid);assert(!sp[sid]->full());sp[sid]->push(mf,gpu.gpu_sim_cycle);unsigned target=responses+1;for(unsigned j=0;j<2000&&responses<target;++j)step_cache();assert(responses==target);++n;addr+=128;}}
 assert(cache[0]->ep_l2_wad_occupancy()>2);unsigned original_wb=cache[0]->ep_l2_wad_occupancy()+cache[1]->ep_l2_wad_occupancy();auto dram=part.m_dram;unsigned blocked=0,held=0,queuefull=0,hol=0,returnfull=0,pin_completion=0;unsigned maxrwq=0;std::map<std::pair<unsigned,unsigned long long>,unsigned> grants;std::set<unsigned> wb_uids;std::set<unsigned> generations;bool pressure_done=false,return_done=false;unsigned pause_cache=ret?500:0;unsigned read_sent=0;
 // Directed real reads on the other slice build the finite DRAM->L2/ReturnQ
 // pressure; CPU config uses returnq4 and dram->L2 FIFO1 for this scenario.
 if(ret){new_addr_type addr=0;while(read_sent<8){addrdec_t dec;mc->m_address_mapping.addrdec_tlx(addr,&dec);if(dec.sub_partition!=1){addr+=128;continue;}auto mf=make(addr,false);assert(!sp[1]->full());sp[1]->push(mf,gpu.gpu_sim_cycle);for(unsigned j=0;j<200;++j)step_cache();++read_sent;addr+=128;}}
 std::unique_ptr<l2_cache::tvd_directory::read_lease> lease;ep_l2_payload_store::payload_handle pinned_handle;unsigned pinned_sid=0;new_addr_type pinned_addr=0;
 auto one_dram=[&](){auto head=dram->rwq->top();bool last=head&&head->data->get_access_type()==L2_WRBK_ACC&&head->dqbytes+mc->dram_atom_size>=head->nbytes;bool unavailable=last&&!part.can_complete_writeback(head->data);unsigned sid=last?head->data->get_sub_partition_id():0;mem_fetch*mf=last?head->data:nullptr;unsigned dq=last?head->dqbytes:0,uid=last?mf->get_request_uid():0,id=last?mf->get_ep_l2_payload_id():0,gen=last?mf->get_ep_l2_payload_generation():0;new_addr_type address=last?mf->get_addr():0;
  if(last){wb_uids.insert(uid);generations.insert(gen);}
  if(pin&&last&&!lease){auto dir=cache[sid]->m_tvd.get();auto ticket=dir->find(address);auto obs=dir->preview_ticket(ticket,1,l2_cache::tvd_directory::READ_OP);assert(obs.status==l2_cache::tvd_directory::READ_READY);lease.reset(new l2_cache::tvd_directory::read_lease);assert(dir->begin_read(obs,1,*lease)==l2_cache::tvd_directory::OK);pinned_handle=lease->handle();cache[sid]->m_ep_l2_payload.pin(pinned_handle);pinned_sid=sid;pinned_addr=address;}
  if(last&&(scenario=="stale_uid"||scenario=="wrong_address")){watch_part=&part;watch_cache=cache[sid];watch_address=address;watch_credit=credit(&part);negative_armed=true;if(scenario=="stale_uid")mf->m_request_uid+=1000000;else mf->set_addr(address^(1ULL<<32));dram->cycle();assert(false);}
  unsigned long long before[2]={cache[0]->m_tvd_indexed_completions,cache[1]->m_tvd_indexed_completions};if(unavailable){++blocked;for(auto q=dram->rwq->m_head;q;q=q->m_next)if(q->m_data&&q->m_data->data->get_sub_partition_id()!=sid){++hol;break;}}
  bool retfull=dram->returnq_full();auto top_return=dram->return_queue_top();bool return_pop=top_return&&!sp[top_return->get_sub_partition_id()]->dram_L2_queue_full();if(retfull)++returnfull;part.dram_cycle();maxrwq=std::max(maxrwq,dram->rwq->get_length());if(dram->rwq->full())++queuefull;
  for(unsigned s=0;s<2;++s){auto delta=cache[s]->m_tvd_indexed_completions-before[s];assert(delta<=1);if(delta){for(auto value:{uint64_t(s),uint64_t(gpu.gpu_sim_cycle),uint64_t(uid),uint64_t(address),uint64_t(id),uint64_t(gen),uint64_t(credit(&part))})hash_event(value);auto key=std::make_pair(s,gpu.gpu_sim_cycle);assert(++grants[key]<=1);if(pin&&s==pinned_sid&&address==pinned_addr){assert(cache[s]->m_ep_l2_payload.inspect(pinned_handle).pins>0);++pin_completion;}}}
  if(unavailable){assert(dram->rwq->top()==head&&head->dqbytes==dq&&head->data==mf);assert(mf->get_request_uid()==uid&&mf->get_addr()==address&&mf->get_ep_l2_payload_id()==id&&mf->get_ep_l2_payload_generation()==gen);++held;}
  if(retfull&&!return_pop)assert(cache[0]->m_tvd_indexed_completions==before[0]&&cache[1]->m_tvd_indexed_completions==before[1]);
 };
 calendar cal;cal.cp=cal.ip=cal.lp=1./1132.;cal.dp=1./double(mhz);unsigned steps=0;
 auto pending=[&](){return part.busy()||cache[0]->ep_l2_wad_occupancy()||cache[1]->ep_l2_wad_occupancy()||!cache[0]->ft_drained()||!cache[1]->ft_drained()||!part.l2_char_no_credit_leak();};
 while((pending()||lease)&&steps++<2000000){int mask=cal.next();if(mask&4){one_dram();if(pressure&&!pressure_done&&!grants.empty()){int before=credit(&part);unsigned long long issued_before=part.m_l2_char_dram_issue_count;unsigned wads=cache[0]->ep_l2_wad_occupancy();for(unsigned z=0;z<80;++z){auto head=dram->rwq->top();if(head&&head->data->get_access_type()==L2_WRBK_ACC&&head->dqbytes+mc->dram_atom_size>=head->nbytes&&!part.can_complete_writeback(head->data)){unsigned q=head->dqbytes;auto data=head->data;auto uid=data->get_request_uid(),gen=data->get_ep_l2_payload_generation();part.dram_cycle();assert(dram->rwq->top()==head&&head->dqbytes==q&&data==head->data&&uid==data->get_request_uid()&&gen==data->get_ep_l2_payload_generation());++blocked;++held;}else part.dram_cycle();maxrwq=std::max(maxrwq,dram->rwq->get_length());if(dram->rwq->full())++queuefull;}assert(credit(&part)==before+int(part.m_l2_char_dram_issue_count-issued_before)&&cache[0]->ep_l2_wad_occupancy()==wads);pressure_done=true;}}
  if(mask&8){if(pause_cache)--pause_cache;else{part.cache_cycle(gpu.gpu_sim_cycle);collect();}}
  if(lease&&cache[pinned_sid]->ep_l2_wad_occupancy()==0){auto dir=cache[pinned_sid]->m_tvd.get();assert(dir->at(dir->find(pinned_addr).index).status==l2_cache::tvd_directory::WB_COMPLETE);assert(dir->cancel_read(*lease)==l2_cache::tvd_directory::OK);cache[pinned_sid]->m_ep_l2_payload.unpin(pinned_handle);lease.reset();}
  if(mask&1)++gpu.gpu_sim_cycle;
 }
 assert(!pending()&&part.l2_char_no_credit_leak());for(auto s:sp)assert(s->l2_char_no_resource_leak());assert(responses==writes*num_slices+read_sent);assert(wb_uids.size()==original_wb);if(mhz>1132&&!ret&&cache[0]->tvd_enabled())assert(blocked>0&&held==blocked);if(pressure)assert(queuefull>0&&maxrwq==mc->CL+1);if(ret)assert(returnfull>0&&read_responses==read_sent);if(pin)assert(pin_completion>0);
 printf("CPU_EVENT_SIGNATURE|value=%016llx\n",static_cast<unsigned long long>(signature));
 printf("PROTOCOL_CPU_PASS|case=%s|MHz=%u|requests=%u|responses=%u|WB=%u|unique_WB_UID=%zu|gen_pop=%zu|blocked=%u|held_identity_checks=%u|RWQmax=%u|RWQbound=%u|full=%u|same_partition_other_slice_HOL=%u|ReturnQfull=%u|pinned_complete=%u|credit_clean=1|port_per_slice_core=1|Trace_reads=0|application_kernels=0\n",scenario.c_str(),mhz,writes*num_slices+read_sent,responses,original_wb,wb_uids.size(),generations.size(),blocked,held,maxrwq,mc->CL+1,queuefull,hol,returnfull,pin_completion);
}
