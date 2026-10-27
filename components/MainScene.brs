' Riverside Town screensaver: parallax scene, cars, clock, and Open-Meteo weather.

sub init()
    ' ---------- Settings ----------
    ' Location for ZIP code 46220 (Indianapolis). Roku does not give apps the
    ' device's ZIP code, so it is set here. Change these to get the forecast for
    ' a different location.
    m.LAT = "39.8676"
    m.LON = "-86.1137"

    ' Scroll speed of each scenery layer in pixels per second. Farther = slower.
    m.layerSpeeds = { clouds: 8, far: 5, near: 12, hills: 24, town: 55 }
    ' Width of each layer before it repeats. The town is three different 1920 px tiles.
    m.layerWidths = { clouds: 1920, far: 1920, near: 1920, hills: 1920, town: 5760 }
    ' The street moves with the town layer, so cars use this as the ground speed offset.
    m.cameraSpeed = 55

    ' Cars. "ground" is the speed along the road in pixels per second.
    ' wheels = wheel centers inside the car image, r = wheel radius,
    ' bottom = lowest pixel of the tires in the car image.
    m.carDefs = [
        { name: "sedan", w: 280, h: 104, wheels: [[62, 80], [218, 80]],   r: 22, bottom: 102, ground: 300 },
        { name: "van",   w: 310, h: 130, wheels: [[66, 104], [246, 104]], r: 24, bottom: 128, ground: 220 },
        { name: "jeep",  w: 270, h: 140, wheels: [[68, 108], [214, 108]], r: 28, bottom: 136, ground: 200 },
        { name: "truck", w: 300, h: 130, wheels: [[70, 104], [238, 104]], r: 24, bottom: 128, ground: 140 },
        { name: "sports", w: 304, h: 104, wheels: [[64, 84], [234, 84]], r: 18, bottom: 102, ground: 480 }
    ]

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
    ' Layers that have a different image for some seasons. This must match
    ' SEASONAL in tools/generate_images.py.
    allSeasons = ["spring", "summer", "fall", "winter"]
    m.seasonalLayers = { far: ["winter"], near: ["winter"], hills: allSeasons, town_a: allSeasons, town_b: allSeasons, town_c: allSeasons }

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
    m.season = ""
    m.sceneKey = ""
    m.precipKind = ""
    m.storm = false

    m.lightningTimer = m.top.createChild("Timer")
    m.lightningTimer.repeat = false
    m.lightningTimer.observeField("fire", "onLightning")

    m.planeAnim.observeField("state", "onPlaneState")
    m.planeTimer = m.top.createChild("Timer")
    m.planeTimer.repeat = false
    m.planeTimer.observeField("fire", "onPlaneTimer")
    m.planeTimer.duration = 10 + Rnd(30)
    m.planeTimer.control = "start"

    ' ---------- Start ----------
    applyScene()
    startParallax()
    buildCars()
    parkCar()
    updateClock()

    m.weatherTask = m.top.findNode("weatherTask")
    m.weatherTask.lat = m.LAT
    m.weatherTask.lon = m.LON
    m.weatherTask.observeField("result", "onWeather")
    m.weatherTask.control = "RUN"

    makeTimer(10, "onClockTick")
    makeTimer(60, "onPeriodTick")
    makeTimer(900, "onWeatherTick")
    makeTimer(300, "onMoveInfo")
end sub

' ================= Scenery =================

sub startParallax()
    for each name in m.layerSpeeds
        anim = m.top.findNode(name + "Anim")
        anim.duration = m.layerWidths[name] / m.layerSpeeds[name]
        anim.control = "start"
    end for
end sub

' Returns "day", "dusk", or "night" using today's sunrise and sunset.
' Dusk covers 40 minutes on each side of sunrise and sunset.
function currentPeriod() as string
    now = nowMinutes()
    sunriseMin = 420
    sunsetMin = 1140
    if m.weather <> invalid and m.weather.sunrise <> ""
        sunriseMin = isoMinutes(m.weather.sunrise)
        sunsetMin = isoMinutes(m.weather.sunset)
    end if
    if Abs(now - sunsetMin) <= 40 or Abs(now - sunriseMin) <= 40 then return "dusk"
    if now > sunriseMin and now < sunsetMin then return "day"
    return "night"
