// Pipelined multiply-accumulate unit with a selectable multiplier.
//   MUL = 0 : exact
//   MUL = 1 : column-truncated (parameter K)
//   MUL = 2 : Mitchell logarithmic
// Stage 1 registers the product, stage 2 accumulates into 32 bits.
// 'clr' restarts the accumulation with the incoming product.
module mac #(
    parameter integer MUL = 0,
    parameter integer K   = 4
) (
    input  wire               clk,
    input  wire               rst,
    input  wire               en,
    input  wire               clr,
    input  wire signed [7:0]  a,
    input  wire signed [7:0]  b,
    output reg  signed [31:0] acc
);
    wire signed [15:0] p;

    generate
        if (MUL == 1) begin : g_trunc
            mul_trunc #(.K(K)) u_mul (.a(a), .b(b), .p(p));
        end else if (MUL == 2) begin : g_mitchell
            mul_mitchell u_mul (.a(a), .b(b), .p(p));
        end else begin : g_exact
            mul_exact u_mul (.a(a), .b(b), .p(p));
        end
    endgenerate

    reg signed [15:0] p_q;
    reg               v_q, clr_q;

    always @(posedge clk) begin
        if (rst) begin
            p_q   <= 16'sd0;
            v_q   <= 1'b0;
            clr_q <= 1'b0;
            acc   <= 32'sd0;
        end else begin
            p_q   <= p;
            v_q   <= en;
            clr_q <= clr;
            if (v_q)
                acc <= (clr_q ? 32'sd0 : acc) + {{16{p_q[15]}}, p_q};
        end
    end
endmodule
