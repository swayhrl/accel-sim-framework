#ifndef ACCEL_SIM_AG7_POLICYB_PROGRESS_H
#define ACCEL_SIM_AG7_POLICYB_PROGRESS_H

// Experimental, default-OFF, observational producer. This header never receives
// a model pointer. Only the simulation thread supplies coherent scalar snapshots.
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>

namespace dtc_ag7 {
struct PreserveErrno {
  int saved = errno;
  ~PreserveErrno() { errno = saved; }
};
class ProgressProducer {
 public:
  ProgressProducer() {
    PreserveErrno preserve_errno;
    const char *opt_in = std::getenv("DTC_AG7_POLICY_B_PROGRESS");
    if (!opt_in || std::strcmp(opt_in, "1") != 0) return;
    // Invalid requested configurations emit nothing: the independently bound
    // receiver must reject absent/stale data. Never repair flags or model state.
    const char *fd = std::getenv("DTC_AG7_PROGRESS_FD");
    const char *generation = std::getenv("DTC_AG7_GENERATION");
    const char *input = std::getenv("DTC_AG7_INPUT_SHA");
    const char *roi = std::getenv("DTC_AG7_ROI_SHA");
    uint64_t descriptor = 0;
    if (!decimal(fd, descriptor) || descriptor < 3 || descriptor > 1048575 ||
        !token(generation) || !hex(input, 64) || !hex(roi, 64)) return;
    fd_ = static_cast<int>(descriptor);
    const int flags = fcntl(fd_, F_GETFL);
    int type = 0;
    socklen_t size = sizeof(type);
    sockaddr_un address{};
    socklen_t address_size = sizeof(address);
    if (flags < 0 || !(flags & O_NONBLOCK) ||
        getsockopt(fd_, SOL_SOCKET, SO_TYPE, &type, &size) != 0 ||
        (type != SOCK_DGRAM && type != SOCK_SEQPACKET) ||
        getsockname(fd_, reinterpret_cast<sockaddr *>(&address),
                    &address_size) != 0 || address.sun_family != AF_UNIX) return;
    pid_ = getpid();
    if (!read_start_ticks(start_ticks_)) return;
    std::memcpy(input_, input, 65);
    std::memcpy(roi_, roi, 65);
    std::strcpy(generation_, generation);
    enabled_ = true;
  }

  bool enabled() const { return enabled_; }

  // epoch=0 is the whole-input cumulative instruction epoch. phase_epoch only
  // identifies phase transitions; it NEVER resets a receiver's finite deadline.
  // stream_id=-1 means whole-input/multiple-or-no-active-stream, not stream zero.
  void observe(const char *phase, uint64_t completed, bool semantic_valid,
               bool force = false, const char *terminal = "NONE",
               int64_t stream_id = -1) {
    PreserveErrno preserve_errno;
    if (!enabled_) return;
    if (getpid() != pid_ || (semantic_valid && completed < last_completed_)) {
      enabled_ = false;
      return;
    }
    timespec ts{};
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0 || ts.tv_sec < 0) {
      enabled_ = false;
      return;
    }
    const uint64_t now = uint64_t(ts.tv_sec) * 1000000000ULL + ts.tv_nsec;
    if (now < last_clock_) { enabled_ = false; return; }
    last_clock_ = now;
    if (semantic_valid) last_completed_ = completed;
    if (std::strcmp(phase_, phase) != 0) {
      if (std::strlen(phase) >= sizeof(phase_)) {
        enabled_ = false;
        return;
      }
      std::strcpy(phase_, phase);
      ++phase_epoch_;
      force = true;
    }
    if (!force && emitted_ && now - last_emitted_ns_ < kCadenceNs) return;
    if (sequence_ >= kMaximumRecords) { enabled_ = false; return; }
    char packet[kMaximumPacket];
    const int bytes = std::snprintf(
        packet, sizeof(packet),
        "{\"v\":1,\"pid\":%ld,\"start_ticks\":%llu,"
        "\"generation\":\"%s\",\"input\":\"%s\",\"roi\":\"%s\","
        "\"seq\":%llu,\"mono_ns\":%llu,\"epoch\":0,"
        "\"phase_epoch\":%llu,\"phase\":\"%s\",\"stream_id\":%lld,"
        "\"stream_scope\":\"whole_input\",\"completed\":%llu,"
        "\"end\":\"%s\"}\n",
        static_cast<long>(pid_), static_cast<unsigned long long>(start_ticks_),
        generation_, input_, roi_,
        static_cast<unsigned long long>(sequence_ + 1),
        static_cast<unsigned long long>(now),
        static_cast<unsigned long long>(phase_epoch_), phase_,
        static_cast<long long>(stream_id),
        static_cast<unsigned long long>(completed), terminal);
    if (bytes < 0 || static_cast<size_t>(bytes) >= sizeof(packet)) {
      enabled_ = false;
      return;
    }
    // No retries, queue draining, disk writes, SIGPIPE, callbacks, state repair,
    // model writes or blocking transport. Missing data is fail-closed upstream.
    const ssize_t sent = send(fd_, packet, static_cast<size_t>(bytes),
                              MSG_DONTWAIT | MSG_NOSIGNAL);
    if (sent != bytes) { enabled_ = false; return; }
    ++sequence_;
    emitted_ = true;
    last_emitted_ns_ = now;
  }

