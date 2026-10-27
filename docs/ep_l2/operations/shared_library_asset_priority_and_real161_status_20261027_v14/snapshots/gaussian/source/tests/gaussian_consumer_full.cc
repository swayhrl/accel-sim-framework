#include <bits/stdc++.h>
#include "../consumer/trace_parser.h"
int main(int argc,char**argv){try{
 if(argc!=2)throw std::runtime_error("one exact grouped trace path required");
 trace_parser p;auto*k=p.parse_kernel_info(argv[1]);
 uint64_t threads=uint64_t(k->tb_dim_x)*k->tb_dim_y*k->tb_dim_z;
 uint64_t blocks=uint64_t(k->grid_dim_x)*k->grid_dim_y*k->grid_dim_z;
 if(!threads||threads>1024||!blocks||blocks>1000000)throw std::runtime_error("finite exact launch dimensions");
 unsigned nw=(threads+31)/32;std::vector<std::vector<inst_trace_t>>v(nw);std::vector<std::vector<inst_trace_t>*>w;for(auto&x:v)w.push_back(&x);
 std::set<std::tuple<unsigned,unsigned,unsigned>>seen;uint64_t records=0,calls=0,rets=0,cl=0,rl=0,el=0;
 for(uint64_t i=0;i<blocks;i++){
  p.get_next_threadblock_traces(w,k->trace_verion,k->enable_lineinfo,k->pipeReader,unsigned(threads));auto a=p.last_block;
  if(!a.present||a.x>=k->grid_dim_x||a.y>=k->grid_dim_y||a.z>=k->grid_dim_z||!seen.emplace(a.x,a.y,a.z).second)throw std::runtime_error("missing/duplicate/out-of-range CTA");
  records+=a.raw_records;calls+=a.call_issues;rets+=a.ret_issues;cl+=a.call_lanes;rl+=a.ret_lanes;el+=a.exit_lanes;
 }
 p.get_next_threadblock_traces(w,k->trace_verion,k->enable_lineinfo,k->pipeReader,unsigned(threads));
 if(p.last_block.present)throw std::runtime_error("extra CTA beyond exact launch");
 k->pipeReader.close_checked();
 std::cout<<"GAUSSIAN_CPU_FULL_TRACE_JSON {\"schema\":\"GAUSSIAN16_CONSUMER_FULL_RECORD_V2\",\"kernel_id\":"<<k->kernel_id<<",\"CTAs\":"<<seen.size()<<",\"warps_per_CTA\":"<<nw<<",\"source_records\":"<<records<<",\"CALL_issue_records\":"<<calls<<",\"RET_issue_records\":"<<rets<<",\"CALL_effective_lanes\":"<<cl<<",\"RET_effective_lanes\":"<<rl<<",\"EXIT_effective_lanes\":"<<el<<",\"all_CTA_warp_EXIT_CFI_closed\":true,\"EOF_decompressor_closed\":true,\"dynamic_device_observer_joined\":false,\"input_numeric_qualification\":false,\"simulator_qualification\":false}\n";
 p.kernel_finalizer(k);return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 2;}}
