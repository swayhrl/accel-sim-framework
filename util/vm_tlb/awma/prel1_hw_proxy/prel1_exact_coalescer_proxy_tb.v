`timescale 1ns/1ps

module prel1_exact_coalescer_proxy_tb #(
    parameter REGISTER_COMPARE = 0,
    parameter WAITER_META_W = 32
);
  reg clk = 0;
  always #5 clk = ~clk;
  reg rst;
  reg req_valid;
  reg [31:0] req_asid;
  reg [32:0] req_vpn;
  reg req_page;
  reg [63:0] req_generation;
  reg [1:0] req_access;
  reg [31:0] req_tag;
  reg [WAITER_META_W-1:0] req_waiter_meta;
  wire decision_valid, leader_launch, follower_admit;
  wire entry_full_fallback, waiter_full_fallback, decision_entry;
  reg completion_valid;
  reg [31:0] completion_tag;
  reg [32:0] completion_ppn;
  wire completion_match;
  wire follower_out_valid;
  wire [WAITER_META_W-1:0] follower_out_meta;
  wire [32:0] follower_out_ppn;
  wire [1:0] debug_state0, debug_state1;
  wire [5:0] debug_waiters0, debug_waiters1;

  prel1_exact_coalescer_proxy #(
      .WAITER_META_W(WAITER_META_W),
      .REGISTER_COMPARE(REGISTER_COMPARE)
  ) dut (
      .clk(clk), .rst(rst), .req_valid(req_valid), .req_asid(req_asid),
      .req_vpn(req_vpn), .req_page(req_page),
      .req_generation(req_generation), .req_access(req_access),
      .req_tag(req_tag), .req_waiter_meta(req_waiter_meta),
      .decision_valid(decision_valid), .leader_launch(leader_launch),
      .follower_admit(follower_admit),
      .entry_full_fallback(entry_full_fallback),
      .waiter_full_fallback(waiter_full_fallback),
      .decision_entry(decision_entry),
      .completion_valid(completion_valid), .completion_tag(completion_tag),
      .completion_ppn(completion_ppn), .completion_match(completion_match),
      .follower_out_valid(follower_out_valid),
      .follower_out_meta(follower_out_meta),
      .follower_out_ppn(follower_out_ppn),
      .debug_state0(debug_state0), .debug_state1(debug_state1),
      .debug_waiters0(debug_waiters0), .debug_waiters1(debug_waiters1));

  integer failures = 0;
  integer follower_outputs = 0;
  reg [255:0] seen;

  task check;
    input condition;
    input [8*80-1:0] message;
    begin
      if (!condition) begin
        $display("FAIL %s", message);
        failures = failures + 1;
      end
    end
  endtask

  task send_req;
    input [31:0] asid;
    input [32:0] vpn;
    input [63:0] generation;
    input [1:0] access;
    input [31:0] tag;
    input [WAITER_META_W-1:0] meta;
    begin
      @(negedge clk);
      req_valid = 1;
      req_asid = asid;
      req_vpn = vpn;
      req_page = 0;
      req_generation = generation;
      req_access = access;
      req_tag = tag;
      req_waiter_meta = meta;
      @(posedge clk); #1;
      req_valid = 0;
      if (REGISTER_COMPARE) begin
        @(posedge clk); #1;
      end
      check(decision_valid, "request decision missing");
    end
  endtask

  task complete;
    input [31:0] tag;
    input [32:0] ppn;
    begin
      @(negedge clk);
      completion_valid = 1;
      completion_tag = tag;
      completion_ppn = ppn;
      @(posedge clk); #1;
      completion_valid = 0;
      check(completion_match, "completion tag did not match");
    end
  endtask

  integer i;
  integer meta_index;
  initial begin
    rst = 1;
    req_valid = 0;
    completion_valid = 0;
    req_asid = 0; req_vpn = 0; req_page = 0;
    req_generation = 0; req_access = 0; req_tag = 0;
    req_waiter_meta = 0; completion_tag = 0; completion_ppn = 0;
    seen = 0;
    repeat (2) @(posedge clk);
    @(negedge clk); rst = 0;

    // Unique request occupies entry 0.
    send_req(0, 33'd10, 64'd1, 2'd0, 32'd1, 32'd1);
    check(leader_launch && !decision_entry, "unique request is not leader0");

    // Exact in-flight duplicate becomes a follower.
    send_req(0, 33'd10, 64'd1, 2'd0, 32'd2, 32'd2);
    check(follower_admit && !decision_entry, "exact follower not admitted");

    // Different VPN occupies entry 1; a third identity sees entry-full.
    send_req(0, 33'd11, 64'd1, 2'd0, 32'd3, 32'd3);
    check(leader_launch && decision_entry, "different VPN merged incorrectly");
    send_req(0, 33'd12, 64'd1, 2'd0, 32'd4, 32'd4);
    check(entry_full_fallback, "two-entry full fallback missing");
    complete(32'd3, 33'd11);

    // ASID, generation and access mismatches each allocate rather than merge.
    send_req(32'd1, 33'd10, 64'd1, 2'd0, 32'd5, 32'd5);
    check(leader_launch && decision_entry, "ASID mismatch merged");
    complete(32'd5, 33'd10);
    send_req(0, 33'd10, 64'd2, 2'd0, 32'd6, 32'd6);
    check(leader_launch && decision_entry, "generation mismatch merged");
    complete(32'd6, 33'd10);
    send_req(0, 33'd10, 64'd1, 2'd1, 32'd7, 32'd7);
    check(leader_launch && decision_entry, "access mismatch merged");
    complete(32'd7, 33'd10);

    // Entry 0 already has follower meta 2. Add 31 more, then reject the 33rd.
    for (i = 0; i < 31; i = i + 1) begin
      send_req(0, 33'd10, 64'd1, 2'd0, 32'd20+i, 32'd20+i);
      check(follower_admit, "bounded follower admission failed");
    end
    check(debug_waiters0 == 32, "waiter count is not 32");
    send_req(0, 33'd10, 64'd1, 2'd0, 32'd99, 32'd99);
    check(waiter_full_fallback, "32-waiter full fallback missing");

    complete(32'd1, 33'd1000);
    while (follower_outputs < 32) begin
      @(posedge clk); #1;
      if (follower_out_valid) begin
        meta_index = follower_out_meta[7:0];
        check(!seen[meta_index], "duplicate follower completion");
        seen[meta_index] = 1'b1;
        check(follower_out_ppn == 33'd1000, "wrong completion PPN");
        follower_outputs = follower_outputs + 1;
      end
    end
    @(posedge clk); #1;
    check(!follower_out_valid, "extra follower completion");
    check(debug_state0 == 0 && debug_waiters0 == 0,
          "entry did not drain/free");

    // Freed entry is reusable.
    send_req(0, 33'd99, 64'd3, 2'd2, 32'd100, 32'd100);
    check(leader_launch, "drained entry was not reusable");
    complete(32'd100, 33'd99);
    check(debug_state0 == 0, "zero-waiter completion did not free entry");

    if (failures == 0)
      $display("PREL1_RTL_PROXY_TEST PASS registered=%0d waiter_meta=%0d",
               REGISTER_COMPARE, WAITER_META_W);
    else
      $display("PREL1_RTL_PROXY_TEST FAIL count=%0d", failures);
    $finish(failures != 0);
  end
endmodule