 private:
  static constexpr uint64_t kCadenceNs = 10000000000ULL;
  static constexpr uint64_t kMaximumRecords = 8192;
  static constexpr size_t kMaximumPacket = 1024;
  static bool token(const char *text) {
    if (!text || !*text || std::strlen(text) > 64) return false;
    for (const char *p = text; *p; ++p)
      if (!((*p >= 'a' && *p <= 'z') || (*p >= 'A' && *p <= 'Z') ||
            (*p >= '0' && *p <= '9') || *p == '-' || *p == '_' ||
            *p == '.' || *p == ':')) return false;
    return true;
  }
  static bool decimal(const char *text, uint64_t &out) {
    if (!text || !*text || std::strlen(text) > 20) return false;
    uint64_t value = 0;
    for (const char *p = text; *p; ++p) {
      if (*p < '0' || *p > '9') return false;
      const unsigned digit = unsigned(*p - '0');
      if (value > (UINT64_MAX - digit) / 10) return false;
      value = value * 10 + digit;
    }
    out = value;
    return true;
  }
  static bool hex(const char *text, size_t length) {
    if (!text || std::strlen(text) != length) return false;
    for (size_t i = 0; i < length; ++i)
      if (!((text[i] >= '0' && text[i] <= '9') ||
            (text[i] >= 'a' && text[i] <= 'f'))) return false;
    return true;
  }
  static bool read_start_ticks(uint64_t &out) {
    const int fd = open("/proc/self/stat", O_RDONLY | O_CLOEXEC);
    if (fd < 0) return false;
    char data[4096];
    const ssize_t bytes = read(fd, data, sizeof(data) - 1);
    close(fd);
    if (bytes <= 0 || bytes >= static_cast<ssize_t>(sizeof(data) - 1)) return false;
    data[bytes] = '\0';
    char *p = std::strrchr(data, ')');
    if (!p || p[1] != ' ') return false;
    p += 2;  // field 3 (state), after the parenthesized comm field.
    for (unsigned field = 3; field < 22; ++field) {
      p = std::strchr(p, ' ');
      if (!p) return false;
      ++p;
    }
    char *end = std::strchr(p, ' ');
    if (!end) return false;
    *end = '\0';
    return decimal(p, out) && out > 0;
  }
  bool enabled_ = false;
  bool emitted_ = false;
  int fd_ = -1;
  pid_t pid_ = 0;
  uint64_t start_ticks_ = 0, sequence_ = 0;
  uint64_t last_clock_ = 0, last_emitted_ns_ = 0, last_completed_ = 0;
  uint64_t phase_epoch_ = 0;
  char input_[65]{}, roi_[65]{}, generation_[65]{}, phase_[32]{};
};
}  // namespace dtc_ag7
#endif
