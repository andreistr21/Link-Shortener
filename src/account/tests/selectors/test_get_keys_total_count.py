from django.test import TestCase
from fakeredis import FakeStrictRedis

from account.selectors import get_keys_total_count


captured_commands = []


def capture_command(*args, **kwargs):
    captured_commands.append((args, kwargs))


class GetKeysTotalCountTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:  # sourcery skip: remove-unnecessary-cast
        cls.redis_keys = [
            "youtube:08.09",
            "linkedin:08.09",
            "linkedin:08.08",
            "twitch:05.08",
        ]
        cls.keys_tuples = [(int(0), [key.encode()]) for key in cls.redis_keys]

    def test_with_populated_list(
        self,
    ):  # sourcery skip: remove-unnecessary-cast
        redis_con = FakeStrictRedis()
        redis_pipeline = redis_con.pipeline()

        # Monkey-patch the pipeline's execute_command method
        redis_pipeline.execute_command = capture_command

        global captured_commands
        captured_commands = []

        get_keys_total_count(self.keys_tuples, redis_pipeline)

        expected_pipeline = [(("LLEN", key), {}) for key in self.redis_keys]
        self.assertEqual(captured_commands, expected_pipeline)

    def test_with_empty_list(self):
        redis_con = FakeStrictRedis()
        redis_pipeline = redis_con.pipeline()

        # Monkey-patch the pipeline's execute_command method
        redis_pipeline.execute_command = capture_command

        global captured_commands
        captured_commands = []

        get_keys_total_count([], redis_pipeline)

        expected_pipeline = []
        self.assertEqual(captured_commands, expected_pipeline)