end function

' Returns "spring", "summer", "fall", or "winter" from today's date. The
' dates are close to the equinoxes and solstices, which move by a day or so
' from year to year.
function currentSeason() as string
    if m.seasonOverride <> "" then return m.seasonOverride
    dt = CreateObject("roDateTime")
    dt.ToLocalTime()
    md = dt.GetMonth() * 100 + dt.GetDayOfMonth()
    if md >= 1221 or md < 320 then return "winter"
    if md < 621 then return "spring"
    if md < 922 then return "summer"
    return "fall"
end function

' Returns the image for a scenery layer. variant is the season to draw. A
' layer without an image for that season uses its summer image, which has no
' season in the file name.
function layerUri(name as string, variant as string, period as string) as string
    seasons = m.seasonalLayers[name]
    if seasons <> invalid
        for each s in seasons
            if s = variant then return "pkg:/images/" + name + "_" + variant + "_" + period + ".png"
        end for
    end if
    return "pkg:/images/" + name + "_" + period + ".png"
end function

' Sets every image for the time of day, the season, and the weather. It does
' nothing when none of them changed.
sub applyScene()
    period = currentPeriod()
    season = currentSeason()
    ' While snow is falling, the ground shows snow in any season.
    ground = season
    if m.precipKind = "snow" then ground = "winter"
    key = period + "," + season + "," + ground + "," + m.precipKind
    if key = m.sceneKey then return
    m.sceneKey = key
    m.period = period
    m.season = season

    m.sky.uri = "pkg:/images/sky_" + period + ".png"
    for each name in ["clouds", "far", "near", "hills"]
        uri = layerUri(name, ground, period)
        m.top.findNode(name + "1").uri = uri
        m.top.findNode(name + "2").uri = uri
    end for
    m.top.findNode("townA1").uri = layerUri("town_a", ground, period)
    m.top.findNode("townA2").uri = layerUri("town_a", ground, period)
    m.top.findNode("townB").uri = layerUri("town_b", ground, period)
    m.top.findNode("townC").uri = layerUri("town_c", ground, period)
    updateSeasonFx(season, period)
    updatePlaneImage()
    if period = "night"
        m.fog.opacity = 0.6
    else
        m.fog.opacity = 1
    end if
    if period = "day"
        m.stars.opacity = 0
        m.sun.uri = "pkg:/images/sun.png"
        m.sun.translation = [150, 110]
    else if period = "dusk"
        m.stars.opacity = 0.35
        m.sun.uri = "pkg:/images/sun.png"
        m.sun.translation = [180, 340]
    else
        m.stars.opacity = 1
        m.sun.uri = "pkg:/images/moon.png"
        m.sun.translation = [150, 100]
    end if
end sub

sub onPeriodTick()
    applyScene()
end sub

' Falling leaves in fall, falling petals in spring, and fireflies on summer
' nights. They are hidden while rain or snow is falling.
sub updateSeasonFx(season as string, period as string)
    fx = ""
    if m.precipKind = ""
        if season = "fall" then fx = "leaves"
        if season = "spring" then fx = "petals"
    end if
    m.seasonFxAnim.control = "stop"
    if fx = ""
        m.seasonFx.visible = false
    else
        m.seasonFx1.uri = "pkg:/images/" + fx + ".png"
        m.seasonFx2.uri = "pkg:/images/" + fx + ".png"
        if fx = "leaves"
            m.seasonFxAnim.duration = 16
        else
            m.seasonFxAnim.duration = 22
        end if
        m.seasonFx.visible = true
        m.seasonFxAnim.control = "start"
    end if

    flies = season = "summer" and period = "night" and m.precipKind = ""
    m.fireflies.visible = flies
    if flies
        m.firefliesAnim.control = "start"
    else
        m.firefliesAnim.control = "stop"
    end if
