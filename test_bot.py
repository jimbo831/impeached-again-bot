import os
import tempfile
import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import bot


class TestOrdinal(unittest.TestCase):
    def test_suffixes(self):
        cases = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 11: "11th", 12: "12th",
                 13: "13th", 21: "21st", 22: "22nd", 23: "23rd", 111: "111th", 101: "101st"}
        for n, expected in cases.items():
            self.assertEqual(bot.ordinal(n), expected)


class TestTrigger(unittest.TestCase):
    def test_matches(self):
        for msg in ["Trump was impeached again", "Impeached, again", "impeached... again",
                    "impeached *again*", "impeached him (again)", "IMPEACH HIM YET AGAIN"]:
            self.assertTrue(bot.TRIGGER_RE.search(msg), msg)

    def test_non_matches(self):
        for msg in ["impeach them against their will", "he is unimpeachable once again",
                    "impeached once more", "again impeached"]:
            self.assertFalse(bot.TRIGGER_RE.search(msg), msg)


class TestResponses(unittest.TestCase):
    def test_every_response_formats_and_includes_count(self):
        values = {"count": 7777, "ordinal": "7777th", "age": 80, "approval": 38, "gas_price": "3.12"}
        for template in bot.RESPONSES + [bot.COUNT_RESPONSE]:
            self.assertIn("7777", template.format(**values), template)

    def test_skips_responses_missing_live_values(self):
        for _ in range(len(bot.RESPONSES) * 2):
            response = bot.make_response(5)
            self.assertNotIn("{", response)
            self.assertNotIn("Approval rating", response)


class TestShuffleBag(unittest.TestCase):
    def test_every_response_once_per_round_with_no_repeats(self):
        bot._bag.clear()
        drawn = [bot.next_template() for _ in range(len(bot.RESPONSES) * 3)]
        self.assertCountEqual(drawn[:len(bot.RESPONSES)], bot.RESPONSES)
        for a, b in zip(drawn, drawn[1:]):
            self.assertNotEqual(a, b)


class TestLiveValues(unittest.TestCase):
    def tearDown(self):
        bot.live_values.clear()
        bot.live_failures.clear()

    def test_parses_sources(self):
        with patch.object(bot, "fetch_json", return_value={"average": {"Approve": 37.6}}):
            self.assertEqual(bot.fetch_approval(), 38)
        eia = {"response": {"data": [{"value": "3.995"}]}}
        with patch.object(bot, "fetch_json", return_value=eia), patch.object(bot, "EIA_API_KEY", "key"):
            self.assertEqual(bot.fetch_gas_price(), "4.00")

    def test_uses_live_values_when_available(self):
        bot.live_values.update(approval=37, gas_price="3.99")
        bot._bag.clear()  # start a fresh round so every response is drawn once
        responses = [bot.make_response(5) for _ in range(len(bot.RESPONSES))]
        self.assertTrue(any("37% and falling" in r for r in responses))
        self.assertTrue(any("$3.99 a gallon" in r for r in responses))

    def test_reports_problem_only_after_three_failures(self):
        bot.live_failures["gas_price"] = (2, "timed out")
        self.assertIsNone(bot.live_data_problem())
        bot.live_failures["gas_price"] = (3, "timed out")
        self.assertIn("gas_price: timed out", bot.live_data_problem())


class TestAge(unittest.TestCase):
    def test_birthday(self):
        self.assertEqual(bot.trump_age(date(2026, 6, 13)), 79)
        self.assertEqual(bot.trump_age(date(2026, 6, 14)), 80)


class TestCounter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.original_file = bot.COUNTER_FILE
        bot.COUNTER_FILE = os.path.join(self.tmp.name, "counter.json")

    def tearDown(self):
        bot.COUNTER_FILE = self.original_file
        self.tmp.cleanup()

    def test_increment_starts_at_one_and_persists(self):
        guild = SimpleNamespace(id=42, name="Test Server")
        self.assertEqual(bot.increment_count(guild), 1)
        self.assertEqual(bot.increment_count(guild), 2)
        self.assertEqual(bot.get_count(bot.load_data(), 42), 2)

    def test_servers_are_counted_separately(self):
        bot.increment_count(SimpleNamespace(id=1, name="A"))
        self.assertEqual(bot.get_count(bot.load_data(), 2), 0)


if __name__ == "__main__":
    unittest.main()
