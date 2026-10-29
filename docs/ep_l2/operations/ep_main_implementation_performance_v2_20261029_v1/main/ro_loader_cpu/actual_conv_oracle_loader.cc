#include <cassert>
#include <fstream>
#include <sstream>
#include <cstdio>
#include "/root/data/ep_l2_full_workload_performance_20261027_v1/research/implementation_performance_v2_20261029_v1/agent_d/core/src/gpgpu-sim/ep-l2-ro-oracle.h"
int main(int argc,char**argv){assert(argc==3);std::ifstream f(argv[1]);ep_l2_ro::oracle_certificate c(f,argv[2],"TRACE_MODEL_CLOSED_WORLD");assert(c.range_count()>0 && c.manifest_sha256()==argv[2]);std::ifstream again(argv[1]);std::string line;std::getline(again,line);unsigned rows=0;while(std::getline(again,line)){if(!line.empty()&&line.back()=='\r')line.pop_back();auto a=std::stoull(line.substr(0,16),nullptr,16),b=std::stoull(line.substr(17),nullptr,16);assert(c.contains(a)&&c.contains(b)&&!c.contains(a+1)&&c.overlaps_bytes(a,1));++rows;}assert(rows==c.range_count());bool reject=false;try{std::ifstream in(argv[1]);ep_l2_ro::oracle_certificate denied(in,argv[2],"NO_READONLY_CERTIFICATION");}catch(const std::invalid_argument&){reject=true;}assert(reject);printf("ACTUAL_CONV_NEW_SOURCE_RO_LOADER|ranges=%u|boundary_alignment_and_scope=PASS|application_run=0\n",rows);return 0;}