end sub

' ================= Weather =================

sub onWeatherTick()
    m.weatherTask.control = "RUN"
end sub

sub onWeather()
    r = m.weatherTask.result
    if r = invalid then return
    if not r.ok then return
    m.weather = r
    m.tempLabel.text = CInt(r.temp).ToStr() + Chr(176) + "F"
    m.condLabel.text = weatherText(r.code)
    setPrecip(r.code)
    setFog(r.code)
    setStorm(r.code)
    applyScene()
end sub

sub setFog(code as dynamic)
    c = Int(code)
    m.fog.visible = c = 45 or c = 48
end sub

' Thunderstorm codes flash lightning at random times.
sub setStorm(code as dynamic)
    storm = Int(code) >= 95
    if storm and not m.storm
        m.lightningTimer.duration = 3 + Rnd(8)
        m.lightningTimer.control = "start"
    end if
    m.storm = storm
end sub

' ================= Airplane =================

' Starts a flight, or waits again if the weather is bad for flying.
sub onPlaneTimer()
    if m.precipKind <> "" or m.fog.visible or m.storm
        schedulePlane()
        return
    end if
    m.planeLeft = Rnd(2) = 2
    y = 236 + Rnd(50)
    if m.planeLeft
        ' Flying against the scroll direction looks faster
        fromX = 1980
        toX = -80
        speed = m.planeSpeed + m.layerSpeeds.far
    else
        fromX = -80
        toX = 1980
        speed = m.planeSpeed - m.layerSpeeds.far
    end if
    m.planeMove.keyValue = [[fromX, y], [toX, y]]
    m.planeAnim.duration = Abs(toX - fromX) / speed
    m.plane.translation = [fromX, y]
    m.plane.visible = true
    updatePlaneImage()
    m.planeAnim.control = "start"
end sub

sub onPlaneState(event as object)
    if event.getData() <> "stopped" then return
    m.plane.visible = false
    m.strobeAnim.control = "stop"
    schedulePlane()
end sub

sub schedulePlane()
    m.planeTimer.duration = m.planeWaitMin + Rnd(m.planeWaitMore)
    m.planeTimer.control = "start"
end sub

' Sets the plane image for its direction and the time of day. The strobe on
' the tail blinks at dusk and night, and is larger and brighter at night.
sub updatePlaneImage()
    suffix = ""
    strobeX = 1
    if m.planeLeft
        suffix = "_left"
        strobeX = 47
    end if
    m.planeBody.uri = "pkg:/images/plane" + suffix + "_" + m.period + ".png"
    ' At night the strobe uses a larger, brighter image with the same center
    if m.period = "night"
        m.planeStrobe.uri = "pkg:/images/plane_strobe_night.png"
        m.planeStrobe.width = 16
        m.planeStrobe.height = 16
        m.planeStrobe.translation = [strobeX - 4, -6]
    else
        m.planeStrobe.uri = "pkg:/images/plane_strobe.png"
        m.planeStrobe.width = 8
        m.planeStrobe.height = 8
        m.planeStrobe.translation = [strobeX, -2]
    end if
    if m.period = "day"
        m.strobeAnim.control = "stop"
        m.planeStrobe.opacity = 0
    else if m.plane.visible
        m.strobeAnim.control = "start"
    end if
end sub

sub onLightning()
    if not m.storm then return
    m.flashAnim.control = "start"
    m.lightningTimer.duration = 6 + Rnd(14)
    m.lightningTimer.control = "start"
end sub

function weatherText(code as dynamic) as string
    key = Int(code).ToStr()
    if m.codeText.DoesExist(key) then return m.codeText[key]
    return ""
end function

