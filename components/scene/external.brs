' The network settings file (external_config_url in town.json). The task in
' components/ExternalConfigTask.brs downloads it and keeps a saved copy.
' These subs run in the scope of MainScene (see MainScene.xml), so they
' share m with MainScene.brs.
'
' The settings are applied in three layers: the defaults in loadTownConfig(),
' then town_config.json in the zip (m.baseConfig), then the network file.
' Every new network file is applied to m.baseConfig again, not to the
' settings from the file before it, so a field that is removed from the file
' goes back to its value in the zip. A list in the file replaces the whole
' list from the zip.

sub startExternalConfig()
    m.externalFresh = false
    ' When the last good file was downloaded, in seconds (roDateTime.AsSeconds), or 0
    m.externalLastOk = 0
    if m.config.externalConfigUrl = "" then return
    m.externalTask = m.top.findNode("externalConfigTask")
    m.externalTask.url = m.config.externalConfigUrl
    m.externalTask.keepDays = m.externalKeepDays
    m.externalTask.readSaved = true
    m.externalTask.observeField("saved", "onExternalSaved")
    m.externalTask.observeField("result", "onExternalResult")
    m.externalTask.control = "RUN"
    m.externalTimer = makeTimer(m.externalRefreshDefault * 60, "onExternalTick")
end sub

sub onExternalTick()
    m.externalTask.readSaved = false
    m.externalTask.control = "RUN"
end sub

' The saved copy from an earlier download. It is used until the new download
' finishes, and in its place if the download fails.
sub onExternalSaved()
    s = m.externalTask.saved
    if s = invalid or s.data = invalid or m.externalFresh then return
    print "External settings: using the saved copy"
    m.externalLastOk = s.saved
    applyExternal(s.data)
end sub

sub onExternalResult()
    r = m.externalTask.result
    if r = invalid then return
    now = CreateObject("roDateTime").AsSeconds()
    if r.status = "ok"
        m.externalFresh = true
        m.externalLastOk = now
        applyExternal(r.data)
        setExternalRefresh(r.data)
    else if r.status = "removed"
        print "External settings: the file is gone (404), so the settings in the zip are used"
        m.externalFresh = true
        m.externalLastOk = 0
        applyExternal({})
    else
        print "External settings: could not use the file: " + r.reason
        ' Keep the settings from the last good file for up to
        ' m.externalKeepDays, then go back to the settings in the zip.
        if m.externalLastOk > 0 and now - m.externalLastOk > m.externalKeepDays * 86400
            print "External settings: the last good file is more than " + m.externalKeepDays.ToStr() + " days old, so the settings in the zip are used"
            m.externalLastOk = 0
            applyExternal({})
        end if
    end if
end sub

' Sets how often the file is downloaded, from refresh_minutes (1 to 1440).
sub setExternalRefresh(data as object)
    minutes = m.externalRefreshDefault
    v = data["refresh_minutes"]
    if isNumber(v)
        minutes = Int(v)
        if minutes < 1 then minutes = 1
        if minutes > 1440 then minutes = 1440
    end if
    if m.externalTimer.duration <> minutes * 60
        m.externalTimer.duration = minutes * 60
        m.externalTimer.control = "start"
    end if
end sub

' Applies the network file on top of the settings in the zip, and updates
' the parts of the scene whose settings changed.
sub applyExternal(data as object)
    cfg = {}
    for each key in m.baseConfig
        cfg[key] = m.baseConfig[key]
    end for
    ext = externalSettings(data)
    for each key in ext
        cfg[key] = ext[key]
    end for
    old = m.config
    m.config = cfg

    if old.lat <> cfg.lat or old.lon <> cfg.lon or old.temperatureUnit <> cfg.temperatureUnit
        m.weatherTask.lat = cfg.lat
        m.weatherTask.lon = cfg.lon
        m.weatherTask.unit = cfg.temperatureUnit
        m.weatherTask.control = "RUN"
    end if
    if old.clock24 <> cfg.clock24 then updateClock()
    if not sameList(old.cars, cfg.cars) or not sameList(old.specialCars, cfg.specialCars) then applyCars()
    if old.airplane <> cfg.airplane then applyAirplane()
    if old.fireflies <> cfg.fireflies or old.fallingLeaves <> cfg.fallingLeaves or old.seasons <> cfg.seasons then applyScene()
