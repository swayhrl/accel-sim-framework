#include <algorithm>
#include <cassert>
#include <cstdio>
#include <map>
#define CORE 0x01
#define ICNT 0x02
#define DRAM 0x04
#define L2 0x08
static double min3(double a,double b,double c){return std::min(a,std::min(b,c));}
struct Periods{double core_period,icnt_period,dram_period,l2_period;};
struct Calendar{double core_time=0,icnt_time=0,dram_time=0,l2_time=0;Periods m_config;int next_clock_domain(void);};
int Calendar::next_clock_domain(void) {
  double smallest = min3(core_time, icnt_time, dram_time);
  int mask = 0x00;
  if (l2_time <= smallest) {
    smallest = l2_time;
    mask |= L2;
    l2_time += m_config.l2_period;
  }
  if (icnt_time <= smallest) {
    mask |= ICNT;
    icnt_time += m_config.icnt_period;
  }
  if (dram_time <= smallest) {
    mask |= DRAM;
    dram_time += m_config.dram_period;
  }
  if (core_time <= smallest) {
    mask |= CORE;
    core_time += m_config.core_period;
  }
  return mask;
}
int main(){for(double dram:{850.,1020.,1132.,1275.,1700.}){Calendar c;c.m_config={1./1132.,1./1132.,1./dram,1./1132.};unsigned core=0,max_dram=0;std::map<unsigned,unsigned> counts;unsigned first=~0u;while(core<10000){int m=c.next_clock_domain();if(m&DRAM){unsigned n=++counts[core];max_dram=std::max(max_dram,n);if(n>1&&first==~0u)first=core;}if(m&CORE)++core;}assert((dram<=1132.&&max_dram==1)||(dram>1132.&&max_dram>=2));printf("CLOCK_CALENDAR_CPU|CORE=1132|DRAM=%.0f|max_DRAM_callbacks_same_GPU_counter=%u|first_possible_duplicate=%u|GPU_objects=0|WB_packets=0|cycles_simulated=0|assert_predicate_only=1|PASS\n",dram,max_dram,first);}return 0;}
