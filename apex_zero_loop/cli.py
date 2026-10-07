"""Unified Command Line Interface for Apex Zero Loop.

Pure Python standard library: zero external dependencies.
"""

from __future__ import annotations

import argparse
import json
import sys
from apex_zero_loop.core.models import ContractSpec, StateNode, StateTransition
from apex_zero_loop.gate import ZeroLoopGate


def main():
    parser = argparse.ArgumentParser(
        prog="apex-zero-loop",
        description="Apex Zero Loop: Sub-Millisecond Zero-Iteration Agent Verification and Hoare Logic Kernel",
    )
    subparsers = parser.add_subparsers(dest="command", help="Verification sub-commands")

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify Python code snippet against contracts and hazards")
    p_verify.add_argument("--code", type=str, help="Python code string or file path")
    p_verify.add_argument("--pre", type=str, default="", help="Precondition (e.g. 'x > 0')")
    p_verify.add_argument("--post", type=str, default="", help="Postcondition (e.g. 'result > 0')")
    p_verify.add_argument("--no-repair", action="store_true", help="Disable deterministic auto-correction")

    # autocorrect
    p_correct = subparsers.add_parser("autocorrect", help="Apply deterministic microsecond AST patches")
    p_correct.add_argument("--file", type=str, required=True, help="Python file path to patch")

    # check-state
    p_state = subparsers.add_parser("check-state", help="Check agent state machine for deadlocks and livelocks")
    p_state.add_argument("--demo", action="store_true", help="Run demonstration state machine audit")

    # benchmark
    subparsers.add_parser("benchmark", help="Execute full microsecond benchmark telemetry suite")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    gate = ZeroLoopGate()

    if args.command == "verify":
        sample_code = args.code or """
def compute_rate(total, count):
    return total / count
"""
        contracts = []
        if args.pre and args.post:
            contracts.append(ContractSpec(
                function_name="target",
                preconditions=[args.pre],
                postconditions=[args.post],
            ))

        print("\n[Apex-Zero-Loop] Verifying code payload...")
        rep = gate.verify_code(sample_code, contracts=contracts, auto_repair=not args.no_repair)
        print(f"Status:            {rep.status.value.upper()}")
        print(f"Paths Explored:    {rep.paths_explored}")
        print(f"Hazards Flagged:   {len(rep.violations)}")
        print(f"Patches Applied:   {len(rep.auto_corrections)}")
        print(f"Latency:           {rep.elapsed_microseconds:.2f} µs ({rep.elapsed_microseconds / 1000.0:.3f} ms)")

        if rep.auto_corrections:
            print("\n[Auto-Corrections Applied]:")
            for c in rep.auto_corrections:
                print(f"  - [{c.rule_name}] Line {c.line_number}: {c.original_snippet} -> {c.corrected_snippet}")
            print("\n[Repaired Code]:")
            print(rep.corrected_code)
        print()

    elif args.command == "check-state":
        print("\n[Apex-Zero-Loop] Auditing Agent Workflow State Machine...")
        nodes = [
            StateNode("IDLE", is_initial=True),
            StateNode("PLANNING"),
            StateNode("CODING"),
            StateNode("LOCKED_DEADLOCK"),
            StateNode("DONE", is_terminal=True),
        ]
        transitions = [
            StateTransition("IDLE", "PLANNING"),
            StateTransition("PLANNING", "CODING"),
            StateTransition("CODING", "LOCKED_DEADLOCK"),
            StateTransition("CODING", "DONE"),
        ]
        report = gate.verify_workflow(nodes, transitions)
        print(f"Is Sound:          {report.is_sound}")
        print(f"Deadlock States:   {report.deadlock_states}")
        print(f"Livelock Cycles:   {report.livelock_cycles}")
        print(f"Unreachable:       {report.unreachable_states}")
        print(f"Latency:           {report.elapsed_microseconds:.2f} µs\n")

    elif args.command == "benchmark":
        from benchmarks.benchmark_telemetry import run_benchmarks
        run_benchmarks()


if __name__ == "__main__":
    main()
