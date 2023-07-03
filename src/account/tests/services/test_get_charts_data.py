import json
import random
from datetime import datetime, timedelta
from functools import lru_cache

from django.test import TestCase
from django.utils import timezone
from fakeredis import FakeStrictRedis
from redis import Redis

from account.services import get_charts_data


class GetChartsDataTests(TestCase):
    def test_for_expected_return_values(self):
        test_data = self._get_test_data()

        clicks_chart_data, countries_chart_data = get_charts_data(test_data)

        (
            expected_clicks_chart_data,
            expected_countries_chart_data,
        ) = self._get_charts_data(test_data)
        self.assertEqual(expected_clicks_chart_data, clicks_chart_data)
        self.assertEqual(
            expected_countries_chart_data,
            countries_chart_data,
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

        return clicks_chart_data, countries_chart_data

    @lru_cache(maxsize=1)
    def _redis_connection(self) -> Redis:
        """Creates redis connection during first call and returns it. During
        next call cached value will be returned"""
        return FakeStrictRedis()

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