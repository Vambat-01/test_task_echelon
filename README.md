# Тестовое задание для АО "Эшелон Технологии"

Описание задания не очень четкое, поэтому я решил разбить задание на 2 части: 
- 1. Скрипт для обхода сайтов с погодой и заполнения базы, который будет запускаться раз в сутки. 
- 1. Сервер, предоставляющий API для доступа к этой базе.

## Установка зависимостей
1. Установите зависимости: `pip install -r requirements.txt`

## Запуск скрипта для создания и заполнения базы данных. 
Скрипт проходит по городам из базы и загружает погоду для каждого города с сайтов
1. Выставите переменную окружения `KEY_WEATHERBIT`:  `export KEY_WEATHERBIT=<api key for site>`
1. Выставите переменную окружения `KEY_OPENWEATHERMAP`:  `export KEY_OPENWEATHERMAP=<api key for site>`
1. Перейдите в терминале в репозитории и выполните команду: `python offline/download_weather.py`

## Запуск Web-приложения используя [Docker](https://www.docker.com/)
1. Cоздайте `Docker` образ приложения: `docker build -t test_task_echelon .`
1. Запустите `Docker` контейнер: `docker run --name task_echelon -p 8000:8000 test_task_echelon`
1. Проверьте работоспособность приложения.
    1. Отправьте запрос на сервер выполнив команду: `curl --request GET 'http://localhost:8000/api/weather?city=Le%20Creusot&latitude=46.80714&longitude=4.41632'`
        - Ответ должен содержать информацию о городе и прогноз. Это ответ сервера, если запрашиваевая локация есть в базе и для нее был ранее загружен прогноз погоды. Ожидаеный ответ: 
        ```
            {
                "city": {
                    "country": "France",
                    "latitude": 46.80714,
                    "longitude": 4.41632,
                    "name": "Le Creusot"
                },
                "entries": [
                    {
                        "source": "weatherbit",
                        "temperature": 21.9,
                        "timestamp": "2021-09-12T19:00:00+02:00"
                    },
                    {
                        "source": "openweathermap",
                        "temperature": 23.73,
                        "timestamp": "2021-09-12T18:00:00+02:00"
                    },
                    ...
                ]
            }
        ```
    1. Отправьте запрос на сервер выполнив команду: `curl --location --request GET 'http://localhost:8000/api/weather?city=Le%D1%81&latitude=46.80714&longitude=40.41632'`
        - Если запрашиваемой локации нет в базе, то сервер вернет статус код `404`