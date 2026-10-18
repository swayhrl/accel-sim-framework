// Repeated, bounded standard-cell word. Separate module avoids constructing
// thousands of procedural writers to one giant packed vector in EDA frontends.
// SUPPORT_RES=0 is a static staging slot: resident-only fields are constants.
module ep_l2_metadata_word_r2 #(
    parameter integer GEN_W=32,TAG_W=10,SUPPORT_RES=1,DYNAMIC_OWNER=1,STATIC_RESIDENT=0
)(
    input wire clk,rst_n,
    input wire reserve_resident,reserve_wb,
    input wire [TAG_W-1:0] new_owner,
    input wire pin_update,pin_increment,read_pin_add,read_pin_release,
    input wire fill_update,input wire [3:0] fill_sectors,
    input wire become_wb,install,already_reserved,
    input wire install_old_live,
    input wire [3:0] install_ready,install_pending,install_dirty,
    input wire hit_write,input wire [3:0] write_ready,write_dirty,
    input wire invalidate,rollback_release,lower_release,
    output reg [2:0] role,
    output reg [GEN_W-1:0] generation,
    output wire [TAG_W-1:0] owner_tag,
    output reg [5:0] pins,
    output reg [3:0] sectors_ready,sectors_pending,dirty
);
    reg [TAG_W-1:0] dynamic_owner;
    // Preserve procedural precedence, including coincident release events:
    // later release/invalidate overrides install with a +1 generation step.
    wire install_step_two=SUPPORT_RES && install && !already_reserved &&
        install_old_live && !invalidate &&
        (STATIC_RESIDENT || (!rollback_release && !lower_release));
    // Parallel-prefix increment by1/2; exact modular arithmetic, no new state.
    localparam integer PREFIX_L=$clog2(GEN_W);
    wire [GEN_W-1:0] prefix[0:PREFIX_L];
    assign prefix[0]={generation[GEN_W-1:1],generation[0]|install_step_two};
    generate for(genvar level=0;level<PREFIX_L;level=level+1)begin: increment_prefix
      localparam [GEN_W-1:0] LOW_ONES={GEN_W{1'b1}} >> (GEN_W-(1<<level));
      assign prefix[level+1]=prefix[level]&((prefix[level]<<(1<<level))|LOW_ONES);
    end endgenerate
    wire [GEN_W-1:0] carry={prefix[PREFIX_L][GEN_W-2:0],!install_step_two};
    wire [GEN_W-1:0] next_generation;
    assign next_generation=generation^carry;
    assign owner_tag=DYNAMIC_OWNER ? dynamic_owner : {TAG_W{1'b0}};
    always @(posedge clk) begin
        if(!rst_n)begin
            role<=0;generation<=0;dynamic_owner<=0;pins<=0;
            sectors_ready<=0;sectors_pending<=0;dirty<=0;
        end else begin
            if(SUPPORT_RES)begin
                if(pin_update)pins<=pin_increment?pins+1:pins-1;
                if(fill_update)begin sectors_ready<=sectors_ready|fill_sectors;sectors_pending<=sectors_pending&~fill_sectors;end
                if(read_pin_add)pins<=pins+1;
                if(!STATIC_RESIDENT && reserve_resident)begin role<=3;generation<=next_generation;dynamic_owner<=new_owner;end
            end
            if(!STATIC_RESIDENT && reserve_wb)begin role<=4;generation<=next_generation;end
            if(!STATIC_RESIDENT && become_wb)role<=2;
            if(SUPPORT_RES)begin
                if(install)begin
                    if(!already_reserved)generation<=next_generation;
                    role<=1;dynamic_owner<=new_owner;sectors_ready<=install_ready;sectors_pending<=install_pending;dirty<=install_dirty;
                end
                if(hit_write)begin dirty<=dirty|write_dirty;sectors_ready<=sectors_ready|write_ready;end
                if(invalidate)begin role<=0;generation<=next_generation;sectors_ready<=0;dirty<=0;end
            end
            if(!STATIC_RESIDENT && rollback_release)begin role<=0;generation<=next_generation;end
            if(SUPPORT_RES && read_pin_release)pins<=pins-1;
            if(!STATIC_RESIDENT && lower_release)begin role<=0;generation<=next_generation;sectors_ready<=0;dirty<=0;end
        end
    end
endmodule
module ep_l2_tag_map_word_r2 #(parameter integer PID_W=11)(
    input wire clk,rst_n,write,input wire [PID_W-1:0] data,output reg [PID_W-1:0] payload
);
    always @(posedge clk)begin
        if(!rst_n)payload<=0;else if(write)payload<=data;
    end
endmodule

// R2: bounded binary tree. Lowest eligible index is identical to the R1
// ascending first-free loop, with O(log N) serial decisions, no state/cycles.
module ep_l2_first_one_r2 #(parameter integer N=128,W=$clog2(N),P=(1<<W))(
 input wire [N-1:0] eligible,output wire found,output wire [W-1:0] index
);
 wire [2*P-1:1] valid;
 wire [W-1:0] value[1:2*P-1];
 genvar i;
 generate for(i=0;i<P;i=i+1)begin: leaves
   if(i<N)assign valid[P+i]=eligible[i];
   else assign valid[P+i]=1'b0;
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
module ep_l2_index_mux_r2 #(parameter integer N=1168,W=32,IW=$clog2(N),BLOCK=16,
 GROUPS=(N+BLOCK-1)/BLOCK,GP=(1<<$clog2(GROUPS)))(
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
 wire [W-1:0] reduction[1:2*GP-1];
 generate for(genvar k=0;k<GP;k=k+1)begin: reduce_leaf
   if(k<GROUPS)assign reduction[GP+k]=groups[k*W +:W];
   else assign reduction[GP+k]=0;
 end
 for(genvar k=1;k<GP;k=k+1)begin: reduce_node
   assign reduction[k]=reduction[2*k]|reduction[2*k+1];
 end endgenerate
 assign data=reduction[1];
endmodule

// Portable real combinational repeaters. Keep hierarchy/cells so the open
// mapper charges the reset distribution instead of aliasing it to one net.
// DC may globally optimize/rebuffer the same function under the same SDC.
 module ep_l2_control_inverter_r2(input wire i,output wire o);
 assign o=~i;
endmodule
 module ep_l2_control_buffer_r2(input wire i,output wire o);
 wire n;
  ep_l2_control_inverter_r2 invert_a(i,n);
  ep_l2_control_inverter_r2 invert_b(n,o);
endmodule
