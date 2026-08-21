// Simulation-only protocol checks for c2p_snapshot_banked_frontend.
// Included inside the frontend module when C2P_SIM_ASSERTS is defined.
integer c2p_sim_copy_i;
integer c2p_sim_bank_i;
integer c2p_sim_other_bank_i;
reg [ENGINE_W-1:0] c2p_sim_owner_i;
reg [ENGINE_W-1:0] c2p_sim_other_owner_i;

/* verilator lint_off BLKSEQ */
always @(posedge clk) begin
    if (!reset) begin
        for (c2p_sim_copy_i = 0; c2p_sim_copy_i < 4;
             c2p_sim_copy_i = c2p_sim_copy_i + 1) begin
            for (c2p_sim_bank_i = 0; c2p_sim_bank_i < NUM_BANKS;
                 c2p_sim_bank_i = c2p_sim_bank_i + 1) begin
                c2p_sim_owner_i = bank_rsp_owner[
                    (c2p_sim_copy_i*NUM_BANKS + c2p_sim_bank_i)*ENGINE_W +: ENGINE_W];
                if (bank_rsp_valid[c2p_sim_copy_i*NUM_BANKS + c2p_sim_bank_i] &&
                    bank_rsp_ready[c2p_sim_copy_i*NUM_BANKS + c2p_sim_bank_i]) begin
                    if (c2p_sim_owner_i >= ENGINES)
                        $fatal(1, "C2P response owner out of range: copy=%0d bank=%0d owner=%0d",
                               c2p_sim_copy_i, c2p_sim_bank_i, c2p_sim_owner_i);
                    if (!engine_valid[c2p_sim_owner_i] ||
                        !engine_sent[c2p_sim_owner_i][c2p_sim_copy_i])
                        $fatal(1, "C2P response has no outstanding owner: copy=%0d bank=%0d owner=%0d",
                               c2p_sim_copy_i, c2p_sim_bank_i, c2p_sim_owner_i);
                    for (c2p_sim_other_bank_i = c2p_sim_bank_i + 1;
                         c2p_sim_other_bank_i < NUM_BANKS;
                         c2p_sim_other_bank_i = c2p_sim_other_bank_i + 1) begin
                        c2p_sim_other_owner_i = bank_rsp_owner[
                            (c2p_sim_copy_i*NUM_BANKS + c2p_sim_other_bank_i)*ENGINE_W +: ENGINE_W];
                        if (bank_rsp_valid[c2p_sim_copy_i*NUM_BANKS + c2p_sim_other_bank_i] &&
                            bank_rsp_ready[c2p_sim_copy_i*NUM_BANKS + c2p_sim_other_bank_i] &&
                            (c2p_sim_owner_i == c2p_sim_other_owner_i))
                            $fatal(1, "C2P duplicate response owner: copy=%0d owner=%0d",
                                   c2p_sim_copy_i, c2p_sim_owner_i);
                    end
                end
            end
        end
    end
end
/* verilator lint_on BLKSEQ */
