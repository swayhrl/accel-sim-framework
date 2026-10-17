// Synthesizable integration top: changed-path controller +4 SRAM boundaries.
// Traditional Tag/MSHR remain external. Open cost/STA uses controller timing cut.
module ep_l2_slice #(
    parameter integer MODE=0, N_TAG=1024, N_PAYLOAD=1168,
    parameter integer STATIC_WB=(MODE==2 ? 64 : 16), N_WAD=128,
    parameter integer GEN_W=32, ADDR_W=64,
    parameter integer TAG_W=$clog2(N_TAG), PID_W=$clog2(N_PAYLOAD),
    parameter integer WAD_W=$clog2(N_WAD), ROW_W=$clog2(N_PAYLOAD/4)
)(
    input wire clk, rst_n,
    // ops: 0=install/replace, 1=resident read, 2=resident byte write, 3=clean invalidate
    input wire req_valid, output wire req_ready,
    input wire [1:0] req_op, input wire [31:0] req_id,
    input wire [TAG_W-1:0] req_tag,
    input wire [ADDR_W-1:0] req_addr, req_victim_addr,
    input wire [1023:0] req_data,
    input wire [127:0] req_be, req_victim_be,
    input wire [3:0] req_ready_sectors, req_pending_sectors,
    input wire req_install_dirty, req_resources_ready,
    // Approval is a reservation/precheck, NOT the Tag commit handshake.
    // The upstream Tag changes only on native_commit, using captured native_tag.
    input wire native_ready, native_abort,
    output wire native_commit,
    output wire [TAG_W-1:0] native_tag,
    output wire [PID_W-1:0] native_pid,
    output wire [GEN_W-1:0] native_gen,
    output wire rsp_valid, input wire rsp_ready,
    output wire [31:0] rsp_id, output wire rsp_retry,
    output wire [PID_W-1:0] rsp_pid,
    output wire [GEN_W-1:0] rsp_gen,
    output wire [1023:0] rsp_data,
    // Real lower-fill identity. Dirty byte protection comes from the reused
    // native Tag byte mask; the AND/byte write path is implemented here.
    input wire fill_valid, output wire fill_ready,
    input wire [TAG_W-1:0] fill_tag,
    input wire [PID_W-1:0] fill_pid,
    input wire [GEN_W-1:0] fill_gen,
    input wire [3:0] fill_sectors,
    input wire [1023:0] fill_data,
    input wire [127:0] fill_be, fill_protect_be,
    output wire fill_dropped,
    // One finite descriptor-reference operation per cycle. Global max512,
    // per physical line max32. Internal read snapshots share this accounting.
    input wire pin_valid, output wire pin_ready, input wire pin_increment,
    input wire [PID_W-1:0] pin_pid, input wire [GEN_W-1:0] pin_gen,
    output wire wb_valid, input wire wb_ready,
    output wire [1023:0] wb_data,
    output wire [127:0] wb_be,
    output wire [ADDR_W-1:0] wb_addr,
    output wire [WAD_W-1:0] wb_ticket,
    output wire [GEN_W-1:0] wb_ticket_gen,
    input wire done_valid, output wire done_ready,
    input wire [WAD_W-1:0] done_ticket,
    input wire [GEN_W-1:0] done_gen,
    output wire done_dropped,
    output wire module_drained, output wire generation_blocked,
    output wire [WAD_W:0] wad_count, wb_count,
    output wire [9:0] reference_count
);
    wire [3:0] ram_enable,ram_write;
    wire [4*ROW_W-1:0] ram_row;
    wire [511:0] ram_be;
    wire [4095:0] ram_wdata,ram_rdata;
    ep_l2_slice_ctrl #(.MODE(MODE),.N_TAG(N_TAG),.N_PAYLOAD(N_PAYLOAD),.STATIC_WB(STATIC_WB),.N_WAD(N_WAD),.GEN_W(GEN_W),.ADDR_W(ADDR_W)) controller(.*);
    ep_l2_payload_banks #(.N_PAYLOAD(N_PAYLOAD),.ROW_W(ROW_W)) payload(.*);
endmodule
