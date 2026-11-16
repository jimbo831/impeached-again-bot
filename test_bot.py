import os
import tempfile
import unittest
from types import SimpleNamespace

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
    def test_every_response_includes_count(self):
        for template in bot.RESPONSES + [bot.COUNT_RESPONSE]:
            self.assertIn("7", template.format(n=7, ord=bot.ordinal(7)))


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
