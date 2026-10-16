// Lane 5 consumer-owned reference: drives the frozen Lane 2 directory directly.
// Backing bytes are TEST-ONLY. This does not qualify l2_cache producer wiring.
#include <array>
#include <cassert>
#include <cstdio>
#include <map>
#include <utility>
#include "gpgpu-sim/ep-l2-tvd-directory.h"

typedef ep_l2::PayloadHandle Handle;
typedef ep_l2_tvd_directory<Handle> Directory;
typedef std::array<unsigned char, 32> Sector;
typedef std::array<Sector, 4> Line;
typedef std::pair<unsigned, unsigned> HandleKey;

static Line pattern(unsigned seed) {
  Line line;
  for (unsigned sector = 0; sector < 4; ++sector)
    for (unsigned byte = 0; byte < 32; ++byte)
      line[sector][byte] = static_cast<unsigned char>(seed + sector * 37 + byte);
  return line;
}

static Directory::ticket install(Directory &directory, unsigned line,
                                 Handle handle, unsigned valid, unsigned dirty,
                                 bool writeback, unsigned cycle) {
  Directory::install_plan plan = directory.preview_install(line, writeback);
  assert(plan.status == Directory::OK);
  Directory::ticket ticket;
  assert(directory.commit_install(plan, line, handle, valid, dirty, 0,
                                  writeback, cycle, ticket) == Directory::OK);
  return ticket;
}

static void verify_read(Directory &directory, unsigned line, unsigned sector,
                        const Line &independent_expected,
                        const std::map<HandleKey, Line> &backing,
                        unsigned miss_cycle, unsigned response_cycle) {
  Directory::observation observed = directory.preview_access(
      line, 1u << sector, Directory::READ, miss_cycle, miss_cycle + 1);
  assert(observed.status == Directory::READ_READY);
  Directory::read_lease lease;
  assert(directory.begin_read(observed, 1u << sector, lease) == Directory::OK);
  const Handle actual = lease.handle();
  const Sector &actual_bytes = backing.at(HandleKey(actual.payload_id,
                                                  actual.generation))[sector];
  // Compare the actual handle's bytes with address/version reference bytes,
  // rather than asserting a constant unrelated to the module's returned handle.
  assert(actual_bytes == independent_expected[sector]);
  assert(directory.response_commit(lease, response_cycle) == Directory::OK);
  assert(directory.response_commit(lease, response_cycle) == Directory::STALE);
}

int main() {
  std::map<HandleKey, Line> backing;
  const Handle a(11, 7), b(12, 8);
  const Line expected_a = pattern(17), expected_b = pattern(91);
  backing[HandleKey(11, 7)] = expected_a;
  backing[HandleKey(12, 8)] = expected_b;
  Directory directory(2, true, true);
  Directory::ticket ta = install(directory, 0x1000, a, 15, 0, false, 0);
  Directory::ticket tb = install(directory, 0x2000, b, 5, 5, true, 0);
  assert(directory.preview_access(0x1000, 1, Directory::READ, 4, 4).status ==
         Directory::LOOKUP_DELAY);
  verify_read(directory, 0x1000, 3, expected_a, backing, 4, 6);

  // Missing sector on a dirty victim must not become a whole-line TVD hit.
  assert(directory.preview_access(0x2000, 2, Directory::READ, 6, 7).status ==
         Directory::WAIT_WRITEBACK);
  assert(directory.lower_accept(tb, false, 7) == Directory::DATA_TRANSFER_UNPROVEN);
  assert(directory.at(tb.index).status == Directory::WB_STAGED);
  assert(directory.lower_accept(tb, true, 8) == Directory::OK);
  assert(directory.preview_access(0x2000, 1, Directory::WRITE, 8, 9).status ==
         Directory::WAIT_WRITEBACK);
  assert(directory.preview_access(0x2000, 1, Directory::ATOMIC, 8, 9).status ==
         Directory::WAIT_WRITEBACK);
  verify_read(directory, 0x2000, 2, expected_b, backing, 9, 11);
  assert(directory.stats().dirty_forward_responses == 1);
  assert(directory.set_done(tb, 12) == Directory::OK);
  assert(directory.preview_access(0x2000, 2, Directory::READ, 12, 13).status ==
         Directory::MISSING_SECTOR);

  // Promotion returns the same handle; update its TEST-ONLY bytes as a write,
  // then check the next directory incarnation against the new reference version.
  Handle promoted;
  assert(directory.promote(ta, promoted, 13) == Directory::OK);
  assert(promoted == a && !directory.live(ta));
  const Line new_version = pattern(221);
  backing[HandleKey(a.payload_id, a.generation)] = new_version;
  Directory::ticket ta2 = install(directory, 0x1000, a, 15, 0, false, 14);
  assert(ta2.incarnation != ta.incarnation);
  verify_read(directory, 0x1000, 0, new_version, backing, 14, 16);
  Handle released;
  assert(directory.reclaim(ta, released, 17) == Directory::STALE);
  assert(directory.live(ta2));
  assert(directory.reclaim(ta2, released, 17) == Directory::OK && released == a);
  assert(directory.reclaim(tb, released, 17) == Directory::OK && released == b);
  assert(directory.occupied() == 0 && directory.epoch_ready());
  assert(directory.stats().read_responses == 3);
  assert(directory.stats().avoided_lower_bytes == 96);
  assert(directory.stats().lower_accepts == 1 && directory.stats().wb_completions == 1);
  std::puts("LANE5_TVD_CONSUMER_REFERENCE_MODULE_PASS: 3 byte/version reads; exact-once; dirty handoff; stale incarnation");
}
