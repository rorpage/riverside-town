' Riverside Town screensaver: parallax scene, cars, clock, and Open-Meteo weather.
'
' This file has init(), the settings, and small helpers. The rest of the
' scene is in components/scene/, one file for each part. MainScene.xml loads
' all of them, and they share m:
'   scenery.brs    the scenery layers, the time of day, the season, and applyScene()
'   christmas.brs  the Christmas images and the blinking lights in December
'   weather.brs    the weather request, the panel text, clouds, fog, rain, snow, and lightning
'   airplane.brs   the airplane
'   panel.brs      the clock and weather panel
'   cars.brs       the cars on the street and the car parked at the gas station
'   sidewalk.brs   the animals and the street lamps
'   external.brs   the network settings file (external_config_url in town.json)
'   messages.brs   the birthdays and messages to show today

sub init()
    ' ---------- Settings ----------
    ' The town's settings come from components/town_config.json, which
    ' tools/generate_images.py writes from town.json. They include the weather
    ' location (Roku does not give apps the device's ZIP code), the units, the
    ' number of town sections, the cars, the animals, and the extras.
    m.config = loadTownConfig()
    ' The settings from the zip. The network settings file is applied on top
    ' of these each time it is downloaded (see components/scene/external.brs).
    m.baseConfig = m.config
    m.sections = m.config.sections
    ' Days to keep using the last good network settings file when it cannot
    ' be downloaded. After that, the settings in the zip are used again.
    m.externalKeepDays = 7
    ' Minutes between downloads of the network settings file, when the file
    ' has no refresh_minutes
    m.externalRefreshDefault = 10

    ' Scroll speed of each scenery layer in pixels per second. Farther = slower.
    m.layerSpeeds = { clouds: 8, far: 5, near: 12, hills: 24, town: 55 }
    ' Width of each layer before it repeats. The far and near mountains are two
    ' different 1920 px tiles each, the hills are three, and the town has one
    ' 1920 px tile for each town section.
    m.layerWidths = { clouds: 1920, far: 3840, near: 3840, hills: 5760, town: m.sections * 1920 }
    ' The street moves with the town layer, so cars use this as the ground speed offset.
    m.cameraSpeed = 55

    ' Cars. "ground" is the speed along the road in pixels per second.
    ' wheels = wheel centers inside the car image, r = wheel radius,
    ' bottom = lowest pixel of the tires in the car image.
    ' Special cars have their own wheel image, wheel_<name>.png (see wheelUri).
    allCars = [
        { name: "sedan", w: 280, h: 104, wheels: [[62, 80], [218, 80]],   r: 22, bottom: 102, ground: 300 },
        { name: "van",   w: 310, h: 130, wheels: [[66, 104], [246, 104]], r: 24, bottom: 128, ground: 220 },
        { name: "jeep",  w: 270, h: 140, wheels: [[68, 108], [214, 108]], r: 28, bottom: 136, ground: 200 },
        { name: "truck", w: 300, h: 130, wheels: [[70, 104], [238, 104]], r: 24, bottom: 128, ground: 185 },
        { name: "sports", w: 304, h: 104, wheels: [[64, 84], [234, 84]], r: 18, bottom: 102, ground: 480 },
        { name: "buggy",  w: 250, h: 112, wheels: [[52, 84], [198, 84]],  r: 26, bottom: 110, ground: 260 },
        { name: "aston",    w: 300, h: 106, wheels: [[86, 84], [244, 84]],   r: 19, bottom: 103, ground: 330, special: true },
        { name: "herbie",   w: 270, h: 106, wheels: [[62, 86], [217, 86]],   r: 19, bottom: 105, ground: 280, special: true },
        { name: "kitt",     w: 300, h: 92,  wheels: [[67, 69], [228, 69]],   r: 18, bottom: 87,  ground: 400, special: true },
        { name: "ecto1",    w: 360, h: 150, wheels: [[82, 124], [293, 124]], r: 18, bottom: 142, ground: 240, special: true },
        { name: "delorean", w: 310, h: 112, wheels: [[76, 85], [245, 85]],   r: 18, bottom: 103, ground: 360, special: true },
        { name: "mcqueen",  w: 300, h: 106, wheels: [[75, 71], [245, 71]],   r: 28, bottom: 99,  ground: 420, special: true },
        { name: "mustang",  w: 310, h: 96,  wheels: [[71, 77], [243, 77]],   r: 18, bottom: 95,  ground: 380, special: true }
    ]
    ' Only the cars listed in the settings drive by (see enabledCars). The
    ' network settings file can change the list while the screensaver runs.
    m.allCars = allCars
    m.carDefs = enabledCars()
    ' Special cars drive by less often. Seconds before the first trip: at least
    ' specialFirstMin, plus up to specialFirstMore. Seconds between trips: at
    ' least specialWaitMin, plus up to specialWaitMore. Regular cars wait 2 to 9
    ' seconds between trips.
    m.specialFirstMin = 20
    m.specialFirstMore = 60
    m.specialWaitMin = 90
    m.specialWaitMore = 150
    ' After a car leaves a lane, the lane stays empty for a random time between
    ' laneGapMin and laneGapMax milliseconds (1 to 10 seconds) before the next
    ' car can use it.
    m.laneGapMin = 1000
    ' The animal posters that have a darker image for night (see addAnimal)
    m.nightAnimals = []
    ' The street lamp posters (see buildLamps)
    m.lampPosters = []
    m.laneGapMax = 10000

    ' Open-Meteo weather codes (WMO) to text
    m.codeText = {
        "0": "Clear", "1": "Mostly clear", "2": "Partly cloudy", "3": "Overcast",
        "45": "Fog", "48": "Fog",
        "51": "Light drizzle", "53": "Drizzle", "55": "Heavy drizzle",
        "56": "Freezing drizzle", "57": "Freezing drizzle",
        "61": "Light rain", "63": "Rain", "65": "Heavy rain",
        "66": "Freezing rain", "67": "Freezing rain",
        "71": "Light snow", "73": "Snow", "75": "Heavy snow", "77": "Snow grains",
        "80": "Rain showers", "81": "Rain showers", "82": "Heavy rain showers",
        "85": "Snow showers", "86": "Heavy snow showers",
        "95": "Thunderstorm", "96": "Thunderstorm with hail", "99": "Thunderstorm with hail"
    }

    ' Season to always show, for previewing: "spring", "summer", "fall", or "winter".
    ' Leave it as "" to choose the season from today's date.
    m.seasonOverride = ""
    ' Set to "on" or "off" to always show or never show the Christmas
    ' decorations, for previewing. Leave it as "" to show them in December.
    m.christmasOverride = ""
    ' Layers that have a different image for some seasons. This must match
    ' SEASONAL in tools/generate_images.py. Every town section has an image
    ' for each season.
    allSeasons = ["spring", "summer", "fall", "winter"]
    m.seasonalLayers = { far: ["winter"], far_b: ["winter"], near: ["winter"], near_b: ["winter"], hills: allSeasons, hills_b: allSeasons, hills_c: allSeasons }
    m.townNames = []
    for i = 0 to m.sections - 1
        name = "town_" + Mid("abcde", i + 1, 1)
        m.townNames.Push(name)
        m.seasonalLayers[name] = allSeasons
    end for

    ' Airplane (a Cessna). It flies at the distance of the far mountains, so the
    ' camera adds or takes away m.layerSpeeds.far from its speed on screen, the
    ' same way m.cameraSpeed works for cars. planeSpeed is its own speed at that
    ' distance in pixels per second: a Cessna is about 4 times as fast as the
    ' sedan (300), and the far mountains move 5 / 55 as fast as the street, so
    ' 4 * 300 * 5 / 55 is about 110.
    m.planeSpeed = 110
    ' Seconds to wait between flights: at least planeWaitMin, plus up to planeWaitMore.
    m.planeWaitMin = 45
    m.planeWaitMore = 120

    ' Falling leaves in fall come and go. They fall for leafOnMin seconds plus up
    ' to leafOnMore, then stop for leafOffMin plus up to leafOffMore, and so on.
    ' Each change fades over 3 seconds.
    m.leafOnMin = 25
    m.leafOnMore = 45
    m.leafOffMin = 15
    m.leafOffMore = 45

    ' Positions for the clock panel. It stays in the top-right corner and moves a
    ' small amount every few minutes to protect TVs from burn-in. The sun and
    ' moon stay in the top-left corner, so the panel never covers them.
    m.infoSpots = [[1260, 60], [1230, 80], [1245, 45]]
    m.infoIndex = 0

    ' ---------- Node references ----------
    m.sky = m.top.findNode("sky")
    m.stars = m.top.findNode("stars")
    m.sun = m.top.findNode("sun")
    m.farLane = m.top.findNode("farLane")
    m.nearLane = m.top.findNode("nearLane")
    m.precip = m.top.findNode("precip")
    m.precip1 = m.top.findNode("precip1")
    m.precip2 = m.top.findNode("precip2")
    m.precipAnim = m.top.findNode("precipAnim")
    m.info = m.top.findNode("info")
    m.clockLabel = m.top.findNode("clockLabel")
    m.tempLabel = m.top.findNode("tempLabel")
    m.condLabel = m.top.findNode("condLabel")
    m.fireflies = m.top.findNode("fireflies")
    m.firefliesAnim = m.top.findNode("firefliesAnim")
    m.seasonFx = m.top.findNode("seasonFx")
    m.seasonFx1 = m.top.findNode("seasonFx1")
    m.seasonFx2 = m.top.findNode("seasonFx2")
    m.seasonFxAnim = m.top.findNode("seasonFxAnim")
    m.leafFadeAnim = m.top.findNode("leafFadeAnim")
    m.leafFade = m.top.findNode("leafFade")
    m.infoMoveAnim = m.top.findNode("infoMoveAnim")
    m.infoMove = m.top.findNode("infoMove")
    m.leavesOn = false
    m.fog = m.top.findNode("fog")
    m.flashAnim = m.top.findNode("flashAnim")
    m.plane = m.top.findNode("plane")
    m.planeBody = m.top.findNode("planeBody")
    m.planeStrobe = m.top.findNode("planeStrobe")
    m.planeAnim = m.top.findNode("planeAnim")
    m.planeMove = m.top.findNode("planeMove")
    m.strobeAnim = m.top.findNode("strobeAnim")
    m.planeLeft = false

    m.top.backgroundColor = "0x16242FFF"

    m.weather = invalid
    m.period = ""
    m.ground = ""
    m.christmas = false
    m.season = ""
    m.sceneKey = ""
    m.precipKind = ""
    ' Cloud level: "few", "scattered", "broken", or "overcast" (see cloudLevel)
    m.cloudLevel = "few"
    m.storm = false

    m.lightningTimer = m.top.createChild("Timer")
    m.lightningTimer.repeat = false
    m.lightningTimer.observeField("fire", "onLightning")

    m.leafTimer = m.top.createChild("Timer")
    m.leafTimer.repeat = false
    m.leafTimer.observeField("fire", "onLeafTimer")

    m.planeAnim.observeField("state", "onPlaneState")
    m.planeTimer = m.top.createChild("Timer")
    m.planeTimer.repeat = false
    m.planeTimer.observeField("fire", "onPlaneTimer")
    m.planeTimer.duration = 10 + Rnd(30)
    if m.config.airplane then m.planeTimer.control = "start"

    ' ---------- Start ----------
    buildTown()
    buildBlink()
    buildTowerLight()
    applyScene()
    startParallax()
    buildCars()
    parkCar()
    placeAnimals()
    buildLamps()
    updateClock()

    m.weatherTask = m.top.findNode("weatherTask")
    m.weatherTask.lat = m.config.lat
    m.weatherTask.lon = m.config.lon
    m.weatherTask.unit = m.config.temperatureUnit
    m.weatherTask.observeField("result", "onWeather")
    m.weatherTask.control = "RUN"

    makeTimer(10, "onClockTick")
    makeTimer(60, "onPeriodTick")
    makeTimer(900, "onWeatherTick")
    makeTimer(300, "onMoveInfo")

    printMessages()
    startExternalConfig()
