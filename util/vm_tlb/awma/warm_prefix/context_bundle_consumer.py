#!/usr/bin/env python3
import json,hashlib,sys
from pathlib import Path
m=json.loads(Path(sys.argv[1]).read_text()); assert len(m["members"])==35
print("CONTEXT_BUNDLE_VALID")
