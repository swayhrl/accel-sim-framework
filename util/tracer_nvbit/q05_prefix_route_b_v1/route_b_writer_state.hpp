#pragma once

#include <cstdio>

enum class RouteBWriterState { UNOPENED, OPEN, TERMINAL_ACKED, CLOSED };

struct RouteBWriter {
  RouteBWriterState state = RouteBWriterState::UNOPENED;
  FILE* handle = nullptr;
};
