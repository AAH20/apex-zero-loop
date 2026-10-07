"""Unit tests for Agent State Machine Soundness and Tarjan SCC Checker."""

import unittest
from apex_zero_loop.core.models import StateNode, StateTransition
from apex_zero_loop.core.state_checker import StateMachineChecker


class TestStateMachineChecker(unittest.TestCase):
    def setUp(self):
        self.checker = StateMachineChecker()

    def test_sound_linear_fsm(self):
        nodes = [
            StateNode("START", is_initial=True),
            StateNode("PROCESS"),
            StateNode("END", is_terminal=True),
        ]
        transitions = [
            StateTransition("START", "PROCESS"),
            StateTransition("PROCESS", "END"),
        ]
        report = self.checker.analyze(nodes, transitions)
        self.assertTrue(report.is_sound)
        self.assertEqual(len(report.deadlock_states), 0)
        self.assertEqual(len(report.livelock_cycles), 0)
        self.assertEqual(len(report.unreachable_states), 0)

    def test_deadlock_detection(self):
        nodes = [
            StateNode("START", is_initial=True),
            StateNode("TRAP_STATE"),  # Non-terminal with no outgoing edge
            StateNode("END", is_terminal=True),
        ]
        transitions = [
            StateTransition("START", "TRAP_STATE"),
            StateTransition("START", "END"),
        ]
        report = self.checker.analyze(nodes, transitions)
        self.assertFalse(report.is_sound)
        self.assertIn("TRAP_STATE", report.deadlock_states)

    def test_livelock_cycle_detection(self):
        nodes = [
            StateNode("START", is_initial=True),
            StateNode("LOOP_A"),
            StateNode("LOOP_B"),
            StateNode("END", is_terminal=True),
        ]
        # LOOP_A and LOOP_B form an infinite cycle with no path to END
        transitions = [
            StateTransition("START", "LOOP_A"),
            StateTransition("LOOP_A", "LOOP_B"),
            StateTransition("LOOP_B", "LOOP_A"),
        ]
        report = self.checker.analyze(nodes, transitions)
        self.assertFalse(report.is_sound)
        self.assertTrue(len(report.livelock_cycles) >= 1)

    def test_unreachable_state_detection(self):
        nodes = [
            StateNode("START", is_initial=True),
            StateNode("ORPHAN"),
            StateNode("END", is_terminal=True),
        ]
        transitions = [
            StateTransition("START", "END"),
        ]
        report = self.checker.analyze(nodes, transitions)
        self.assertIn("ORPHAN", report.unreachable_states)


if __name__ == "__main__":
    unittest.main()
