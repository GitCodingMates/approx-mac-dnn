"""Technology-independent logic synthesis of every multiplier and MAC with
Yosys + ABC, mapped to a basic 2-input gate library.

Area is reported as NAND2-equivalent gates (GE) using typical relative
cell areas of a standard-cell library; delay is reported as the logic
depth (longest combinational path, in gates). Results are written to
results/synth.csv.

Requires Yosys on PATH as `yosys`, or the pip package `yowasp-yosys`.
"""
import csv
import json
import os
import re
import shutil
import subprocess
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RTL = sorted(os.path.join(ROOT, "rtl", f) for f in os.listdir(os.path.join(ROOT, "rtl"))
             if f.endswith(".v"))

# relative area of each ABC gate in NAND2 equivalents
GE = {"$_NOT_": 0.67, "$_NAND_": 1.0, "$_NOR_": 1.0, "$_AND_": 1.33,
      "$_OR_": 1.33, "$_ANDNOT_": 1.33, "$_ORNOT_": 1.33,
      "$_XOR_": 2.33, "$_XNOR_": 2.33, "$_MUX_": 2.33, "$_DFF_P_": 4.33,
      "$_SDFF_PP0_": 5.33, "$_SDFFE_PP0P_": 6.0, "$_DFFE_PP_": 5.33}

# name, top module, parameters
DESIGNS = [
    ("exact",    "mul_exact",    {}),
    ("trunc_k4", "mul_trunc",    {"K": 4}),
    ("trunc_k6", "mul_trunc",    {"K": 6}),
    ("trunc_k8", "mul_trunc",    {"K": 8}),
    ("mitchell", "mul_mitchell", {}),
    ("mac_exact",    "mac", {"MUL": 0}),
    ("mac_trunc_k6", "mac", {"MUL": 1, "K": 6}),
    ("mac_trunc_k8", "mac", {"MUL": 1, "K": 8}),
    ("mac_mitchell", "mac", {"MUL": 2}),
]


def yosys_cmd():
    for exe in ("yosys", "yowasp-yosys"):
        if shutil.which(exe):
            return exe
    raise SystemExit("Yosys not found (pip install yowasp-yosys)")


LOG_DIR = os.path.join(ROOT, "results", "synth")


def synth(name, top, params, tmp):
    # Paths are relative to ROOT: the WebAssembly Yosys build can only
    # access its working directory.
    rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")
    chparam = "".join(f"chparam -set {k} {v} {top}; " for k, v in params.items())
    stat_json = rel(os.path.join(tmp, "stat.json"))
    log = rel(os.path.join(LOG_DIR, f"{name}.log"))
    netlist = rel(os.path.join(LOG_DIR, f"{name}_netlist.v"))
    script = (
        "read_verilog " + " ".join(rel(p) for p in RTL) + "; "
        f"{chparam}"
        f"synth -flatten -top {top}; "
        "abc -g AND,NAND,OR,NOR,XOR,XNOR,ANDNOT,ORNOT,MUX; opt_clean; "
        "stat; "
        f"tee -q -o {stat_json} stat -json; "
        "ltp -noff; "
        f"write_verilog -noattr {netlist}"
    )
    out = subprocess.run([yosys_cmd(), "-q", "-l", log, "-p", script],
                         capture_output=True, text=True, cwd=ROOT)
    if out.returncode != 0:
        raise RuntimeError(out.stderr[-2000:] or out.stdout[-2000:])
    with open(os.path.join(ROOT, stat_json)) as f:
        cells = json.load(f)["design"]["num_cells_by_type"]
    cells.pop("$scopeinfo", None)        # hierarchy metadata, not logic
    with open(os.path.join(ROOT, log)) as f:
        depth = int(re.findall(r"length=(\d+)", f.read())[-1])
    return cells, depth


def main():
    rows = []
    os.makedirs(LOG_DIR, exist_ok=True)
    ver = subprocess.run([yosys_cmd(), "-V"], capture_output=True, text=True).stdout.split("(")[0]
    print(f"{ver.strip()} + ABC, 2-input gate library\n")
    with tempfile.TemporaryDirectory(dir=ROOT, prefix=".synth_") as tmp:
        for name, top, params in DESIGNS:
            cells, depth = synth(name, top, params, tmp)
            unknown = set(cells) - set(GE)
            if unknown:
                raise RuntimeError(f"no GE weight for {unknown}")
            ge = sum(GE[c] * n for c, n in cells.items())
            ff = sum(n for c, n in cells.items() if "DFF" in c)
            rows.append({"design": name, "cells": sum(cells.values()), "flip_flops": ff,
                         "area_GE": round(ge, 1), "logic_depth": depth})

    base = {"mul": rows[0]["area_GE"], "mac": rows[5]["area_GE"]}
    for r in rows:
        ref = base["mac" if r["design"].startswith("mac") else "mul"]
        r["area_saving_%"] = round(100 * (1 - r["area_GE"] / ref), 1)

    path = os.path.join(ROOT, "results", "synth.csv")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    print(f"{'design':14s} {'cells':>6s} {'FFs':>4s} {'GE':>8s} {'saving%':>8s} {'depth':>6s}")
    for r in rows:
        print(f"{r['design']:14s} {r['cells']:6d} {r['flip_flops']:4d} {r['area_GE']:8.1f} "
              f"{r['area_saving_%']:8.1f} {r['logic_depth']:6d}")
    print(f"saved {path}")


if __name__ == "__main__":
    main()
