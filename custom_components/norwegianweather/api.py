from datetime import datetime, timedelta, timezone
import pytz
import datetime as dt
import logging
import asyncio
import socket
from typing import List, Optional, Union
import aiohttp
import async_timeout
import xml.etree.ElementTree as ET
import re
import argparse
import json
import io

from decimal import Decimal
import email.utils as eut

# image stuff
import os, sys
from PIL import Image, TarIO, ImageDraw, ImageFont

# matplotstuff
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

API_NAME = "norwegianweather"
API_ATTRIBUTION = "Data from MET Norway (www.met.no)"
VERSION = "0.1.0"
API_USER_AGENT = f"{API_NAME}/{VERSION} https://github.com/tmjo/ha-norwegianweather"
API_STRINGTIME = "%Y-%m-%dT%H:%M:%S%z"
API_LANG = "nb"
TIMEOUT = 20

DEFAULT_TIME_ZONE: dt.tzinfo = pytz.timezone("Europe/Oslo")

# Directories
CONST_DIR_THIS = os.path.split(__file__)[0]
CONST_DIR_WEATHERICONS = os.path.join(CONST_DIR_THIS, "weathericon")
CONST_DIR_FONTS = os.path.join(CONST_DIR_THIS, "fonts")
CONST_DIR_DEFAULT = os.path.join(CONST_DIR_THIS, "tmp")

# Filepaths
CONST_FILE_WEATHERICONS = os.path.join(CONST_DIR_WEATHERICONS, "weathericon.tar")
CONST_FILE_FONT = os.path.join(CONST_DIR_FONTS, "NotoSans-Regular.ttf")
CONST_FILE_FONT_PIL = os.path.join(CONST_DIR_FONTS, "NotoSans-25.pil")


_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}

CONST_DISPLAY_UNITS = {
    "celsius": "°C",
    "degrees": "°",
    "1": "",
}

CONST_WEATHERDATA = {
    "air_pressure_at_sea_level": "Barometer",
    "air_temperature": "Temperature",
    "air_temperature_max": "Max",
    "air_temperature_min": "Min",
    "cloud_area_fraction": "Clouds",
    "cloud_area_fraction_high": "Clouds high",
    "cloud_area_fraction_low": "Clouds low",
    "cloud_area_fraction_medium": "Clouds medium",
    "dew_point_temperature": "Dew point",
    "fog_area_fraction": "Fog",
    "precipitation_amount": "Rain",
    "precipitation_amount_max": "Max",
    "precipitation_amount_min": "Min",
    "probability_of_precipitation": "Probability rain",
    "probability_of_thunder": "Probability thunder",
    "relative_humidity": "Humidity",
    "ultraviolet_index_clear_sky": "UV index",
    "wind_from_direction": "Wind direction",
    "wind_speed": "Wind speed",
    "wind_speed_of_gust": "Wind gusts",
    # CUSTOM
    "time": "Time",
    "date": "Date",
    "symbol_code": "Image",
    "wind_speed_bf_desc": "Beaufort",
    "wind_speed_bf": "Beaufort",
    "wind_speed_knot": " Wind speed knot",
    "wind_from_direction_cardinal": "Wind direction",
}

CONST_IMAGEVALUES = [
    "air_temperature",
    "precipitation_amount",
    "probability_of_precipitation",
    "wind_from_direction",
    "wind_from_direction_cardinal",
    "symbol_code",
    "wind_speed_bf_desc",
    "wind_speed_bf",
    "wind_speed",
    "wind_speed_of_gust",
    "air_pressure_at_sea_level",
    "relative_humidity",
]

CONST_INTERVAL_INST = "instant"
CONST_INTERVAL_1H = "next_1_hours"
CONST_INTERVAL_6H = "next_6_hours"
CONST_INTERVAL_12H = "next_12_hours"

CONST_INTERVALS = [
    CONST_INTERVAL_INST,
    CONST_INTERVAL_1H,
    CONST_INTERVAL_6H,
    CONST_INTERVAL_12H,
]


