#include <cassert>
#include <cstdint>
#include <deque>
#include <map>
#include <iostream>
namespace dtc_l1 { constexpr unsigned kLogicalLineBytes=128; constexpr unsigned kSectorsPerLogicalLine=4;
inline bool response_sector_is_new(uint8_t expected, uint8_t received,
                                   unsigned sector) {
  return sector < kSectorsPerLogicalLine && (expected & (1U << sector)) &&
         !(received & (1U << sector));
}
}
struct mem_fetch {uint64_t addr=0;unsigned uid=0;bool atomic=false,write=false;mem_fetch* original=nullptr;unsigned atomic_side_effects=0;
 bool isatomic()const{return atomic;}void do_atomic(){++atomic_side_effects;}unsigned get_num_flits(bool)const{return 1;}unsigned get_request_uid()const{return uid;}mem_fetch*get_original_mf()const{return original;}uint64_t get_addr()const{return addr;}bool get_is_write()const{return write;}};
struct GPU{unsigned completed=0;void dtc_l1_complete_lower_request(){++completed;}};
struct shader_core_ctx {GPU gpu;unsigned traffic=0;GPU*get_gpu(){return &gpu;}void inc_simt_to_mem(unsigned n){traffic+=n;}};
struct simt_core_cluster {std::deque<mem_fetch*>q;unsigned capacity=1;bool response_queue_full(){return q.size()>=capacity;}void push_response_fifo(mem_fetch*m){q.push_back(m);}};
struct mem_fetch_interface {virtual bool full(unsigned,bool)const=0;virtual void push(mem_fetch*)=0;virtual~mem_fetch_interface()=default;};
class perfect_memory_interface : public mem_fetch_interface {
 public:
  perfect_memory_interface(shader_core_ctx *core, simt_core_cluster *cluster) {
    m_core = core;
    m_cluster = cluster;
  }
  virtual bool full(unsigned size, bool write) const {
    return m_cluster->response_queue_full();
  }
  virtual void push(mem_fetch *mf) {
    if (mf && mf->isatomic())
      mf->do_atomic();  // execute atomic inside the "memory subsystem"
    m_core->inc_simt_to_mem(mf->get_num_flits(true));
    m_cluster->push_response_fifo(mf);
  }

 private:
  shader_core_ctx *m_core;
  simt_core_cluster *m_cluster;
};
struct Frontend {unsigned completed=0;void complete(unsigned){++completed;}void complete_sector(unsigned,unsigned){++completed;}};
struct ldst_unit {struct dtc_l1_oo_inflight{unsigned physical;uint64_t line_address;unsigned inst_uid;uint8_t expected_sector_mask;uint8_t response_sector_mask=0;};
 std::map<unsigned,dtc_l1_oo_inflight>m_dtc_l1_oo_inflight;Frontend f;Frontend*m_dtc_l1_sector_frontend=&f,*m_dtc_l1_oo_frontend=&f;shader_core_ctx*m_core;unsigned m_dtc_l1_oo_lower_responses=0;bool sector_mode=false;
 bool dtc_l1_paper_oo_active(){return true;}bool dtc_l1_sector_oo_active(){return sector_mode;}bool dtc_l1_oo_consume_response(mem_fetch*);};
