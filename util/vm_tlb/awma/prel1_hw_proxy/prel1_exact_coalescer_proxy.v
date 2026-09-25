`timescale 1ns/1ps

// Technology-neutral proxy for the frozen PREL1 exact request coalescer.
// This module deliberately excludes the TLB array, page walker, scheduler and
// memory pipeline. It models two exact-key live entries, 32 bounded follower
// continuations per entry, completion-tag matching and finite drain/reuse.
module prel1_exact_coalescer_proxy #(
    parameter ASID_W = 32,
    parameter VPN_W = 33,
    parameter PAGE_W = 1,
    parameter GENERATION_W = 64,
    parameter ACCESS_W = 2,
    parameter TAG_W = 32,
    parameter PPN_W = 33,
    parameter WAITER_META_W = 32,
    parameter REGISTER_COMPARE = 0
) (
    input wire clk,
    input wire rst,

    input wire req_valid,
    input wire [ASID_W-1:0] req_asid,
    input wire [VPN_W-1:0] req_vpn,
    input wire [PAGE_W-1:0] req_page,
    input wire [GENERATION_W-1:0] req_generation,
    input wire [ACCESS_W-1:0] req_access,
    input wire [TAG_W-1:0] req_tag,
    input wire [WAITER_META_W-1:0] req_waiter_meta,

    output reg decision_valid,
    output reg leader_launch,
    output reg follower_admit,
    output reg entry_full_fallback,
    output reg waiter_full_fallback,
    output reg decision_entry,

    input wire completion_valid,
    input wire [TAG_W-1:0] completion_tag,
    input wire [PPN_W-1:0] completion_ppn,
    output reg completion_match,

    output reg follower_out_valid,
    output reg [WAITER_META_W-1:0] follower_out_meta,
    output reg [PPN_W-1:0] follower_out_ppn,

    output wire [1:0] debug_state0,
    output wire [1:0] debug_state1,
    output wire [5:0] debug_waiters0,
    output wire [5:0] debug_waiters1
);

  localparam STATE_FREE  = 2'd0;
  localparam STATE_LIVE  = 2'd1;
  localparam STATE_DRAIN = 2'd2;

  reg [1:0] state0, state1;
  reg [ASID_W-1:0] asid0, asid1;
  reg [VPN_W-1:0] vpn0, vpn1;
  reg [PAGE_W-1:0] page0, page1;
  reg [GENERATION_W-1:0] generation0, generation1;
  reg [ACCESS_W-1:0] access0, access1;
  reg [TAG_W-1:0] leader_tag0, leader_tag1;
  reg [PPN_W-1:0] result_ppn0, result_ppn1;
  reg [5:0] waiter_count0, waiter_count1;
  reg [5:0] drain_index0, drain_index1;
  reg [WAITER_META_W-1:0] waiter_meta0 [0:31];
  reg [WAITER_META_W-1:0] waiter_meta1 [0:31];

  reg pending_valid;
  reg [ASID_W-1:0] pending_asid;
  reg [VPN_W-1:0] pending_vpn;
  reg [PAGE_W-1:0] pending_page;
  reg [GENERATION_W-1:0] pending_generation;
  reg [ACCESS_W-1:0] pending_access;
  reg [TAG_W-1:0] pending_tag;
  reg [WAITER_META_W-1:0] pending_waiter_meta;

  wire eff_valid = REGISTER_COMPARE ? pending_valid : req_valid;
  wire [ASID_W-1:0] eff_asid = REGISTER_COMPARE ? pending_asid : req_asid;
  wire [VPN_W-1:0] eff_vpn = REGISTER_COMPARE ? pending_vpn : req_vpn;
  wire [PAGE_W-1:0] eff_page = REGISTER_COMPARE ? pending_page : req_page;
  wire [GENERATION_W-1:0] eff_generation =
      REGISTER_COMPARE ? pending_generation : req_generation;
  wire [ACCESS_W-1:0] eff_access =
      REGISTER_COMPARE ? pending_access : req_access;
  wire [TAG_W-1:0] eff_tag = REGISTER_COMPARE ? pending_tag : req_tag;
  wire [WAITER_META_W-1:0] eff_waiter_meta =
      REGISTER_COMPARE ? pending_waiter_meta : req_waiter_meta;

  wire match0 = state0 == STATE_LIVE && asid0 == eff_asid &&
      vpn0 == eff_vpn && page0 == eff_page &&
      generation0 == eff_generation && access0 == eff_access;
  wire match1 = state1 == STATE_LIVE && asid1 == eff_asid &&
      vpn1 == eff_vpn && page1 == eff_page &&
      generation1 == eff_generation && access1 == eff_access;
  wire free0 = state0 == STATE_FREE;
  wire free1 = state1 == STATE_FREE;

  assign debug_state0 = state0;
  assign debug_state1 = state1;
  assign debug_waiters0 = waiter_count0;
  assign debug_waiters1 = waiter_count1;

  integer i;
  always @(posedge clk) begin
    if (rst) begin
      state0 <= STATE_FREE;
      state1 <= STATE_FREE;
      waiter_count0 <= 0;
      waiter_count1 <= 0;
      drain_index0 <= 0;
      drain_index1 <= 0;
      pending_valid <= 0;
      decision_valid <= 0;
      leader_launch <= 0;
      follower_admit <= 0;
      entry_full_fallback <= 0;
      waiter_full_fallback <= 0;
      decision_entry <= 0;
      completion_match <= 0;
      follower_out_valid <= 0;
      follower_out_meta <= 0;
      follower_out_ppn <= 0;
      asid0 <= 0; asid1 <= 0;
      vpn0 <= 0; vpn1 <= 0;
      page0 <= 0; page1 <= 0;
      generation0 <= 0; generation1 <= 0;
      access0 <= 0; access1 <= 0;
      leader_tag0 <= 0; leader_tag1 <= 0;
      result_ppn0 <= 0; result_ppn1 <= 0;
      for (i = 0; i < 32; i = i + 1) begin
        waiter_meta0[i] <= 0;
        waiter_meta1[i] <= 0;
      end
    end else begin
      decision_valid <= 0;
      leader_launch <= 0;
      follower_admit <= 0;
      entry_full_fallback <= 0;
      waiter_full_fallback <= 0;
      completion_match <= 0;
      follower_out_valid <= 0;

      // A registered compare variant captures the request one cycle before
      // the exact CAM decision. The state capacity and waiter semantics are
      // otherwise identical.
      if (REGISTER_COMPARE) begin
        pending_valid <= req_valid;
        if (req_valid) begin
          pending_asid <= req_asid;
          pending_vpn <= req_vpn;
          pending_page <= req_page;
          pending_generation <= req_generation;
          pending_access <= req_access;
          pending_tag <= req_tag;
          pending_waiter_meta <= req_waiter_meta;
        end
      end else begin
        pending_valid <= 0;
      end

      // One finite follower-completion channel drains a completed entry.
      // Entry 0 has deterministic priority when both entries are draining.
      if (state0 == STATE_DRAIN && drain_index0 < waiter_count0) begin
        follower_out_valid <= 1;
        follower_out_meta <= waiter_meta0[drain_index0];
        follower_out_ppn <= result_ppn0;
        if (drain_index0 + 1 == waiter_count0) begin
          state0 <= STATE_FREE;
          waiter_count0 <= 0;
          drain_index0 <= 0;
        end else begin
          drain_index0 <= drain_index0 + 1;
        end
      end else if (state1 == STATE_DRAIN && drain_index1 < waiter_count1) begin
        follower_out_valid <= 1;
        follower_out_meta <= waiter_meta1[drain_index1];
        follower_out_ppn <= result_ppn1;
        if (drain_index1 + 1 == waiter_count1) begin
          state1 <= STATE_FREE;
          waiter_count1 <= 0;
          drain_index1 <= 0;
        end else begin
          drain_index1 <= drain_index1 + 1;
        end
      end

      if (completion_valid) begin
        if (state0 == STATE_LIVE && leader_tag0 == completion_tag) begin
          completion_match <= 1;
          result_ppn0 <= completion_ppn;
          if (waiter_count0 == 0)
            state0 <= STATE_FREE;
          else begin
            state0 <= STATE_DRAIN;
            drain_index0 <= 0;
          end
        end else if (state1 == STATE_LIVE && leader_tag1 == completion_tag) begin
          completion_match <= 1;
          result_ppn1 <= completion_ppn;
          if (waiter_count1 == 0)
            state1 <= STATE_FREE;
          else begin
            state1 <= STATE_DRAIN;
            drain_index1 <= 0;
          end
        end
      end

      if (eff_valid) begin
        decision_valid <= 1;
        if (match0) begin
          decision_entry <= 0;
          if (waiter_count0 < 32) begin
            follower_admit <= 1;
            waiter_meta0[waiter_count0] <= eff_waiter_meta;
            waiter_count0 <= waiter_count0 + 1;
          end else begin
            waiter_full_fallback <= 1;
          end
        end else if (match1) begin
          decision_entry <= 1;
          if (waiter_count1 < 32) begin
            follower_admit <= 1;
            waiter_meta1[waiter_count1] <= eff_waiter_meta;
            waiter_count1 <= waiter_count1 + 1;
          end else begin
            waiter_full_fallback <= 1;
          end
        end else if (free0) begin
          decision_entry <= 0;
          leader_launch <= 1;
          state0 <= STATE_LIVE;
          asid0 <= eff_asid;
          vpn0 <= eff_vpn;
          page0 <= eff_page;
          generation0 <= eff_generation;
          access0 <= eff_access;
          leader_tag0 <= eff_tag;
          waiter_count0 <= 0;
        end else if (free1) begin
          decision_entry <= 1;
          leader_launch <= 1;
          state1 <= STATE_LIVE;
          asid1 <= eff_asid;
          vpn1 <= eff_vpn;
          page1 <= eff_page;
          generation1 <= eff_generation;
          access1 <= eff_access;
          leader_tag1 <= eff_tag;
          waiter_count1 <= 0;
        end else begin
          entry_full_fallback <= 1;
        end
      end
    end
  end
endmodule
