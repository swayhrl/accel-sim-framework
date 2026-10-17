from pathlib import Path
r=Path('/workspace/worktrees/accel-sim-ep-l2-rtl-cost-r2/rtl/ep_l2')
p=r/'rtl/ep_l2_metadata_word.sv';s=p.read_text().replace('GEN_W=32,TAG_W=10,SUPPORT_RES=1','GEN_W=32,TAG_W=10,SUPPORT_RES=1,STATIC_OWNER=-1').replace('output reg [TAG_W-1:0] owner_tag,','output wire [TAG_W-1:0] owner_tag,')
s=s.replace('    always @(posedge clk) begin','    reg [TAG_W-1:0] dynamic_owner;\n    assign owner_tag=STATIC_OWNER>=0 ? TAG_W\'(STATIC_OWNER) : dynamic_owner;\n    always @(posedge clk) begin',1).replace('owner_tag<=','dynamic_owner<=')
# Compute local installation generation instead of distributing a selected
# global generation and its increment across all physical words.
s=s.replace('input wire [GEN_W-1:0] install_generation,','input wire install_old_live,')
s=s.replace('if(!already_reserved)generation<=install_generation;','if(!already_reserved)generation<=generation+(install_old_live ? 2 : 1);')
p.write_text(s)
# Keep helpers in existing metadata file so the exact R1/DC filelists still apply.
with p.open('a') as f:f.write('''
// R2: bounded binary tree. Lowest eligible index is identical to the R1
// ascending first-free loop, with O(log N) serial decisions, no state/cycles.
module ep_l2_first_one #(parameter integer N=128,W=$clog2(N),P=(1<<W))(
 input wire [N-1:0] eligible,output wire found,output wire [W-1:0] index
);
 wire [2*P-1:1] valid;
 wire [W-1:0] value[1:2*P-1];
 genvar i;
 generate for(i=0;i<P;i=i+1)begin: leaves
   assign valid[P+i]=(i<N)?eligible[i]:1'b0;
   assign value[P+i]=W'(i);
 end
 for(i=1;i<P;i=i+1)begin: nodes
   assign valid[i]=valid[2*i]|valid[2*i+1];
   assign value[i]=valid[2*i]?value[2*i]:value[2*i+1];
 end endgenerate
 assign found=valid[1];
 assign index=found?value[1]:{W{1'b0}};
endmodule

// R2 hierarchical selection: decode low bits locally, OR selected groups.
// Every retained metadata bit is a real input; no abstract/free storage.
module ep_l2_index_mux #(parameter integer N=1168,W=32,IW=$clog2(N),BLOCK=16,
 GROUPS=(N+BLOCK-1)/BLOCK)(
 input wire [N*W-1:0] words,input wire [IW-1:0] index,output wire [W-1:0] data
);
 wire [GROUPS*W-1:0] groups;
 genvar g;
 generate for(g=0;g<GROUPS;g=g+1)begin: group_mux
   wire [BLOCK*W-1:0] local_words;
   for(genvar j=0;j<BLOCK;j=j+1)begin: slot
     if(g*BLOCK+j<N)assign local_words[j*W +:W]=words[(g*BLOCK+j)*W +:W];
     else assign local_words[j*W +:W]=0;
   end
   assign groups[g*W +:W]=(index/IW'(BLOCK)==g)?local_words[(index%IW'(BLOCK))*W +:W]:{W{1'b0}};
 end endgenerate
 reg [W-1:0] selected;
 always @* begin
   selected=0;
   for(integer k=0;k<GROUPS;k=k+1)selected=selected|groups[k*W +:W];
 end
 assign data=selected;
endmodule
''')
p=r/'rtl/ep_l2_slice_ctrl.sv';s=p.read_text()
s=s.replace('wire [PID_W-1:0] old_pid = old_live ? tag_map_bits[(req_tag)*PID_W +:PID_W] : req_tag;','wire [PID_W-1:0] old_pid;\n    generate if(MODE==1)begin\n        assign old_pid=old_live ? tag_map_bits[req_tag*PID_W +:PID_W] : req_tag;\n    end else begin\n        assign old_pid=req_tag; // static resident handle invariant, see R2 proof\n    end endgenerate')
start=s.index('    reg hazard, have_wad, have_landing')
end=s.index('    wire old_unpinned',start)
s=s[:start]+'''    wire hazard, have_wad, have_landing, have_staging, free_bank_exists;
    wire [WAD_W-1:0] free_wad;
    wire [PID_W-1:0] free_landing, free_staging;
    wire [N_WAD-1:0] wad_hazards, wad_eligible;
    generate for(genvar w=0;w<N_WAD;w=w+1)begin: wad_search
        assign wad_hazards[w]=wad_live[w] && wad_addr[w]==req_addr;
        assign wad_eligible[w]=!wad_live[w] && wad_generation[w]!=GMAX;
    end endgenerate
    assign hazard=|wad_hazards;
    ep_l2_first_one #(.N(N_WAD),.W(WAD_W)) wad_encoder(wad_eligible,have_wad,free_wad);
    wire [3:0] bank_found, bank_free;
    wire [4*ROW_W-1:0] bank_first;
    generate for(genvar b=0;b<4;b=b+1)begin: allocation_bank
        wire [N_PAYLOAD/4-1:0] eligible,free_slots;
        for(genvar row=0;row<N_PAYLOAD/4;row=row+1)begin: candidate
            localparam integer ID=4*row+b;
            assign free_slots[row]=role_bits[ID*3 +:3]==FREE;
            assign eligible[row]=free_slots[row] && generation_bits[ID*GEN_W +:GEN_W]<GMAX-1;
        end
        assign bank_free[b]=|free_slots;
        ep_l2_first_one #(.N(N_PAYLOAD/4),.W(ROW_W)) encoder(eligible,bank_found[b],bank_first[b*ROW_W +:ROW_W]);
    end endgenerate
    assign have_landing=MODE==1 && bank_found[req_tag[1:0]];
    assign free_bank_exists=bank_free[req_tag[1:0]];
    assign free_landing=have_landing ? {bank_first[req_tag[1:0]*ROW_W +:ROW_W],req_tag[1:0]} : {PID_W{1'b0}};
    wire [STATIC_WB-1:0] staging_eligible;
    wire [$clog2(STATIC_WB)-1:0] staging_index;
    wire staging_found;
    generate for(genvar w=0;w<STATIC_WB;w=w+1)begin: staging_search
        localparam integer ID=WB_BEGIN+w;
        assign staging_eligible[w]=role_bits[ID*3 +:3]==FREE && generation_bits[ID*GEN_W +:GEN_W]<GMAX-1;
    end endgenerate
    ep_l2_first_one #(.N(STATIC_WB)) staging_encoder(staging_eligible,staging_found,staging_index);
    assign have_staging=MODE!=1 && staging_found;
    assign free_staging=have_staging ? PID_W'(WB_BEGIN)+staging_index : {PID_W{1'b0}};
'''+s[end:]
s=s.replace('.SUPPORT_RES(MODE==1 || m<N_TAG))','.SUPPORT_RES(MODE==1 || m<N_TAG),.STATIC_OWNER(MODE!=1 && m<N_TAG ? m : -1))')
s=s.replace('.install_generation(landing_generation)', '.install_old_live(p_old_live)')
s=s.replace('        ep_l2_tag_map_word #(.PID_W(PID_W)) word_state', '        if(MODE!=1)begin: fixed_mapping\n            assign tag_map_bits[t*PID_W +:PID_W]=PID_W\'(t);\n        end else begin: dynamic_mapping\n        ep_l2_tag_map_word #(.PID_W(PID_W)) word_state')
s=s.replace('.payload(tag_map_bits[t*PID_W +:PID_W]));\n    end endgenerate','.payload(tag_map_bits[t*PID_W +:PID_W]));\n        end\n    end endgenerate')
# Replace variable reads of all metadata buses by explicit bounded selectors.
import re
width={'role_bits':3,'generation_bits':'GEN_W','owner_tag_bits':'TAG_W','pins_bits':6,'sectors_ready_bits':4,'sectors_pending_bits':4,'dirty_bits':4}
reads={}
for bus,w in width.items():
 pattern=re.compile(r'\b'+bus+r'\[\((\w+)\)\*'+str(w)+r' \+:'+str(w)+r'\]')
 for idx in pattern.findall(s):
  # Only runtime scalar handles, never generated constant slots.
  if idx not in ('old_pid','p_landing','fill_pid','pin_pid','active_pid','p_old','free_staging','head_pid'):continue
  name=bus.removesuffix('_bits')+'_'+idx
  s=pattern.sub(lambda m:name if m.group(1)==idx else m.group(0),s)
  reads[name]=(bus,w,idx)
decl='\n    // R2 explicit local metadata read ports; same information/cycles as R1.\n'
for name,(bus,w,idx) in reads.items():
 decl+=f'    wire [{w}-1:0] {name};\n    ep_l2_index_mux #(.N(N_PAYLOAD),.W({w}),.IW(PID_W)) select_{name}({bus},{idx},{name});\n'
s=s.replace('    // Direct vector slices keep every combinational dependency explicit.',decl+'\n    // Direct vector slices keep every combinational dependency explicit.')
p.write_text(s)
