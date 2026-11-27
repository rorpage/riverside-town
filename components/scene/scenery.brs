' The scenery layers: the town strip, the radio tower light, the parallax
' animations, the time of day and season, and applyScene(), which sets
' every image for the time of day, the season, and the weather.
' These subs run in the scope of MainScene (see MainScene.xml), so they
' share m with MainScene.brs.

' Creates one poster for each town section, then a second copy of the first
' section at the end of the strip, so the strip repeats without a jump.
sub buildTown()
    strip = m.top.findNode("townStrip")
    m.townPosters = []
    for i = 0 to m.sections
        p = strip.createChild("Poster")
        p.id = "town" + i.ToStr()
        p.width = 1920
        p.height = 530
        p.translation = [i * 1920, 0]
        m.townPosters.Push(p)
    end for
    m.top.findNode("townMove").keyValue = [[0, 0], [-m.sections * 1920, 0]]
end sub

' The blinking red light on top of the radio tower on the hills. radioLight in
' the settings is the center of the light in hills strip coordinates, or empty
' if there is no tower. Hills tile A is at x = 0 and again at x = 5760, so
' there is a light in both copies. It blinks at dusk and night, like the
' airplane's tail light.
sub buildTowerLight()
    m.towerLightAnim = invalid
    if m.config.radioLight.Count() < 2 then return
    strip = m.top.findNode("hillsStrip")
    anim = m.top.createChild("Animation")
    anim.id = "towerLightAnim"
    anim.repeat = true
    anim.easeFunction = "linear"
    anim.duration = 1.8
    m.towerLights = []
    for i = 0 to 1
        light = strip.createChild("Poster")
        light.id = "towerLight" + i.ToStr()
        light.uri = "pkg:/images/tower_light.png"
        light.width = 24
        light.height = 24
        light.translation = [m.config.radioLight[0] + i * m.layerWidths.hills - 12, m.config.radioLight[1] - 12]
        light.opacity = 0
        interp = anim.createChild("FloatFieldInterpolator")
        interp.key = [0.0, 0.12, 0.22, 1.0]
        interp.keyValue = [1.0, 1.0, 0.0, 0.0]
        interp.fieldToInterp = light.id + ".opacity"
        m.towerLights.Push(light)
    end for
    m.towerLightAnim = anim
end sub

sub updateTowerLight(period as string)
    if m.towerLightAnim = invalid then return
    if period = "day"
        m.towerLightAnim.control = "stop"
        for each light in m.towerLights
            light.opacity = 0
        end for
    else
        m.towerLightAnim.control = "start"
    end if
end sub

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
' With seasons turned off in the settings, it is always summer. In the
' southern hemisphere the seasons are the other way around.
function currentSeason() as string
    if m.seasonOverride <> "" then return m.seasonOverride
    if not m.config.seasons then return "summer"
    dt = CreateObject("roDateTime")
    dt.ToLocalTime()
    md = dt.GetMonth() * 100 + dt.GetDayOfMonth()
    season = "fall"
    if md >= 1221 or md < 320
        season = "winter"
    else if md < 621
        season = "spring"
    else if md < 922
        season = "summer"
    end if
    if m.config.hemisphere = "south"
        other = { winter: "summer", summer: "winter", spring: "fall", fall: "spring" }
        season = other[season]
    end if
    return season
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
    leaves = leafMonths()
    christmas = christmasTime()
    key = period + "," + season + "," + ground + "," + m.precipKind + "," + m.cloudLevel + "," + leaves.ToStr() + "," + christmas.ToStr()
    if key = m.sceneKey then return
    m.sceneKey = key
    m.period = period
    m.season = season
    m.ground = ground
    m.christmas = christmas

    ' An overcast sky is gray, with no stars, sun, or moon (see the end of
    ' this sub).
    overcast = m.cloudLevel = "overcast"
    if overcast
        m.sky.uri = "pkg:/images/sky_overcast_" + period + ".png"
    else
        m.sky.uri = "pkg:/images/sky_" + period + ".png"
    end if
    cloudUri = "pkg:/images/clouds_" + m.cloudLevel + "_" + period + ".png"
    m.top.findNode("clouds1").uri = cloudUri
    m.top.findNode("clouds2").uri = cloudUri
    for each name in ["far", "near", "hills"]
        uri = layerUri(name, ground, period)
        m.top.findNode(name + "1").uri = uri
        m.top.findNode(name + "2").uri = uri
    end for
    m.top.findNode("farB").uri = layerUri("far_b", ground, period)
    m.top.findNode("nearB").uri = layerUri("near_b", ground, period)
    m.top.findNode("hillsB").uri = layerUri("hills_b", ground, period)
    m.top.findNode("hillsC").uri = layerUri("hills_c", ground, period)
    updateTowerLight(period)
    updateAnimals(period)
    updateOutside()
    updateLamps()
    for i = 0 to m.sections
        m.townPosters[i].uri = townUri(m.townNames[i MOD m.sections], ground, period)
    end for
    updateBlink()
    updateSeasonFx(season, period, leaves)
    updatePlaneImage()
    updateBannerImage()
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
    m.sun.opacity = 1
    if overcast
        m.stars.opacity = 0
        m.sun.opacity = 0
    end if