sub setPrecip(code as dynamic)
    c = Int(code)
    kind = ""
    if (c >= 51 and c <= 67) or (c >= 80 and c <= 82) or c >= 95 then kind = "rain"
    if (c >= 71 and c <= 77) or c = 85 or c = 86 then kind = "snow"
    if kind = m.precipKind then return
    m.precipKind = kind
    m.precipAnim.control = "stop"
    if kind = ""
        m.precip.visible = false
        return
    end if
    uri = "pkg:/images/" + kind + ".png"
    m.precip1.uri = uri
    m.precip2.uri = uri
    if kind = "rain"
        m.precipAnim.duration = 0.8
    else
        m.precipAnim.duration = 14
    end if
    m.precip.visible = true
    m.precipAnim.control = "start"
end sub

' ================= Clock and panel =================

sub onClockTick()
    updateClock()
end sub

sub updateClock()
    dt = CreateObject("roDateTime")
    dt.ToLocalTime()
    h = dt.GetHours()
    mins = dt.GetMinutes()
    suffix = "AM"
    if h >= 12 then suffix = "PM"
    h12 = h MOD 12
    if h12 = 0 then h12 = 12
    mm = mins.ToStr()
    if mins < 10 then mm = "0" + mm
    m.clockLabel.text = h12.ToStr() + ":" + mm + " " + suffix
end sub

sub onMoveInfo()
    m.infoIndex = (m.infoIndex + 1) MOD m.infoSpots.Count()
    m.info.translation = m.infoSpots[m.infoIndex]
end sub

' ================= Cars =================

sub buildCars()
    m.cars = {}
    m.laneBusy = { near: "", far: "" }
    for each def in m.carDefs
        makeCar(def)
    end for
end sub

sub makeCar(def as object)
    name = def.name
    car = m.nearLane.createChild("Group")
    car.id = name + "_car"
    car.visible = false

    body = car.createChild("Poster")
    body.uri = "pkg:/images/car_" + name + ".png"
    body.width = def.w
    body.height = def.h

    ' Wheel spin: one full turn per (2 * pi * radius) pixels of road
    spin = m.top.createChild("Animation")
    spin.id = name + "_spin"
    spin.repeat = true
    spin.easeFunction = "linear"
    spin.duration = 2 * 3.14159 * def.r / def.ground
    wheels = []
    interps = []
    i = 0
    for each w in def.wheels
        wheel = car.createChild("Poster")
        wheel.id = name + "_wheel" + i.ToStr()
        wheel.uri = "pkg:/images/wheel.png"
        wheel.width = def.r * 2
        wheel.height = def.r * 2
        wheel.translation = [w[0] - def.r, w[1] - def.r]
        wheel.scaleRotateCenter = [def.r, def.r]
        interp = spin.createChild("FloatFieldInterpolator")
        interp.key = [0.0, 1.0]
        interp.keyValue = [0.0, -6.28318]
        interp.fieldToInterp = wheel.id + ".rotation"
        wheels.Push(wheel)
        interps.Push(interp)
        i = i + 1
    end for

    move = m.top.createChild("Animation")
    move.id = name + "_move"
    move.repeat = false
    move.easeFunction = "linear"
    moveInterp = move.createChild("Vector2DFieldInterpolator")
    moveInterp.key = [0.0, 1.0]
    moveInterp.fieldToInterp = car.id + ".translation"
    move.observeField("state", "onCarMoveState")

    timer = m.top.createChild("Timer")
    timer.id = name + "_timer"
    timer.repeat = false
    timer.duration = 1 + Rnd(6)
    timer.observeField("fire", "onCarTimer")
    timer.control = "start"

    m.cars[name] = { def: def, node: car, body: body, wheels: wheels, interps: interps, move: move, moveInterp: moveInterp, spin: spin, timer: timer, lane: "" }
end sub

function carNameFromId(id as string) as string
    return Left(id, Instr(1, id, "_") - 1)
end function

sub onCarTimer(event as object)
    spawnCar(carNameFromId(event.getNode()))
end sub

