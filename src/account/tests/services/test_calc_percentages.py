from django.test import TestCase

from account.services import calc_percentages


class CalcPercentagesTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.raw_countries_chart_data = {"DE": 60, "IT": 10, "PL": 80, "ES": 50}
        cls.expected_percentages_countries_chart_data = {
            "PL": 40,
            "DE": 30,
            "ES": 25,
            "IT": 5,
        }

    def test_returned_data(self):
        resp = calc_percentages(self.raw_countries_chart_data)
        
        self.assertEqual(resp, self.expected_percentages_countries_chart_data)
