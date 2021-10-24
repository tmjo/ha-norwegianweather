# Norwegian Weather
[![Buy Me A Coffee](https://img.shields.io/badge/support-buymeacoffee-222222.svg?style=flat-square)](https://www.buymeacoffee.com/tmjo)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) ![Maintenance](https://img.shields.io/maintenance/yes/2021.svg)

{% if pending_update %}
## New version is available
{% endif %}
{% if prerelease %}
### NB!: This is a Beta version!
{% endif %}

This is a Home Assistant custom integration for Norwegian Weather which is interfacing an open API by the [MET Norway (The Norwegian Meteorological Institute)](https://met.no/en/), more precisely [api.met.no](https://api.met.no/).  **All data from MET Norway**. The service also provides data for geographical locations outside of Norway.

What makes this integration different from most weather integrations in HA is that it provides much more detailed data and is meant to be used with graph cards to give weather nerds something to play with. It also provides a camera entity which serves a forecast picture that can be displayed in UI or sent as a notification to mobile phone and similar.

## Configuration
Configuration is done through UI/Lovelace. In Home Assistant, click on Configuration > Integrations where you add it with the + icon.

You will be asked to give your location a name and to provide latitude and longitude as geographical position for the location you want to track. Finally select which sensors you would like the integration to add. More detailed description of this will be added.

Entities can be added and removed by clicking *Options* in HA integreation view at any time. It is also possible to enable more than one location by adding the integration several times.

## Usage
Use the integration as you please, but I strongly recommend to take a look at the [Apexchart-card](https://github.com/RomRider/apexcharts-card) by Romrider - it is an excellent graph card for lovelace which also enables the possibility to show future values. This is necessary to display forecast values which are stored as attributes in the main sensor.

If you are curious about specific details and definitions, please see [api.met.no](https://api.met.no/).

## Issues and development
Please report issues on github. If you would like to contribute to development, please do so through PRs.

For further information, see [README](https://github.com/tmjo/ha-norwegianweather)