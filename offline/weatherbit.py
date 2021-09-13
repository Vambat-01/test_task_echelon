from marshmallow_dataclass import dataclass
from marshmallow import EXCLUDE
from typing import List
from shared.models import CityWeatherDataPoint, WeatherDataPoint, City, Record
from datetime import datetime
import pytz
import requests
import os


@dataclass(frozen=True)
class WeatherBitEntry:
    """
        Класс для хранения данных о времени и погоде
    """
    timestamp_local: str
    temp: float

    class Meta:
        unknown = EXCLUDE


@dataclass(frozen=True)
class WeatherBitResponse:
    """
        Класс для удобного хранения данных API-запроса с сайта `https://www.weatherbit.io`
    """
    data: List[WeatherBitEntry]
    city_name: str
    lon: float
    timezone: str
    lat: float

    class Meta:
        unknown = EXCLUDE

    def to_datapoints(self, city_id: int) -> List[CityWeatherDataPoint]:
        datapoint = []
        for city in self.data:
            tz = pytz.timezone(self.timezone)
            dt = datetime.fromisoformat(city.timestamp_local)
            timestamp = tz.localize(dt)
            datapoint.append(CityWeatherDataPoint(city_id, WeatherDataPoint(city.temp, timestamp, "weatherbit")))
        return datapoint


def download_weather_from_weatherbit(cities: List[Record[City]]) -> List[List[CityWeatherDataPoint]]:
    """
        Получает почасовой прогноз погоды на сайта https://www.weatherbit.io
    :param cities: список городов из таблицы cities

    """
    cities_weather = []
    url = "http://api.weatherbit.io/v2.0/forecast/hourly"
    for city in cities:
        response = requests.get(url, params={
                                "lat": city.item.latitude,
                                "lon": city.item.longitude,
                                "key": os.environ["KEY_WEATHERBIT"]
                                })
        response_body = response.json()
        response = WeatherBitResponse.Schema().load(response_body)
        cities_weather.append(response.to_datapoints(city.id))
    return cities_weather
