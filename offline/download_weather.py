import os
from shared.weather_storage import WeatherStorage
import requests
import sqlite3
import pandas as pd
import gzip
from io import StringIO
from typing import List
from shared.models import City
from pathlib import Path
from openweathermap import download_weather_from_openweathermap
from weatherbit import download_weather_from_weatherbit


file_url = 'https://www.weatherbit.io/static/exports/cities_20000.csv.gz'   # Файл для заполнения таблицы cities


def get_cities_from_file(file_url: str) -> List[City]:
    """
        Скачиваем файл и возвращаем список городов
    :param file_url: адресс файла
    """
    r = requests.get(file_url)
    unzipped = gzip.decompress(r.content)
    text = unzipped.decode()

    all_cities = []
    df_cities = pd.read_csv(StringIO(text))
    for city in df_cities.itertuples():
        all_cities.append(City(city.city_name, city.lat, city.lon, city.country_full))
    return all_cities


def main():
    cities = get_cities_from_file(file_url)
    path_to_database = Path(os.getcwd()).parent / 'online' / 'weather_db.sqlite'
    connection = sqlite3.connect(path_to_database)
    weather_storage = WeatherStorage(connection)
    weather_storage.create_tables()
    weather_storage.add_cities(cities)

    cities_for_weatherbit = weather_storage.get_cities(0, 11)   # Получим с 1 по 10 город из базы данных таблицы cities
    cities_weatherbit = download_weather_from_weatherbit(cities_for_weatherbit)
    weather_storage.add_weather_data(cities_weatherbit)

    cities_for_openweathermap = weather_storage.get_cities(4, 16)   # Получим с 5 по 15 город из базы данных таблицы
    # cities
    cities_openweathermap = download_weather_from_openweathermap(cities_for_openweathermap)
    weather_storage.add_weather_data(cities_openweathermap)


if __name__ == "__main__":
    main()
