# Exhaustive multiplier test (2^16 operand pairs x 5 designs).
# GUI:   vsim -do sim_mul.do      Batch: vsim -c -do "do sim_mul.do; quit -f"

vsim -coverage -onfinish stop -voptargs=+acc work.tb_mul

if {![batch_mode]} {
    add wave -divider Operands
    add wave -radix decimal /tb_mul/a /tb_mul/b
    add wave -divider Products
    add wave -radix decimal /tb_mul/p_exact /tb_mul/p_k4 /tb_mul/p_k6 \
                            /tb_mul/p_k8 /tb_mul/p_mitchell
    add wave -divider Mismatches
    add wave -radix unsigned /tb_mul/e_exact /tb_mul/e_k4 /tb_mul/e_k6 \
                             /tb_mul/e_k8 /tb_mul/e_mitchell
}

run -all
coverage save tb_mul.ucdb
