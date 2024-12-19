import requests

from exceptions import APIError

API_KEY = 'qDljHMNmC8wqtYkWqbqjmYy5yGEYNonE'


def get_weather(city: str) -> list[dict]:
    try:
        data = requests.get(
            'http://dataservice.accuweather.com/locations/v1/cities/search',
            params=dict(apikey=API_KEY, q=city, details=True),
        ).json()
        location_key = data[0].get('Key')
    except IndexError:
        raise APIError(f'Не удалось найти город {city}')
    except Exception:
        raise APIError(f'Неизвестаня ошибка при получении города {city}')

    try:
        data = requests.get(
            f'http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}',
            params=dict(apikey=API_KEY, details=True, metric=True),
        ).json()

    except Exception:
        raise APIError(f'не удалось получить погоду города {city}')

    forecasts = []
    for day in data.get('DailyForecasts', []):
        try:
            min_temperature = day.get('Temperature', {}).get('Minimum', {}).get('Value', 0)
            max_temperature = day.get('Temperature', {}).get('Maximum', {}).get('Value', 0)
            forecasts.append({
                'date': day.get('Date'),
                'temperature': (min_temperature + max_temperature) / 2,
            })
        except Exception:
            raise APIError(f'Не удалось распаковать погоду города {city}')

    return forecasts
