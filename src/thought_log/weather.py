from email import message
from typing import Tuple
import geocoder
from pyowm import OWM

from .config import OPENWEATHER_API_KEY


def get_weather(coords: Tuple[float] = None):
    if not coords:
        coords = get_location()

    owm = OWM(OPENWEATHER_API_KEY)
    mgr = owm.weather_manager()
    observation = mgr.weather_at_coords(*coords)
    return observation.weather


def get_location():
    location = geocoder.ip("me")
    latitude = location.geojson["features"][0]["properties"]["lat"]
    longitude = location.geojson["features"][0]["properties"]["lng"]
    return latitude, longitude
