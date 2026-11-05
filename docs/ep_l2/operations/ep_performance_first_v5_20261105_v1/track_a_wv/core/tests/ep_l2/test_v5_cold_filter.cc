#include "ms_victim/native_fixture.h"
int main(int argc,char **argv) {
  assert(argc==4);const std::string mode=argv[3];
  char two[]="2",sixteen[]="16",zero[]="0",one[]="1";
  char *args[]={argv[0],argv[1],argv[2],two,sixteen,zero,zero,one};
  victim_fixture f(args,"512:2:64:64","S:32:128:8,L:B:m:L:L,A:128:1,256:0,32");
  auto cache=f.cache;auto dir=cache->tvd_for_test();assert(dir && dir->never_installed());
  const bool enabled=mode!="off";
  f.read(0);
  assert(dir->never_installed());
  assert(enabled ? (cache->tvd_lookup_queries_for_test()==0 && cache->tvd_cold_bypasses_for_test()>0)
                 : (cache->tvd_lookup_queries_for_test()>0 && cache->tvd_cold_bypasses_for_test()==0));
  std::vector<new_addr_type> lines;lines.push_back(0);
  for(new_addr_type a=128;lines.size()<10;a+=128)
    if(f.gpu->getMemoryConfig()->m_L2_config.set_index(a)==0)lines.push_back(a);
  if(mode=="dirty")f.write(0);
  for(unsigned i=1;i<9;++i)f.read(lines[i]);
  assert(!dir->never_installed());
  const auto bypasses=cache->tvd_cold_bypasses_for_test();
  const auto queries=cache->tvd_lookup_queries_for_test();
  if(mode=="dirty") {
    assert(cache->ep_l2_wad_contains(0));
    auto r=f.make(0,false);const auto uid=r->get_request_uid();f.send(r);
    for(unsigned i=0;i<6;++i)f.step();
    assert(cache->tvd_lookup_queries_for_test()>queries);
    f.complete_writebacks(); f.wait(uid);
  } else {
    f.read(0);assert(cache->tvd_lookup_queries_for_test()>queries);
  }
  assert(cache->tvd_cold_bypasses_for_test()==bypasses);
  f.finish();assert(!dir->occupied() && !dir->never_installed());
  f.read(lines[9]);assert(cache->tvd_cold_bypasses_for_test()==bypasses);
  f.finish();printf("V5_COLD_FILTER_PASS|mode=%s|queries=%llu|bypasses=%llu\n",
      mode.c_str(),cache->tvd_lookup_queries_for_test(),cache->tvd_cold_bypasses_for_test());
}
