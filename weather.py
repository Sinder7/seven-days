import requests
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_session():
    """
    Создает HTTP-сессию с политикой повторных попыток для надежных запросов.
    """
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def get_coordinates(city_name, session):
    """
    Получает координаты (широту и долготу) по названию города с помощью Open-Meteo Geocoding API.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1, "language": "ru", "format": "json"}
    try:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.SSLError:
        # Попытка без проверки SSL
        response = session.get(url, params=params, verify=False, timeout=10)
        response.raise_for_status()

    data = response.json()
    if "results" in data and data["results"]:
        loc = data["results"][0]
        return loc["latitude"], loc["longitude"], loc.get("name", city_name)
    raise ValueError(f"Город '{city_name}' не найден")


def get_weather(latitude, longitude, session):
    """
    Получает текущую погоду для заданных координат с помощью Open-Meteo Weather API.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True,
        "timezone": "auto",
    }
    try:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.SSLError:
        response = session.get(url, params=params, verify=False, timeout=10)
        response.raise_for_status()

    data = response.json()
    if "current_weather" in data:
        return data["current_weather"]
    raise RuntimeError("Не удалось получить данные о текущей погоде")


def main():
    if len(sys.argv) < 2:
        print("Использование: python weather.py <название_города>")
        sys.exit(1)

    city = " ".join(sys.argv[1:])
    session = create_session()

    try:
        lat, lon, name = get_coordinates(city, session)
        weather = get_weather(lat, lon, session)

        print(f"Погода в городе {name} (lat={lat}, lon={lon}):")
        print(f"  Температура: {weather['temperature']}°C")
        print(f"  Скорость ветра: {weather['windspeed']} м/с")
        print(f"  Направление ветра: {weather['winddirection']}°")
        print(f"  Код погоды: {weather.get('weathercode', 'N/A')}")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
