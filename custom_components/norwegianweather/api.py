"""Sample API Client."""
from datetime import datetime, timedelta, timezone
import datetime as dt
import logging
import asyncio
import socket
from typing import Optional
import aiohttp
import async_timeout
import xml.etree.ElementTree as ET
import re

# from homeassistant.util import dt
from decimal import Decimal
import email.utils as eut

# image stuff
import os, sys
from PIL import Image, TarIO, ImageDraw, ImageFont

TIMEOUT = 20
API_USER_AGENT = "https://github.com/tmjo"  # requirement yr: If this is missing or generic, you will get a 403 Forbidden response. Do not fake this or you are likely to be permanently blacklisted!
API_PREDICTION = "prediction"
API_OBSERVATION = "observation"
API_STRINGTIME = "%Y-%m-%dT%H:%M:%S%z"
API_LANG = "nb"
API_NAME = "norwegianweather"


# Directories
CONST_DIR_THIS = os.path.split(__file__)[0]
CONST_DIR_WEATHERICONS = os.path.join(CONST_DIR_THIS, "weathericon")
CONST_DIR_FONTS = os.path.join(CONST_DIR_THIS, "fonts")
CONST_DIR_DEFAULT = os.path.join(CONST_DIR_THIS, "tmp")

# Filepaths
CONST_FILE_WEATHERICONS = os.path.join(CONST_DIR_WEATHERICONS, "weathericon.tar")
CONST_FILE_FONT = os.path.join(CONST_DIR_FONTS, "NotoSansJP-Regular.otf")


CONST_WIND_DIR_CARDINAL = "wind_direction_cardinal"
CONST_WIND_DIR_BEARING = "wind_from_direction"
CONST_WIND_SPEED = "wind_speed"
CONST_WIND_SPEED_GUST = "wind_speed_of_gust"
CONST_WIND = [CONST_WIND_DIR_BEARING, CONST_WIND_SPEED, CONST_WIND_SPEED_GUST]

CONST_IMAGEVALUES = [
    "air_temperature",
    "precipitation_amount",
    CONST_WIND_DIR_BEARING,
    CONST_WIND_SPEED,
    CONST_WIND_SPEED_GUST,
    "air_pressure_at_sea_level",
]

CONST_DISPLAY_UNITS = {
    "celsius": "°C",
    "degrees": "°",
}


