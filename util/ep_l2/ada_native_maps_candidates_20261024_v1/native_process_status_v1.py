"""Process resource sampling with explicit exit-race handling; no SIM execution."""
import pathlib
def sample_live_rss(process,read_status=None):
 if process.poll() is not None:return None
 if read_status is None:read_status=lambda:(pathlib.Path('/proc')/str(process.pid)/'status').read_text()
 try:
  status=read_status()
  rss=int(next(line.split()[1]for line in status.splitlines()if line.startswith('VmRSS:')))*1024
 except (FileNotFoundError,ProcessLookupError,StopIteration) as error:
  if process.poll() is not None:return None
  raise RuntimeError('live process RSS/status unreadable') from error
 if process.poll() is not None:return None
 return rss
