# Cycle-accurate MAC test (exact, truncated K=6, Mitchell).
# GUI:   vsim -do sim_mac.do      Batch: vsim -c -do "do sim_mac.do; quit -f"

vsim -coverage -onfinish stop -voptargs=+acc work.tb_mac

if {![batch_mode]} { do wave_mac.do }

run -all
coverage save tb_mac.ucdb
