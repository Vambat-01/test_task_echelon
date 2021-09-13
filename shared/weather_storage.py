from typing import List, Optional
import sqlite3
from .models import City, WeatherDataPoint, CityWeatherDataPoint, Forecast, Record
import threading


class CreateDatabaseException(Exception):
    """
        Ошибка создания SQLite базы данных
    """
    pass


class WeatherStorage:
    """
        Класс для чтения вопросов из SQLite базы данных
    """

    def __init__(self, connection: sqlite3.Connection):
        """
        :param connection: подключение к базе данных
        """
        self.connection = connection
        self.connection_lock = threading.Lock()

    def create_tables(self):
        """
            Создаст все необходимые таблицы в SQLite базе данных. Таблицы будут пустыми
        """
        with self.connection:
            self.connection.executescript("""
                                            CREATE TABLE cities (
                                            id INTEGER PRIMARY KEY,
                                            name TEXT NOT NULL,
                                            latitude REAL NOT NULL,
                                            longitude REAL NOT NULL,
                                            country TEXT NULL
                                            );
    
                                            CREATE TABLE weather (
                                           id INTEGER PRIMARY KEY,
                                           city_id INTEGER NOT NULL,
                                           timestamp TEXT NOT NULL,
                                           temperature INTEGER NOT NULL,
                                           source TEXT NOT NULL,
                                           FOREIGN KEY(city_id) REFERENCES questions (id))
                                            """)

    def add_cities(self, cities: List[City]):
        """
            Заполняет таблицу городов в базе данных
        :param cities: список городов
        """
        with self.connection_lock:
            with self.connection:
                for city in cities:
                    self.connection.execute("INSERT INTO cities(name, latitude, longitude, country) VALUES(?, ?, ?, ?)",
                                            (city.name, city.latitude, city.longitude, city.country))

    def add_weather_data(self, data: List[List[CityWeatherDataPoint]]):
        """
            Заполняет таблицу погоды в базе данных
        :param data: прогноз погоды
        """
        with self.connection_lock:
            with self.connection:
                for d in data:
                    for w in d:
                        timestamp = w.data.timestamp.isoformat()
                        self.connection.execute("INSERT INTO weather(city_id, timestamp, temperature, source) "
                                                "VALUES (?, ? , ?, ?)",
                                                (w.city_id, timestamp, w.data.temperature, w.data.source))

    def get_forecast(self, city_name: str, latitude: float, longitude: float) -> Optional[Forecast]:
        """
                Возвращает почасовой прогноз погоды для города из базы данных
            :param city_name: название города
            :param latitude: широта
            :param longitude: долгота
            """
        eps = 0.001  # Города могут быть с одинаковым названием, и разные сайты использовать разное количестко знаков
        # после запятой, поэтому погрешность в определение координат города в 11.11км мне кажется разумной
        with self.connection_lock:
            with self.connection:
                city_weather = self.connection.execute("""
                            SELECT t1.name, t1.latitude, t1.longitude, t1.country, t2.timestamp, t2.temperature, t2.source
                            FROM cities AS t1 INNER JOIN weather AS t2
                            ON t1.id = t2.city_id
                            WHERE name = ? AND latitude >= ? AND latitude <= ?
                            AND longitude >= ? AND longitude <= ?
                            """, (city_name, latitude - eps, latitude + eps, longitude - eps, longitude + eps))

        if not city_weather:
            return None

        entries = []
        name = ""
        latitude = 0.0
        longitude = 0.0
        country = ""
        for hour in city_weather:
            entries.append(WeatherDataPoint(hour[5], hour[4], hour[6]))
            name = hour[0]
            latitude = hour[1]
            longitude = hour[2]
            country = hour[3]

        return Forecast(City(name, latitude, longitude, country), entries)

    def get_cities(self, start: int, end: int) -> List[Record[City]]:
        """
            Возвращает список городов из базы данных по запросу
        :param start: начало поиска
        :param end: конец поиска
        """
        cities = []
        with self.connection_lock:
            with self.connection:
                cities_table = self.connection.execute("SELECT * FROM cities WHERE id > ? and id < ?", (start, end))
        for city in cities_table:
            cities.append(Record(City(city[1], city[2], city[3], city[4]), city[0]))
        return cities
