"""Microsecond Benchmark Telemetry Suite for Apex Zero Loop.

Pure Python 3.10+ standard library.
"""

from __future__ import annotations

import os
from pathlib import Path
import statistics
import sys
import time
from typing import Callable, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from apex_zero_loop.core.auto_corrector import AutoCorrector
from apex_zero_loop.core.hoare_engine import HoareEngine
from apex_zero_loop.core.models import ContractSpec, StateNode, StateTransition
from apex_zero_loop.core.sat_verifier import BooleanSATSolver
from apex_zero_loop.core.state_checker import StateMachineChecker
from apex_zero_loop.core.symbolic_executor import SymbolicExecutor
from apex_zero_loop.gate import ZeroLoopGate


def benchmark_call(fn: Callable, runs: int = 30) -> Tuple[float, float, float]:
    """Measures execution latency over multiple runs.
    
    Returns (mean_us, p95_us, ops_per_sec).
    """
    times_us: List[float] = []
    # Warmup
    fn()

    for _ in range(runs):
        t0 = time.perf_counter_ns()
        fn()
        t1 = time.perf_counter_ns()
        times_us.append((t1 - t0) / 1000.0)

    mean_us = statistics.mean(times_us)
    times_us.sort()
    p95_idx = int(0.95 * len(times_us))
    p95_us = times_us[min(p95_idx, len(times_us) - 1)]
    ops_per_sec = 1_000_000.0 / mean_us if mean_us > 0 else 0.0

    return mean_us, p95_us, ops_per_sec


def run_benchmarks():
    gate = ZeroLoopGate()
    sat_solver = BooleanSATSolver()
    hoare_engine = HoareEngine()
    symbolic_exec = SymbolicExecutor()
    corrector = AutoCorrector()
    state_checker = StateMachineChecker()

    print("================================================================================")
    print("           APEX ZERO LOOP - MICROSECOND BENCHMARK TELEMETRY                     ")
    print("================================================================================\n")

    results = []

    # 1. SAT Implication Verification
    mean_us, p95_us, ops = benchmark_call(
        lambda: sat_solver.verify_implication("(A and B) or (C and not D)", "A or C"),
        runs=50,
    )
    results.append(("DPLL SAT Solver", "Tseitin CNF (4 terms)", mean_us, p95_us, ops))

    # 2. Hoare Weakest Precondition Calculus
    code_hoare = """
x = x + 10
if x > 50:
    y = x * 2
else:
    y = x + 20
"""
    mean_us, p95_us, ops = benchmark_call(
        lambda: hoare_engine.verify_hoare_triple("x > 0", code_hoare, "y > 20"),
        runs=50,
    )
    results.append(("Hoare wp Calculus", "If/Else + Assign AST", mean_us, p95_us, ops))

    # 3. Symbolic Hazard Execution
    code_hazard = """
def process_data(data, scale):
    ratio = scale / len(data)
    user_id = data['id']
    return ratio
"""
    mean_us, p95_us, ops = benchmark_call(
        lambda: symbolic_exec.analyze_code(code_hazard),
        runs=50,
    )
    results.append(("Symbolic Hazard Tracer", "Exception Path Tracing", mean_us, p95_us, ops))

    # 4. Deterministic AST Auto-Corrector
    mean_us, p95_us, ops = benchmark_call(
        lambda: corrector.repair_code(code_hazard),
        runs=50,
    )
    results.append(("AST Auto-Corrector", "Ternary & .get() Synthesis", mean_us, p95_us, ops))

    # 5. Tarjan SCC State Machine Audit (20 nodes)
    nodes = [StateNode(f"S_{i}", is_initial=(i == 0), is_terminal=(i == 19)) for i in range(20)]
    transitions = [StateTransition(f"S_{i}", f"S_{i+1}") for i in range(19)]
    transitions.append(StateTransition("S_10", "S_5"))  # Safe internal loop
    mean_us, p95_us, ops = benchmark_call(
        lambda: state_checker.analyze(nodes, transitions),
        runs=50,
    )
    results.append(("State Machine Auditor", "20 States, Tarjan SCC", mean_us, p95_us, ops))

    # 6. End-to-End ZeroLoopGate Interception
    contracts = [ContractSpec("process_data", ["scale > 0"], ["result >= 0"])]
    mean_us, p95_us, ops = benchmark_call(
        lambda: gate.verify_code(code_hazard, contracts=contracts, auto_repair=True),
        runs=30,
    )
    results.append(("ZeroLoopGate Master", "Full Pre-Exec Interception", mean_us, p95_us, ops))

    # Print Table
    header = f"| {'Verification Kernel':<24} | {'Target Benchmark Payload':<28} | {'Mean Latency (µs)':<18} | {'p95 Latency (µs)':<18} | {'Throughput (ops/s)':<18} |"
    sep = f"|{'-'*26}|{'-'*30}|{'-'*20}|{'-'*20}|{'-'*20}|"
    print(header)
    print(sep)
    for kernel, payload, mean_u, p95_u, ops_s in results:
        print(f"| {kernel:<24} | {payload:<28} | {mean_u:>16.2f} µs | {p95_u:>16.2f} µs | {ops_s:>16.1f} /s |")
    print(sep)


if __name__ == "__main__":
    run_benchmarks()
