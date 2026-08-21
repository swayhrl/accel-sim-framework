`timescale 1ns/1ps

module tb_c2p_snapshot_banked_frontend;
    localparam integer ENGINES = 64;
    localparam integer TAG_W = 64;
    localparam integer ROW_W = 13;
    localparam integer ENGINE_W = 6;
    reg clk = 1'b0;
    reg reset = 1'b1;
    reg [ENGINES-1:0] in_valid = 0;
    wire [ENGINES-1:0] in_ready;
    reg [ENGINES*TAG_W-1:0] in_tag = 0;
    reg [ENGINES-1:0] in_aux = 0;
    wire [255:0] bank_req_valid;
    wire [255:0] bank_req_ready;
    wire [4*64*ENGINE_W-1:0] bank_req_owner;
    wire [4*64*ROW_W-1:0] bank_req_row;
    reg [255:0] bank_rsp_valid = 0;
    wire [255:0] bank_rsp_ready;
    reg [4*64*ENGINE_W-1:0] bank_rsp_owner = 0;
    reg [4*64*64-1:0] bank_rsp_data = 0;
    wire [ENGINES-1:0] out_valid;
    reg [ENGINES-1:0] out_ready = {ENGINES{1'b1}};
    wire [ENGINES*64-1:0] out_data0;
    wire [ENGINES*64-1:0] out_data1;
    wire [ENGINES*64-1:0] out_data2;
    wire [ENGINES*64-1:0] out_data3;
    wire [ENGINES-1:0] out_aux;
    integer copy_i;
    integer bank_i;
    integer count0;
    integer count_i;
    reg [ENGINES-1:0] completed = 0;

    always #5 clk = ~clk;

    c2p_snapshot_banked_frontend #(.ENGINES(ENGINES)) dut (
        .clk(clk), .reset(reset), .in_valid(in_valid), .in_ready(in_ready),
        .in_tag(in_tag), .in_aux(in_aux),
        .bank_req_valid(bank_req_valid), .bank_req_owner(bank_req_owner),
        .bank_req_ready(bank_req_ready),
        .bank_req_row(bank_req_row),
        .bank_rsp_valid(bank_rsp_valid), .bank_rsp_ready(bank_rsp_ready),
        .bank_rsp_owner(bank_rsp_owner),
        .bank_rsp_data(bank_rsp_data),
        .out_valid(out_valid), .out_ready(out_ready),
        .out_data0(out_data0), .out_data1(out_data1),
        .out_data2(out_data2), .out_data3(out_data3), .out_aux(out_aux)
    );

    assign bank_req_ready = ~bank_rsp_valid | bank_rsp_ready;

    // A synchronous physical bank returns the command owner and row data in
    // the following cycle. The response order can differ by copy; the DUT
    // must join all four before completing an engine.
    always @(posedge clk) begin
        for (bank_i = 0; bank_i < 4*64; bank_i = bank_i + 1) begin
            if (bank_rsp_valid[bank_i] && bank_rsp_ready[bank_i])
                bank_rsp_valid[bank_i] <= 1'b0;
            if (bank_req_valid[bank_i]) begin
                if (bank_rsp_valid[bank_i] && !bank_rsp_ready[bank_i])
                    $fatal(1, "test bank response overflow at bank %0d", bank_i);
                bank_rsp_valid[bank_i] <= 1'b1;
                bank_rsp_owner[bank_i*ENGINE_W +: ENGINE_W] <=
                    bank_req_owner[bank_i*ENGINE_W +: ENGINE_W];
                bank_rsp_data[bank_i*64 +: 64] <= {56'b0, bank_i[7:0]};
            end
        end
        completed <= completed | out_valid;
    end

    task check_replica_count;
        begin
            count0 = 0;
            for (bank_i = 0; bank_i < 64; bank_i = bank_i + 1)
                if (bank_req_valid[bank_i]) count0 = count0 + 1;
        end
    endtask

    initial begin
        repeat (3) @(posedge clk);
        @(negedge clk);
        reset = 1'b0;

        // Identical tags collide in all four copies. The four independent
        // bank arbiters each issue one owner-tagged row; the other engines
        // remain pending until their own rows are granted.
        in_tag[0*TAG_W +: TAG_W] = 64'h1234;
        in_tag[1*TAG_W +: TAG_W] = 64'h1234;
        in_tag[2*TAG_W +: TAG_W] = 64'h1234;
        in_tag[3*TAG_W +: TAG_W] = 64'h1234;
        in_aux[3:0] = 4'b1010;
        in_valid[3:0] = 4'b1111;
        @(negedge clk);
        in_valid = 0;
        while (!(|bank_req_valid)) @(negedge clk);
        check_replica_count();
        if (count0 != 1)
            $fatal(1, "identical tags should grant one lane, got %0d", count0);
        // The joined result must remain stable until its consumer accepts it;
        // otherwise owner 0 could be reused while a four-copy response is
        // still visible.
        out_ready[3:0] = 4'b0000;
        while (!out_valid[0]) @(negedge clk);
        repeat (2) @(negedge clk);
        if (!out_valid[0])
            $fatal(1, "response joiner dropped a backpressured result");
        out_ready[3:0] = 4'b1111;

        // Let the remaining held engines drain, then inject four independent
        // tags. Their rows may use different banks in each copy, so completion
        // is tracked per row rather than requiring equal per-copy counts.
        repeat (12) @(negedge clk);
        while (in_ready[3:0] != 4'b1111) @(negedge clk);
        in_tag[0*TAG_W +: TAG_W] = 64'h0000000000000000;
        in_tag[1*TAG_W +: TAG_W] = 64'h1111111111111111;
        in_tag[2*TAG_W +: TAG_W] = 64'h2222222222222222;
        in_tag[3*TAG_W +: TAG_W] = 64'h3333333333333333;
        in_valid[3:0] = 4'b1111;
        @(negedge clk);
        in_valid = 0;
        while (!(|bank_req_valid)) @(negedge clk);
        if (!(|bank_req_valid))
            $fatal(1, "independent tags made no Snapshot progress");
        repeat (40) @(negedge clk);
        if (in_ready[3:0] != 4'b1111)
            $fatal(1, "per-copy request bookkeeping did not drain: %b", in_ready[3:0]);
        if (completed[3:0] != 4'b1111)
            $fatal(1, "owner-tagged response joiner missed completions: %b", completed[3:0]);
        $display("PASS tb_c2p_snapshot_banked_frontend");
        $finish;
    end

    initial begin
        #10000;
        $fatal(1, "tb_c2p_snapshot_banked_frontend timeout");
    end
endmodule
