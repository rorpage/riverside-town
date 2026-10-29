# Plan: let people build their own town

This plan describes how to let anyone make their own version of Riverside Town by editing one configuration file. It covers the file format, the code changes, and two ways to build a version without installing the tools: a Docker image and a GitHub Action.

This plan has been built. The decisions on the open questions are in [Decisions](#decisions) at the end. Where the build differs from the plan, README.md describes what was built.

## Goals

- A person edits one file, `town.json`, and gets a Roku zip of their own town.
- The current town is described by the example `town.json`. Building from it gives the same screensaver as today.
- People do not need to install Python, Cairo, or fonts. They can use a Docker image, or a GitHub Action in their own repository.
- Mistakes in `town.json` give clear error messages that name the field and say what is wrong.

## The configuration file

`town.json` sits at the root of the repository. JSON is used because Python and BrightScript can both read it without extra libraries.

### Fields

| Field | What it sets | Default if left out |
|---|---|---|
| `title` | The screensaver name in Settings > Theme > Screensavers (`screensaver_title` and `title` in the manifest) | `"Riverside Town"` |
| `location.zip` and `location.country` | Where the weather comes from. The build looks up the coordinates. | none; `location` is required |
| `location.lat` and `location.lon` | Coordinates to use directly, instead of a ZIP code | none |
| `units.temperature` | `"F"` or `"C"` | `"F"` |
| `units.clock` | `"12h"` or `"24h"` | `"12h"` |
| `hemisphere` | `"north"` or `"south"`. In the south, the season dates move by 6 months. | `"north"` |
| `houses` | A list of house numbers, or objects with `number`, `color`, `font`, and `stories` | none |
| `buildings` | A list of buildings in street order, each with a `type`, a `name`, and options (see below) | none |
| `pets` | A list of animals on the sidewalk, each with a `type` and `colors` | none |
| `cars` | Which of the cars drive by | all six |
| `extras` | Turn on or off: `airplane`, `kayaks`, `fireflies`, `falling_leaves`, `seasons`, `table_mountain` | all on |
| `gas_price` | The price on the gas station sign, if there is a gas station | `"2.05"` |

Houses and buildings are placed in one street, in the order given. A house can appear in `buildings` with `"type": "house"` to place it between shops. Houses listed in `houses` are spread through the street automatically.

### Building types

Each type is a reusable drawing. Every type takes `name`, and most also take `color`, `font`, `stories`, and `window`.

| Type | Based on | Options |
|---|---|---|
| `house` | the current houses | `number`, `color`, `font`, `stories` (1 or 2) |
| `shop` | Long's Donuts, Forever Books, the section C shops | `sign_color`, `awning` (`"plain"`, `"striped"`, or none), `awning_colors`, `window` |
| `diner` | Luke's | `window_lettering` (for example `"WILLIAMS HARDWARE"`) |
| `computer_store` | E-gineering | `sign_text_color` |
| `ice_cream` | Cabana's | `awning_colors` |
| `restaurant` | Mama BreeBree's | `awning_colors` |
| `church` | New City and ITS | `style` (`"steeple"` or `"tower"`), `cross` (true or false) |
| `school` | Holy Cross and Covenant | `color`, `cross`, `bell_tower` |
| `columned_hall` | the courthouse and Cedarville | `clock` (true or false), `clock_time`, `letter_colors` |
| `gas_station` | Fuel Stop and Kroger | `store_name`, `price` |
| `drive_through` | Chick-fil-A | `roof_color` |

`window` choices for shops: `"books"`, `"camera"`, `"palette"`, `"computer"`, `"ice_cream"`, `"pets"`, `"table"`, or none.

### Pets

| Type | Colors |
|---|---|
| `cat` | `"black"`, `"gray"`, `"dark_gray_striped"`, `"tabby"` |
| `guinea_pig` | `"black_orange"`, `"white_orange"` |

New animal types, such as dogs, each need a drawing in the generator.

### Example

This is the start of the example file that recreates the current town. The full file would list every building.

```json
{
  "title": "Riverside Town",
  "location": { "zip": "46220", "country": "US" },
  "units": { "temperature": "F", "clock": "12h" },
  "buildings": [
    { "type": "house", "number": "5401", "color": "#F3E3B8", "font": "signika" },
    { "type": "shop", "name": "Long's Donuts", "font": "script", "awning": "plain", "stories": 2 },
    { "type": "house", "number": "135", "color": "#CFE3D4", "font": "hanken", "stories": 2 },
    { "type": "shop", "name": "Forever Books", "font": "playfair", "window": "books" },
    { "type": "computer_store", "name": "E-gineering", "font": "sharetech" },
    { "type": "diner", "name": "Luke's", "font": "kaushan", "window_lettering": "WILLIAMS HARDWARE" },
    { "type": "church", "name": "New City", "style": "steeple", "cross": true },
    { "type": "gas_station", "store_name": "Kroger", "price": "2.05" },
    { "type": "columned_hall", "name": "HILL VALLEY COURTHOUSE MALL", "clock": true, "clock_time": "10:04" }
  ],
  "pets": [
    { "type": "cat", "colors": "black" },
    { "type": "cat", "colors": "dark_gray_striped" },
    { "type": "cat", "colors": "tabby" },
    { "type": "guinea_pig", "colors": "black_orange" },
    { "type": "guinea_pig", "colors": "white_orange" }
  ]
}
```

A JSON Schema file, `town.schema.json`, describes every field. Editors such as VS Code use it to suggest field names and point out mistakes while typing.

## Code changes

### 1. Read the configuration

- `tools/generate_images.py` gets a `--config` option and reads `town.json`.
- It checks the file against `town.schema.json` and stops with a clear message if something is wrong.
- **Location:** for a ZIP code, it looks up the coordinates once, at build time. A free service such as Zippopotam.us returns coordinates for US ZIP codes. Coordinates given in the file are used as they are, so the build also works without a network connection.
- **Settings file:** it writes `components/town_config.json` into the screensaver package. This holds the coordinates, units, cars, pets, extras, the number of town sections, and the gas station position.
- **Manifest:** it writes `title` and `screensaver_title` into `manifest`.

### 2. Read the settings in the screensaver

- `MainScene.brs` reads `pkg:/components/town_config.json` with `ReadAsciiFile()` and `ParseJson()` in `init()`.
- These values replace the ones written in the code today: `m.LAT`, `m.LON`, the car list, the pet list, `m.layerWidths.town`, `m.seasonalLayers`, and the parked car position.
- `WeatherTask.brs` uses the temperature unit from the settings.
- The clock uses the 12 or 24 hour setting. The longest 24 hour value, "23:59", fits the current label width.
- **Town strip:** the town posters are created in code from the number of sections, instead of being listed in `MainScene.xml`.

### 3. Turn the drawings into building types

- Each current building becomes a function that takes its options and a width, and returns its drawing. Most of the work is in the one-of-a-kind buildings: the churches, the schools, the columned halls, the gas station, and the drive-through.
- Long names shrink to fit their signs, using `text_width()`.
- Houses and buildings without a color get one from a set of colors chosen to look good together. Houses without a font get one from the house number fonts.

### 4. Lay out the street automatically

- Buildings are placed in the order given, with a small gap between them.
- When the next building would cross a 1920 pixel section edge, it moves to the next section.
- Trees fill leftover space at the end of a section.
- **Memory limit:** the layout allows at most 5 sections, about 20 MB of screen memory for the town. If the buildings do not fit, the build stops and says how many to remove.
- **Section A:** the first section appears twice in the strip, so the layout puts no gas station in it. The parked car needs a station that appears only once.
- **Pets:** they are placed only outside section A, as now.

### 5. Keep the current town the same

The example `town.json` recreates the current town. A check compares the generated images against the current ones and reports any building that moved or changed. Small differences are expected where a one-of-a-kind building becomes a general type, and each one will be listed for approval.

## Building without installing anything

### Docker image

The Docker image holds everything needed to build a town:

- Python, the Cairo library, the Python packages (`cairosvg`, `pillow`, `fonttools`), and `zip`
- the generator and the fonts in `tools/`
- the screensaver code (`manifest`, `source`, `components`) as a starting point

The image is built from a `Dockerfile` in this repository and published to the GitHub Container Registry as `ghcr.io/rorpage/riverside-town-roku-generator`.

To build a town on any computer with Docker, run this in a folder that has a `town.json`:

```
docker run --rm -v "$PWD:/work" ghcr.io/rorpage/riverside-town-roku-generator:1
```

It writes `riverside-town.zip` and the preview images into `out/` in that folder.

### GitHub Action

People who do not want to install Docker can use GitHub instead. The Action uses the same Docker image, so both ways build exactly the same zip.

**In this repository:**
- **Publish workflow:** `.github/workflows/riverside-town-roku-generator.yml` builds the Docker image and pushes it to the GitHub Container Registry when a version tag such as `v1.2.0` is pushed. It also updates the `1` tag, so users get fixes within version 1. The image package must be set to public so anyone can pull it without signing in.
- **Action file:** `action.yml` describes a Docker container action that runs the published image. Other repositories use it with `uses: rorpage/riverside-town@v1`.

**For people making their own town:**
- **Template repository:** a small template repository, `rorpage/riverside-town-sample`, holds an example `town.json` and a workflow file.
- **Getting started:** they click "Use this template" on GitHub, edit `town.json` in the browser, and commit.
- **Building:** the workflow runs on each commit that changes `town.json`. It builds the town with the Action and attaches `riverside-town.zip` and the preview images to the workflow run as downloadable files.
- **Installing:** they download the zip and install it on their Roku with the developer web page, as described in the README. The Action cannot install it, because it cannot reach the Roku on their home network.

The workflow in the template repository would be about this short:

```yaml
name: Build my town
on:
  push:
    paths: ["town.json"]
  workflow_dispatch:
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: rorpage/riverside-town@v1
        with:
          config: town.json
      - uses: actions/upload-artifact@v4
        with:
          name: riverside-town
          path: out/
```

### Recommendation

Build both. They share one Docker image, so the extra work for the Action is small:

- the publish workflow
- `action.yml`
- the template repository

The Docker image suits people who are comfortable with a terminal. The GitHub Action suits everyone else, because it only needs a GitHub account and a web browser.

## Steps

Each step is a separate pull request. Each one leaves the screensaver working.

1. **Configuration file and simple settings.**
   - Add `town.json`, `town.schema.json`, `--config`, and `town_config.json`.
   - Move the location, units, title, cars, pets, and extras out of the code.
   - Add the ZIP code lookup and the 24 hour clock.
2. **Building types.** Turn every current building into a building type, without changing how the town looks.
3. **Automatic layout.**
   - Build the street from the `buildings` list.
   - Create the town posters in code.
   - Move the parked car and the pets to positions from the layout.
4. **Docker image.** Add the `Dockerfile`, a build command in the image, and the publish workflow.
5. **GitHub Action and template repository.** Add `action.yml`, create the template repository, and write the setup steps in the README.
6. **Docs.** Update README.md and AGENTS.md, including a guide to every `town.json` field with examples.

Steps 1 and 4 are the smallest and are useful on their own. Step 2 is the largest.

## Decisions

1. **License:** The Unlicense, which puts the code and art in the public domain. The fonts keep their own SIL Open Font License.
2. **Names:** the Docker image and the publish workflow are `riverside-town-roku-generator`. The template repository is `rorpage/riverside-town-sample`.
3. **Brand names:** the README says that a town with real business names is for personal use.
4. **Custom drawings:** not supported for now. New building types need Python code in the generator.
5. **The current town:** this repository and the template use a simpler, generic sample town. The owner's family town is in the private repository `rorpage/riverside-town-page-family`, built with the Action.

Other changes from the plan:

- `extras.table_mountain` is off by default, because the sample town does not use it.
- Pets and the parked car can be in any town section, including section A. Section A appears twice in the strip, so the screensaver adds a second copy of anything placed there.
- A ZIP code is looked up with the Open-Meteo geocoding service first, and Zippopotam.us second.
