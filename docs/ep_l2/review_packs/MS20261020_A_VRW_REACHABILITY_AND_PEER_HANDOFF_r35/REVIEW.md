# Shared V/R/W control: compile repaired, scenario not qualified

Original B fixture was present but excluded from the producer build. Its first real compile failed at a mixed-type constauto declaration. A test-only branch8027ec55 splits that declaration and rebinds only source/manifest/config hashes. ProductionCore27/src/libcuda/CMake and main773 remain identical.

The repaired fixture compiles, then actually exitsSIGABRT at submit_ro(0), mainline134. One bounded GDB replay confirms A0 attached=1/reuse_seen=1/required15/issued15/ready0/waiters5; ROlowerpackets stay20 and bytes640. The 128B frontendrequest becomes four32B children. Merges set persistent reuse_seen, which forbidsTagdetachment. Thus the later A0request merges with the stillattached transaction and needs no lowersector, while the fixture waits for a newpacket. This is a source/observed-state reachability conflict, not a passed jointscenario.

Keep the frozen productionpolicy and compiledmain. B/C must review actual sectorchild identities, descriptor count and a reachable jointscenario. Original18descriptor and22packet/704B completion expectations are not observedresults. ParentUID response assembly is another source-level review item; laterassertions did not execute. Do not loosen reuse_seen merely to force this fixture through. No nativeDRAM/SASS/performance claim follows from this externallycontrolledversion fixture.

R31compilefailure, R32actualabort, R33GDBstartup failure from inheritedEDA PythonHOME, and R34successfuldiagnostic are all retained. R34 clears PythonHOME/PYTHONPATH only in its own GDBchild, uses oneGDBworker, disables downloads/indexcache/core dumps and runs under a real Etestlease. Allfourleases are released; no owninferior remains. No fullapplication was started; counter stays3/40.

Main773's earlier20affected+4detailed passes remain their exact scoped records. E alone independently accepts the productionprofile and determines whether a replacement jointscenario is required by its gate review. ExistingoldS and all sourceholds/data remain untouched. This checkpoint grants neither scientificacceptance nor a gate waiver.
