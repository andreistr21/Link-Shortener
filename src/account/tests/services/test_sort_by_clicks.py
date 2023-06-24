from django.test import TestCase

from account.services import sort_by_clicks


class SortByClicksTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.default_list = [
            ("", 7),
            ("", 6),
            ("", 9),
            ("", 43),
            ("", 13),
            ("", 1),
        ]
        cls.ascending_list = [
            ("", 1),
            ("", 6),
            ("", 7),
            ("", 9),
            ("", 13),
            ("", 43),
        ]
        cls.descending_list = [
            ("", 43),
            ("", 13),
            ("", 9),
            ("", 7),
            ("", 6),
            ("", 1),
        ]

    def test_ascending_sort(self):
        mapped_clicks = sort_by_clicks(self.default_list, "clicks")

        self.assertEqual(mapped_clicks, self.ascending_list)

    def test_descending_sort(self):
        mapped_clicks = sort_by_clicks(self.default_list, "-clicks")

        self.assertEqual(mapped_clicks, self.descending_list)