end sub

' Reads components/town_config.json. If it is missing or cannot be read, the
' defaults below are used, so the screensaver still starts.
function loadTownConfig() as object
    cfg = {
        lat: "39.7684", lon: "-86.1581", temperatureUnit: "fahrenheit", clock24: false, hemisphere: "north", driveOn: "right",
        sections: 1, cars: ["sedan", "van", "jeep", "truck", "sports", "buggy"], specialCars: [], pets: [], parkedCarX: -1, radioLight: [], lamps: [],
        airplane: true, fireflies: true, fallingLeaves: true, seasons: true, christmasSeasons: [], christmasBlink: [],
        externalConfigUrl: "", birthdays: [], messages: []
    }
    text = ReadAsciiFile("pkg:/components/town_config.json")
    data = invalid
    if text <> "" then data = ParseJson(text)
    if data = invalid
        print "MainScene: could not read town_config.json, using the defaults"
        return cfg
    end if
    ' A for each loop over an associative array literal gives its keys in lower
    ' case (for example, "specialcars"), but the keys from ParseJson keep their
    ' case ("specialCars"). Compare the keys in lower case, or every setting
    ' with a capital letter in its name keeps its default.
    found = {}
    for each key in data
        found[LCase(key)] = data[key]
    end for
    for each key in cfg
        k = LCase(key)
        if found.DoesExist(k) and found[k] <> invalid then cfg[k] = found[k]
    end for
    cfg.sections = Int(cfg.sections)
    if cfg.sections < 1 then cfg.sections = 1
    return cfg
end function

function makeTimer(seconds as float, callback as string) as object
    t = m.top.createChild("Timer")
    t.duration = seconds
    t.repeat = true
    t.observeField("fire", callback)
    t.control = "start"
    return t
end function

function nowMinutes() as integer
    dt = CreateObject("roDateTime")
    dt.ToLocalTime()
    return dt.GetHours() * 60 + dt.GetMinutes()
end function

' Converts "2026-10-26T08:05" to minutes after midnight
function isoMinutes(s as string) as integer
    return Int(Val(Mid(s, 12, 2))) * 60 + Int(Val(Mid(s, 15, 2)))
end function
