# Semantic commits

Core range `3be79d4d..ec81a777`:

- prior recovery commits establish dedicated root/sector response ownership,
  FIFO PIB writeback, mode-specific dependency cardinality, and lower credits;
- `58e4c3d9` extends directed I06-I11 coverage;
- `ec81a777` adds physical/partial/duplicate/HOL/Tag observability, compact
  resource-deadlock diagnostics, same Tag-bank timing, and high-MLP coverage.

Framework range `57b21037..9754e807` records recovery evidence and makes the
strict summary parser understand `PAPER_IO`. All commits were explicit-path
staged.