class NorwegianWeatherApiClient:
    def __init__(
        self,
        place,
        latitude,
        longitude,
        session: aiohttp.ClientSession,
        altitude=0,
        output_dir=CONST_DIR_DEFAULT,
    ) -> None:

        """Sample API Client."""
        self._session = session
        self.location = Location(place, latitude, longitude, altitude)
        self.yrdata = None
        self.data = None
        self.current = None
        self.expires = None
        self.last_modified = None
        self.output_dir = output_dir
        self.file_image = API_NAME + "_" + self.location.name + "_img.png"
        self.file_plot = API_NAME + "_" + self.location.name + "_plot.png"

    def get_url(
        self,
        datatype="complete",
        latitude=None,
        longitude=None,
        altitude=None,
    ):
        if latitude is None:
            latitude = self.location.latitude
        if longitude is None:
            longitude = self.location.longitude
        if altitude is None:
            altitude = self.location.altitude

        url = f"https://api.met.no/weatherapi/locationforecast/2.0/{datatype}?lat={latitude}&lon={longitude}&altitude={altitude}"
        return url

    async def async_get_data(self) -> dict:
        """Get data from the API."""

        if self.expires is None or datetime.now(timezone.utc) > self.expires:
            _LOGGER.debug(
                f"Calling API to fetch new data (expired: {self.expires} now: {datetime.now(timezone.utc)})"
            )
            headers = {"User-Agent": API_USER_AGENT}
            self.yrdata = await self.api_wrapper("get", self.get_url(), headers)
        else:
            _LOGGER.debug(
                f"Data still valid, skipping call to API (expires: {self.expires} now: {datetime.now(timezone.utc)})."
            )

        if self.yrdata is not None:
            self.process_data()
            return self.data
        return None

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

        except asyncio.TimeoutError as e:
            _LOGGER.error(f"Timeout error fetching information from API")
            _LOGGER.debug(f"Timeout {url} - {e}")
        except (KeyError, TypeError) as e:
            _LOGGER.error(f"Error parsing information from API")
            _LOGGER.debug(f"Timeout {url} - {e}")
        except (aiohttp.ClientError, socket.gaierror) as e:
            _LOGGER.error(f"Error fetching information from API")
            _LOGGER.debug(f"Timeout {url} - {e}")
        except Exception as e:  # pylint: disable=broad-except
            _LOGGER.error(f"Something really wrong happend!")
            _LOGGER.debug(f"Timeout {url} - {e}")

    def process_data(self, maxserie=10):
        _LOGGER.debug("Processing data.")
        if self.yrdata is not None:
            # Add yrdata
            props = self.yrdata.get("properties", None)
            if props is not None:
                self.location.met_units = props.get("meta").get("units")
                for key, unit in self.location.met_units.items():
                    self.location.units[key] = CONST_DISPLAY_UNITS.get(unit, unit)
                _LOGGER.debug(f"Processing data - {len(self.location.units)} units.")
                timeseries = props.get("timeseries", None)
                if timeseries is not None:
                    _LOGGER.debug(f"Processing data - {len(timeseries)} timeseries.")
                    self.location.time_series = []
                    for serie in timeseries:
                        self.location.time_series.append(
                            Timeserie(
                                self.location, serie.get("time"), serie.get("data")
                            )
                        )
            # Internal tweaks
            self.data = {}
            intervals = []
            i = 0
            for serie in self.location.time_series:
                if i >= maxserie:
                    break
                i += 1
                intervals.append(serie.get_intervals_hourly_data())

            try:
                self.process_weather_image(intervals)
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.warning(f"Error processing weather image: {e}")

            try:
                self.process_weather_plot(intervals)
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.warning(f"Error processing weather plot: {e}")

            self.current = self.location.get_timeserie_time_hourlydata(dt_now())

            self.data["timeseries"] = intervals
            self.data["latitude"] = self.location.latitude
            self.data["longitude"] = self.location.longitude
            self.data["place"] = self.location.name
            for data in CONST_WEATHERDATA:
                self.data[data] = self.current.get(data, None)

    def process_weather_image(self, weatherdata, filename=None, qty=6):
        images = []
        if weatherdata is not None:
            _LOGGER.debug(
                f"Processing weather image from {len(weatherdata)} time intervals - creating {qty} images."
            )
            cnt = 0
            font = image_font()
            for data in weatherdata:
                time = data.get("time", None)
                imagedata = image_create_process_data(time, data, self.location.units)

                if cnt == 0:
                    # Create image legend by tweaking content
                    legenddata = {}
                    for k in imagedata:
                        legenddata[k] = CONST_WEATHERDATA.get(k, k)
                    legenddata["time"] = imagedata["date"] + "\n" + self.location.name
                    legenddata["symbol_code"] = None
                    imagelegend = image_create(legenddata, font)
                    images.append(imagelegend)
                elif cnt >= qty:
                    break
                cnt += 1

                image = image_create(imagedata, font)
                images.append(image)
                _LOGGER.debug(
                    f"Processing image for interval {time} - size: {image.size}"
                )
            font = None
        else:
            _LOGGER.debug("Could not find any intervals for image processing.")

        _LOGGER.debug(f"Processing image - combining {len(images)} images.")
        newimage = image_list_combine(images)

        if filename is None:
            filename = os.path.join(self.output_dir, self.file_image)

        _LOGGER.debug(f"Saving image {filename}.")
        newimage.save(filename, "png")
        newimage.close()
        images = None

    def process_weather_plot(self, weatherdata, filename=None):
        if filename is None:
            filename = os.path.join(self.output_dir, self.file_plot)
        _LOGGER.debug(f"Saving plot {filename}.")
        plot_weatherdata(
            weatherdata, show=False, filename=filename, location_name=self.location.name
        )


