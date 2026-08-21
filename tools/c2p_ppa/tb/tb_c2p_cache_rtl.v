`timescale 1ns/1ps

module tb_c2p_cache_rtl;
    reg clk = 1'b0;
    reg reset = 1'b1;
    reg update_valid = 1'b0;
    wire update_ready;
    reg [5:0] update_sid = 6'd0;
    reg [63:0] update_tag = 64'd0;
    reg miss_valid = 1'b0;
    wire miss_ready;
    reg [5:0] miss_sid = 6'd0;
    reg [63:0] miss_tag = 64'd0;
    wire probe_req_valid;
    wire [5:0] probe_req_sid;
    wire [63:0] probe_req_tag;
    reg probe_rsp_valid = 1'b0;
    wire probe_rsp_ready;
    reg probe_rsp_hit = 1'b0;
    wire peer_hit_valid;
    wire [5:0] peer_hit_sid;
    wire [63:0] peer_hit_tag;
    wire lower_req_valid;
    wire [63:0] lower_req_tag;
    wire lower_req_no_candidate;

    always #5 clk = ~clk;

    c2p_cache_rtl dut (
        .clk(clk), .reset(reset),
        .update_valid(update_valid), .update_ready(update_ready),
        .update_sid(update_sid), .update_tag(update_tag),
        .miss_valid(miss_valid), .miss_ready(miss_ready),
        .miss_sid(miss_sid), .miss_tag(miss_tag),
        .probe_req_valid(probe_req_valid), .probe_req_ready(1'b1),
        .probe_req_sid(probe_req_sid), .probe_req_tag(probe_req_tag),
        .probe_rsp_valid(probe_rsp_valid), .probe_rsp_ready(probe_rsp_ready),
        .probe_rsp_hit(probe_rsp_hit),
        .peer_hit_valid(peer_hit_valid), .peer_hit_ready(1'b1),
        .peer_hit_sid(peer_hit_sid), .peer_hit_tag(peer_hit_tag),
        .lower_req_valid(lower_req_valid), .lower_req_ready(1'b1),
        .lower_req_tag(lower_req_tag),
        .lower_req_no_candidate(lower_req_no_candidate)
    );

    task push_update;
        input [5:0] sid;
        input [63:0] tag;
        begin
            while (!update_ready) @(negedge clk);
            update_sid = sid;
            update_tag = tag;
            update_valid = 1'b1;
            @(negedge clk);
            update_valid = 1'b0;
        end
    endtask

    task push_miss;
        input [5:0] sid;
        input [63:0] tag;
        begin
            while (!miss_ready) @(negedge clk);
            miss_sid = sid;
            miss_tag = tag;
            miss_valid = 1'b1;
            @(negedge clk);
            miss_valid = 1'b0;
        end
    endtask

    task expect_probe;
        input [5:0] expected_sid;
        input expected_hit;
        begin
            while (!probe_req_valid) @(negedge clk);
            if (probe_req_sid !== expected_sid)
                $fatal(1, "expected probe sid %0d, got %0d", expected_sid,
                       probe_req_sid);
            @(negedge clk);
            probe_rsp_hit = expected_hit;
            probe_rsp_valid = 1'b1;
            @(negedge clk);
            probe_rsp_valid = 1'b0;
        end
    endtask

    task expect_peer_hit;
        input [5:0] expected_sid;
        input [63:0] expected_tag;
        begin
            while (!peer_hit_valid) @(negedge clk);
            if (peer_hit_sid !== expected_sid || peer_hit_tag !== expected_tag)
                $fatal(1, "unexpected peer-hit completion");
        end
    endtask

    task expect_lower;
        input [63:0] expected_tag;
        input expected_no_candidate;
        begin
            while (!lower_req_valid) @(negedge clk);
            if (lower_req_tag !== expected_tag ||
                lower_req_no_candidate !== expected_no_candidate)
                $fatal(1, "unexpected lower-memory fallback");
        end
    endtask

    initial begin
        repeat (3) @(posedge clk);
        reset = 1'b0;
        // The matrix reset clears one of the 5,120 rows per cycle.
        while (!update_ready) @(negedge clk);

        // Two candidate owners exist.  The same-cluster owner must be tried
        // first; its exact miss then advances to the next candidate.
        push_update(6'd3, 64'h1234);
        push_update(6'd9, 64'h1234);
        push_miss(6'd1, 64'h1234);
        expect_probe(6'd3, 1'b0);
        expect_probe(6'd9, 1'b1);
        expect_peer_hit(6'd9, 64'h1234);

        // A line with no metadata candidate falls through without a probe.
        push_miss(6'd2, 64'habc0);
        expect_lower(64'habc0, 1'b1);

        // An exact probe miss after a real candidate is an exhausted-candidate
        // fallback, distinct from the no-candidate fast path.
        push_update(6'd6, 64'hface);
        push_miss(6'd2, 64'hface);
        expect_probe(6'd6, 1'b0);
        expect_lower(64'hface, 1'b0);

        // Equidistant clusters retain the C++ tie break: lower SID first.
        // The timing-oriented RTL walker may spend extra cycles scanning, but
        // it must not change this externally visible probe order.
        push_update(6'd5, 64'hbeef);
        push_update(6'd35, 64'hbeef);
        push_miss(6'd20, 64'hbeef);
        expect_probe(6'd5, 1'b0);
        expect_probe(6'd35, 1'b1);
        expect_peer_hit(6'd35, 64'hbeef);

        // The requester is always removed from its own candidate bitmap.
        push_update(6'd4, 64'hfeed);
        push_miss(6'd4, 64'hfeed);
        expect_lower(64'hfeed, 1'b1);

        $display("PASS tb_c2p_cache_rtl");
        $finish;
    end

    initial begin
        #200000;
        $fatal(1, "tb_c2p_cache_rtl timeout");
    end
endmodule
