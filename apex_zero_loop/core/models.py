"""Formal Verification and Hoare Logic Domain Models for Apex Zero Loop.

Zero external dependencies: 100% pure Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class VerificationStatus(str, Enum):
    """Formal verification verdict."""
    VERIFIED = "verified"
    VIOLATED = "violated"
    SYNTAX_ERROR = "syntax_error"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class ContractSpec:
    """Design-by-Contract formal specification for a function or code block."""
    function_name: str
    preconditions: List[str] = field(default_factory=list)      # Requires clauses: P
    postconditions: List[str] = field(default_factory=list)     # Ensures clauses: Q
    invariants: List[str] = field(default_factory=list)         # Loop invariants: I
    forbidden_exceptions: List[str] = field(default_factory=list) # e.g. ["ZeroDivisionError", "KeyError"]


@dataclass
class HoareTriple:
    """Hoare Triple formal representation: {P} C {Q}."""
    precondition: str
    command: str
    postcondition: str
    weakest_precondition: Optional[str] = None
    is_valid: bool = False
    counterexample: Optional[Dict[str, Any]] = None
    proof_steps: List[str] = field(default_factory=list)


@dataclass
class SymbolicPath:
    """A symbolic execution execution trace branch."""
    path_id: int
    path_conditions: List[str] = field(default_factory=list)
    symbolic_state: Dict[str, str] = field(default_factory=dict)
    potential_exceptions: List[Tuple[str, str, int]] = field(default_factory=list)  # (exc_type, expr, line_no)
    return_expression: Optional[str] = None
    terminates: bool = True


@dataclass
class StateNode:
    """Node in an agent or workflow state machine."""
    state_id: str
    is_initial: bool = False
    is_terminal: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateTransition:
    """Edge in an agent or workflow state machine."""
    from_state: str
    to_state: str
    trigger: str = ""
    guard: str = ""


@dataclass
class StateGraphReport:
    """Formal deadlock, livelock, and reachability audit of a state machine."""
    is_sound: bool
    deadlock_states: List[str]
    livelock_cycles: List[List[str]]
    unreachable_states: List[str]
    terminal_reachable_from_all: bool
    elapsed_microseconds: float


@dataclass
class AutoCorrection:
    """A deterministic source patch synthesized without LLM invocation."""
    rule_name: str
    line_number: int
    original_snippet: str
    corrected_snippet: str
    explanation: str


@dataclass
class VerificationReport:
    """Comprehensive zero-loop verification and auto-correction verdict."""
    status: VerificationStatus
    contracts_checked: int
    paths_explored: int
    violations: List[Dict[str, Any]] = field(default_factory=list)
    counterexamples: List[Dict[str, Any]] = field(default_factory=list)
    auto_corrections: List[AutoCorrection] = field(default_factory=list)
    corrected_code: Optional[str] = None
    elapsed_microseconds: float = 0.0
