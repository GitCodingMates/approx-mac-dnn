# Compile RTL and testbenches into the 'work' library.
# Run from sim/modelsim:   vsim -c -do compile.do
# RTL is compiled with statement/branch/condition/expression/toggle coverage.

set RTL ../../rtl
set TB  ../../tb

if {[file exists work]} { vdel -lib work -all }
vlib work
vmap work work

vlog -work work +cover=bcest -quiet \
    $RTL/sign_mag.v $RTL/mul_exact.v $RTL/mul_trunc.v \
    $RTL/mul_mitchell.v $RTL/mac.v

vlog -work work -quiet {+define+VEC_DIR="../../tb/vectors"} \
    $TB/tb_mul.v $TB/tb_mac.v
