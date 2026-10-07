"""Unit tests for BooleanSATSolver and DPLL engine."""

import unittest
from apex_zero_loop.core.sat_verifier import BooleanSATSolver


class TestBooleanSATSolver(unittest.TestCase):
    def setUp(self):
        self.solver = BooleanSATSolver()

    def test_satisfiable_cnf(self):
        # (x1 or x2) and (not x1 or x2) => SAT with x2 = True
        clauses = [[1, 2], [-1, 2]]
        model = self.solver.solve_cnf(clauses, 2)
        self.assertIsNotNone(model)
        self.assertTrue(model[2])

    def test_unsatisfiable_cnf(self):
        # (x1) and (not x1) => UNSAT
        clauses = [[1], [-1]]
        model = self.solver.solve_cnf(clauses, 1)
        self.assertIsNone(model)

    def test_implication_valid(self):
        # (A and B) => A is always true
        is_valid, counterexample = self.solver.verify_implication("A and B", "A")
        self.assertTrue(is_valid)
        self.assertIsNone(counterexample)

    def test_implication_invalid_with_counterexample(self):
        # A => (A and B) is invalid (when A=True, B=False)
        is_valid, counterexample = self.solver.verify_implication("A", "A and B")
        self.assertFalse(is_valid)
        self.assertIsNotNone(counterexample)
        self.assertTrue(counterexample.get("A"))
        self.assertFalse(counterexample.get("B"))


if __name__ == "__main__":
    unittest.main()
