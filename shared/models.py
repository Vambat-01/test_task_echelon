from dataclasses import dataclass
from datetime import datetime
from typing import List, TypeVar, Generic

T = TypeVar('T')


@dataclass(frozen=True)
class Record(Generic[T]):
    item: T
    id: int


@dataclass(frozen=True)
class City:
    """
        Класс для хранения данных о городе
    """
    name: str
    latitude: float
    longitude: float
    country: str


@dataclass(frozen=True)
class WeatherDataPoint:
    """
        Класс для хранения данных о погоде
    """
    temperature: float
    timestamp: datetime
    source: str


@dataclass(frozen=True)
class CityWeatherDataPoint:
    """
        Класс для хранения данных о погоде и идентификатора города
    """
    city_id: int
    data: WeatherDataPoint


@dataclass(frozen=True)
class Forecast:
    """
        Класс для хранения прогноза погоды
    """
    city: City
    entries: List[WeatherDataPoint]
