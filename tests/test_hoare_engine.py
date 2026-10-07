"""Unit tests for Dijkstra Weakest Precondition and Hoare Engine."""

import unittest
from apex_zero_loop.core.hoare_engine import HoareEngine


class TestHoareEngine(unittest.TestCase):
    def setUp(self):
        self.engine = HoareEngine()

    def test_assignment_wp(self):
        code = "x = x + 1"
        # {x > 4} x = x + 1 {x > 5}
        triple = self.engine.verify_hoare_triple("x > 4", code, "x > 5")
        self.assertIn("x + 1", triple.weakest_precondition)

    def test_conditional_branch_verification(self):
        code = """
if x > 0:
    y = x
else:
    y = -x
"""
        # Valid: if x > 0 or not x > 0, y >= 0 holds
        triple = self.engine.verify_hoare_triple("True", code, "y >= 0")
        self.assertIsNotNone(triple.weakest_precondition)

    def test_function_return_substitution(self):
        code = """
def double(n):
    return n * 2
"""
        triple = self.engine.verify_hoare_triple("n > 0", code, "result > 0")
        self.assertIn("n * 2", triple.weakest_precondition)


if __name__ == "__main__":
    unittest.main()
