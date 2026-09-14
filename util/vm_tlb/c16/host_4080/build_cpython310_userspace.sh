#!/usr/bin/env bash
# Build CPython 3.10.12 and its non-system dependency closure under /data/c16.
set -euo pipefail
umask 077

usage() { echo "usage: $0 --build" >&2; }
[[ $# -eq 1 && $1 == --build ]] || { usage; exit 2; }
[[ $EUID -ne 0 && $(id -un) == huangrulin ]] || { echo "must run as huangrulin, not root" >&2; exit 2; }

prefix=/data/c16/env/build-deps-cpython310
python_prefix=/data/c16/env/cpython-3.10.12
cache=/data/c16/cache/userspace-sources
stamp=$(date -u +%Y%m%dT%H%M%SZ)
build_root=/data/c16/env/build-cpython-3.10.12-$stamp
receipt=/data/c16/results/C16_U1_CPYTHON310_BUILD_$stamp
jobs=$(nproc)

[[ ! -e $prefix && ! -e $python_prefix && ! -e $build_root ]] || {
  echo "refusing to overwrite an existing userspace build prefix" >&2
  exit 2
}
mkdir -p "$cache" "$build_root" "$receipt"

fetch() {
  local url=$1 file=$2
  if [[ ! -e $cache/$file ]]; then
    curl --fail --location --retry 3 --output "$cache/$file" "$url"
  fi
  sha256sum "$cache/$file" >>"$receipt/SOURCE_SHA256SUMS.txt"
}

fetch https://sourceware.org/pub/bzip2/bzip2-1.0.8.tar.gz bzip2-1.0.8.tar.gz
fetch https://github.com/libffi/libffi/releases/download/v3.4.6/libffi-3.4.6.tar.gz libffi-3.4.6.tar.gz
fetch https://ftp.gnu.org/gnu/ncurses/ncurses-6.5.tar.gz ncurses-6.5.tar.gz
fetch https://ftp.gnu.org/gnu/readline/readline-8.2.tar.gz readline-8.2.tar.gz
fetch https://www.sqlite.org/2024/sqlite-autoconf-3460100.tar.gz sqlite-autoconf-3460100.tar.gz
fetch https://github.com/tukaani-project/xz/releases/download/v5.4.6/xz-5.4.6.tar.gz xz-5.4.6.tar.gz
fetch https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz Python-3.10.12.tgz

expected_python_sha=a43cd383f3999a6f4a7db2062b2fc9594fefa73e175b3aedafa295a51a7bb65c
[[ $(sha256sum "$cache/Python-3.10.12.tgz" | awk '{print $1}') == "$expected_python_sha" ]] || {
  echo "CPython source hash mismatch" >&2
  exit 1
}

extract() {
  local file=$1 dir=$2
  tar -xf "$cache/$file" -C "$build_root"
  [[ -d $build_root/$dir ]]
}

extract bzip2-1.0.8.tar.gz bzip2-1.0.8
extract libffi-3.4.6.tar.gz libffi-3.4.6
extract ncurses-6.5.tar.gz ncurses-6.5
extract readline-8.2.tar.gz readline-8.2
extract sqlite-autoconf-3460100.tar.gz sqlite-autoconf-3460100
extract xz-5.4.6.tar.gz xz-5.4.6
extract Python-3.10.12.tgz Python-3.10.12

export CFLAGS='-O2 -fPIC'
export CPPFLAGS="-I$prefix/include"
export LDFLAGS="-L$prefix/lib -Wl,-rpath,$prefix/lib"
export PKG_CONFIG_PATH="$prefix/lib/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"

run_logged() {
  local name=$1; shift
  printf '%q ' "$@" >>"$receipt/COMMANDS.txt"; printf '\n' >>"$receipt/COMMANDS.txt"
  "$@" >"$receipt/$name.log" 2>&1
}

cd "$build_root/bzip2-1.0.8"
run_logged bzip2_make make -j"$jobs" CFLAGS="$CFLAGS"
run_logged bzip2_install make install PREFIX="$prefix"

cd "$build_root/libffi-3.4.6"
run_logged libffi_configure ./configure --prefix="$prefix" --disable-docs
run_logged libffi_make make -j"$jobs"
run_logged libffi_install make install

cd "$build_root/ncurses-6.5"
run_logged ncurses_configure ./configure --prefix="$prefix" --with-shared --without-debug --without-ada --enable-widec
run_logged ncurses_make make -j"$jobs"
run_logged ncurses_install make install

cd "$build_root/readline-8.2"
run_logged readline_configure ./configure --prefix="$prefix" --with-curses
run_logged readline_make make -j"$jobs"
run_logged readline_install make install

cd "$build_root/sqlite-autoconf-3460100"
run_logged sqlite_configure ./configure --prefix="$prefix" --enable-shared --disable-static
run_logged sqlite_make make -j"$jobs"
run_logged sqlite_install make install

cd "$build_root/xz-5.4.6"
run_logged xz_configure ./configure --prefix="$prefix" --enable-shared --disable-static
run_logged xz_make make -j"$jobs"
run_logged xz_install make install

export CPPFLAGS="-I$prefix/include"
export LDFLAGS="-L$prefix/lib -Wl,-rpath,$prefix/lib"
cd "$build_root/Python-3.10.12"
run_logged python_configure ./configure --prefix="$python_prefix" --with-ensurepip=install --enable-shared
run_logged python_make make -j"$jobs"
run_logged python_install make install

wrapper="$python_prefix/bin/c16-python3.10"
{
  printf '%s\n' '#!/usr/bin/env bash'
  printf 'export LD_LIBRARY_PATH=%q"${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"\n' "$python_prefix/lib:$prefix/lib"
  printf 'exec %q "$@"\n' "$python_prefix/bin/python3.10"
} >"$wrapper"
chmod 0755 "$wrapper"

{
  printf 'built_utc=%s\n' "$(date -u +%FT%TZ)"
  printf 'research_user=%s uid=%s gid=%s\n' "$(id -un)" "$(id -u)" "$(id -g)"
  printf 'dependency_prefix=%s\npython_prefix=%s\n' "$prefix" "$python_prefix"
  printf 'python_source_sha256=%s\n' "$expected_python_sha"
  printf 'gcc='; gcc --version | head -n1
  printf 'python='; "$wrapper" --version
  printf 'linked_libraries:\n'; ldd "$python_prefix/bin/python3.10" || true
  printf 'stdlib_imports:\n'
  "$wrapper" -c 'import bz2, ctypes, lzma, readline, sqlite3, ssl, zlib; print("STDLIB_IMPORTS_PASS")'
} >"$receipt/BUILD_RECEIPT.txt"
sha256sum "$receipt"/* >"$receipt/SHA256SUMS.txt"
printf 'CPYTHON_BUILD_PASS receipt=%s python=%s\n' "$receipt" "$python_prefix/bin/python3.10"
