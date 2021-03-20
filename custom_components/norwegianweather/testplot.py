# importing the required module
import matplotlib.pyplot as plt

import logging
import json

_LOGGER: logging.Logger = logging.getLogger(__package__)


def weatherplot(data):
    # x axis values
    _LOGGER.debug(data)

    x = []
    y = []
    ylist = []

    dd = massage_yrdata(data)

    x = data.keys()
    for key, val in dd.items():
        if len(x) != len(val):
            val[len(x)] = 0
        plt.plot(x, val, label=key)

    # for key, val in data.items():
    # x.append(key)
    # y.append(val.get("wind_speed"))

    # x = [1, 2, 3]
    # y = [2, 4, 1]

    # plotting the points
    # plt.plot(x, y)

    # naming the x axis
    plt.xlabel("x - axis")
    # naming the y axis
    plt.ylabel("y - axis")

    # giving a title to my graph
    plt.title("Weather")

    # show a legend on the plot
    plt.legend()

    # function to show the plot
    plt.show()


def massage_yrdata(wd):
    dd = {}
    for time, data in wd.items():
        for key, value in data.items():
            if dd.get(key, None) is None:
                dd[key] = []
            dd[key].append(value)

    for key, value in dd.items():
        if len(wd.keys()) != len(value):
            add = len(wd.keys()) - len(value)
            for i in range(add):
                value.append(0)

    return dd
