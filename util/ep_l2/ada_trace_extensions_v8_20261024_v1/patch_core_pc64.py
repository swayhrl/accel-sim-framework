import pathlib,re,json
C=pathlib.Path('/root/data/ada_trace_extensions_v8_20261024_v1/core64')
F=pathlib.Path('/root/data/ada_trace_extensions_v8_20261024_v1/consumer')
names=r'(?:pc|rpc|npc|PC|callee_pc|callee_rpc|m_PC|m_NPC|m_RPC|m_start_PC|g_assemble_code_next_pc)'
changed=[]
for root in [C/'src',F]:
 for p in root.rglob('*'):
  if p.is_symlink()or p.suffix not in ['.h','.cc','.cpp']:continue
  s=p.read_text();original=s
  s=re.sub(r'\bunsigned(?:\s+int)?(\s*\*\s*)('+names+r')\b',r'address_type\1\2',s)
  s=re.sub(r'\bunsigned(?:\s+int)?(\s+)('+names+r')\b',r'address_type\1\2',s)
  s=re.sub(r'\bunsigned\s+(get_pc|get_rpc|get_return_PC|get_start_PC)\s*\(',r'address_type \1(',s)
  s=s.replace('std::map<unsigned, function_info *>','std::map<address_type, function_info *>')
  s=s.replace('std::map<unsigned /*pc*/','std::map<address_type /*pc*/')
  s=s.replace('unsigned index = pc - m_start_PC;','address_type index = pc - m_start_PC;').replace('unsigned index = PC - m_start_PC;','address_type index = PC - m_start_PC;')
  if s!=original:p.write_text(s);changed.append(str(p))
# The frozen snapshot's old out-of-tree zlib header links are absent in native namespace.
# Replace only this isolated copy with explicitly recorded installed headers, not old runtime.
for p in (C/'src').rglob('*'):
 if p.is_symlink()and p.name in['zlib.h','zconf.h']and not p.exists():
  p.unlink();p.symlink_to('/usr/include/'+p.name);changed.append(str(p))
(C.parent/'evidence/CORE64_PROMOTED_PATHS.json').write_text(json.dumps(changed,indent=2)+'\n')
print('Changed PC64 paths',len(changed))
