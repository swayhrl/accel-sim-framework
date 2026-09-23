# Pre-repair V2 diagnosis

Pre-repair V2 passed `!ready_application_v2` to `translate`. In V2 mode this observed READY without consuming its controller lookup, then applied PA/outcome to the resident access so the later head no longer consumed it. The published pre-repair evidence is retained as `PRE_REPAIR_READY_RETENTION_INVALID_FOR_FINAL_CLASSIFICATION`; it is not deleted or reclassified as final evidence.
