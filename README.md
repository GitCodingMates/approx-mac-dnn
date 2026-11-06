# Approximate Multiply–Accumulate Units for Energy-Efficient DNN Accelerators

**Error Characterization and Application-Level Evaluation**

Sina Mozaffari Rad, Fatemeh Dastyafteh

Full report: [`docs/report.pdf`](docs/report.pdf)

---

## Abstract

Multiply–accumulate (MAC) operations dominate both the computation and the
energy budget of deep neural network (DNN) inference. Because DNNs tolerate
small numerical errors, the exact multiplier inside each MAC can be replaced
with a cheaper approximate multiplier. This work studies that trade-off for
8-bit signed arithmetic. Bit-accurate models of an exact array multiplier,
three column-truncated multipliers and Mitchell's logarithmic multiplier were
characterized exhaustively over all 2<sup>16</sup> input pairs. A
fully-connected network was trained on MNIST, quantized to int8 with int32
accumulation, and evaluated with every multiplication routed through each
design. All designs were implemented in Verilog, verified exhaustively in
ModelSim against the reference models, and synthesized with Yosys. The
truncated multiplier with *K* = 8 reduces multiplier area by 59.8 % and
complete MAC area by 38.9 % at a cost of 0.42 % in accuracy, whereas the
logarithmic multiplier saves less than 5 % at this operand width.

## 1. Multiplier Designs

All designs operate on 8-bit two's-complement operands and are implemented
in sign-magnitude form, so that every approximation error is symmetric
around zero.

| Design | Principle | Hardware |
|---|---|---|
| Exact | Sum of all 64 partial-product bits | AND array + adder tree |
| Truncated (*K*) | Partial-product bits in result columns < *K* are removed | Smaller array; *K* = 4, 6, 8 removes 10, 21, 36 bits |
| Mitchell [1] | log₂(*ab*) ≈ *k*₁ + *k*₂ + *f*₁ + *f*₂ | Two leading-one detectors, shifters, one adder |

The designs are combined into a two-stage pipelined MAC unit with a 32-bit
accumulator. Only the multiplier block differs between variants.

<p align="center">
  <img src="docs/figures/mac_unit.png" width="850" alt="MAC block diagram">
  <br><em>Figure 1. Pipelined MAC unit (<code>rtl/mac.v</code>).</em>
</p>

## 2. Methodology

1. **Reference models.** Each multiplier is described at bit level in
   Python/NumPy and serves as the golden reference for RTL verification.
2. **Error characterization.** All 65,536 operand pairs are evaluated using
   the standard metrics of [2]: error rate (ER), mean error distance (MED),
   normalized MED (NMED), mean relative error distance (MRED) and maximum
   error.
3. **Application-level evaluation.** A 784–128–10 MLP is trained on MNIST
   [5] and quantized to int8 following the integer-only scheme of [4]; every
   multiplication in both layers is routed through the multiplier under test.
4. **RTL implementation and verification.** Synthesizable Verilog-2001,
   verified in ModelSim SE 2020.4 with self-checking testbenches and code
   coverage.
5. **Logic synthesis.** Yosys 0.70 with ABC, mapped to a 2-input gate
   library; area is reported in NAND2 gate equivalents (GE) and delay as
   logic depth.

## 3. Results

### 3.1 Arithmetic Error

| Multiplier | ER (%) | MED | NMED (%) | MRED (%) | Max ED |
|---|---:|---:|---:|---:|---:|
| Exact | 0.00 | 0.00 | 0.000 | 0.00 | 0 |
| Truncated *K*=4 | 81.25 | 12.25 | 0.075 | 1.72 | 49 |
| Truncated *K*=6 | 93.75 | 80.25 | 0.490 | 7.59 | 321 |
| Truncated *K*=8 | 98.05 | 384.75 | 2.348 | 23.87 | 1537 |
| Mitchell | 87.89 | 151.34 | 0.924 | 3.70 | 1024 |

<p align="center">
  <img src="results/error_heatmaps.png" width="900" alt="Relative error heatmaps">
  <br><em>Figure 2. Relative error of each approximate multiplier over the operand space.</em>
</p>

### 3.2 Logic Synthesis

Each design is synthesized with Yosys 0.70 and ABC. For every design the
complete Yosys log (cell statistics, longest path) and the gate-level netlist
are stored in [`results/synth/`](results/synth).

<p align="center">
  <img src="results/synth/yosys_terminal.png" width="620" alt="Yosys synthesis run">
  <br><em>Figure 3. Synthesis flow output and Yosys cell statistics of the truncated multiplier (K = 8).
  The 155 logic cells match the table below; <code>$scopeinfo</code> is hierarchy metadata.</em>
</p>

<p align="center">
  <img src="results/synth/mac_schematic.png" width="950" alt="Yosys schematic of the MAC">
  <br><em>Figure 4. Yosys schematic of the MAC unit with the truncated multiplier (K = 8) after <code>proc</code> and <code>opt -full</code>:
  multiplier instance, pipeline registers with synchronous reset (<code>$sdff</code>, <code>$sdffe</code>), the clear multiplexer
  (<code>$mux</code>) and the accumulator adder (<code>$add</code>).</em>
</p>

### 3.3 Hardware Cost and Accuracy

