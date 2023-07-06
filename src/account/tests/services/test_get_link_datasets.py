import json
from datetime import timedelta
from unittest import mock

from django.test import TestCase

from account.services import get_link_datasets


class GetLinkDatasetsTests(TestCase):
    class linkObj:
        alias = "test-alias"

    @classmethod
    def setUpTestData(cls) -> None:
        cls.dummy_link = cls.linkObj()
        cls.charts_data = [
            json.dumps({"time": "time_str", "country": "PL"}).encode("utf-8"),
            json.dumps({"time": "time_str", "country": "PL"}).encode("utf-8"),
            json.dumps({"time": "time_str", "country": "DE"}).encode("utf-8"),
            json.dumps({"time": "time_str", "country": "ES"}).encode("utf-8"),
            json.dumps({"time": "time_str", "country": "ES"}).encode("utf-8"),
            json.dumps({"time": "time_str", "country": ""}).encode("utf-8"),
        ]
        cls.clicks_chart_data = {"30.06": 3, "29.06": 2}
        cls.countries_chart_data = {"PL": 2, "DE": 1, "ES": 2, "": 1}
        cls.expected_countries_chart_data = {
            "PL": 2,
            "DE": 1,
            "ES": 2,
            "Unknown": 1,
        }

    @mock.patch("account.services.get_charts_data")
    @mock.patch("account.services.get_link_statistics")
    def test_returns_expected_chart_datasets(
        self, get_link_statistics_mock, get_charts_data_mock
    ):
        get_link_statistics_mock.return_value = self.charts_data
        get_charts_data_mock.return_value = (
            self.clicks_chart_data.copy(),
            self.countries_chart_data.copy(),
        )

        clicks_chart_dataset, country_chart_dataset = get_link_datasets(
            self.dummy_link
        )

        expected_clicks_chart_dataset = json.dumps(
            {
                "title": "Clicks in last 60 days",
                "data": {
                    "labels": list(self.clicks_chart_data.keys()),
                    "datasets": [
                        {
                            "label": "Clicks",
                            "backgroundColor": "#20a7f8",
                            "data": list(self.clicks_chart_data.values()),
                        }
                    ],
                },
            }
        )
        expected_country_chart_dataset = json.dumps(
            {
                "title": "Clicks by Country",
                "data": {
                    "labels": list(self.expected_countries_chart_data.keys()),
                    "datasets": [
                        {
                            "label": "Clicks (%)",
                            "data": list(
                                self.expected_countries_chart_data.values()
                            ),
                        }
                    ],
                },
            }
        )
        self.assertEqual(clicks_chart_dataset, expected_clicks_chart_dataset)
        self.assertEqual(country_chart_dataset, expected_country_chart_dataset)
        get_link_statistics_mock.assert_called_once_with(self.dummy_link.alias)
        get_charts_data_mock.assert_called_once_with(self.charts_data)