class Location:
    def __init__(self, name: str, latitude: float, longitude: float, altitude: int = 0):
        self.name = name
        self.latitude = round(latitude, 4)
        self.longitude = round(longitude, 4)
        self.altitude = round(altitude, 0)
        self.met_units = {}
        self.units = {}
        self.time_series = []

    def coordinates(self):
        return (self.latitude, self.longitude)

    def get_timeserie_time(self, time: dt.datetime):
        for i in range(len(self.time_series)):
            if time > self.time_series[i].time and time < self.time_series[i + 1].time:
                return self.time_series[i]
        return None

    def get_timeserie_time_hourlydata(self, time: dt.datetime):
        interval = self.get_timeserie_time(time)
        if interval is not None:
            return interval.get_intervals_hourly_data()
        return None


class Timeserie:
    def __init__(self, location, time: dt.datetime, data):
        self.location = location
        self.time = dt_parse_datetime(time)
        self.data = data
        self.intervals = [
            Interval(self, interval, data) for interval in CONST_INTERVALS
        ]

    def __str__(self):
        astr = f"Time: {self.time} with {len(self.intervals)} intervals"
        for i in self.intervals:
            astr += f" {i} "
        return astr

    def get_interval(self, intervaltype):
        for interval in self.intervals:
            if interval.intervaltype == intervaltype:
                return interval
        return None

    def get_intervals(self, intervaltypes: list):
        intervals = []
        for intervaltype in intervaltypes:
            interval = self.get_interval(intervaltype)
            if interval is not None:
                intervals.append(interval)
        return intervals

    def get_intervals_hourly(self):
        return self.get_intervals([CONST_INTERVAL_INST, CONST_INTERVAL_1H])

    def get_interval_data(self, intervaltype, data="all"):
        interval = self.get_interval(intervaltype)
        if interval is not None:
            return interval.get_data(data)
        return None

    def get_intervals_data(self, intervaltypes: list, data="all"):
        intervalsdata = {}
        intervals = self.get_intervals(intervaltypes)
        for interval in intervals:
            intervaldata = interval.get_data(data)
            if intervaldata is not None:
                intervalsdata = {
                    **intervalsdata,
                    **intervaldata,
                }
        if intervalsdata:
            return intervalsdata
        else:
            return None

    def get_intervals_hourly_data(self, data="all"):
        return self.get_intervals_data([CONST_INTERVAL_INST, CONST_INTERVAL_1H], data)