| Design | Area (GE) | Saving (%) | Logic depth | MNIST accuracy (%) |
|---|---:|---:|---:|---:|
| Exact multiplier | 573.2 | – | 35 | 96.81 |
| Truncated *K*=4 | 465.1 | 18.9 | 33 | 96.82 |
| Truncated *K*=6 | 368.5 | 35.7 | 32 | 96.77 |
| Truncated *K*=8 | 230.7 | 59.8 | 24 | 96.39 |
| Mitchell | 544.9 | 4.9 | 49 | 96.77 |
| MAC, exact | 1167.2 | – | 63 | |
| MAC, truncated *K*=6 | 870.3 | 25.4 | 51 | |
| MAC, truncated *K*=8 | 713.5 | 38.9 | 47 | |
| MAC, Mitchell | 1145.5 | 1.9 | 63 | |

The float32 reference accuracy is 96.82 %.

<p align="center">
  <img src="results/pareto.png" width="850" alt="Design space">
  <br><em>Figure 5. Accuracy and mean relative error versus multiplier area.</em>
</p>

### 3.4 Functional Verification

| Testbench | Designs | Checks | Mismatches |
|---|---|---:|---:|
| `tb_mul` | exact, truncated *K*=4/6/8, Mitchell | 5 × 65,536 | 0 |
| `tb_mac` | exact, truncated *K*=6, Mitchell | 20,005 cycles | 0 |

Merged code coverage of the RTL: statements, branches, conditions and
expressions 100 %; toggles 88.5 %, where all unexercised toggle bins are
structurally constant (truncated low-order product bits, product bit 15,
upper accumulator bits). The complete transcript of the regression is kept in
[`results/modelsim_regression.log`](results/modelsim_regression.log).

<p align="center">
  <img src="results/modelsim_regression.png" width="680" alt="ModelSim batch regression">
  <br><em>Figure 6. Batch regression in ModelSim: exhaustive multiplier test, cycle-accurate MAC test and merged coverage.</em>
</p>

<p align="center">
  <img src="results/modelsim_wave.png" width="900" alt="ModelSim wave window">
  <br><em>Figure 7. ModelSim wave window during <code>tb_mac</code>; each MAC accumulator is shown above its reference.</em>
</p>

## 4. Discussion

- **Column truncation provides a near-linear area–error trade-off.** Removing
  low-order columns also shortens the carry chain of the final adder, which
  reduces logic depth.
- **The saving is diluted at MAC level.** Operand conversion, pipeline
  registers, the adder and the accumulator are common to all variants, so the
  59.8 % multiplier saving becomes 38.9 % for the complete MAC.
- **Mitchell's multiplier is inefficient at 8 bits.** Its leading-one
  detectors, shifters and output multiplexer form a roughly constant
  overhead, while the partial-product array it replaces is still small at this
  width.
- **Arithmetic error metrics do not predict accuracy.** Truncation at *K* = 6
  has twice the MRED of Mitchell but the same accuracy, owing to error
  averaging over 784-term dot products and the robustness of the `argmax`
  decision.

## 5. Repository Structure

```
rtl/                       Verilog: sign_mag, mul_exact, mul_trunc, mul_mitchell, mac
tb/                        self-checking testbenches (tb_mul, tb_mac)
sim/modelsim/              ModelSim project, do-scripts, coverage flow
python/approx_mult.py      bit-accurate multiplier models
python/error_analysis.py   exhaustive error metrics and heatmaps
python/train_quantize.py   MLP training and int8 quantization
python/approx_inference.py inference through approximate multipliers
python/gen_vectors.py      golden vectors for RTL verification
python/synth.py            Yosys/ABC synthesis, area and logic depth
python/synth_report.py     cell statistics from a synthesis log
python/pareto.py           design-space plot and summary table
results/                   metrics (CSV), figures, quantized model
docs/                      report (LaTeX source and PDF)
```

## 6. Reproduction

Requirements: Python 3 with the packages in `requirements.txt`, ModelSim or
Questa (Icarus Verilog is also supported by `tb/run_sim.sh`), and a LaTeX
distribution for the report.

```sh
pip install -r requirements.txt

python python/error_analysis.py
python python/train_quantize.py
python python/approx_inference.py
python python/gen_vectors.py
python python/synth.py
python python/pareto.py

cd sim/modelsim
vsim -c -do regression.do        # batch regression with coverage
vsim -do gui.do                  # interactive wave view
```

## References

1. J. N. Mitchell, "Computer multiplication and division using binary
   logarithms," *IRE Trans. Electronic Computers*, vol. EC-11, no. 4,
   pp. 512–517, 1962.
2. H. Jiang, F. J. H. Santiago, H. Mo, L. Liu, and J. Han, "Approximate
   arithmetic circuits: A survey, characterization, and recent applications,"
   *Proc. IEEE*, vol. 108, no. 12, pp. 2108–2135, 2020.
3. V. Mrazek, R. Hrbacek, Z. Vasicek, and L. Sekanina, "EvoApprox8b: Library
   of approximate adders and multipliers for circuit design and benchmarking
   of approximation methods," in *Proc. DATE*, 2017, pp. 258–261.
4. B. Jacob *et al.*, "Quantization and training of neural networks for
   efficient integer-arithmetic-only inference," in *Proc. CVPR*, 2018,
   pp. 2704–2713.
5. Y. LeCun, L. Bottou, Y. Bengio, and P. Haffner, "Gradient-based learning
   applied to document recognition," *Proc. IEEE*, vol. 86, no. 11,
   pp. 2278–2324, 1998.
