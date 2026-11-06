#!/usr/bin/env sh
# Regenerate golden vectors and run both testbenches.
# Uses ModelSim/Questa if available, otherwise Icarus Verilog.
set -e
cd "$(dirname "$0")"
python ../python/gen_vectors.py > /dev/null

if command -v vsim > /dev/null 2>&1; then
    rm -rf work && vlib work > /dev/null
    vlog -quiet ../rtl/*.v tb_mul.v tb_mac.v
    vsim -c -quiet tb_mul -do "run -all; quit -f"
    vsim -c -quiet tb_mac -do "run -all; quit -f"
else
    iverilog -g2005 -o tb_mul.vvp ../rtl/*.v tb_mul.v && vvp tb_mul.vvp
    iverilog -g2005 -o tb_mac.vvp ../rtl/*.v tb_mac.v && vvp tb_mac.vvp
fi