_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class NorwegianWeatherApiClient:
    def __init__(
        self,
        place,
        latitude,
        longitude,
        session: aiohttp.ClientSession,
        altitude=None,
        output_dir=CONST_DIR_DEFAULT,
    ) -> None:

        """Sample API Client."""
        self._session = session
        self.place = place
        self.lat = round(latitude, 4)  # max 4 digits ref yr terms
        self.lon = round(longitude, 4)  # max 4 digits ref yr terms
        self.altitude = altitude
        self.yrdata = None
        self.expires = None
        self.last_modified = None
        self.output_dir = output_dir

    def get_url(
        self,
        datatype="complete",
        lang=API_LANG,
        interval=10,
    ):
        url = f"https://api.met.no/weatherapi/locationforecast/2.0/{datatype}?lat={self.lat}&lon={self.lon}"
        if self.altitude is not None:
            url += f"&altitude={self.altitude}"
        return url

    async def async_get_data(self) -> dict:
        """Get data from the API."""

        if self.expires is None or datetime.now(timezone.utc) > self.expires:
            _LOGGER.debug(
                f"Calling API to fetch new data (expired: {self.expires} now: {datetime.now(timezone.utc)})"
            )
            await self.fetch_data()
        else:
            _LOGGER.debug(
                f"Data still valid, skipping call to API (expires: {self.expires} now: {datetime.now(timezone.utc)})."
            )

        _LOGGER.debug(f"{self.yrdata}")
        if self.yrdata is not None:
            try:
                self.test()
            except Exception as e:
                _LOGGER.error(f"Exception running tests: {e}")
                pass
        _LOGGER.debug("Async returning yrdata.")
        return self.yrdata

    async def fetch_data(self):
        headers = {"User-Agent": API_USER_AGENT}
        self.yrdata = await self.api_wrapper("get", self.get_url(), headers)

    async def api_wrapper(
        self, method: str, url: str, data: dict = {}, headers: dict = {}
    ) -> dict:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(TIMEOUT, loop=asyncio.get_event_loop()):
                if self.last_modified is not None:
                    ims_headers = {
                        "If-Modified-Since": eut.format_datetime(
                            self.last_modified, usegmt=True
                        )
                    }
                    response = await self._session.get(
                        url, headers={**headers, **ims_headers}
                    )
                    if response.status == 304:  # 304 - not modified
                        _LOGGER.debug(
                            f"API response: {response.status} Expires: {self.expires} Last modified: {self.last_modified} Returning existing data."
                        )
                        return self.yrdata
                response = await self._session.get(url, headers=headers)
                self.expires = parse_http_date(response.headers["expires"])
                self.last_modified = parse_http_date(response.headers["last-modified"])
                _LOGGER.debug(
                    f"API response: {response.status} Expires: {self.expires} Last modified: {self.last_modified}"
                )
                return await response.json()

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happend! - %s", exception)

    def get_unit(self, unit, display=False):
        try:
            yr_unit = (
                self.yrdata.get("properties").get("meta").get("units").get(unit, "")
            )
            if display:
                display_unit = CONST_DISPLAY_UNITS.get(yr_unit, yr_unit)
                return display_unit
            return yr_unit
        except AttributeError:
            _LOGGER.error(f"Could not find unit {unit}")
            return "test"

    def test(self, filename=None):
        prop = self.yrdata.get("properties", None)
        timeseries = None
        if prop is not None:
            timeseries = prop.get("timeseries", None)

        images = []
        if timeseries is not None:
            _LOGGER.debug(f"Found timeseries - checking")
            cnt = 0
            for timeserie in timeseries:
                if cnt >= 6:
                    break
                time = timeserie.get("time")
                data = timeserie.get("data", None)
                next_1h = data.get("next_1_hours", None)
                if next_1h is not None:
                    symbol_code = next_1h.get("summary").get("symbol_code", None)
                    if symbol_code is not None:
                        cnt += 1
                        image = self.get_weather_symbol(symbol_code)
                        image = self.create_weather_image(image, timeserie)
                        images.append(image)
                        _LOGGER.debug(f"{time}: {symbol_code} size: {image.size}")

        else:
            _LOGGER.debug("Could not find any timeseries.")

        _LOGGER.debug(f"Combining {len(images)} images.")
        newimage = imagelist_combine(images)

        if filename is None:
            filename = os.path.join(self.output_dir, API_NAME + ".png")

        _LOGGER.debug(f"Saving image {filename}.")
        newimage.save(filename, "png")

    def test4plot(self):
        res = {}
        prop = self.yrdata.get("properties", None)
        timeseries = None
        if prop is not None:
            timeseries = prop.get("timeseries", None)

        if timeseries is not None:
            _LOGGER.debug(f"Found timeseries - checking")
            cnt = 0
            for timeserie in timeseries:
                if cnt >= 6:
                    break
                time = datetime.strptime(timeserie.get("time"), API_STRINGTIME)

                data = timeserie.get("data", None)
                details = data.get("instant").get("details")
                res[time] = details
            return res
        else:
            _LOGGER.debug("Could not find any timeseries.")

    def get_weather_symbol(self, weatherstr=None):
        _LOGGER.debug(
            f"Trying to open tar archive {CONST_FILE_WEATHERICONS} looking for {weatherstr}"
        )
        fp = TarIO.TarIO(CONST_FILE_WEATHERICONS, f"png/{weatherstr}.png")
        im = Image.open(fp)
        return im

    def create_weather_image(self, image, timeserie):
        _LOGGER.debug("Creating weather image.")

        imagevalues = self.timeserie_imagevalues(timeserie)
        newimage = Image.new(
            image.mode, size=(image.size[0], image.size[1] + 250), color=(255, 255, 255)
        )
        newimage.paste(image, (0, 20), image)

        draw = ImageDraw.Draw(newimage)
        textcolor = (0, 0, 0)
        font = ImageFont.truetype(CONST_FILE_FONT, 25)

        time = datetime.strptime(timeserie.get("time"), API_STRINGTIME)
        time = time.strftime("%H:%M")
        draw.text(xy=(30, 0), text=time, fill=textcolor, font=font)

        height = 250
        for attr, val in imagevalues.items():
            text = f"{val} {self.get_unit(attr, True)}"
            draw.text(xy=(30, height), text=text, fill=textcolor, font=font)
            height += 27
        return newimage

    def timeserie_imagevalues(self, timeserie):
        result = {}
        for attr in CONST_IMAGEVALUES:
            if attr == CONST_WIND_DIR_BEARING:
                bearing = self.timeserie_values(timeserie, attr)
                result[
                    CONST_WIND_DIR_CARDINAL
                ] = f"{get_compass(bearing)} ({round(bearing)})"
            elif attr in CONST_WIND:
                result[attr] = round(self.timeserie_values(timeserie, attr))
            else:
                result[attr] = self.timeserie_values(timeserie, attr)

        return result

    def timeserie_values(self, timeserie, attr):
        res = timeserie.get("data").get("instant").get("details").get(attr, None)
        if res is None:
            res = (
                timeserie.get("data").get("next_1_hours").get("details").get(attr, None)
            )
            if res is None:
                res = "N/A"
        return res

    def get_config(self):
        try:
            return {
                "expires": self.expires.strftime(API_STRINGTIME),
                "last_modified": self.last_modified.strftime(API_STRINGTIME),
            }
        except (AttributeError, TypeError, ValueError) as e:
            _LOGGER.debug(f"Unable to get dateformat from config. {e}")

    def set_config(self, config):
        try:
            self.expires = datetime.strptime(config.get("expires"), API_STRINGTIME)
            self.last_modified = datetime.strptime(
                config.get("last_modified", None), API_STRINGTIME
            )
        except (AttributeError, TypeError, ValueError) as e:
            _LOGGER.debug(f"Unable to set dateformat from config file. {e}")


def parse_http_date(text):
    try:
        # return dt.datetime(*eut.parsedate(text)[:6])
        return eut.parsedate_to_datetime(text)
    except Exception as e:
        _LOGGER.error(f"Error parsing http date: {e}")


def image_margin(pil_img, top=0, right=0, bottom=0, left=0, color=(255, 255, 255)):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result


def image_combine_right(im1, im2):
    result = Image.new(
        im1.mode, size=(im1.size[0] + im2.size[0], im1.size[1]), color=(255, 255, 255)
    )
    result.paste(im1, (0, 0))
    result.paste(im2, (im1.size[0], 0))
    return result


def imagelist_combine(images):
    newimage = None
    previmage = None
    for image in images:
        if previmage is not None:
            newimage = image_combine_right(newimage, image)
        else:
            newimage = image
        previmage = image
    return newimage


def get_compass(bearing):
    if bearing is not None:
        dirs = [
            "N",
            "NNE",
            "NE",
            "ENE",
            "E",
            "ESE",
            "SE",
            "SSE",
            "S",
            "SSW",
            "SW",
            "WSW",
            "W",
            "WNW",
            "NW",
            "NNW",
        ]
        ix = round(bearing / (360.0 / len(dirs)))
        return dirs[ix % len(dirs)]
    return None
