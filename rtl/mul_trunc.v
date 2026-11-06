// Column-truncated 8x8 signed multiplier.
// Partial-product bits a_i & b_j with i + j < K are not generated,
// which removes their AND gates and adder cells from the array.
module mul_trunc #(
    parameter integer K = 4
) (
    input  wire signed [7:0]  a,
    input  wire signed [7:0]  b,
    output wire signed [15:0] p
);
    wire [7:0] ma, mb;
    wire       neg;
    sign_mag u_sm (.a(a), .b(b), .ma(ma), .mb(mb), .neg(neg));

    // One row per bit of mb; bits below column K are masked to zero.
    wire [15:0] row [0:7];
    genvar j;
    generate
        for (j = 0; j < 8; j = j + 1) begin : g_row
            localparam integer SH = (K > j) ? (K - j) : 0;
            localparam [7:0]   KEEP = (SH >= 8) ? 8'h00 : (8'hFF << SH);
            assign row[j] = {8'd0, ma & KEEP & {8{mb[j]}}} << j;
        end
    endgenerate

    wire [15:0] mag = row[0] + row[1] + row[2] + row[3]
                    + row[4] + row[5] + row[6] + row[7];
    assign p = neg ? -$signed(mag) : $signed(mag);
endmodule
