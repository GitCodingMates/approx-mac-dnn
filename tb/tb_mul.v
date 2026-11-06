`timescale 1ns/1ps
// Exhaustive self-checking testbench: every multiplier is compared against
// the Python golden model for all 2^16 signed 8-bit operand pairs.
// Run from the tb/ directory so the vectors/ paths resolve.
module tb_mul;
    reg  signed [7:0]  a, b;
    wire signed [15:0] p_exact, p_k4, p_k6, p_k8, p_mitchell;

    mul_exact          u_exact    (.a(a), .b(b), .p(p_exact));
    mul_trunc #(.K(4)) u_k4       (.a(a), .b(b), .p(p_k4));
    mul_trunc #(.K(6)) u_k6       (.a(a), .b(b), .p(p_k6));
    mul_trunc #(.K(8)) u_k8       (.a(a), .b(b), .p(p_k8));
    mul_mitchell       u_mitchell (.a(a), .b(b), .p(p_mitchell));

    reg [15:0] g_exact    [0:65535];
    reg [15:0] g_k4       [0:65535];
    reg [15:0] g_k6       [0:65535];
    reg [15:0] g_k8       [0:65535];
    reg [15:0] g_mitchell [0:65535];

    integer i;
    integer e_exact, e_k4, e_k6, e_k8, e_mitchell;

    task check;
        input [15:0]    got, exp;
        input [8*8-1:0] name;
        inout integer   errs;
        begin
            if (got !== exp) begin
                if (errs < 5)
                    $display("MISMATCH %0s: a=%0d b=%0d got=%0d exp=%0d",
                             name, a, b, $signed(got), $signed(exp));
                errs = errs + 1;
            end
        end
    endtask

    initial begin
        $readmemh("vectors/exact.hex",    g_exact);
        $readmemh("vectors/trunc_k4.hex", g_k4);
        $readmemh("vectors/trunc_k6.hex", g_k6);
        $readmemh("vectors/trunc_k8.hex", g_k8);
        $readmemh("vectors/mitchell.hex", g_mitchell);
        e_exact = 0; e_k4 = 0; e_k6 = 0; e_k8 = 0; e_mitchell = 0;

        for (i = 0; i < 65536; i = i + 1) begin
            {a, b} = i[15:0];
            #1;
            check(p_exact,    g_exact[i],    "exact",    e_exact);
            check(p_k4,       g_k4[i],       "trunc_k4", e_k4);
            check(p_k6,       g_k6[i],       "trunc_k6", e_k6);
            check(p_k8,       g_k8[i],       "trunc_k8", e_k8);
            check(p_mitchell, g_mitchell[i], "mitchell", e_mitchell);
        end

        $display("exact    : %0d / 65536 mismatches", e_exact);
        $display("trunc_k4 : %0d / 65536 mismatches", e_k4);
        $display("trunc_k6 : %0d / 65536 mismatches", e_k6);
        $display("trunc_k8 : %0d / 65536 mismatches", e_k8);
        $display("mitchell : %0d / 65536 mismatches", e_mitchell);
        if (e_exact + e_k4 + e_k6 + e_k8 + e_mitchell == 0)
            $display("PASS: all multipliers match the golden model");
        else
            $display("FAIL");
        $finish;
    end
endmodule
