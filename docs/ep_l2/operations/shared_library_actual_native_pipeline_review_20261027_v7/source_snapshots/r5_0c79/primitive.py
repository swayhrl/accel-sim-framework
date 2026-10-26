"""Standalone exact no-replace primitive, derived from frozen v9 SHA6fd13ab5. No historical runtime import."""
from pathlib import Path
import os,ctypes,errno
class Hold(RuntimeError):pass
def require(ok, reason):
    if not ok:
        raise Hold(reason)

def no_symlinks(path):
    p = Path(path).absolute()
    for q in [p, *p.parents]:
        if os.path.lexists(q):
            require(not q.is_symlink(), 'symlink traversal')
    return p

def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        try:
            os.fsync(fd)
        except OSError as error:
            if error.errno not in (errno.EINVAL, errno.ENOTSUP):
                raise
    finally:
        os.close(fd)

def rename_noreplace(source, target):
    """Linux RENAME_NOREPLACE; unsupported filesystems HOLD, never os.replace.

    Caller keeps both paths under one verified transaction filesystem.
    """
    no_symlinks(source); no_symlinks(target)
    require(Path(source).parent.stat().st_dev == Path(target).parent.stat().st_dev, 'cross-filesystem finalization')
    libc = ctypes.CDLL(None, use_errno=True)
    require(hasattr(libc, 'renameat2'), 'RENAME_NOREPLACE unavailable')
    fn = libc.renameat2
    fn.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    fn.restype = ctypes.c_int
    if fn(-100, os.fsencode(source), -100, os.fsencode(target), 1):
        err = ctypes.get_errno()
        if err in (errno.EINVAL, errno.ENOSYS, errno.ENOTSUP) and Path(source).is_file():
            # Verified on real SSHFS: LINK fails EEXIST without replacement.
            # The source is an owned durable temporary, never a scientific original.
            try:
                os.link(source, target, follow_symlinks=False)
            except FileExistsError:
                raise Hold('exclusive link collision: reconcile owned temporary, never replace')
            # Successful LINK is the no-replacement primitive. SSHFS inode
            # projections are deliberately not used as native identity proof.
            require(Path(source).stat().st_size == Path(target).stat().st_size, 'exclusive link size')
            os.unlink(source)
        else:
            raise Hold('no-replace finalize: ' + os.strerror(err))
    fsync_dir(Path(target).parent)
