import unittest
from src.arc_verify_core.money import parse_usdc_micro,native_raw_to_usdc_micro
M=10**12
class Money(unittest.TestCase):
    def test_parse_ok(self):
        self.assertEqual(parse_usdc_micro("1.5"),1_500_000); self.assertEqual(parse_usdc_micro("12"),12_000_000)
        self.assertEqual(parse_usdc_micro("0.000001"),1); self.assertEqual(parse_usdc_micro(2),2_000_000)
    def test_reject_float(self):
        for v in (1.5,True,float("nan")): self.assertRaises(ValueError,parse_usdc_micro,v)
    def test_reject_precision(self):
        for v in ("0.0000001","-1","1e3","","0"): self.assertRaises(ValueError,parse_usdc_micro,v)
    def test_native_divisible(self):
        self.assertEqual(native_raw_to_usdc_micro(1_500_000*M),(1_500_000,0))
    def test_native_dust_not_rounded(self):
        micro,dust=native_raw_to_usdc_micro(1_500_000*M+7)
        self.assertIsNone(micro); self.assertEqual(dust,7)
    def test_zero(self): self.assertEqual(native_raw_to_usdc_micro(0),(0,0))