class Interval:
    def __init__(self, timeserie, type, data):
        self.timeserie: Timeserie = timeserie
        self.intervaltype = type
        self.data = self.parse_interval_data(type, data)
        self.data = self.add_calculated_data(self.data)

    def parse_interval_data(self, interval, data):
        intervaldata = data.get(interval, None)
        if intervaldata is not None:
            details = intervaldata.get("details", None)
            summary = intervaldata.get("summary", None)
            if details is not None and summary is not None:
                return {**details, **summary}
            elif details is not None:
                return details
            elif summary is not None:
                return summary
        return None

    def add_calculated_data(self, data):
        if data is not None:
            calc = {}
            if "wind_speed" in data.keys():
                wind_speed_ms = data.get("wind_speed")
                bf = get_wind_ms_beaufort(wind_speed_ms)
                calc["wind_speed_bf"] = bf
                calc["wind_speed_bf_desc"] = CONST_BEAUFORT_EN[bf]
                calc["wind_speed_knot"] = get_wind_ms_to_knot(wind_speed_ms)
            if "wind_from_direction" in data.keys():
                wind_dir = data.get("wind_from_direction")
                calc["wind_from_direction_cardinal"] = get_compass(wind_dir)
            return {**data, **calc}
        return None

    def __str__(self):
        if self.data is not None:
            return f"{self.intervaltype} ({len(self.data)} items)"
        else:
            return f"{self.intervaltype} (0 items)"

    def get_data(self, data="all"):
        default = {
            "time": self.timeserie.time,
        }
        found_data = {}
        if data == "all":
            found_data = {**self.data}
        elif self.data is not None:
            if isinstance(data, str):
                found_data = {data: self.data.get(data, None)}
            elif isinstance(data, list):
                for datareq in data:
                    d = self.data.get(datareq, None)
                    if d is not None:
                        found_data[datareq] = d

        return {**default, **found_data}

    def show_data(self, data="all"):
        found_data = self.get_data(data)
        if found_data is not None:
            for k, val in found_data.items():
                print(
                    f"{CONST_WEATHERDATA.get(k)}: {val}{self.timeserie.location.units.get(k)} ",
                    end=" ",
                )


CONST_DIR_TEMP = "tmp"
CONST_RAWFILE = os.path.join(CONST_DIR_TEMP, "rawdata.json")
CONST_SETUPFILE = os.path.join(CONST_DIR_TEMP, "setup.json")
CONST_LOGFILE = os.path.join(CONST_DIR_TEMP, API_NAME + ".log")

_LOGGER = logging.getLogger(API_NAME)


