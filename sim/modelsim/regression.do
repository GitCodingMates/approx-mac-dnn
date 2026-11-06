# Full regression: compile, run both testbenches, merge coverage and
# write a report.
# Run from sim/modelsim:   vsim -c -do regression.do
# Golden vectors must exist (python ../../python/gen_vectors.py).

do compile.do

do sim_mul.do
quit -sim
do sim_mac.do
quit -sim

vcover merge -quiet regression.ucdb tb_mul.ucdb tb_mac.ucdb
vcover report -summary regression.ucdb       -output coverage_summary.txt
vcover report -details -code bcest regression.ucdb -output coverage_details.txt
echo [exec cat coverage_summary.txt]
quit -f
