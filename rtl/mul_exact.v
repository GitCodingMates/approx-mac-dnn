// Exact 8x8 signed multiplier (sign-magnitude), baseline design.
module mul_exact (
    input  wire signed [7:0]  a,
    input  wire signed [7:0]  b,
    output wire signed [15:0] p
);
    wire [7:0] ma, mb;
    wire       neg;
    sign_mag u_sm (.a(a), .b(b), .ma(ma), .mb(mb), .neg(neg));

    wire [15:0] mag = ma * mb;
    assign p = neg ? -$signed(mag) : $signed(mag);
endmodule
