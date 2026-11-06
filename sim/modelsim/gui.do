# Interactive session: compile, run the MAC test and open the wave window.
# Run from sim/modelsim:   vsim -do gui.do

do compile.do
do sim_mac.do
view wave
wave zoom range 20ns 240ns