bool ldst_unit::dtc_l1_oo_consume_response(mem_fetch *mf) {
  if (!dtc_l1_paper_oo_active()) return false;
  auto it = m_dtc_l1_oo_inflight.find(mf->get_request_uid());
  if (it == m_dtc_l1_oo_inflight.end() && mf->get_original_mf())
    it = m_dtc_l1_oo_inflight.find(
        mf->get_original_mf()->get_request_uid());
  if (it == m_dtc_l1_oo_inflight.end()) return false;
  dtc_l1_oo_inflight &record = it->second;
  const uint64_t aligned_address =
      mf->get_addr() & ~(dtc_l1::kLogicalLineBytes - 1);
  const unsigned sector =
      static_cast<unsigned>((mf->get_addr() - record.line_address) / 32);
  if (mf->get_is_write() || aligned_address != record.line_address ||
      !dtc_l1::response_sector_is_new(record.expected_sector_mask,
                                     record.response_sector_mask, sector)) {
    assert(false && "OO response identity/address mismatch");
  }
  record.response_sector_mask |= static_cast<uint8_t>(1U << sector);
  mem_fetch *original = mf->get_original_mf();
  const bool request_complete =
      record.response_sector_mask == record.expected_sector_mask;
  if (request_complete) {
    if (dtc_l1_sector_oo_active())
      m_dtc_l1_sector_frontend->complete_sector(record.physical, sector);
    else
      m_dtc_l1_oo_frontend->complete(record.physical);
    m_core->get_gpu()->dtc_l1_complete_lower_request();
    m_dtc_l1_oo_inflight.erase(it);
    ++m_dtc_l1_oo_lower_responses;
  }
  delete mf;
  if (original && request_complete) delete original;
  return true;
}
int main(int argc,char**argv){
 if(argc>1){shader_core_ctx core;ldst_unit u;u.m_core=&core;u.m_dtc_l1_oo_inflight.emplace(1,ldst_unit::dtc_l1_oo_inflight{7,0x1000,9,15,0});auto*m=new mem_fetch;m->uid=1;
  if(std::string(argv[1])=="wrong_address"){m->addr=0x2000;u.dtc_l1_oo_consume_response(m);return 3;}
  if(std::string(argv[1])=="duplicate_sector"){u.m_dtc_l1_oo_inflight.at(1).response_sector_mask=1;m->addr=0x1000;u.dtc_l1_oo_consume_response(m);return 3;}
  if(std::string(argv[1])=="unknown_uid"){m->uid=77;m->addr=0x1000;assert(!u.dtc_l1_oo_consume_response(m));delete m;std::cout<<"UNKNOWN_UID_NOT_CONSUMED\n";return 0;}
 }

 shader_core_ctx core;simt_core_cluster cluster;perfect_memory_interface pi(&core,&cluster);assert(!pi.full(128,false));
 auto*root=new mem_fetch;root->addr=0x1000;root->uid=1;ldst_unit u;u.m_core=&core;u.m_dtc_l1_oo_inflight.emplace(1,ldst_unit::dtc_l1_oo_inflight{7,0x1000,9,0xf,0});pi.push(root);assert(pi.full(128,false));assert(cluster.q.size()==1&&cluster.q.front()==root);cluster.q.pop_front();assert(u.dtc_l1_oo_consume_response(root));assert(u.m_dtc_l1_oo_inflight.size()==1);assert(u.m_dtc_l1_oo_inflight.at(1).response_sector_mask==1);assert(core.gpu.completed==0&&u.f.completed==0&&u.m_dtc_l1_oo_lower_responses==0);
 // A finite idle wait cannot invent absent sector returns. This is an API-path counterexample, not a full model replay.
 for(unsigned i=0;i<64;++i){assert(cluster.q.empty());assert(!u.m_dtc_l1_oo_inflight.empty());}
 shader_core_ctx c2;ldst_unit control;control.m_core=&c2;auto*r2=new mem_fetch;r2->uid=2;r2->addr=0x2000;control.m_dtc_l1_oo_inflight.emplace(2,ldst_unit::dtc_l1_oo_inflight{8,0x2000,10,0xf,0});
 for(unsigned sector=0;sector<4;++sector){auto*child=new mem_fetch;child->uid=10+sector;child->addr=0x2000+sector*32;child->original=r2;assert(control.dtc_l1_oo_consume_response(child));if(sector<3)assert(!control.m_dtc_l1_oo_inflight.empty());}
 assert(control.m_dtc_l1_oo_inflight.empty()&&c2.gpu.completed==1&&control.f.completed==1&&control.m_dtc_l1_oo_lower_responses==1);
 shader_core_ctx c3;simt_core_cluster q3;perfect_memory_interface p3(&c3,&q3);mem_fetch a;a.atomic=true;p3.push(&a);assert(a.atomic_side_effects==1&&q3.q.size()==1);
 assert(!dtc_l1::response_sector_is_new(15,1,0));assert(dtc_l1::response_sector_is_new(15,1,1));
 std::cout<<"{\"status\":\"PASS_EXPECTED_COUNTEREXAMPLE_AND_CONTROL\",\"perfect_whole128_response_mask\":1,\"expected_mask\":15,\"inflight_remaining\":1,\"lower_credit_releases\":0,\"four_sector_control_completed\":true,\"atomic_callback_once\":true,\"response_FIFO_backpressure_preserved\":true,\"model_main_executed\":false}\n";
}
