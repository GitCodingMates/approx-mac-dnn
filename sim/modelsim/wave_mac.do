# Waveform layout for tb_mac (loaded automatically by sim_mac.do in GUI mode).
onerror {resume}
quietly WaveActivateNextPane {} 0

add wave -divider Control
add wave /tb_mac/clk /tb_mac/rst /tb_mac/en /tb_mac/clr
add wave -divider Operands
add wave -radix decimal /tb_mac/a /tb_mac/b

add wave -divider {Exact MAC}
add wave -radix decimal -label p      /tb_mac/u_exact/p
add wave -radix decimal -label p_q    /tb_mac/u_exact/p_q
add wave -radix decimal -label acc    /tb_mac/u_exact/acc
add wave -radix decimal -label ref    /tb_mac/r_exact

add wave -divider {Truncated K=6 MAC}
add wave -radix decimal -label acc    /tb_mac/u_k6/acc
add wave -radix decimal -label ref    /tb_mac/r_k6

add wave -divider {Mitchell MAC}
add wave -radix decimal -label acc    /tb_mac/u_mitchell/acc
add wave -radix decimal -label ref    /tb_mac/r_mitchell

add wave -divider Checker
add wave -radix unsigned /tb_mac/checks /tb_mac/errs

configure wave -namecolwidth 160 -valuecolwidth 90 -timelineunits ns
WaveRestoreZoom {0 ns} {300 ns}
