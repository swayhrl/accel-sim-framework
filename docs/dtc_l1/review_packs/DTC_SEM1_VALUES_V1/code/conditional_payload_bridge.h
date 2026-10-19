// PREPARED_NOT_TESTED / UNBOUND. Not a production test or payload implementation.
// No entrypoint, no dispatcher, no reference-memory access. See bridge contract.
#ifndef DTC_SEM1_CONDITIONAL_PAYLOAD_BRIDGE_H
#define DTC_SEM1_CONDITIONAL_PAYLOAD_BRIDGE_H
#include <array>
#include <cstdint>
#include <map>
#include <stdexcept>
#include <utility>
namespace dtc_sem1 {
struct identity { unsigned id; std::uint64_t generation; };
using sector_bytes = std::array<std::uint8_t, 32>;
struct observation {
  std::uint64_t consumer_uid;
  identity physical;
  unsigned sector;
  sector_bytes bytes;
};
// Owned by an isolated diagnostic Core. Uninstantiated/default OFF in production.
class conditional_payload_bridge {
  struct line {
    std::uint64_t generation;
    std::uint8_t received = 0;
    std::array<sector_bytes, 4> sectors{};
  };
  struct root { identity physical; std::uint8_t expected; };
  std::map<unsigned, line> lines_;
  std::map<std::uint64_t, root> roots_;
  line &live(identity p) {
    auto it = lines_.find(p.id);
    require(it != lines_.end() && it->second.generation == p.generation,
            "stale or missing physical generation");
    return it->second;
  }
  static void require(bool ok, const char *why) {
    if (!ok) throw std::logic_error(why);
  }
 public:
  // Called only after successful actual allocation, never from a prediction.
  void allocated(identity p) {
    require(lines_.emplace(p.id, line{p.generation}).second,
            "allocation before prior generation release");
  }
  // Caller supplies the exact successful production inflight insertion.
  void root_accepted(std::uint64_t uid, identity p, std::uint8_t expected) {
    (void)live(p);
    require(expected && !(expected & ~0xFU), "invalid expected sectors");
    require(roots_.emplace(uid, root{p, expected}).second, "duplicate root UID");
  }
  // Test bytes originate in a fixture refill packet, NOT in expected memory.
  // Actual production reply identity/address/sector validation must run first.
  void reply_accepted(std::uint64_t root_uid, unsigned sector,
                      const sector_bytes &packet_bytes) {
    auto it = roots_.find(root_uid);
    require(it != roots_.end() && sector < 4, "unknown root or bad sector");
    auto &data = live(it->second.physical);
    const auto bit = static_cast<std::uint8_t>(1U << sector);
    require((it->second.expected & bit) && !(data.received & bit),
            "unexpected or duplicate sector");
    data.sectors[sector] = packet_bytes;
    data.received |= bit;
    if ((data.received & it->second.expected) == it->second.expected)
      roots_.erase(it);
  }
  // Called once for an actual committed collection quota, using its adapter
  // cursor's accepted physical/sector. Adapter must retain cursor on WB reject.
  // Actual consumer readiness is a production predicate, never a fixture guess.
  observation collected(std::uint64_t uid, identity p, unsigned sector,
                        bool production_consumer_ready) {
    auto &data = live(p);
    require(production_consumer_ready, "unnotified or unready consumer");
    require(sector < 4 && (data.received & (1U << sector)), "missing sector");
    return {uid, p, sector, data.sectors[sector]};
  }
  // This is an assertion on a real production release, not permission to release.
  void released(identity p, std::uint64_t production_refs) {
    (void)live(p);
    require(production_refs == 0, "release with live production Ref");
    for (const auto &kv : roots_)
      require(kv.second.physical.id != p.id ||
                  kv.second.physical.generation != p.generation,
              "release with pending root");
    lines_.erase(p.id);
  }
};
} // namespace dtc_sem1
#endif
