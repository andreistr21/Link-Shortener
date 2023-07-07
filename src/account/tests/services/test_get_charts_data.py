import json
from collections import OrderedDict
from datetime import datetime, timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from account.services import get_charts_data


class GetChartsDataTests(TestCase):
    @mock.patch("account.services.calc_percentages")
    def test_for_expected_return_values(self, calc_percentages_mock):
        test_data = self._get_test_data()

        clicks_chart_data, _ = get_charts_data(test_data)

        (
            expected_clicks_chart_data,
            expected_countries_chart_data,
        ) = self._get_charts_data(test_data)
        self.assertEqual(clicks_chart_data, expected_clicks_chart_data)
        calc_percentages_mock.assert_called_once_with(
            expected_countries_chart_data
        )

    def _get_charts_data(
        self, link_statistics: list[tuple[str, str]]
    ) -> tuple[dict[str, int], dict[str, int]]:
        clicks_chart_data = {}
        countries_chart_data = {}

        for stat in link_statistics:
            parsed_stat = json.loads(stat)
            date = datetime.fromisoformat(parsed_stat["time"]).strftime(
                "%m.%d"
            )
            if not clicks_chart_data.get(date):
                clicks_chart_data[date] = 0
            clicks_chart_data[date] += 1

            country_code = parsed_stat["country"]
            if not countries_chart_data.get(country_code):
                countries_chart_data[country_code] = 0
            countries_chart_data[country_code] += 1

        clicks_chart_data = OrderedDict(
            reversed(list(clicks_chart_data.items()))
        )

        return clicks_chart_data, countries_chart_data

    def _get_test_data(self) -> list:
        test_data = []
        date = timezone.now()
        countries_list = ["PL", "DE", "ES", "IT"]
        for i in range(61):
            current_day = date - timedelta(days=i)
            clicks_amount = 3
            for y in range(clicks_amount):
                current_time = current_day - timedelta(minutes=y)
                test_data.append(
                    json.dumps(
                        {
                            "time": current_time.isoformat(),
                            "country": countries_list[y],
                        }
                    ).encode("utf-8"),
                )

        return test_data