class MetController:
    def __init__(self, latitude, longitude, session, place=None) -> None:

        """Sample API Client."""
        self.config = {}
        self.lat = latitude
        self.lon = longitude
        self.place = place
        self.api = NorwegianWeatherApiClient(
            latitude=self.lat,
            longitude=self.lon,
            place=self.place,
            session=session,
        )
        self.readconfig()

    # def get_config(self):
    #     return self.api.get_config()

    def get_config(self):
        try:
            return {
                "expires": self.api.expires.strftime(API_STRINGTIME),
                "last_modified": self.api.last_modified.strftime(API_STRINGTIME),
            }
        except (AttributeError, TypeError, ValueError) as e:
            _LOGGER.debug(f"Unable to get dateformat from config. {e}")

    def set_config(self, config):
        try:
            self.api.expires = datetime.strptime(config.get("expires"), API_STRINGTIME)
            self.api.last_modified = datetime.strptime(
                config.get("last_modified", None), API_STRINGTIME
            )
        except (AttributeError, TypeError, ValueError) as e:
            _LOGGER.debug(f"Unable to set dateformat from config file. {e}")

    def readconfig(self):
        _LOGGER.debug("Reading config and rawdata from files.")
        try:
            self.api.yrdata = self.readjson(CONST_RAWFILE)
            self.config = self.readjson(CONST_SETUPFILE)
        except FileNotFoundError as e:
            _LOGGER.debug(
                f"Did not find rawdata or config file, new ones will be created. {e}"
            )
            self.writejson(CONST_RAWFILE, {})
            self.writejson(CONST_SETUPFILE, {})
        # self.api.set_config(self.config)
        self.set_config(self.config)

    def writeconfig(self):
        _LOGGER.debug("Writing config and rawdata to files.")
        self.writejson(CONST_RAWFILE, self.api.yrdata)
        # self.writejson(CONST_SETUPFILE, self.api.get_config())
        self.writejson(CONST_SETUPFILE, self.get_config())

    def readjson(self, rawfile):
        # JSON LOAD FROM FILE
        with open(rawfile, "r") as file:
            return json.load(file)

    def writejson(self, rawfile, datadict):
        # JSON DUMP TO FILE
        with open(rawfile, "w") as jsonfile:
            json.dump(datadict, jsonfile)

    async def async_update(self):
        data = await self.api.async_get_data()
        self.writeconfig()
        return data


def parse_arguments():
    """Argument parser for running API separately."""
    parser = argparse.ArgumentParser(description=f"{API_NAME}: {API_ATTRIBUTION}")
    parser.add_argument(
        "-lat", "--latitude", help="Latitude", required=True, type=float
    )
    parser.add_argument(
        "-lon", "--longitude", help="Longitude", required=True, type=float
    )
    parser.add_argument("-p", "--place", help="Place name", required=False, type=str)
    parser.add_argument(
        "-s", "--show", help="Show plot", required=False, action="store_true"
    )
    parser.add_argument(
        "-l", "--loop", help="Loop every 10 seconds", action="store_true"
    )
    args = parser.parse_args()
    return args


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


def image_list_combine(images):
    newimage = None
    previmage = None
    for image in images:
        if previmage is not None:
            newimage = image_combine_right(newimage, image)
        else:
            newimage = image
        previmage = image
    return newimage


def image_create_process_data(time, data, units, datafilter=CONST_IMAGEVALUES):
    _LOGGER.debug("Processing data for image creation.")
    imagedata = {}

    # time = datetime.strptime(time, API_STRINGTIME)
    time = time.astimezone(DEFAULT_TIME_ZONE)
    imagedata["time"] = time.strftime("%H:%M")
    imagedata["date"] = time.strftime("%d.%m.%Y")

    # All data in filter
    for key in datafilter:
        unit = units.get(key, None)
        if unit is not None:
            imagedata[key] = f"{data.get(key, 'N/A')} {unit}"
        else:
            imagedata[key] = f"{data.get(key, 'N/A')}"

    # Special treatment
    if "wind_speed" in imagedata.keys() and "wind_speed_of_gust" in imagedata.keys():
        imagedata.pop("wind_speed_of_gust")
        windspeed = data.get("wind_speed")
        gusts = data.get("wind_speed_of_gust")
        unit = units.get("wind_speed", "")
        imagedata["wind_speed"] = f"{windspeed} ({gusts}) {unit}"
    if "wind_from_direction_cardinal" in imagedata.keys():
        imagedata.pop("wind_from_direction")
    if "wind_speed_bf_desc" in imagedata.keys():
        bf = imagedata.pop("wind_speed_bf")
        bf_desc = imagedata.get("wind_speed_bf_desc")
        imagedata["wind_speed_bf_desc"] = f"{bf_desc} {bf}"

    return imagedata