end sub

' Reads the settings that the network file can change and returns them with
' the names that m.config uses. A value with the wrong type or an unknown
' value is left out, so the value from the zip is used. Settings that change
' the images (the buildings, the sections, the lamps, the animals, and the
' hemisphere) can only be set in town.json, because the images are made
' when the town is built.
' ParseJson keeps the case of the keys, so the keys here must be written in
' lower case, as they are in the file.
function externalSettings(data as object) as object
    out = {}
    if type(data) <> "roAssociativeArray" then return out

    extras = data["extras"]
    if type(extras) = "roAssociativeArray"
        for each pair in [["airplane", "airplane"], ["fireflies", "fireflies"], ["falling_leaves", "fallingLeaves"], ["seasons", "seasons"]]
            v = extras[pair[0]]
            if isBool(v)
                out[pair[1]] = v
            else if v <> invalid
                print "External settings: extras." + pair[0] + " must be true or false"
            end if
        end for
    end if

    units = data["units"]
    if type(units) = "roAssociativeArray"
        t = units["temperature"]
        if isString(t) and t = "F"
            out.temperatureUnit = "fahrenheit"
        else if isString(t) and t = "C"
            out.temperatureUnit = "celsius"
        else if t <> invalid
            print "External settings: units.temperature must be F or C"
        end if
        c = units["clock"]
        if isString(c) and c = "12h"
            out.clock24 = false
        else if isString(c) and c = "24h"
            out.clock24 = true
        else if c <> invalid
            print "External settings: units.clock must be 12h or 24h"
        end if
    end if

    loc = data["location"]
    if type(loc) = "roAssociativeArray"
        lat = coordText(loc["lat"], 90)
        lon = coordText(loc["lon"], 180)
        if lat <> "" and lon <> ""
            out.lat = lat
            out.lon = lon
        else
            print "External settings: location needs both lat and lon, as numbers"
        end if
    end if

    cars = carNames(data["cars"], false)
    if cars <> invalid
        if cars.Count() >= 2
            out.cars = cars
        else
            print "External settings: cars must list at least 2 cars"
        end if
    end if
    special = carNames(data["special_cars"], true)
    if special <> invalid then out.specialCars = special
    return out
end function

' The car names in list that are cars of the right kind (special or not), or
' invalid if list is not a list. Unknown names are left out.
function carNames(list as dynamic, special as boolean) as dynamic
    if list = invalid then return invalid
    if type(list) <> "roArray"
        print "External settings: cars and special_cars must be lists"
        return invalid
    end if
    out = []
    for each name in list
        found = false
        for each def in m.allCars
            if isString(name) and name = def.name and isSpecial(def) = special then found = true
        end for
        if found
            out.Push(name)
        else
            print "External settings: " + FormatJson(name) + " is not a car that can be listed there"
        end if
    end for
    return out
end function

' A latitude or longitude as text (see the note about floats in AGENTS.md),
' or "" if v is not a number between -limit and limit.
function coordText(v as dynamic, limit as integer) as string
    s = ""
    if isString(v)
        s = v.Trim()
    else if isNumber(v)
        s = Str(v).Trim()
    else
        return ""
    end if
    re = CreateObject("roRegex", "^-?[0-9]+(\.[0-9]+)?$", "")
    if not re.IsMatch(s) then return ""
    if Abs(Val(s)) > limit then return ""
    return s
end function

function isBool(v as dynamic) as boolean
    t = type(v)
    return t = "roBoolean" or t = "Boolean"
end function

function isString(v as dynamic) as boolean
    t = type(v)
    return t = "roString" or t = "String"
end function

function isNumber(v as dynamic) as boolean
    t = type(v)
    return t = "roInt" or t = "roInteger" or t = "Integer" or t = "roFloat" or t = "Float" or t = "roDouble" or t = "Double" or t = "LongInteger" or t = "roLongInteger"
end function

function sameList(a as object, b as object) as boolean
    if a.Count() <> b.Count() then return false
    for i = 0 to a.Count() - 1
        if a[i] <> b[i] then return false
    end for
    return true
end function
