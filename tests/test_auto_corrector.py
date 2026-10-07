"""Unit tests for AutoCorrector and ZeroLoopGate."""

import unittest
from apex_zero_loop.core.auto_corrector import AutoCorrector
from apex_zero_loop.core.models import ContractSpec, VerificationStatus
from apex_zero_loop.gate import ZeroLoopGate


class TestAutoCorrectorAndGate(unittest.TestCase):
    def setUp(self):
        self.corrector = AutoCorrector()
        self.gate = ZeroLoopGate()

    def test_repair_safe_division(self):
        code = "res = x / y"
        repaired, corrections = self.corrector.repair_code(code)
        self.assertTrue(len(corrections) >= 1)
        self.assertIn("y != 0", repaired)

    def test_repair_safe_dict_get(self):
        code = "val = data['user_id']"
        repaired, corrections = self.corrector.repair_code(code)
        self.assertTrue(len(corrections) >= 1)
        self.assertIn(".get('user_id', None)", repaired)

    def test_repair_off_by_one(self):
        code = "for i in range(len(items) + 1): pass"
        repaired, corrections = self.corrector.repair_code(code)
        self.assertTrue(len(corrections) >= 1)
        self.assertIn("range(len(items))", repaired)

    def test_gate_auto_repair_end_to_end(self):
        # Flawed code: division by zero
        flawed_code = """
def compute_ratio(a, b):
    return a / b
"""
        report = self.gate.verify_code(flawed_code, auto_repair=True)
        self.assertEqual(report.status, VerificationStatus.VERIFIED)
        self.assertTrue(len(report.auto_corrections) >= 1)
        self.assertIsNotNone(report.corrected_code)
        self.assertIn("b != 0", report.corrected_code)


if __name__ == "__main__":
    unittest.main()
