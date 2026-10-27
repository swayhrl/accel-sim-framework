# Race-safe byte accounting only for the caller's private owned output tree.
import pathlib,os,stat,errno
def owned_output_bytes(root):
 root=pathlib.Path(root)
 def root_check():
  s=os.lstat(root)
  if not stat.S_ISDIR(s.st_mode)or stat.S_ISLNK(s.st_mode):raise RuntimeError('OWN_OUTPUT_ROOT_NOT_DIRECTORY_OR_SYMLINK')
 root_check()
 def transient(e,path):
  path=pathlib.Path(path)
  return e.errno in (errno.ENOENT,errno.ENOTDIR)and path!=root and path.is_relative_to(root)
 def walk_error(e):
  if e.filename is not None and transient(e,e.filename):return
  raise e
 total=0
 for current,dirs,files in os.walk(root,topdown=True,onerror=walk_error,followlinks=False):
  current=pathlib.Path(current)
  if not current.is_relative_to(root):raise RuntimeError('OWN_OUTPUT_ESCAPE')
  try:
   s=os.lstat(current)
   if stat.S_ISLNK(s.st_mode):raise RuntimeError('OWN_OUTPUT_DIRECTORY_SYMLINK')
  except OSError as e:
   if transient(e,current):continue
   raise
  for name in files:
   p=current/name
   try:
    s=os.lstat(p)
    if stat.S_ISLNK(s.st_mode):raise RuntimeError('OWN_OUTPUT_FILE_SYMLINK')
    if stat.S_ISREG(s.st_mode):total+=s.st_size
   except OSError as e:
    if transient(e,p):continue
    raise
 root_check()
 return total
