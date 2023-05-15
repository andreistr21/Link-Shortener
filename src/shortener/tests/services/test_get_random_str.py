import string
from unittest import TestCase

from shortener.services import gen_random_str


class GetRandomStringTests(TestCase):
    def test_contained_characters(self):
        allowed_characters = string.ascii_lowercase + string.digits

        for _ in range(100):
            random_str = gen_random_str()
            for character in random_str:
                self.assertTrue(character in allowed_characters)

    def test_length_of_str(self):
        random_str = gen_random_str()
        self.assertEqual(len(random_str), 8)
