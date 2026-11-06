`timescale 1ns/1ps
// Self-checking MAC testbench. Random operand streams with periodic
// accumulator clears are applied to one MAC per multiplier type; a
// reference accumulator built from the golden product tables checks
// every output cycle, including the 2-cycle pipeline latency.
module tb_mac;
    localparam integer N_OPS = 20000;

    reg clk = 0, rst = 1, en = 0, clr = 0;
    reg signed [7:0] a = 0, b = 0;
    always #5 clk = ~clk;

    wire signed [31:0] acc_exact, acc_k6, acc_mitchell;
    mac #(.MUL(0))         u_exact    (.clk(clk), .rst(rst), .en(en), .clr(clr), .a(a), .b(b), .acc(acc_exact));
    mac #(.MUL(1), .K(6))  u_k6       (.clk(clk), .rst(rst), .en(en), .clr(clr), .a(a), .b(b), .acc(acc_k6));
    mac #(.MUL(2))         u_mitchell (.clk(clk), .rst(rst), .en(en), .clr(clr), .a(a), .b(b), .acc(acc_mitchell));

    reg [15:0] g_exact    [0:65535];
    reg [15:0] g_k6       [0:65535];
    reg [15:0] g_mitchell [0:65535];

    // reference model with the same 2-stage latency
    reg signed [31:0] r_exact, r_k6, r_mitchell;
    reg [15:0] idx_q;
    reg        en_q, clr_q;
    integer    n, errs, checks;
    integer    seed = 2026;

    always @(posedge clk) begin
        if (rst) begin
            en_q <= 0; clr_q <= 0; idx_q <= 0;
            r_exact <= 0; r_k6 <= 0; r_mitchell <= 0;
        end else begin
            idx_q <= {a, b};
            en_q  <= en;
            clr_q <= clr;
            if (en_q) begin
                r_exact    <= (clr_q ? 0 : r_exact)    + $signed(g_exact[idx_q]);
                r_k6       <= (clr_q ? 0 : r_k6)       + $signed(g_k6[idx_q]);
                r_mitchell <= (clr_q ? 0 : r_mitchell) + $signed(g_mitchell[idx_q]);
            end
        end
    end

    always @(negedge clk) if (!rst) begin
        checks = checks + 1;
        if (acc_exact !== r_exact || acc_k6 !== r_k6 || acc_mitchell !== r_mitchell) begin
            if (errs < 5)
                $display("MISMATCH t=%0t exact %0d/%0d k6 %0d/%0d mitchell %0d/%0d", $time,
                         acc_exact, r_exact, acc_k6, r_k6, acc_mitchell, r_mitchell);
            errs = errs + 1;
        end
    end

    initial begin
        $readmemh("vectors/exact.hex",    g_exact);
        $readmemh("vectors/trunc_k6.hex", g_k6);
        $readmemh("vectors/mitchell.hex", g_mitchell);
        errs = 0; checks = 0;
        repeat (3) @(posedge clk);
        rst <= 0;
        for (n = 0; n < N_OPS; n = n + 1) begin
            @(posedge clk);
            a   <= $random(seed);
            b   <= $random;
            en  <= ($random % 8) != 0;     // occasional idle cycles
            clr <= (n % 784) == 0;         // new dot product every 784 terms
        end
        @(posedge clk) en <= 0;
        repeat (4) @(posedge clk);
        $display("MAC: %0d cycles checked, %0d mismatches", checks, errs);
        $display("final acc: exact=%0d trunc_k6=%0d mitchell=%0d",
                 acc_exact, acc_k6, acc_mitchell);
        if (errs == 0) $display("PASS"); else $display("FAIL");
        $finish;
    end
endmodule