def image_create(imagedata, font):
    _LOGGER.debug("Creating weather image.")
    weathersymbol = get_weather_symbol(imagedata.get("symbol_code"))

    newwidth = weathersymbol.size[0] + 25
    newheight = weathersymbol.size[1] + 0 + len(imagedata) * 30
    newimage = Image.new(
        weathersymbol.mode,
        size=(newwidth, newheight),
        color=(255, 255, 255),
    )
    newimage.paste(weathersymbol, (0, 20), weathersymbol)

    draw = ImageDraw.Draw(newimage)
    textcolor = (0, 0, 0)

    draw.text(xy=(30, 0), text=imagedata.get("time"), fill=textcolor, font=font)
    dropdata = ["time", "date", "symbol_code"]

    height = 250
    for key, val in imagedata.items():
        if key not in dropdata:
            draw.text(xy=(30, height), text=val, fill=textcolor, font=font)
            height += 27
    draw = None
    return newimage


def image_font():
    font = None
    try:
        font = ImageFont.truetype(CONST_FILE_FONT, 25)
        _LOGGER.debug(f"Loaded font {CONST_FILE_FONT} {font}.")
    except (TypeError, FileNotFoundError, OSError) as e:
        _LOGGER.debug(f"Could not apply truetype font {CONST_FILE_FONT} ({e}).")

    if font is None:
        try:
            font = ImageFont.load(CONST_FILE_FONT_PIL)
            _LOGGER.debug(f"Loaded PIL-font {CONST_FILE_FONT_PIL}.")
        except (TypeError, FileNotFoundError, OSError, AttributeError) as e:
            _LOGGER.debug(
                f"Could not apply PIL-font {CONST_FILE_FONT_PIL}. Will have to use ugly default font, sorry. ({e})"
            )
    return font


def plot_weatherdata(data, filename=None, show=False, location_name="LOCATION"):
    _LOGGER.debug("Creating plot")
    x = []
    y1 = []
    y2 = []
    y3 = []
    for d in data:
        # x.append(dt_parse_datetime(d.get("time")))
        x.append(d.get("time"))
        y1.append(float(d.get("wind_speed", 0.0)))
        y2.append(float(d.get("wind_from_direction", 0.0)))
        y3.append(float(d.get("wind_speed_of_gust", 0.0)))

    # Min/max/now
    ymin = min(y1 + y2 + y3)
    ymax = max(y1 + y2 + y3)
    now = dt_now()

    # Plot the data
    fig, ax = plt.subplots(1)
    fig.subplots_adjust(right=0.75)
    twin1 = ax.twinx()
    twin2 = ax.twinx()
    ax.set_ylim(0, 63)
    twin1.set_ylim(0, 360)
    twin2.set_ylim()

    twin2.spines["right"].set_position(("axes", 1.2))
    ax.plot(x, y1, label="Wind speed", color="green", linewidth=3)
    twin1.plot(x, y2, label="Wind direction", color="darkorange", linewidth=3)
    ax.plot(x, y3, label="Wind gusts", color="blue", linewidth=3)
    # plt.axvline(x=now, color="red", linestyle="dashed", linewidth=1)
    # plt.text(
    #     now,
    #     -5,
    #     f" Now ",
    #     color="red",
    #     fontsize=8,
    # )

    # self.plot_add_highlow(plt, self.highlow, color="darkorange", fontsize=8)

    # Formatting
    plt.gcf().autofmt_xdate()
    xfmt = mdates.DateFormatter("%H:%M", tz=now.tzinfo)  # %d-%m-%y %H:%M
    xloc = mdates.MinuteLocator(interval=30)
    ax.xaxis.set_major_formatter(xfmt)
    ax.xaxis.set_major_locator(xloc)
    ax.set(
        title=f"Weather for {location_name}",
        ylabel="Variables",
    )
    plt.xticks(rotation=90, ha="center")

    # Custom scaling
    # ylim_min = ymin if ymin < -10 else -10
    # ylim_max = ymax if ymax > 140 else 140
    # ax.set_ylim([ylim_min, ylim_max])

    # Add a legend
    # plt.legend(bbox_to_anchor=(1, 1), loc="upper left")
    plt.legend()

    # Save image
    if filename is None:
        filename = os.path.join(CONST_DIR_DEFAULT, API_NAME + "_plot.png")
        _LOGGER.debug(f"Saving image {filename}.")
    plt.savefig(filename)

    # Show
    if show:
        plt.show()
    plt.close()


