# ISA and trace-driven source anchors

The narrow exception is source-backed and applies only to exact `LDGDEPBAR`.

- `gpu-simulator/ISA_Def/ampere_opcode.h:138` maps `LDGDEPBAR` to `OP_LDGDEPBAR, ALU_OP`.
- The adjacent `:139` maps `LDGSTS` to `OP_LDGSTS, LOAD_OP`; it remains address-bearing.

```cpp
{"LDGDEPBAR", OpcodeChar(OP_LDGDEPBAR, ALU_OP)},
{"LDGSTS", OpcodeChar(OP_LDGSTS, LOAD_OP)},
```

`gpu-simulator/trace-driven/trace_driven.cc:373-377` says LDGDEPBAR forms a group from prior ungrouped LDGSTS instructions and sets `m_is_ldgdepbar`.

```cpp
// LDGDEPBAR is to form a group containing the previous LDGSTS instructions
case OP_LDGDEPBAR:
  m_is_ldgdepbar = true;
  break;
```

The validator exception therefore prevents lexical `LD*` prefix confusion without weakening true load/store validation.