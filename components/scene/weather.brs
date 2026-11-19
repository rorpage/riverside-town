' The weather: the request to WeatherTask, the panel text, the cloud level,
' fog, rain, snow, and lightning.
' These subs run in the scope of MainScene (see MainScene.xml), so they
' share m with MainScene.brs.

sub onWeatherTick()
    m.weatherTask.control = "RUN"
end sub

sub onWeather()
    r = m.weatherTask.result
    if r = invalid then return
    if not r.ok then return
    m.weather = r
    unit = "F"
    if m.config.temperatureUnit = "celsius" then unit = "C"
    m.tempLabel.text = CInt(r.temp).ToStr() + Chr(176) + unit
    m.condLabel.text = weatherText(r.code)
    setPrecip(r.code)
    setFog(r.code)
    setStorm(r.code)
    m.cloudLevel = cloudLevel(r.code, r.cloudCover)
    applyScene()
end sub

' Picks the cloud level from the cloud cover in percent. The weather code sets
' a lowest level, so the sky always matches the weather text: "Overcast" (3),
' rain, drizzle, snow, and thunderstorms show an overcast sky, fog and showers
' at least broken clouds, and "Partly cloudy" (2) at least scattered clouds.
' A cover of -1 means the weather had no cloud cover, and the code alone is used.
function cloudLevel(code as dynamic, cover as dynamic) as string
    levels = ["few", "scattered", "broken", "overcast"]
    n = 0
    if cover <> invalid
        pct = Int(cover)
        if pct >= 85
            n = 3
        else if pct >= 50
            n = 2
        else if pct >= 25
            n = 1
        end if
    end if
    c = Int(code)
    least = 0
    if c = 2 then least = 1
    if c = 45 or c = 48 or (c >= 80 and c <= 86) then least = 2
    if c = 3 or (c >= 51 and c <= 77) or c >= 95 then least = 3
    if least > n then n = least
    return levels[n]
end function

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
