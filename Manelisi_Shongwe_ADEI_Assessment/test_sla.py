import unittest

from clean import is_breach


class SlaThresholdTest(unittest.TestCase):
    def test_equal_to_target_meets_sla(self):
        self.assertFalse(is_breach(120, 120))

    def test_one_minute_over_target_breaches_sla(self):
        self.assertTrue(is_breach(121, 120))


if __name__ == "__main__":
    unittest.main()