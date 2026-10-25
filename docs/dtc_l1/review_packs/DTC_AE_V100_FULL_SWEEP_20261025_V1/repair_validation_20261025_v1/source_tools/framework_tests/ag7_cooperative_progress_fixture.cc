#include "../ag7_policyb_progress.h"
#include "../trace-parser/trace_parser.h"
#include "../trace-parser/warp_trace_stream.h"
#include <chrono>
#include <stdexcept>
#include <thread>
#include <vector>
#include <cstdio>

static unsigned long long decode(const std::string &line) {
  inst_trace_t inst;
  assert(inst.parse_from_string(line, 3, 0));
  if (inst.memadd_info) {
    assert(inst.memadd_info->addrs[0] == 0x1000);
    assert(inst.memadd_info->addrs[1] == 0x1004);
    return inst.memadd_info->addrs[0] + inst.memadd_info->addrs[1];
  }
  assert(inst.tma_memadd_info && inst.tma_memadd_info->addrs.size() == 2);
  assert(inst.tma_memadd_info->addrs[0] == 0x1000);
  assert(inst.tma_memadd_info->addrs[1] == 0x1004);
  return inst.tma_memadd_info->addrs[0] + inst.tma_memadd_info->addrs[1];
}

static void put32(FILE *f, uint32_t value) { assert(fwrite(&value,4,1,f)==1); }
static void put64(FILE *f, uint64_t value) { assert(fwrite(&value,8,1,f)==1); }
static void tracez_fixture(const std::string &path) {
  FILE *f=fopen(path.c_str(),"wb"); assert(f);
  const char header[]="-kernel name = CPU_ONLY\n";
  assert(fwrite(header,1,sizeof(header),f)==sizeof(header));
  put32(f,0); put32(f,1);
  uint64_t warp_offset=ftello(f); put32(f,2); put32(f,2);
  const std::string line="0 3 1 R1 LDG.E.32 0 4 0 1000 1004 0\n";
  std::vector<char> compressed(ZSTD_compressBound(line.size()));
  size_t bytes=ZSTD_compress(compressed.data(),compressed.size(),line.data(),line.size(),1);
  assert(!ZSTD_isError(bytes));
  for(unsigned i=0;i<2;++i){put32(f,bytes);assert(fwrite(compressed.data(),1,bytes,f)==bytes);}
  uint64_t index_offset=ftello(f); put32(f,1);
  for(unsigned i=0;i<10;++i)put32(f,0);
  put32(f,1); put32(f,2); put32(f,2); put64(f,warp_offset);put32(f,1);put32(f,1);put64(f,index_offset);fclose(f);
  TracezReader reader; assert(reader.open(path)==header);
  const auto *tb=reader.get_next_tb_index();assert(tb&&tb->warp_count==1);
  WarpTraceStream stream;stream.init(reader.fd(),tb->warps[0],reader.ddict(),3,0,dim3(0,0,0),dim3(0,0,0),dim3(0,0,0),0);
  assert(stream.get(0).memadd_info->addrs[1]==0x1004);
  assert(stream.get(1).memadd_info->addrs[1]==0x1004);
  assert(reader.get_next_tb_index()==nullptr);
}

int main(int argc,char **argv) {
  assert(argc>=2);std::string mode=argv[1];dtc_ag7::ProgressProducer producer;
  producer.observe("INIT",17,true,true);
  unsigned long long checksum=0,iterations=0;
  {
    dtc_ag7::ScopedProgressProducer scope(producer);
    if(mode=="cap") {
      for(unsigned i=0;i<8194;++i){producer.observe("SIMULATE",17+i,true,true);usleep(200);}
      producer.observe("BOUNDARY",17+8193,true,true,"NATURAL");
    } else if(mode=="long") {
      producer.observe("SIMULATE",17,true,true);
      const auto end=std::chrono::steady_clock::now()+std::chrono::seconds(33);
      while(std::chrono::steady_clock::now()<end){checksum+=decode("0 3 1 R1 LDG.E.32 0 4 1 1000 4 0");++iterations;}
      producer.observe("BOUNDARY",17,true,true,"NATURAL");
    } else if(mode=="formats") {
      producer.observe("PARSE",17,true,true);
      for(const auto &line:std::vector<std::string>{
        "0 3 1 R1 LDG.E.32 0 4 0 1000 1004 0",
        "0 3 1 R1 LDG.E.32 0 4 1 1000 4 0",
        "0 3 1 R1 LDG.E.32 0 4 2 1000 4 0",
        "0 3 0 UTMALDG 0 4 0 0 8 0 3 2 1000 1004 0",
        "0 3 0 UTMALDG 0 4 0 0 8 0 4 1000 2 4 0"}) checksum+=decode(line);
      assert(argc==3);std::string root=argv[2];
      for(const char *suffix:{".traceg",".traceg.xz"}) {
        PipeReader input(root+"/cpu"+suffix);trace_parser parser;
        std::vector<inst_trace_t> warp;std::vector<std::vector<inst_trace_t>*> tb{&warp};
        parser.get_next_threadblock_traces(tb,3,0,input);assert(warp.size()==1&&warp[0].memadd_info->addrs[1]==0x1004);
      }
      tracez_fixture(root+"/cpu.tracez");
      std::thread background([]{assert(dtc_ag7::progress_slot()==nullptr);dtc_ag7::cooperative_heartbeat_now();});background.join();
      producer.observe("BOUNDARY",17,true,true,"NATURAL");
      for(unsigned i=0;i<3000;++i)dtc_ag7::cooperative_heartbeat_now();
    } else if(mode=="error") {
      try {dtc_ag7::ScopedProgressProducer nested(producer);throw std::runtime_error("CPU fixture parse error");}
      catch(const std::runtime_error &) {}
      producer.observe("BOUNDARY",17,true,true,"ERROR");
    } else if(mode=="broken") {
      for(unsigned i=0;i<3000;++i)dtc_ag7::cooperative_heartbeat_now();
      producer.observe("BOUNDARY",17,true,true,"NATURAL");
      assert(!producer.enabled());
    } else {return 3;}
  }
  assert(dtc_ag7::progress_slot()==nullptr);
  printf("{\"enabled\":%d,\"checksum\":%llu,\"iterations\":%llu}\n",producer.enabled(),checksum,iterations);
  return 0;
}