# def plot_add_highlow(plt, highlow=None, color="darkorange", fontsize=8):
#     if highlow is None:
#         highlow = self.highlow

#     for data in highlow:
#         t = data.get("time")
#         v = data.get("value")
#         f = data.get("flag")
#         if f == "high":
#             addpos = 5
#         else:
#             addpos = 20

#         plt.text(
#             t,
#             float(v) + addpos,
#             f"{dt_strftime(t, '%H:%M')}\n{v}cm",
#             color=color,
#             ha="center",
#             rotation=90,
#             fontsize=fontsize,
#         )


def get_weather_symbol(weatherstr=None):
    if weatherstr is not None:
        _LOGGER.debug(f"Trying to open tar archive looking for '{weatherstr}'")
        try:
            # The weather icons are licensed under the MIT License (MIT). Copyright (c) 2015-2017 Yr.no.
            fp = TarIO.TarIO(CONST_FILE_WEATHERICONS, f"png/{weatherstr}.png")
            im = Image.open(fp)
            return im
        except OSError as e:
            _LOGGER.error(
                f"Could not find file in tar archive ('{weatherstr}'), trying to return default image.\n {e}"
            )
            _LOGGER.debug(f"Filepath: {CONST_FILE_WEATHERICONS}")
    default_im = Image.new("RGBA", size=(200, 200), color=(255, 255, 255))
    return default_im


def get_wind_ms_to_knot(speed_ms, decimal=1):
    # 1 knot = 1.852 kmh (nautical mile)
    speed_knot = round(speed_ms * 60 * 60 / 1852, decimal)
    return speed_knot


def get_wind_knot_to_ms(speed_knot, decimal=1):
    # 1 knot = 1.852 kmh (nautical mile)
    speed_ms = round(speed_knot * 1852 / 60 / 60, decimal)
    return speed_ms


def get_wind_knot_beaufort(speed_knot):
    return get_wind_ms_beaufort(get_wind_knot_to_ms(speed_knot))


def get_wind_ms_beaufort(speed_ms):
    speed_ms = round(speed_ms, 1)
    bf = None
    if speed_ms is not None:
        if speed_ms <= 0.2:
            bf = 0
        elif speed_ms >= 0.3 and speed_ms <= 1.5:
            bf = 1
        elif speed_ms >= 1.6 and speed_ms <= 3.3:
            bf = 2
        elif speed_ms >= 3.4 and speed_ms <= 5.4:
            bf = 3
        elif speed_ms >= 5.5 and speed_ms <= 7.9:
            bf = 4
        elif speed_ms >= 8.0 and speed_ms <= 10.7:
            bf = 5
        elif speed_ms >= 10.8 and speed_ms <= 13.8:
            bf = 6
        elif speed_ms >= 13.9 and speed_ms <= 17.1:
            bf = 7
        elif speed_ms >= 17.2 and speed_ms <= 20.7:
            bf = 8
        elif speed_ms >= 20.8 and speed_ms <= 24.4:
            bf = 9
        elif speed_ms >= 24.5 and speed_ms <= 28.4:
            bf = 10
        elif speed_ms >= 28.5 and speed_ms <= 32.6:
            bf = 11
        elif speed_ms >= 32.7:
            bf = 12
    return bf