' Sends a car across the screen. Only one car uses a lane at a time so faster
' cars never drive through slower ones.
' Near lane: drives left to right, full size.
' Far lane: drives right to left, slightly smaller. It uses a mirrored copy of
' the car image instead of a negative scale, because Roku does not draw spinning
' children correctly inside a mirrored (negative scale) group.
sub spawnCar(name as string)
    c = m.cars[name]
    free = []
    if m.laneBusy.near = "" then free.Push("near")
    if m.laneBusy.far = "" then free.Push("far")
    if free.Count() = 0
        c.timer.duration = 2
        c.timer.control = "start"
        return
    end if

    lane = free[Rnd(free.Count()) - 1]
    m.laneBusy[lane] = name
    c.lane = lane
    d = c.def
    car = c.node
    car.getParent().removeChild(car)

    if lane = "near"
        s = 1.0
        facingLeft = false
        groundY = 1072
        m.nearLane.appendChild(car)
        speed = d.ground - m.cameraSpeed   ' moving with the scroll direction looks slower
        fromX = -d.w - 40
        toX = 1960
    else
        s = 0.86
        facingLeft = true
        groundY = 1002
        m.farLane.appendChild(car)
        speed = d.ground + m.cameraSpeed   ' moving against the scroll direction looks faster
        fromX = 1960
        toX = -d.w - 40
    end if

    car.scaleRotateCenter = [d.w / 2, d.h / 2]
    car.scale = [s, s]

    ' Make the car face its direction of travel: swap the body image, move the wheels to the
    ' mirrored positions, and reverse the spin direction.
    suffix = ""
    turn = -6.28318
    if facingLeft
        suffix = "_left"
        turn = 6.28318
    end if
    c.body.uri = "pkg:/images/car_" + d.name + suffix + ".png"
    for i = 0 to c.wheels.Count() - 1
        wx = d.wheels[i][0]
        if facingLeft then wx = d.w - wx
        c.wheels[i].translation = [wx - d.r, d.wheels[i][1] - d.r]
        c.wheels[i].rotation = 0
        c.interps[i].keyValue = [0.0, turn]
    end for
    y = groundY - d.h / 2 - (d.bottom - d.h / 2) * s
    c.moveInterp.keyValue = [[fromX, y], [toX, y]]
    c.move.duration = Abs(toX - fromX) / speed
    car.translation = [fromX, y]
    car.visible = true
    c.spin.control = "start"
    c.move.control = "start"
end sub

sub onCarMoveState(event as object)
    if event.getData() <> "stopped" then return
    name = carNameFromId(event.getNode())
    c = m.cars[name]
    if c = invalid then return
    if c.lane = "" then return
    c.node.visible = false
    c.spin.control = "stop"
    m.laneBusy[c.lane] = ""
    c.lane = ""
    c.timer.duration = 2 + Rnd(7)
    c.timer.control = "start"
end sub

' Parks a randomly chosen car, facing a random direction, at the gas station in
' town tile B. It is a child of townStrip, so it scrolls with the town. The
' wheels do not spin.
sub parkCar()
    d = m.carDefs[Rnd(m.carDefs.Count()) - 1]
    facingLeft = Rnd(2) = 2
    s = 0.78
    ' Center of the parking space and the ground line, in townStrip coordinates.
    ' Tile B starts at x = 1920. The strip starts at screen y = 550, and the
    ' station ground is at screen y = 898.
    centerX = 1920 + 780
    groundY = 898 - 550

    car = m.top.findNode("townStrip").createChild("Group")
    car.id = "parked_car"
    car.scale = [s, s]
    car.translation = [centerX - d.w * s / 2, groundY - d.bottom * s]

    suffix = ""
    if facingLeft then suffix = "_left"
    body = car.createChild("Poster")
    body.uri = "pkg:/images/car_" + d.name + suffix + ".png"
    body.width = d.w
    body.height = d.h
    for each w in d.wheels
        wx = w[0]
        if facingLeft then wx = d.w - wx
        wheel = car.createChild("Poster")
        wheel.uri = "pkg:/images/wheel.png"
        wheel.width = d.r * 2
        wheel.height = d.r * 2
        wheel.translation = [wx - d.r, w[1] - d.r]
    end for
end sub

' ================= Helpers =================

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
