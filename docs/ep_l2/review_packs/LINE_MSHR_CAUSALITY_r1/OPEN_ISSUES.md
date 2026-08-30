# Open issues

- Promotion of D512 descendants is pending the existing Lane-B
  `D512_PREFLIGHT_PASS` gate. The rows use the exact frozen candidate and may
  be promoted without rerun only if that candidate is promoted unchanged.
- The probe intentionally does not select MSHR256 as a baseline and does not
  implement RO no-MSHR, TVD, or Unified behavior.
