# Norwegian Weather

[![Buy Me A Coffee][buymeacoffee-image]][buymeacoffee-url]
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) ![Maintenance](https://img.shields.io/maintenance/yes/2025.svg)

This is a Home Assistant custom integration for Norwegian Weather which is interfacing an open API by the [MET Norway (The Norwegian Meteorological Institute)](https://met.no/en/), more precisely [api.met.no](https://api.met.no/).  **All data from MET Norway**. The service also provides data for geographical locations outside of Norway.

What makes this integration different from most weather integrations in HA is that it provides much more detailed data and is meant to be used with graph cards to give weather nerds something to play with. It also provides a camera entity which serves a forecast picture that can be displayed in UI or sent as a notification to mobile phone and similar.

## Installation
[HACS](https://hacs.xyz/) is by far the easiest way to install and stay updated for this custom integrationg. This is highly recommended. The installation is currently not included in HACS as a default repo, and must be installed through HACS *by adding this repo as a custom repository*:

1. Make sure you have [HACS](https://hacs.xyz/) installed in your Home Assistant environment.
2. Go to **HACS**, select **Integrations**.
3. Click on the three dots in the upper right corner and select **Custom repositories**
4. Copy/paste the **URL for this repo** `https://github.com/tmjo/ha-norwegianweather` into the URL-field, select **Integration as category** and then click **Add**.
5. You should now find the **Norwegian Weather** integration by searching for it in HACS, proceed to install it.
6. Restart Home Assistant (a warning should be shown in log saying you're using a custom integration).
7. Continue to the Configuration-section.

For manual installation wihtout using HACS you may either copy the `norwegian-weather` folder to your `custom_components` folder or you may install it with git. In these cases, no further details are provided as your are expected to know what you are doing. A restart of HA is required after making the changes.

## Configuration
After installation, your must configure the integration in HA. Configuration is done through UI/Lovelace. In Home Assistant, click on Settings > Devices & Services > Integrations where you add it with the + icon.

You will be asked to give your location a name and to provide latitude and longitude as geographical position for the location you want to track (your HA location is default). Finally select which sensors you would like the integration to add. There are a lot of detailed sensors, including a camera entity with an image created by Matplotlib. 

Entities can be added and removed by clicking *Options* in HA integration view at any time. It is also possible to enable more than one location by adding several devices.

## Usage
The integration entities can be added to the UI as they are and you can track the history as for all entities in Home Assistant.

Use the integration as you please, but I highly recommend to take a look at the [Apexchart-card](https://github.com/RomRider/apexcharts-card) by Romrider or [Plotly-card](https://github.com/dbuezas/lovelace-plotly-graph-card) by dbuezas - they are both excellent graph cards for lovelace which also enables the possibility to show future values. This is necessary to display prediction- and forecast values which are stored as attributes in the main sensor. Examples of how to configure the graphs are found here: [Apexchart example](lovelace/lovelace-apexchart.yaml) and [Plotly example](lovelace/lovelace-plotly.yaml).

Example:
![example](img/norwegianweather_example.png "example")

The camera entity can also be used for UI since it provides a nice plot using Matplotlib, but I personally prefer one of the graph cards since they provide more dynamics. The camera on the other hand can be handy if you would like to send notifications with an included forecast image/plot.

If you are curious about specific details and definitions, please see [api.met.no](https://api.met.no/).

## Issues and development
Please report issues on github. If you would like to contribute to development, please do so through PRs.

## License
MIT © [Tor Magne Johannessen][tmjo]. **All data from MET Norway**.

<!-- Badges -->
[hacs-url]: https://github.com/custom-components/hacs
[hacs-image]: https://img.shields.io/badge/HACS-Custom-orange.svg
[buymeacoffee-url]: https://www.buymeacoffee.com/tmjo
[buymeacoffee-image]: https://img.shields.io/badge/support-buymeacoffee-222222.svg?style=flat-square
[tmjo]: https://github.com/tmjo
