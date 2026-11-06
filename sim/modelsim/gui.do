# Interactive session: compile, run the MAC test and open the wave window
# undocked and maximized.
# Run from sim/modelsim:   vsim -do gui.do

do compile.do
do sim_mac.do

view -undock wave
set w [winfo toplevel .main_pane.wave]
wm state $w zoomed
raise $w
update
wave zoom range 440ns 660ns
