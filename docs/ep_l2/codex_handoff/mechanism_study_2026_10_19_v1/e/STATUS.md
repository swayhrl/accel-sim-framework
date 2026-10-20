# Lane E — Conv failure forensics, no batch dispatch

Verified E HEAD edc888c997990a831072dea5233e8eb8a3cf2e19. Actualstarts6/40, remaining34, acceptedpoints/pairs0. Originalfinitecontroller STOPPED; noactivesim/resourcelease. Alloldbinary/config/input/raw/status files pinned and unchanged.

E005 nativeexit0. Its CLI fails at parse_main_terminal.main:279 -> Coordinator.require_no_hold, field qualification_id=cac1cf6d..., beforeterminalfield decoding. E006 previously placedthe sharedproductionHOLD. Pure read-onlydecoder onE005 yields292932cycles/714547200instructions/all64closure; this is NOT acceptance andoldFAILED remains. No parserpatch orHOLD bypass isjustified.

E006 actualexit-6: ep-l2-tvd-directory.h:157 preview_install asserts !live(find(line)), rawline6264. Originalraw hasnostack/requestUID andnocore retained; B r5stack/UID cannotbe assignedtoE006. Bothcurrent773 Conv/FWTqualifications held pending A/E repair. No FWT orbatch launch.

Preparing ONE exactsame773/config/fulltraceGDBforensicreplay toobserve stack/request; actualnewstartwillspend original40contingency. Existing resourceAPI/startjournal/singleton/CPU2+RAM8GiB/384MiB resultcap/5GiB+2GiBmonitor/Share40GiB/RAM64GiB/cutoffs remain. No statsdisablement/assertion suppression/model/source change. Ten replaybudget/replay-scope controlsPASS; ownedGDBhostattach passes aftersystemGDB-only incompatiblePYTHONHOME cleanup; failedstartup retained.
