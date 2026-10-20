// DECLARED_SYNTHETIC CPU transport probe. Never links/loads a GPU model or trace.
// Source prepared only; execution requires the controller's fresh heavy R2.
#include "ag7_policyb_progress.h"
#include <string>

static bool receive_packet(int fd, unsigned sequence, const char *terminal) {
  char bytes[1024];
  char ancillary[CMSG_SPACE(sizeof(struct ucred))]{};
  iovec data{bytes, sizeof(bytes)};
  msghdr message{};
  message.msg_iov = &data;
  message.msg_iovlen = 1;
  message.msg_control = ancillary;
  message.msg_controllen = sizeof(ancillary);
  const ssize_t received = recvmsg(fd, &message, MSG_DONTWAIT);
  if (received <= 0 || received >= static_cast<ssize_t>(sizeof(bytes)) ||
      message.msg_flags & (MSG_TRUNC | MSG_CTRUNC)) return false;
  bool correct_credentials = false;
  for (cmsghdr *c = CMSG_FIRSTHDR(&message); c; c = CMSG_NXTHDR(&message, c)) {
    if (c->cmsg_level == SOL_SOCKET && c->cmsg_type == SCM_CREDENTIALS &&
        c->cmsg_len == CMSG_LEN(sizeof(struct ucred))) {
      struct ucred credential{};
      std::memcpy(&credential, CMSG_DATA(c), sizeof(credential));
      correct_credentials = credential.pid == getpid() &&
          credential.uid == getuid() && credential.gid == getgid();
    }
  }
  const std::string packet(bytes, static_cast<size_t>(received));
  return correct_credentials && packet.find("\"v\":1,") != std::string::npos &&
      packet.find("\"seq\":" + std::to_string(sequence) + ",") != std::string::npos &&
      packet.find("\"completed\":42,") != std::string::npos &&
      packet.find(std::string("\"end\":\"") + terminal + "\"") != std::string::npos &&
      packet.find("\"pid\":" + std::to_string(getpid()) + ",") != std::string::npos;
}

int main() {
  unsetenv("DTC_AG7_POLICY_B_PROGRESS");
  errno = EDOM;
  dtc_ag7::ProgressProducer off;
  if (off.enabled() || errno != EDOM) return 10;
  int sockets[2];
  if (socketpair(AF_UNIX, SOCK_DGRAM | SOCK_NONBLOCK | SOCK_CLOEXEC,
                 0, sockets)) return 11;
  int one = 1;
  if (setsockopt(sockets[1], SOL_SOCKET, SO_PASSCRED, &one, sizeof(one))) return 12;
  const std::string descriptor = std::to_string(sockets[0]);
  const std::string input(64, '0'), roi(64, '1');
  setenv("DTC_AG7_POLICY_B_PROGRESS", "1", 1);
  setenv("DTC_AG7_PROGRESS_FD", descriptor.c_str(), 1);
  setenv("DTC_AG7_GENERATION", "DECLARED_SYNTHETIC_HEADER_PROBE", 1);
  setenv("DTC_AG7_INPUT_SHA", input.c_str(), 1);
  setenv("DTC_AG7_ROI_SHA", roi.c_str(), 1);
  errno = EDOM;
  dtc_ag7::ProgressProducer on;
  if (!on.enabled() || errno != EDOM) return 13;
  on.observe("INIT", 42, true, true);
  if (errno != EDOM || !receive_packet(sockets[1], 1, "NONE")) return 14;
  errno = EDOM;
  on.observe("BOUNDARY", 42, true, true, "NATURAL");
  if (errno != EDOM || !receive_packet(sockets[1], 2, "NATURAL")) return 15;
  // Closing a dedicated telemetry FD must fail silent, disable telemetry and
  // restore errno; no SIGPIPE, process signal or model callback is involved.
  close(sockets[0]);
  errno = EDOM;
  on.observe("BOUNDARY", 42, true, true, "ERROR");
  if (on.enabled() || errno != EDOM) return 16;
  close(sockets[1]);
  int blocking[2];
  if (socketpair(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0, blocking)) return 17;
  setenv("DTC_AG7_PROGRESS_FD", std::to_string(blocking[0]).c_str(), 1);
  errno = EDOM;
  dtc_ag7::ProgressProducer rejected;
  if (rejected.enabled() || errno != EDOM) return 18;
  close(blocking[0]);
  close(blocking[1]);
  std::puts("DECLARED_SYNTHETIC header transport probe PASS: two real datagrams, constant fake completed=42; actual SCM credentials; OFF/nonblocking/closed-FD/errno checks; no model linked or simulated.");
  return 0;
}
