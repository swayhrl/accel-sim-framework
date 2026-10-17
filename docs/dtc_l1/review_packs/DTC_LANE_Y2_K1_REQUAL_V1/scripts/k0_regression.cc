// Independent CPU probes. Includes an unmodified, published common header.
// No simulator kernels or production source edits. Assertions MUST stay on.
#include "dtc-l1-common.h"
#include <iostream>
#include <string>
#include <cstdlib>
#ifdef NDEBUG
#error "Safety probes require assertions"
#endif
using namespace dtc_l1;
static void require(bool value) { if (!value) std::exit(1); }
static config geometry(mode m) {
  config c; c.selected_mode=m; c.logical_sets=1; c.logical_ways=1;
  c.physical_lines=2; c.allocation_width=4; c.io_pib_entries=8;c.oo_pib_entries=8;
  return c;
}
int main(int argc,char **argv) {
  if(argc!=2)return 64;
  std::string name=argv[1];
  std::cout << std::boolalpha;
  if(name=="io_sidecar_mapping_preserved") {
    io_frontend f(geometry(mode::PAPER_IO));require(f.admit(1));auto a=f.access(1,1,0);f.complete(a.physical);require(f.retire_head());
    require(f.admit(2));f.add_external_dependency(2);require(!f.entry_ready_for(2));f.complete_external_dependency(2);require(f.retire_head());
    require(f.admit(3));auto b=f.access(3,3,0);require(b.kind==io_access_kind::VALID_HIT && b.physical.id==a.physical.id && b.physical.generation==a.physical.generation);
    require(f.retire_head());std::cout<<"{\"mapping_unchanged\":"<<(b.physical.id==a.physical.id && b.physical.generation==a.physical.generation)<<",\"new_misses\":"<<f.new_misses()<<",\"valid_hits\":"<<f.valid_hits()<<",\"occupancy\":"<<f.occupancy()<<"}";
  } else if(name=="oo_sidecar_mapping_preserved") {
    oo_frontend f(geometry(mode::PAPER_OO));require(f.admit(1));auto a=f.access(1,1,0);f.complete(a.physical);require(f.retire_ready_uid(10,1));
    require(f.admit(2));f.add_external_dependency(2);require(!f.entry_ready_for(2));f.complete_external_dependency(2);require(f.retire_ready_uid(11,2));
    require(f.admit(3));auto b=f.access(3,3,0);require(b.kind==io_access_kind::VALID_HIT && b.physical.id==a.physical.id && b.physical.generation==a.physical.generation);
    require(f.retire_ready_uid(12,3));std::cout<<"{\"mapping_unchanged\":"<<(b.physical.id==a.physical.id && b.physical.generation==a.physical.generation)<<",\"new_misses\":"<<f.new_misses()<<",\"valid_hits\":"<<f.valid_hits()<<",\"occupancy\":"<<f.occupancy()<<"}";
  } else if(name=="io_pending_and_replacement") {
    io_frontend f(geometry(mode::PAPER_IO));
    require(f.admit(1));auto a=f.access(1,1,0);
    require(f.admit(2));auto b=f.access(2,2,0);
    require(a.kind==io_access_kind::NEW_MISS && b.kind==io_access_kind::PENDING_HIT);
    require(a.physical.id==b.physical.id && a.physical.generation==b.physical.generation);
    require(f.admit(3));auto c=f.access(3,3,128);
    require(f.allocated_lines()==2 && !f.retire_head());
    f.complete(c.physical);require(!f.retire_head());f.complete(a.physical);
    require(f.retire_head() && f.allocated_lines()==2);
    require(f.retire_head() && f.allocated_lines()==2);
    require(f.retire_head() && f.allocated_lines()==1);
    std::cout<<"{\"occupancy\":"<<f.occupancy()<<",\"allocated\":"<<f.allocated_lines()<<",\"releases\":"<<f.releases()<<",\"pending_hits\":"<<f.pending_hits()<<"}";
  } else if(name=="oo_last_ref_and_reuse" || name=="oo_stale_fill_reject" || name=="oo_slot_reuse") {
    auto cfg=geometry(mode::PAPER_OO);oo_frontend f(cfg);
    require(f.admit(1));auto a=f.access(1,1,0);
    require(f.admit(2));auto b=f.access(2,2,0);
    require(f.ref_count(a.physical)==2 && b.kind==io_access_kind::PENDING_HIT);
    require(f.admit(3));auto c=f.access(3,3,128);
    require(!f.tag_visible(a.physical) && f.is_allocated(a.physical));
    unsigned slot=f.entry_slot(1);auto generation=f.entry_slot_generation(1);
    f.complete(a.physical);require(f.retire_ready_uid(10,1));
    require(f.is_allocated(a.physical) && f.ref_count(a.physical)==1);
    require(f.admit(4));bool slot_advanced=f.entry_slot(4)==slot && f.entry_slot_generation(4)>generation;require(slot_advanced);
    require(f.retire_ready_uid(11,2));require(!f.is_allocated(a.physical));
    auto d=f.access(12,4,256);
    require(d.physical.id==a.physical.id && d.physical.generation>a.physical.generation);
    require(!f.fill_identity_matches(a.physical));
    if(name=="oo_stale_fill_reject") { f.complete(a.physical);return 1; }
    f.complete(c.physical);require(f.retire_ready_uid(13,3));
    require(!f.entry_ready_for(4));f.complete(d.physical);require(f.retire_ready_uid(14,4));
    f.assert_shadow_refs();
    std::cout<<"{\"occupancy\":"<<f.occupancy()<<",\"active_refs\":"<<f.active_refs()<<",\"allocated\":"<<f.allocated_lines()<<",\"final_ref_reclaims\":"<<f.final_ref_reclaims()<<",\"stale_identity_matches\":"<<f.fill_identity_matches(a.physical)<<",\"slot_generation_advanced\":"<<slot_advanced<<"}";
  } else if(name=="oo_late_merge_finite" || name=="oo_duplicate_fill_reject") {
    auto cfg=geometry(mode::PAPER_OO);cfg.finite_service=true;oo_frontend f(cfg);
    f.advance_service(1);require(f.admit(1));auto a=f.access(1,1,0);
    for(unsigned uid=2;uid<=6;++uid){require(f.admit(uid));require(f.access(uid,uid,0).kind==io_access_kind::PENDING_HIT);}
    f.complete(a.physical);
    if(name=="oo_duplicate_fill_reject"){f.complete(a.physical);return 1;}
    f.advance_service(2);require(f.wakeups()==4 && !f.entry_ready_for(1));
    require(f.admit(7));require(f.access(2,7,0).kind==io_access_kind::PENDING_HIT);
    f.advance_service(3);require(f.wakeups()==7);
    for(unsigned uid=1;uid<=7;++uid)require(f.retire_ready_uid(10+uid,uid));
    f.assert_shadow_refs();std::cout<<"{\"occupancy\":"<<f.occupancy()<<",\"active_refs\":"<<f.active_refs()<<",\"wakeups\":"<<f.wakeups()<<",\"pending_hits\":"<<f.pending_hits()<<"}";
  } else if(name=="sector_interleave" || name=="sector_duplicate_reject" || name=="sector_unrequested_reject" || name=="sector_old_generation_reject") {
    sector_oo_frontend f(geometry(mode::MODERN_OO_SECTOR));
    require(f.admit(1));auto a=f.access(1,1,0,15);
    require(f.admit(2));auto b=f.access(2,2,0,15);
    require(a.new_request_mask==15 && b.pending_mask==15 && !b.new_request_mask);
    f.complete_sector(a.physical,3);
    if(name=="sector_duplicate_reject"){f.complete_sector(a.physical,3);return 1;}
    require(f.admit(3));auto c=f.access(3,3,128,1);
    require(!f.tag_visible(a.physical) && f.ref_count(a.physical)==2);
    if(name=="sector_unrequested_reject"){f.complete_sector(c.physical,2);return 1;}
    for(unsigned s:{1u,0u})f.complete_sector(a.physical,s);
    require(!f.entry_ready_for(1));f.complete_sector(a.physical,2);
    require(f.entry_ready_for(1) && f.entry_ready_for(2));
    require(f.retire_ready_uid(10,1) && f.ref_count(a.physical)==1);
    require(f.retire_ready_uid(11,2) && !f.is_allocated(a.physical));
    require(f.admit(4));auto d=f.access(12,4,256,1);
    require(d.physical.id==a.physical.id && d.physical.generation>a.physical.generation);
    if(name=="sector_old_generation_reject"){f.complete_sector(a.physical,0);return 1;}
    f.complete_sector(c.physical,0);f.complete_sector(d.physical,0);
    require(f.retire_ready_uid(13,3) && f.retire_ready_uid(14,4));f.assert_shadow_refs();
    std::cout<<"{\"occupancy\":"<<f.occupancy()<<",\"active_refs\":"<<f.active_refs()<<",\"sector_responses\":"<<f.sector_responses()<<",\"wakeups\":"<<f.wakeups()<<",\"final_ref_reclaims\":"<<f.final_ref_reclaims()<<"}";
  } else if(name=="tag_banks") {
    auto cfg=geometry(mode::PAPER_OO);cfg.logical_sets=32;
    io_frontend io(cfg);oo_frontend oo(cfg);sector_oo_frontend sector(cfg);
    for(unsigned b=0;b<4;++b){require(io.try_serve_tag(1,b*128));require(oo.try_serve_tag(1,b*128));require(sector.try_serve_tag(1,b*128));}
    require(!io.try_serve_tag(1,4*128) && !oo.try_serve_tag(1,4*128) && !sector.try_serve_tag(1,4*128));
    require(io.try_serve_tag(2,4*128) && oo.try_serve_tag(2,4*128) && sector.try_serve_tag(2,4*128));
    require(io.tag_requests()==oo.tag_requests());require(io.tag_conflicts()==oo.tag_conflicts());
    std::cout<<"{\"grants_per_mode\":"<<io.tag_requests()<<",\"conflicts_per_mode\":"<<io.tag_conflicts()<<"}";
  } else if(name=="response_sector_guard") {
    unsigned received=0;
    for(unsigned s:{3u,1u,0u,2u}){require(response_sector_is_new(15,received,s));received|=1u<<s;require(!response_sector_is_new(15,received,s));}
    require(!response_sector_is_new(1,0,3));require(!response_sector_is_new(15,0,4));
    std::cout<<"{\"received\":"<<received<<",\"duplicate_rejected\":"<<!response_sector_is_new(15,received,0)<<",\"unrequested_rejected\":"<<!response_sector_is_new(1,0,3)<<",\"out_of_range_rejected\":"<<!response_sector_is_new(15,0,4)<<"}";
  } else return 78;
  std::cout<<"\n";return 0;
}