CONST_BEAUFORT_NO = {
    0: "Stille",
    1: "Flau vind",
    2: "Svak vind",
    3: "Lett bris",
    4: "Laber bris",
    5: "Frisk bris",
    6: "Liten kuling",
    7: "Stiv kuling",
    8: "Sterk kuling",
    9: "Liten storm",
    10: "Full storm",
    11: "Sterk storm",
    12: "Orkan",
}

CONST_BEAUFORT_EN = {
    0: "Calm",
    1: "Light air",
    2: "Light breeze",
    3: "Gentle breeze",
    4: "Mod. breeze",
    5: "Fresh breeze",
    6: "Strong breeze",
    7: "Near gale",
    8: "Gale",
    9: "Strong gale",
    10: "Storm",
    11: "Violent storm",
    12: "Hurricane",
}


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


def parse_http_date(text):
    try:
        # return dt.datetime(*eut.parsedate(text)[:6])
        return eut.parsedate_to_datetime(text)
    except Exception as e:
        _LOGGER.error(f"Error parsing http date: {e}")


def dt_parse_datetime(dt_str: str) -> Optional[dt.datetime]:
    """Parse string into datetime with API dateformat."""
    try:
        return dt.datetime.strptime(dt_str, API_STRINGTIME).replace(tzinfo=timezone.utc)
    except (ValueError, IndexError) as e:
        _LOGGER.debug(f"{dt_str} - PARSE ERROR: {e}")


def dt_strftime(dt_dt: dt.datetime, format=API_STRINGTIME) -> Optional[str]:
    """Parse datetime into string with API dateformat and timezone."""
    try:
        return dt_dt.astimezone(DEFAULT_TIME_ZONE).strftime(format)
    except ValueError as e:
        _LOGGER.debug(f"{dt_dt} - PARSE ERROR: {e}")


def dt_now(time_zone: Optional[dt.tzinfo] = None) -> dt.datetime:
    """Get now in specified time zone."""
    return dt.datetime.now(time_zone or DEFAULT_TIME_ZONE)


async def main():
    """Main function when runing API separately."""
    args = parse_arguments()
    _LOGGER.debug("args: %s", args)
    session = aiohttp.ClientSession()
    controller = MetController(
        latitude=args.latitude,
        longitude=args.longitude,
        place=args.place,
        session=session,
    )
    # data = await controller.async_update()
    if args.loop:
        while True:
            data = await controller.async_update()
            # print(data)
            print(f"Memory usage: {memory_usage_psutil()}")
            print(f"Figures: {[plt.figure(i) for i in plt.get_fignums()]}")
            await asyncio.sleep(10)
    else:
        data = await controller.async_update()

    print(data)

    # print("*********** UNITS *****************")
    # for unit in controller.api.location.units:
    #     print(unit)

    # intervals = []
    # i = 0
    # for serie in controller.api.location.time_series:
    #     if i >= 10:
    #         break
    #     i += 1
    #     intervals.append(serie.get_intervals_hourly_data())
    # for interval in intervals:
    #     print(f"{interval}\n")
    # controller.api.process_weather_image(intervals)
    # controller.api.process_weather_plot(intervals)

    # current_weather = controller.api.location.get_timeserie_time_hourlydata(dt_now())
    # print(current_weather)

    controller.writeconfig()
    await session.close()


def memory_usage_psutil():
    # return the memory usage in MB
    import psutil

    process = psutil.Process()
    mem = process.memory_info()[0] / float(2 ** 20)
    return mem


if __name__ == "__main__":
    import sys

    _LOGGER: logging.Logger = logging.getLogger(__file__)
    _LOGGER.setLevel(logging.DEBUG)
    fh = logging.StreamHandler()
    fh_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s"
    )
    fh.setFormatter(fh_formatter)
    _LOGGER.addHandler(fh)
    # asyncio.run(main())
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt as e:  # noqa
        # Close connection on user interuption
        print("Interrupted by user")
    except Exception as e:
        print(e)
