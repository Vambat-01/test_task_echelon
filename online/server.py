from flask import Flask, request, jsonify
from marshmallow_dataclass import dataclass
from marshmallow.exceptions import ValidationError
from shared.weather_storage import WeatherStorage
import sqlite3


@dataclass(frozen=True)
class RequestParams:
    city: str
    latitude: float
    longitude: float


def run_server():
    app = Flask(__name__)
    path_to_database = "weather_db.sqlite"
    connection = sqlite3.connect(path_to_database, check_same_thread=False)
    weather_storage = WeatherStorage(connection)

    @app.route('/api/weather', methods=['GET'])
    def get_database():
        if request.method == 'GET':
            try:
                request_body = RequestParams.Schema().load(request.args)
                response = weather_storage.get_forecast(request_body.city,
                                                        request_body.latitude,
                                                        request_body.
                                                        longitude
                                                        )
                if response.entries:
                    return jsonify(response)
                else:
                    return "Not Found 404"
            except ValidationError:
                print("Validation failed. Return 400")

    app.run(host='0.0.0.0', port=8000, debug=False)
    connection.close()


if __name__ == '__main__':
    run_server()
