// Small fixed-priority leaves used by the 128-engine Snapshot bank arbiter.
module c2p_snapshot_prio16 #(parameter integer ROW_W = 13) (
    input wire [15:0] req, input wire [16*ROW_W-1:0] row_in,
    output reg valid, output reg [3:0] index, output reg [ROW_W-1:0] row
);
    integer i;
    always @* begin
        valid = 1'b0; index = 4'b0; row = {ROW_W{1'b0}};
        for (i=0;i<16;i=i+1) if (!valid && req[i]) begin
            valid=1'b1; index=i[3:0]; row=row_in[i*ROW_W +: ROW_W];
        end
    end
endmodule

module c2p_snapshot_prio8 #(parameter integer ROW_W = 13) (
    input wire [7:0] req, input wire [8*7-1:0] owner_in,
    input wire [8*ROW_W-1:0] row_in, output reg valid,
    output reg [6:0] owner, output reg [ROW_W-1:0] row
);
    integer i;
    always @* begin
        valid=1'b0; owner=7'b0; row={ROW_W{1'b0}};
        for (i=0;i<8;i=i+1) if (!valid && req[i]) begin
            valid=1'b1; owner=owner_in[i*7 +: 7]; row=row_in[i*ROW_W +: ROW_W];
        end
    end
endmodule

module c2p_snapshot_bank_copy_arbiter_static128 #(parameter integer ROW_W=13) (
    input wire [127:0] lane_valid, input wire [127:0] lane_need,
    input wire [128*ROW_W-1:0] lane_row, input wire [128*6-1:0] lane_bank,
    input wire [63:0] bank_ready, output wire [63:0] bank_req_valid,
    output wire [64*7-1:0] bank_req_owner, output wire [64*ROW_W-1:0] bank_req_row,
    output wire [127:0] lane_grant
);
    genvar b,g,l,e;
    generate
      for (b=0;b<64;b=b+1) begin:g_bank
        wire [7:0] group_valid; wire [8*7-1:0] group_owner; wire [8*ROW_W-1:0] group_row;
        for (g=0;g<8;g=g+1) begin:g_group
          wire [15:0] req; wire [16*ROW_W-1:0] rows; wire lv; wire [3:0] li; wire [ROW_W-1:0] lr;
          for (l=0;l<16;l=l+1) begin:g_leaf
            localparam integer I = g*16+l;
            assign req[l]=lane_valid[I] && lane_need[I] && (lane_bank[I*6 +: 6] == b);
            assign rows[l*ROW_W +: ROW_W]=lane_row[I*ROW_W +: ROW_W];
          end
          c2p_snapshot_prio16 #(.ROW_W(ROW_W)) leaf(.req(req),.row_in(rows),.valid(lv),.index(li),.row(lr));
          assign group_valid[g]=lv;
          assign group_owner[g*7 +: 7]={g[2:0],li};
          assign group_row[g*ROW_W +: ROW_W]=lr;
        end
        wire win; wire [6:0] wo; wire [ROW_W-1:0] wr;
        c2p_snapshot_prio8 #(.ROW_W(ROW_W)) root(.req(group_valid),.owner_in(group_owner),.row_in(group_row),.valid(win),.owner(wo),.row(wr));
        assign bank_req_valid[b]=win && bank_ready[b];
        assign bank_req_owner[b*7 +: 7]=wo;
        assign bank_req_row[b*ROW_W +: ROW_W]=wr;
      end
      for(e=0;e<128;e=e+1) begin:g_grant
        wire [63:0] hit;
        for(b=0;b<64;b=b+1) assign hit[b]=bank_req_valid[b] && (bank_req_owner[b*7 +: 7] == e);
        assign lane_grant[e]=|hit;
      end
    endgenerate
endmodule
