// Signed 8-bit operands -> 8-bit unsigned magnitudes and product sign.
// |-128| = 128 fits in 8 unsigned bits.
module sign_mag (
    input  wire signed [7:0] a,
    input  wire signed [7:0] b,
    output wire        [7:0] ma,
    output wire        [7:0] mb,
    output wire              neg
);
    assign ma  = a[7] ? (~a + 8'd1) : a;
    assign mb  = b[7] ? (~b + 8'd1) : b;
    assign neg = a[7] ^ b[7];
endmodule
