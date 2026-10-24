"""Lossless observed stdout capture; no simulator or scheduler API."""
import gzip,hashlib,threading,os
class RawCapture:
 def __init__(self,path):
  self.disk=open(path,'xb');self.gz=gzip.GzipFile(fileobj=self.disk,mode='wb',mtime=0);self.hash=hashlib.sha256();self.bytes=0;self.error=None;self.thread=None
 def start(self,pipe):
  def pump():
   try:
    while True:
     block=pipe.read1(64*1024)
     if not block:break
     self.hash.update(block);self.bytes+=len(block);self.gz.write(block)
   except BaseException as e:self.error=repr(e)
   finally:pipe.close()
  self.thread=threading.Thread(target=pump,name='lossless-native-stdout',daemon=False);self.thread.start()
 def flush(self):
  if self.thread:
   self.thread.join(60)
   if self.thread.is_alive():raise RuntimeError('closed stdout capture did not drain')
  self.gz.flush()
 def fileno(self):return self.disk.fileno()
 def close(self):
  self.flush();self.gz.close();self.disk.flush();os.fsync(self.disk.fileno());self.disk.close()
