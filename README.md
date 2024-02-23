# Norwegian Weather
[![Buy Me A Coffee][buymeacoffee-image]][buymeacoffee-url]
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) ![Maintenance](https://img.shields.io/maintenance/yes/2024.svg)

This is a Home Assistant custom integration for Norwegian Weather which is interfacing an open API by the [MET Norway (The Norwegian Meteorological Institute)](https://met.no/en/), more precisely [api.met.no](https://api.met.no/).  **All data from MET Norway**. The service also provides data for geographical locations outside of Norway.

What makes this integration different from most weather integrations in HA is that it provides much more detailed data and is meant to be used with graph cards to give weather nerds something to play with. It also provides a camera entity which serves a forecast picture that can be displayed in UI or sent as a notification to mobile phone and similar.

## Installation
There are different methods of installing the custom component. HACS is by far the simplest way for unexperienced users and is recomended.

### HACS installation
The installation is currently not included in HACS as a default repo, but can be installed through HACS *by adding this repo as a custom repository*.

1. Make sure you have [HACS](https://hacs.xyz/) installed in your Home Assistant environment.
2. Go to **HACS**, select **Integrations**.
3. Click on the three dots in the upper right corner and select **Custom repositories**
4. Copy/paste the **URL for this repo** `https://github.com/tmjo/ha-norwegianweather` into the URL-field, select **Integration as category** and then click **Add**.
5. You should now find the **Norwegian Weather** integration by searching for it in HACS, proceed to install it.
6. Restart Home Assistant (a warning should be shown in log saying you're using a custom integration).
7. Continue to the Configuration-section.


### Manual
1. Navigate to you home assistant configuration folder.
2. Create a `custom_components` folder of it does not already exist, then navigate into it.
3. Download the folder `norwegianweather` from this repo and add it into your custom_components folder.
4. Restart Home Assistant (a warning should be shown in log saying you're using a custom integration).
5. Continue to the Configuration-section.


### Git installation
1. Make sure you have git installed on your machine.
2. Navigate to you home assistant configuration folder.
3. Create a `custom_components` folder of it does not already exist, then navigate into it.
4. Execute the following command: `git clone https://github.com/tmjo/ha-norwegianweather ha-norwegianweather`
5. Run `bash links.sh`
6. Restart Home Assistant (a warning should be shown in log saying you're using a custom integration).
7. Continue to the Configuration-section.

## Configuration
Configuration is done through UI/Lovelace. In Home Assistant, click on Configuration > Integrations where you add it with the + icon.

You will be asked to give your location a name and to provide latitude and longitude as geographical position for the location you want to track. Finally select which sensors you would like the integration to add. More detailed description of this will be added.

Entities can be added and removed by clicking *Options* in HA integreation view at any time. It is also possible to enable more than one location by adding the integration several times.

## Usage
Use the integration as you please, but I strongly recommend to take a look at the [Apexchart-card](https://github.com/RomRider/apexcharts-card) by Romrider - it is an excellent graph card for lovelace which also enables the possibility to show future values. This is necessary to display forecast values which are stored as attributes in the main sensor.

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
