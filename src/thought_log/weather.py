from pyowm import OWM

from .config import OPENWEATHER_API_KEY, DEFAULT_LOCATION


def get_weather(location: str = DEFAULT_LOCATION):
    owm = OWM(OPENWEATHER_API_KEY)
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(location)
    return observation.weather
