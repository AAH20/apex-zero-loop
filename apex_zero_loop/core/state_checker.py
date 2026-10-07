"""Agent Workflow State-Machine Soundness Checker.

Validates finite state machines and autonomous agent workflows for deadlocks,
livelocks (non-terminating strongly connected cycles), and unreachable states
using Tarjan's SCC algorithm.
Zero external dependencies: 100% pure Python standard library.
"""

from __future__ import annotations

import time
from typing import Dict, List, Set, Tuple
from apex_zero_loop.core.models import StateGraphReport, StateNode, StateTransition


class StateMachineChecker:
    """Formal validator for agent workflow state machines."""

    def analyze(
        self,
        nodes: List[StateNode],
        transitions: List[StateTransition],
    ) -> StateGraphReport:
        """Audits state machine graph for deadlocks, livelocks, and reachability."""
        t_start = time.perf_counter_ns()

        node_map = {n.state_id: n for n in nodes}
        adj: Dict[str, List[str]] = {n.state_id: [] for n in nodes}
        rev_adj: Dict[str, List[str]] = {n.state_id: [] for n in nodes}

        for t in transitions:
            if t.from_state in adj and t.to_state in node_map:
                adj[t.from_state].append(t.to_state)
                rev_adj[t.to_state].append(t.from_state)

        initial_states = [n.state_id for n in nodes if n.is_initial]
        terminal_states = set(n.state_id for n in nodes if n.is_terminal)

        # 1. Reachability from Initial States (Forward BFS)
        reachable_from_start: Set[str] = set()
        queue = list(initial_states)
        for s in queue:
            reachable_from_start.add(s)

        while queue:
            curr = queue.pop(0)
            for neighbor in adj.get(curr, []):
                if neighbor not in reachable_from_start:
                    reachable_from_start.add(neighbor)
                    queue.append(neighbor)

        unreachable_states = [n.state_id for n in nodes if n.state_id not in reachable_from_start]

        # 2. Deadlock Detection: Non-terminal state with out-degree 0
        deadlock_states = [
            n.state_id
            for n in nodes
            if not n.is_terminal and len(adj.get(n.state_id, [])) == 0 and n.state_id in reachable_from_start
        ]

        # 3. Reachability to Terminal States (Backward BFS)
        can_reach_terminal: Set[str] = set(terminal_states)
        queue = list(terminal_states)
        while queue:
            curr = queue.pop(0)
            for predecessor in rev_adj.get(curr, []):
                if predecessor not in can_reach_terminal:
                    can_reach_terminal.add(predecessor)
                    queue.append(predecessor)

        # Check if all reachable states can eventually reach a terminal state
        terminal_reachable_from_all = all(s in can_reach_terminal for s in reachable_from_start)

        # 4. Livelock Detection: Find Strongly Connected Components (SCCs) using Tarjan's algorithm
        sccs = self._tarjan_scc(adj)
        livelock_cycles: List[List[str]] = []

        for scc in sccs:
            # An SCC is a cycle candidate if size > 1 or self-loop
            is_cycle = len(scc) > 1 or (len(scc) == 1 and scc[0] in adj.get(scc[0], []))
            if is_cycle:
                # If no state in this SCC can reach any terminal state, it's a trap livelock
                if not any(s in can_reach_terminal for s in scc):
                    livelock_cycles.append(sorted(scc))

        is_sound = (
            len(deadlock_states) == 0 and
            len(livelock_cycles) == 0 and
            terminal_reachable_from_all
        )

        elapsed_us = (time.perf_counter_ns() - t_start) / 1000.0

        return StateGraphReport(
            is_sound=is_sound,
            deadlock_states=sorted(deadlock_states),
            livelock_cycles=livelock_cycles,
            unreachable_states=sorted(unreachable_states),
            terminal_reachable_from_all=terminal_reachable_from_all,
            elapsed_microseconds=round(elapsed_us, 2),
        )

    def _tarjan_scc(self, adj: Dict[str, List[str]]) -> List[List[str]]:
        """Computes Strongly Connected Components using Tarjan's algorithm."""
        index = 0
        indices: Dict[str, int] = {}
        lowlinks: Dict[str, int] = {}
        on_stack: Set[str] = set()
        stack: List[str] = []
        sccs: List[List[str]] = []

        def strongconnect(v: str):
            nonlocal index
            indices[v] = index
            lowlinks[v] = index
            index += 1
            stack.append(v)
            on_stack.add(v)

            for w in adj.get(v, []):
                if w not in indices:
                    strongconnect(w)
                    lowlinks[v] = min(lowlinks[v], lowlinks[w])
                elif w in on_stack:
                    lowlinks[v] = min(lowlinks[v], indices[w])

            if lowlinks[v] == indices[v]:
                scc = []
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.append(w)
                    if w == v:
                        break
                sccs.append(scc)

        for node in adj:
            if node not in indices:
                strongconnect(node)

        return sccs
