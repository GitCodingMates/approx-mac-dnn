// Mitchell logarithmic 8x8 signed multiplier.
//   x = 2^k (1 + f),  k = position of leading one
//   S = x1 * 2^k2 + x2 * 2^k1        (x_i = mantissa bits below the leading one)
//   P = 2^(k1+k2) + S   if S < 2^(k1+k2)
//       2 * S           otherwise
// Datapath: two leading-one detectors, shifters and one adder.
module mul_mitchell (
    input  wire signed [7:0]  a,
    input  wire signed [7:0]  b,
    output wire signed [15:0] p
);
    wire [7:0] ma, mb;
    wire       neg;
    sign_mag u_sm (.a(a), .b(b), .ma(ma), .mb(mb), .neg(neg));

    function [2:0] lod;
        input [7:0] x;
        integer i;
        begin
            lod = 3'd0;
            for (i = 0; i < 8; i = i + 1)
                if (x[i]) lod = i[2:0];
        end
    endfunction

    wire [2:0]  k1 = lod(ma);
    wire [2:0]  k2 = lod(mb);
    wire [7:0]  x1 = ma & ~(8'd1 << k1);
    wire [7:0]  x2 = mb & ~(8'd1 << k2);

    wire [15:0] s    = ({8'd0, x1} << k2) + ({8'd0, x2} << k1);
    wire [3:0]  ksum = {1'b0, k1} + {1'b0, k2};   // 4 bits: up to 14
    wire [15:0] base = 16'd1 << ksum;
    wire        zero = (ma == 8'd0) | (mb == 8'd0);

    wire [15:0] mag = zero        ? 16'd0      :
                      (s < base)  ? (base + s) : (s << 1);
    assign p = neg ? -$signed(mag) : $signed(mag);
endmodule