end sub

sub onPeriodTick()
    applyScene()
end sub

' True in the months when leaves fall: October and November in the northern
' hemisphere, April and May in the southern hemisphere. When a season is
' forced with seasonOverride, leaves fall whenever that season is fall.
function leafMonths() as boolean
    if m.seasonOverride <> "" then return m.seasonOverride = "fall"
    dt = CreateObject("roDateTime")
    dt.ToLocalTime()
    month = dt.GetMonth()
    if m.config.hemisphere = "south" then return month = 4 or month = 5
    return month = 10 or month = 11
end function

' Falling leaves in fall and fireflies on summer nights. They are hidden
' while rain or snow is falling. Nothing falls in spring or winter (unless it
' is snowing). Leaves fall only in fall and only in the months from
' leafMonths(). The leaves start out falling, and then onLeafTimer() stops
' and starts them at random times.
sub updateSeasonFx(season as string, period as string, leaves as boolean)
    fx = ""
    if m.precipKind = "" and m.config.fallingLeaves
        if season = "fall" and leaves then fx = "leaves"
    end if
    m.seasonFxAnim.control = "stop"
    m.leafFadeAnim.control = "stop"
    m.leafTimer.control = "stop"
    if fx = ""
        m.seasonFx.visible = false
        m.leavesOn = false
    else
        m.seasonFx1.uri = "pkg:/images/" + fx + ".png"
        m.seasonFx2.uri = "pkg:/images/" + fx + ".png"
        m.seasonFxAnim.duration = 16
        m.seasonFx.opacity = 1
        m.seasonFx.visible = true
        m.seasonFxAnim.control = "start"
        m.leavesOn = true
        scheduleLeaves()
    end if

    flies = m.config.fireflies and season = "summer" and period = "night" and m.precipKind = ""
    m.fireflies.visible = flies
    if flies
        m.firefliesAnim.control = "start"
    else
        m.firefliesAnim.control = "stop"
    end if
end sub

' Fades the falling leaves out if they are falling, or back in if they are
' not, then waits a random time before the next change. The leaves keep
' moving while they are faded out, so when they fade back in, they are
' already partway down the screen.
sub onLeafTimer()
    if not m.seasonFx.visible then return
    if m.leavesOn
        m.leafFade.keyValue = [m.seasonFx.opacity, 0.0]
    else
        m.leafFade.keyValue = [m.seasonFx.opacity, 1.0]
    end if
    m.leavesOn = not m.leavesOn
    m.leafFadeAnim.control = "start"
    scheduleLeaves()
end sub

sub scheduleLeaves()
    if m.leavesOn
        m.leafTimer.duration = m.leafOnMin + Rnd(m.leafOnMore)
    else
        m.leafTimer.duration = m.leafOffMin + Rnd(m.leafOffMore)
    end if
    m.leafTimer.control = "start"
end sub
