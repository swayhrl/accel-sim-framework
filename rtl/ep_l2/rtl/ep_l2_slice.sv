// Macro boundary companion. Instantiate ep_l2_slice_ctrl with these SRAM ports
// in a SoC wrapper. Keeping this separate makes the controller timing cut exact.
module ep_l2_payload_banks #(
    parameter integer N_PAYLOAD=1168, ROW_W=$clog2(N_PAYLOAD/4)
)(
    input wire clk,
    input wire [3:0] ram_enable, ram_write,
    input wire [4*ROW_W-1:0] ram_row,
    input wire [511:0] ram_be,
    input wire [4095:0] ram_wdata,
    output wire [4095:0] ram_rdata
);
    genvar b;
    generate for (b=0;b<4;b=b+1) begin: bank
        ep_l2_payload_sram #(.ROWS(N_PAYLOAD/4),.ROW_W(ROW_W)) sram(
            .clk(clk),.enable(ram_enable[b]),.write(ram_write[b]),
            .row(ram_row[b*ROW_W +:ROW_W]),
            .byte_enable(ram_be[b*128 +:128]),
            .write_data(ram_wdata[b*1024 +:1024]),
            .read_data(ram_rdata[b*1024 +:1024]));
    end endgenerate
endmodule
