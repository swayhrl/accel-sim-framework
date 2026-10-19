"""Static readelf dependency closure, never executes target ELF or loader --list."""
import subprocess,re,os
from pathlib import Path
from mapping_roles import freeze,require

def metadata(path):
 ph=subprocess.check_output(['/usr/bin/readelf','-lW',str(path)],text=True)
 dy=subprocess.check_output(['/usr/bin/readelf','-dW',str(path)],text=True)
 m=re.search(r'Requesting program interpreter: (.*?)\]',ph)
 return dict(path=str(Path(path).resolve()),interpreter=str(Path(m[1]).resolve()) if m else None,
             needed=re.findall(r'Shared library: \[(.*?)\]',dy),readelf_program_headers=ph,readelf_dynamic=dy)

def freeze_executable(target,private_library_dir):
 # Exact current host ldconfig catalogue is an input to resolution, not permission
 # to accept its entire directory. Only recursive DT_NEEDED paths enter manifest.
 catalogue=subprocess.check_output(['/sbin/ldconfig','-p'],text=True)
 known={}
 for line in catalogue.splitlines():
  m=re.match(r'\s*(\S+) \(([^)]+)\) => (\S+)',line)
  if m and 'x86-64' in m[2]:known.setdefault(m[1],str(Path(m[3]).resolve()))
 first=metadata(target);require(first['interpreter'] is not None,'PT_INTERP_REQUIRED')
 specs=[(first['path'],'ELF_EXECUTABLE','static PT_INTERP/DT_NEEDED before target launch'),(first['interpreter'],'ELF_INTERPRETER','ELF PT_INTERP canonical path'),('/etc/ld.so.cache','LOADER_DATA_CACHE','explicit pre-fork glibc loader cache')]
 todo=[first];seen={first['path'],first['interpreter']};objects=[first]
 while todo:
  item=todo.pop()
  for name in item['needed']:
   require('/' not in name,'DT_NEEDED_ABSOLUTE_OR_RELATIVE_PATH_UNQUALIFIED:'+name)
   private=Path(private_library_dir)/name
   path=str(private.resolve()) if private.is_file() else known.get(name)
   require(path is not None,'UNRESOLVED_STATIC_DT_NEEDED:'+name)
   if path not in seen:
    seen.add(path);m=metadata(path);todo.append(m);objects.append(m)
    specs.append((path,'ELF_SHARED_OBJECT','recursive DT_NEEDED '+name+' from '+item['path']))
 return freeze(specs,first['path'],first['interpreter']),objects
