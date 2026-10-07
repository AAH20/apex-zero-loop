"""Unit tests for Symbolic Executor and Runtime Hazard Detection."""

import unittest
from apex_zero_loop.core.symbolic_executor import SymbolicExecutor


class TestSymbolicExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = SymbolicExecutor()

    def test_detect_unguarded_zero_division(self):
        code = """
def calc_average(total, count):
    return total / count
"""
        paths = self.executor.analyze_code(code)
        self.assertTrue(len(paths) >= 1)
        hazards = [h for p in paths for h in p.potential_exceptions if h[0] == "ZeroDivisionError"]
        self.assertTrue(len(hazards) >= 1)

    def test_guarded_division_safe(self):
        code = """
def calc_average(total, count):
    if count != 0:
        return total / count
    return 0.0
"""
        paths = self.executor.analyze_code(code)
        # In guarded path, count != 0 suppresses hazard
        hazard_paths = [p for p in paths if any(h[0] == "ZeroDivisionError" for h in p.potential_exceptions)]
        # Either no hazards or hazard only in path without guard
        self.assertEqual(len(hazard_paths), 0)

    def test_detect_dict_key_error(self):
        code = """
def process(data):
    val = data['missing_key']
    return val
"""
        paths = self.executor.analyze_code(code)
        hazards = [h for p in paths for h in p.potential_exceptions if h[0] == "KeyError"]
        self.assertTrue(len(hazards) >= 1)


if __name__ == "__main__":
    unittest.main()
