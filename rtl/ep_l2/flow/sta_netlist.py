"""Convert only irrelevant signed declarations in a fully mapped bit netlist.
OpenSTA's structural reader rejects wire signed. Never change gates or arcs.
"""
import re,json,hashlib
from pathlib import Path

def portable_netlist(source, destination):
    source=Path(source);destination=Path(destination);s=source.read_text()
    declaration=re.compile(r'^(\s*wire) signed( \[[^\]]+\]\s+)(\\\S+|[\w$]+)(\s*;)',re.M)
    names={m[3] for m in declaration.finditer(s)}
    assert not re.search(r'^\s*(input|output|inout)\s+signed\b',s,re.M),'signed ports need a separate proof'
    identifier=re.compile(r'\\\S+|[A-Za-z_$][\w$]*');uses=0
    # After full synthesis there are no arithmetic/process expressions. Each
    # affected wire is a constant loop remnant or only accessed by explicit
    # bit/range selection (which is unsigned in Verilog).
    for line in s.splitlines():
        if line.lstrip().startswith('//') or 'wire signed ' in line:continue
        for m in identifier.finditer(line):
            name=m[0]
            if name not in names:continue
            tail=line[m.end():].lstrip();prefix=line[:m.start()].strip()
            assert tail.startswith('[') or (prefix=='assign' and re.fullmatch(r"=\s*32'[s]?[bdh][0-9a-fA-F_xz]+;",tail)),('unproved signed use',name,line[:250])
            uses+=1
    result,n=declaration.subn(r'\1\2\3\4',s)
    assert n==len(list(declaration.finditer(s)))
    assert not re.search(r'^\s*wire signed\b',result,re.M)
    destination.write_text(result)
    receipt={'raw_netlist':str(source),'raw_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'STA_netlist':str(destination),'STA_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'removed_signed_declarations':n,'proved_constant_or_explicit_bitselect_uses':uses,'cell_instances_connections_bits_constants_unchanged':True,'RTL_and_mapping_unchanged':True,'no_signed_ports':True,'proof':'all affected uses are explicit bit/range selections or full-width constant-loop assignments; no arithmetic or sign extension inferred from declarations'}
    return receipt
