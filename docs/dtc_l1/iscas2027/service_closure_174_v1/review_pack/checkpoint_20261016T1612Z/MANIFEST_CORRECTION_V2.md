# Final manifest correction V2

Use FINAL_FILES_SHA256_V2.json for the complete review package. The original
FINAL_FILES_SHA256.json at fdf88a4a0 erroneously includes its own empty-file SHA.
Its other entries all match. Preserve the original bytes and this failed check;
V2 includes them and excludes only its own output. Terminal, strict, input,
resource and numerical results are unchanged; no simulator was rerun or
restarted. This is a receipt-packaging correction, not scientific reacceptance.
