from api import NorwegianWeatherApiClient
import testplot
import aiohttp
import asyncio
import logging
import json
import os, sys

CONST_APPNAME = "yr"
CONST_DIR_TEMP = "tmp"
CONST_RAWFILE = os.path.join(CONST_DIR_TEMP, "rawdata.json")
CONST_SETUPFILE = os.path.join(CONST_DIR_TEMP, "setup.json")
CONST_LOGFILE = os.path.join(CONST_DIR_TEMP, CONST_APPNAME + ".log")

_LOGGER = logging.getLogger(CONST_APPNAME)


class YrController:
    def __init__(self, latitude, longitude, place=None) -> None:

        """Sample API Client."""
        self.config = {}
        self.lat = latitude
        self.lon = longitude
        self.place = place
        self.session = aiohttp.ClientSession = aiohttp.ClientSession()
        self.api = NorwegianWeatherApiClient(
            latitude=self.lat,
            longitude=self.lon,
            place=self.place,
            session=self.session,
        )
        self.readconfig()

    def get_config(self):
        return self.api.get_config()

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
        self.api.set_config(self.config)

    def writeconfig(self):
        _LOGGER.debug("Writing config and rawdata to files.")
        self.writejson(CONST_RAWFILE, self.api.yrdata)
        self.writejson(CONST_SETUPFILE, self.api.get_config())

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


async def main():
    logging.basicConfig(
        filename=CONST_LOGFILE,
        filemode="w",
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(name)-20s  %(message)s",
        datefmt="%Y-%m-%d %H:%M",
    )

    lat = 59.1511  # max 4 decimals ref yr terms
    lon = 5.2252  # max 4 decimals ref yr terms
    place = "Syrevågen"

    controller = YrController(latitude=lat, longitude=lon, place=place)
    data = await controller.async_update()

    plotdata = controller.api.test4plot()
    testplot.weatherplot(plotdata)

    controller.writeconfig()
    await controller.session.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
