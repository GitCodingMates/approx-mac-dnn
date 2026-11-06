# Cycle-accurate MAC test (exact, truncated K=6, Mitchell).
# GUI:   vsim -do sim_mac.do      Batch: vsim -c -do "do sim_mac.do; quit -f"
# Also dumps the first 400 ns of the exact MAC to mac.vcd for documentation.

vsim -coverage -onfinish stop -voptargs=+acc work.tb_mac

vcd file mac.vcd
vcd add /tb_mac/clk /tb_mac/rst /tb_mac/en /tb_mac/clr /tb_mac/a /tb_mac/b
vcd add /tb_mac/u_exact/p /tb_mac/u_exact/p_q /tb_mac/u_exact/acc
vcd add /tb_mac/r_exact

if {![batch_mode]} { do wave_mac.do }

run 400ns
vcd off
run -all
coverage save tb_mac.ucdb
