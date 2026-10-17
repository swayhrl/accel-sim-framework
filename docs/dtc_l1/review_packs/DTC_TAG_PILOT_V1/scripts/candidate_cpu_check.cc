// Directed structural checks; production header is unmodified. No simulation replay.
#include <cassert>
#include <cstdio>
#include "dtc-l1-common.h"

static void ready(dtc_l1::oo_frontend &f, dtc_l1::physical_identity id, uint64_t c) {
  f.advance_service(c);
  f.complete(id);
  f.advance_service(c+1);
  f.advance_service(c+2);
}

static void check_oo(unsigned sets, unsigned ways) {
  dtc_l1::config cfg;
  cfg.selected_mode = dtc_l1::mode::PAPER_OO;
  cfg.finite_service = true;
  cfg.logical_sets = sets;
  cfg.logical_ways = ways;
  dtc_l1::oo_frontend f(cfg);
  for (unsigned bank=0; bank<4; ++bank) {
    assert(f.try_serve_tag(1, bank*128));
    assert(!f.try_serve_tag(1, (sets+bank)*128));
  }
  // Populate every Tag and prove all entries are searchable without reallocating.
  unsigned count=sets*ways;
  for (unsigned line=0; line<count; ++line) {
    uint64_t c=10*line+10;
    f.advance_service(c);
    assert(f.admit(line+1));
    assert(f.try_serve_tag(c,line*128));
    auto a=f.access(c+1,line+1,line*128);
    assert(a.kind==dtc_l1::io_access_kind::NEW_MISS);
    ready(f,a.physical,c+1);
    assert(f.retire_ready_uid(c+4,line+1));
  }
  assert(f.allocated_lines()==count);
  for (unsigned line=0; line<count; ++line) {
    uint64_t c=10*(line+count)+10;
    f.advance_service(c);
    assert(f.admit(10000+line));
    assert(f.access(c,10000+line,line*128).kind==dtc_l1::io_access_kind::VALID_HIT);
    assert(f.retire_ready_uid(c+1,10000+line));
  }
  assert(f.new_misses()==count && f.active_refs()==0 && f.occupancy()==0);
  // Pending old mapping survives same-set replacement and exact old return.
  dtc_l1::oo_frontend pending(cfg);
  dtc_l1::physical_identity old;
  for (unsigned way=0; way<ways; ++way) {
    uint64_t c=10000+10*way;
    pending.advance_service(c);
    assert(pending.admit(way+1));
    auto a=pending.access(c,way+1,way*sets*128);
    assert(a.kind==dtc_l1::io_access_kind::NEW_MISS);
    if (way==0) old=a.physical;
    else { ready(pending,a.physical,c); assert(pending.retire_ready_uid(c+3,way+1)); }
  }
  uint64_t c=11000;
  pending.advance_service(c);
  assert(pending.admit(900));
  auto a=pending.access(c,900,ways*sets*128);
  assert(a.kind==dtc_l1::io_access_kind::NEW_MISS);
  assert(pending.fill_identity_matches(old) && !pending.tag_visible(old));
  assert(pending.ref_count(old)==1);
  ready(pending,old,c+1);
  assert(pending.retire_ready_uid(c+4,1));
  assert(!pending.fill_identity_matches(old));
  ready(pending,a.physical,c+5);
  assert(pending.retire_ready_uid(c+8,900));
  assert(pending.active_refs()==0 && pending.occupancy()==0);
  pending.assert_shadow_refs();
  std::printf("OO sets=%u ways=%u entries=%u bank_quota/search/retained/pending_replacement/generation/ref PASS\n",sets,ways,count);
}

static void check_io128() {
  dtc_l1::config cfg;
  cfg.finite_service=true;
  cfg.io_pib_entries=128;
  dtc_l1::io_frontend f(cfg);
  for (unsigned uid=1; uid<=128; ++uid) assert(f.admit(uid));
  assert(!f.admit(129));
  assert(f.occupancy()==128 && f.allocated_lines()==0);
  std::printf("IO active_PIB128 admission_bound PASS\n");
}

int main() {
  check_io128();
  check_oo(32,4); // unchanged original reference, CPU only
  check_oo(32,8);
  check_oo(64,4);
  check_oo(64,8);
}
