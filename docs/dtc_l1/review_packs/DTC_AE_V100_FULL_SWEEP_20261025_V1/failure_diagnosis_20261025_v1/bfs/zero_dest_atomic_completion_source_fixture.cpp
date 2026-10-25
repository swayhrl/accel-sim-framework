#include <cassert>
#include <map>
#include <iostream>
#include "dtc-l1-common.h"
constexpr unsigned MAX_OUTPUT_VALUES=8;
constexpr int shared_space=1;
struct Space { int get_type() const { return 0; } };
struct warp_inst_t { unsigned out[MAX_OUTPUT_VALUES]={}; Space space; bool m_is_ldgsts=false; bool fence=false; bool atomic=true; unsigned warp_id() const{return 1;} unsigned get_uid() const{return 1;} bool is_syncs() const{return false;} bool is_arrives() const{return false;} bool is_fence() const{return fence;} };
struct Score { void releaseRegister(unsigned,unsigned){} };
struct Core { void warp_inst_complete(warp_inst_t&){} void unset_depbar(warp_inst_t&){} };
class ldst_unit { public: Core core; Score score; Core *m_core=&core; Score *m_scoreboard=&score; std::map<unsigned,std::map<unsigned,unsigned>> m_pending_writes,m_pending_ldgsts; void dtc_l1_r4c2_trace_pending_mutation(warp_inst_t&,unsigned,unsigned,int,unsigned,const char*){} void dtc_l1_retire(warp_inst_t&){} bool writeback_complete(warp_inst_t&); };
bool ldst_unit::writeback_complete(warp_inst_t &inst) {
  bool insn_completed = false;
  for (unsigned r = 0; r < MAX_OUTPUT_VALUES; r++) {
    if (inst.out[r] > 0) {
      if (inst.space.get_type() != shared_space) {
        assert(m_pending_writes[inst.warp_id()][inst.out[r]] > 0);
        const unsigned before = m_pending_writes[inst.warp_id()][inst.out[r]];
        unsigned still_pending =
            --m_pending_writes[inst.warp_id()][inst.out[r]];
        dtc_l1_r4c2_trace_pending_mutation(
            inst, inst.out[r], before, -1, still_pending,
            "CONVENTIONAL_WRITEBACK_COMPLETE");
        if (!still_pending) {
          m_pending_writes[inst.warp_id()].erase(inst.out[r]);
          m_scoreboard->releaseRegister(inst.warp_id(), inst.out[r]);
          insn_completed = true;
        }
      } else {  // shared
        m_scoreboard->releaseRegister(inst.warp_id(), inst.out[r]);
        insn_completed = true;
      }
    } else if (inst.m_is_ldgsts) {  // for LDGSTS instructions where no
                                    // output register is used
      m_pending_ldgsts[inst.warp_id()][inst.get_uid()]--;
      if (m_pending_ldgsts[inst.warp_id()][inst.get_uid()] == 0) {
        insn_completed = true;
      }
      break;
    } else if (inst.is_syncs() || inst.is_arrives() || inst.is_fence()) {
      // For mbarrier instructions and fence instructions that
      // go through the ldst_unit, they might not have output registers,
      // so we capture these and mark them as completed
      // For TMA instructions, they are completed
      // in ldst_unit::cycle()
      insn_completed = true;
    }
  }
  if (insn_completed) {
    m_core->warp_inst_complete(inst);
    dtc_l1_retire(inst);
    if (inst.m_is_ldgsts) {
      // If the LDGSTS instruction is done, we need to erase it from the
      // pending LDGSTS map and unset the DEPBAR
      m_pending_ldgsts[inst.warp_id()].erase(inst.get_uid());
      m_core->unset_depbar(inst);
    }
  }
  return insn_completed;
}

int main(){
 ldst_unit l; warp_inst_t no_dest; bool missing=l.writeback_complete(no_dest); assert(!missing);
 warp_inst_t no_dest_red; assert(!l.writeback_complete(no_dest_red)); // RED and ATOMG decode to LOAD_OP+atomic+global with zero outputs.
 warp_inst_t with_dest; with_dest.out[0]=1;l.m_pending_writes[1][1]=1;assert(l.writeback_complete(with_dest));
 warp_inst_t fence;fence.fence=true;assert(l.writeback_complete(fence));
 for(bool hashed:{false,true}){
 dtc_l1::config c;c.selected_mode=dtc_l1::mode::PAPER_OO;c.finite_service=true;c.logical_sets=64;c.logical_ways=8;c.physical_lines=640;c.oo_pib_entries=128;c.tag_hash_bankrow=hashed;dtc_l1::oo_frontend f(c);
 for(unsigned i=1;i<=128;i++){assert(f.admit(i));f.add_external_dependency(i);assert(!f.entry_ready_for(i));if(l.writeback_complete(no_dest))f.complete_external_dependency(i);assert(!f.entry_ready_for(i));}
 assert(!f.admit(129));f.complete_external_dependency(1);assert(f.entry_ready_for(1));
 }
 std::cout<<"PASS exact frozen writeback_complete zero-dest ATOMG=false and RED=false; returning-atomic destination and fence controls=true; actual OO header external-dependency leak fills 128 and refuses 129 for AE=0 and AE=1\n";
}
