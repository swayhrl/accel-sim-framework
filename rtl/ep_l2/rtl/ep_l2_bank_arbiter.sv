// Three bounded clients, one actual read OR write per bank per clock.
// Round-robin is deliberately finite hardware, not the simulator's unbounded
// pending vector. See SIM_RTL_TIMING_GAP.md before using simulator cycles.
module ep_l2_bank_arbiter (
    input wire clk, input wire rst_n,
    input wire [2:0] request,
    input wire [5:0] bank,
    output reg [2:0] grant
);
    reg [1:0] next_client [0:3];
    integer b, k, c;
    reg chosen;
    always @* begin
        grant = 0;
        for (b = 0; b < 4; b = b + 1) begin
            chosen = 0;
            for (k = 0; k < 3; k = k + 1) begin
                c = next_client[b] + k;
                if (c >= 3) c = c - 3;
                if (!chosen && request[c] && bank[2*c +: 2] == b) begin
                    grant[c] = 1;
                    chosen = 1;
                end
            end
        end
    end
    always @(posedge clk) begin
        if (!rst_n) begin
            for (integer i = 0; i < 4; i = i + 1) next_client[i] <= 0;
        end else begin
            for (integer j = 0; j < 3; j = j + 1)
                if (grant[j]) next_client[bank[2*j +: 2]] <= j == 2 ? 0 : j + 1;
        end
    end
endmodule
