# Preserve configure; bind exact dependency and generated configuration

Source/configuration preparation only. No resource sampling, Doxygen invocation, configure, build or fixture run was performed for this handoff. The original Core1fcf5113, fixture and controller90be68 are unchanged.

The coordinator consumed successful configure publication5a54351b8 and reviewed fixed Core gpgpusim_check.cmake:12 plus system FindDoxygen.cmake:453-458. The source invokes find_package(Doxygen); that module's observed path calls the fixed executable with --version for metadata. The accepted disclosure is confined to this dependency-discovery path. It does not assert that every helper was preregistered before configure and does not authorize standalone Doxygen or documentation builds.

NEXT_BUILD_PREFLIGHT_BINDINGS.json makes four SHA checks explicit for the next coordinated foreground admission: Doxygen, FindDoxygen module, retained CMakeCache and retained compile_commands. Their current hashes match the successful configure identity. No repeat configure is needed. A mismatch must stop the affected role for review rather than silently refreshing the cache or modules.

Next build is a single coordinated root: the parent registered manager must invoke real Popen, or an explicitly released source-bound launcher must do so. SEM1 cannot duplicate that startup from the old worker-only command. Full paired host+cgroup R2, exact tool/config/source checks and all existing output/timeout limits still apply after the parent schedules it. No resource probe or auto-resume is created by this preparation. Diagnostic library/fixture ELFs remain unbuilt; all value/native tests remain0.
