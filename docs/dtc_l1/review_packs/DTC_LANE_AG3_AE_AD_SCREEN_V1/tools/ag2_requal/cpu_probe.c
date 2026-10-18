#include <unistd.h>
extern int ag2_only_cpu_value(void);
int main(void) {
    const char msg[] = "AG2_CPU_ONLY_SYSTEM_LOADER_PROBE_OK\n";
    if (ag2_only_cpu_value() != 174) return 23;
    return write(1, msg, sizeof(msg)-1) == sizeof(msg)-1 ? 0 : 24;
}
