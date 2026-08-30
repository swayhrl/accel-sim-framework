# Metadata fairness

Current entry includes line key (address-width dependent), three sector masks, atomic bit, requester/descriptor references, ready-response lists, and ordering maps. Candidate A must retain all of these plus epoch/generation and transition bookkeeping; no source-proven saving exists. Candidate B may move only tail descriptor references/order/cursor after all-ready, but those references remain fully costed. Descriptor pool entries (`mem_fetch*`, sector mask, response-queued bit) are not counted as a saving in either comparison.
