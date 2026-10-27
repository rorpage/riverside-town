# Riverside Town

A Roku screensaver inspired by Roku City. It shows a small town beside a river with mountains behind it. The scenery scrolls in layers at different speeds (parallax), cars drive along the street, and a panel shows the time, the temperature, and the current weather.

## Features

- Five scenery layers that scroll at different speeds: clouds, far mountains, near mountains, hills with the river, and the town with the street.
- The town has two sections. The first has houses, a bakery, a book store, a hardware store, and a diner called Luke's. The second has a church, a gas station with a small market, and a public library.
- A car is parked at the gas station. The car and the direction it faces are chosen at random each time the screensaver starts.
- Each store sign uses its own font.
- Four cars: a sedan, a van, a Jeep, and an old truck. Each has its own speed, and the wheels spin at a rate that matches it.
- Two lanes. The near lane drives left to right at full size. The far lane drives right to left and draws the cars slightly smaller.
- Weather from [Open-Meteo](https://open-meteo.com/), refreshed every 15 minutes. No API key is needed.
- Day, dusk, and night versions of the scene, chosen from today's real sunrise and sunset times.
- Rain and snow effects when the current weather is rain or snow.
- A clock and weather panel that moves to a new position every 5 minutes to protect TVs from burn-in.

## Project layout

```
manifest                    Roku channel manifest
source/main.brs             Entry point (RunScreenSaver)
components/MainScene.xml    Scene layout: layers, lanes, panel, animations
components/MainScene.brs    Scene logic: parallax, cars, clock, weather, time of day
components/WeatherTask.xml  Task node definition for the weather request
components/WeatherTask.brs  Calls the Open-Meteo API
images/                     All artwork as PNG files
tools/generate_images.py    Draws every image in images/
tools/fonts/                Store sign fonts and their licenses (used only by the generator)
```

## Installing on a Roku

1. Turn on developer mode on the Roku. On the remote, press Home 3 times, Up 2 times, then Right, Left, Right, Left, Right. Follow the steps on screen and set a password.
2. From the repository root, build the zip:
   ```
   zip -r riverside-town.zip manifest source components images -x "*.DS_Store"
   ```
   The manifest must be at the top level of the zip, not inside a folder.
3. In a web browser, go to `http://<roku-ip-address>`, sign in with the username `rokudev` and your password, and upload the zip.
4. On the Roku, go to Settings > Theme > Screensavers and choose Riverside Town.

Because a screensaver cannot be opened from the home screen, use the Preview option in Settings > Theme > Screensavers to see it without waiting for the Roku to go idle.

Developer mode allows only one sideloaded channel at a time. Installing this screensaver replaces any other sideloaded channel on the same Roku.

## Settings

All settings are at the top of `init()` in `components/MainScene.brs`.

| Setting | What it controls |
|---|---|
| `m.LAT`, `m.LON` | Location for the weather. The default is ZIP code 46220 (Indianapolis). Roku does not give apps the device's ZIP code, so the location must be set here. |
| `m.layerSpeeds` | Scroll speed of each scenery layer, in pixels per second. |
| `m.layerWidths` | Width of each scenery layer before it repeats. The town is 3840 because it is two different 1920 pixel sections. |
| `m.cameraSpeed` | Must match the `town` layer speed. Cars use it so their speed looks correct relative to the street. |
| `m.carDefs` | Each car's image size, wheel positions, wheel radius, and `ground` speed in pixels per second. |
| `m.infoSpots` | The positions the clock panel moves between. |

The panel's transparency is set by the `color` value on the `Rectangle` inside the `info` group in `components/MainScene.xml`. The last two characters are the opacity: `00` is fully clear and `FF` is fully solid.

## Changing the artwork

The images are drawn by `tools/generate_images.py`. Edit the shapes or colors in that file, then regenerate:

```
pip install cairosvg pillow fonttools
python3 tools/generate_images.py
```

Requirements:

- Python 3.
- The Cairo graphics library, which `cairosvg` needs. On macOS, install it with `brew install cairo`. On Debian or Ubuntu, install it with `sudo apt install libcairo2`.
- No fonts need to be installed. The store sign fonts are in `tools/fonts`, and the generator converts the sign text to shapes, so the images are the same on every computer.

Store sign fonts:

| Font | Used for |
|---|---|
| Dancing Script | Bakery, Luke's |
| Playfair Display | Books |
| Oswald | Hardware, gas station, Market |
| Cinzel | Public Library |

These are variable fonts from [Google Fonts](https://fonts.google.com/): one file covers a range of weights, and the generator picks the weight for each sign. They are licensed under the SIL Open Font License; the license for each font is in `tools/fonts` next to the font file. The fonts are used only by the generator and are not part of the Roku zip.

This writes every PNG into `images/`, including the mirrored car images used by the far lane. It also writes full-scene previews for day and night into `build/`, which git ignores. There is one preview for each town section (`_a` and `_b`). The `_b` previews include a parked car so its position can be checked.

Notes on the image sizes:

- Each scenery layer is exactly 1920 pixels wide and its left and right edges line up, so two copies placed side by side repeat without a visible seam. The town layer is two different images (`town_a` and `town_b`) placed in the order A, B, A, so the street is 3840 pixels long before it repeats.
- The sky is an 8 pixel wide gradient that the scene stretches to full width. This uses much less memory than a full-size image.
- If you change a car's size or wheel positions in the generator, update the matching entry in `m.carDefs`.

## Debugging

Connect to the screensaver's debug console with:

```
telnet <roku-ip-address> 8087
```

Screensavers use port 8087, not port 8085 like normal channels. Errors from the weather request are printed there with the prefix `WeatherTask:`.

## Known limits

- A screensaver cannot define `Main()`. If it does, Roku does not list it under Settings > Theme > Screensavers. For this reason it cannot be opened from the home screen.
- Only one car uses each lane at a time, so at most two moving cars are on screen.
- Dusk covers 40 minutes on each side of sunrise and sunset. Before the first weather request finishes, the scene assumes sunrise at 7:00 AM and sunset at 7:00 PM.

## Credits

Weather data is provided by [Open-Meteo](https://open-meteo.com/). The free Open-Meteo API is for non-commercial use and its data requires attribution. Check the Open-Meteo terms before using this project for anything commercial.
