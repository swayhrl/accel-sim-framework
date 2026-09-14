#pragma once

struct TargetRecord {
    unsigned int claimed;
    unsigned int present;
    unsigned long long address;
    unsigned long long launch_id;
    unsigned int static_index;
    // Diagnostic-only counters distinguish a predicated-off instruction from
    // an MREF capture whose observed address is zero.
    unsigned long long callback_count;
    unsigned long long predicate_true_count;
    unsigned long long active_lane_count;
    unsigned long long nonzero_mref_count;
    unsigned long long zero_mref_count;
};
