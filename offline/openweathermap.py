from marshmallow_dataclass import dataclass
from marshmallow import EXCLUDE
from typing import List
from shared.models import CityWeatherDataPoint, WeatherDataPoint, City, Record
import os
import requests
from datetime import datetime
import pytz


@dataclass(frozen=True)
class OpenWeatherMapEntry:
    """
        Класс для хранения данных о времени и погоде
    """
    dt: int
    temp: float

    class Meta:
        unknown = EXCLUDE


@dataclass(frozen=True)
class OpenWeatherMapResponse:
    """
        Класс для удобного хранения данных API-запроса с сайта `https://openweathermap.org`
    """
    lat: float
    lon: float
    timezone: str
    hourly: List[OpenWeatherMapEntry]

    class Meta:
        unknown = EXCLUDE

    def to_datapoints(self, city_id: int) -> List[CityWeatherDataPoint]:
        datapoint = []
        for hour in self.hourly:
            tz = pytz.timezone(self.timezone)
            dt = datetime.fromtimestamp(hour.dt, tz)
            datapoint.append(CityWeatherDataPoint(city_id, WeatherDataPoint(hour.temp, dt, "openweathermap")))
        return datapoint


def download_weather_from_openweathermap(cities: List[Record[City]]) -> List[List[CityWeatherDataPoint]]:
    """
        Получает почасовой прогноз погоды на сайте https://openweathermap.org и заполняет таблицу weather
    :param cities: список городов из таблицы cities
    """
    cities_weather = []
    url = "https://api.openweathermap.org/data/2.5/onecall"
    for city in cities:
        response = requests.get(url, params={
            "lat": city.item.latitude,
            "lon": city.item.longitude,
            "exclude": "minutely, daily, alerts",
            "units": "metric",
            "appid": os.environ["KEY_OPENWEATHERMAP"]
        })
        response_body = response.json()
        response = OpenWeatherMapResponse.Schema().load(response_body)
        cities_weather.append(response.to_datapoints(city.id))
    return cities_weather
