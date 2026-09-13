#pragma once

struct TargetRecord {
    unsigned int claimed;
    unsigned int present;
    unsigned long long address;
    unsigned long long launch_id;
    unsigned int static_index;
};
