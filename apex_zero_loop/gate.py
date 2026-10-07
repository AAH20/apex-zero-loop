"""Apex Zero Loop Master Verification Gate.

Intercepts AI coding agent payloads before execution, proving Hoare contract
soundness, auditing symbolic runtime hazards, and synthesizing deterministic
repairs in microseconds.
Zero external dependencies: 100% pure Python standard library.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
from apex_zero_loop.core.auto_corrector import AutoCorrector
from apex_zero_loop.core.hoare_engine import HoareEngine
from apex_zero_loop.core.models import (
    AutoCorrection,
    ContractSpec,
    StateGraphReport,
    StateNode,
    StateTransition,
    VerificationReport,
    VerificationStatus,
)
from apex_zero_loop.core.state_checker import StateMachineChecker
from apex_zero_loop.core.symbolic_executor import SymbolicExecutor


class ZeroLoopGate:
    """Master gate interceptor for AI agent code generation."""

    def __init__(self):
        self.hoare_engine = HoareEngine()
        self.symbolic_executor = SymbolicExecutor()
        self.state_checker = StateMachineChecker()
        self.auto_corrector = AutoCorrector()

    def verify_code(
        self,
        code_str: str,
        contracts: Optional[List[ContractSpec]] = None,
        auto_repair: bool = True,
    ) -> VerificationReport:
        """Verifies code against formal contracts and runtime hazard hazards.
        
        Args:
            code_str: Python source code under verification.
            contracts: Optional list of ContractSpec (pre/postconditions).
            auto_repair: If True, automatically synthesizes patches for hazards.
            
        Returns:
            VerificationReport containing formal status, counterexamples, and patched code.
        """
        t_start = time.perf_counter_ns()
        contracts = contracts or []

        # Step 1: Symbolic hazard analysis
        paths = self.symbolic_executor.analyze_code(code_str)
        violations: List[Dict[str, Any]] = []
        counterexamples: List[Dict[str, Any]] = []

        for p in paths:
            for exc_type, desc, lineno in p.potential_exceptions:
                violations.append({
                    "type": exc_type,
                    "description": desc,
                    "line_number": lineno,
                    "path_conditions": p.path_conditions,
                })

        # Step 2: Hoare Contract Verification
        for contract in contracts:
            for pre in contract.preconditions:
                for post in contract.postconditions:
                    triple = self.hoare_engine.verify_hoare_triple(pre, code_str, post)
                    if not triple.is_valid:
                        violations.append({
                            "type": "ContractViolation",
                            "function": contract.function_name,
                            "precondition": pre,
                            "postcondition": post,
                            "weakest_precondition": triple.weakest_precondition,
                        })
                        if triple.counterexample:
                            counterexamples.append(triple.counterexample)

        # Step 3: Auto-Correction if violations found
        corrections: List[AutoCorrection] = []
        repaired_code: Optional[str] = None

        if violations and auto_repair:
            repaired_code, corrections = self.auto_corrector.repair_code(code_str)
            if corrections:
                # Re-verify repaired code
                re_paths = self.symbolic_executor.analyze_code(repaired_code)
                remaining_hazards = sum(len(p.potential_exceptions) for p in re_paths)
                if remaining_hazards == 0 and not counterexamples:
                    # Clean repair!
                    violations = []

        status = VerificationStatus.VERIFIED if not violations else VerificationStatus.VIOLATED
        elapsed_us = (time.perf_counter_ns() - t_start) / 1000.0

        return VerificationReport(
            status=status,
            contracts_checked=len(contracts),
            paths_explored=len(paths),
            violations=violations,
            counterexamples=counterexamples,
            auto_corrections=corrections,
            corrected_code=repaired_code if corrections else None,
            elapsed_microseconds=round(elapsed_us, 2),
        )

    def verify_workflow(
        self,
        nodes: List[StateNode],
        transitions: List[StateTransition],
    ) -> StateGraphReport:
        """Audits an agent workflow state machine for deadlocks and livelocks."""
        return self.state_checker.analyze(nodes, transitions)
