' Christmas decorations in December: the Christmas town images and the
' blinking lights.
' These subs run in the scope of MainScene (see MainScene.xml), so they
' share m with MainScene.brs.

' True in December when the town has Christmas decorations (extras.christmas
' in town.json). christmasSeasons in the settings lists the seasons that have
' a Christmas image of each town section; it is empty when they are off.
function christmasTime() as boolean
    if m.config.christmasSeasons.Count() = 0 then return false
    if m.christmasOverride <> "" then return m.christmasOverride = "on"
    dt = CreateObject("roDateTime")
    dt.ToLocalTime()
    return dt.GetMonth() = 12
end function

' Returns the image for a town section. In December it is the Christmas image,
' if there is one for the season the ground shows.
function townUri(name as string, ground as string, period as string) as string
    if m.christmas and not m.upside
        for each s in m.config.christmasSeasons
            if s = ground then return "pkg:/images/" + name + "_christmas_" + ground + "_" + period + ".png"
        end for
    end if
    return layerUri(name, ground, period)
end function

' The blinking Christmas lights. christmasBlink in the settings has [x, y, w,
' h] in townStrip coordinates for each building with lights. Each building
' has two posters, one for each blink group, with images of only the lit
' bulbs of that group. The town image draws those bulbs off, so turning a
' poster on and off makes its bulbs blink. Town section 0 is shown twice in
' the strip, so a building there gets posters in the second copy too.
sub buildBlink()
    m.blinkPosters = []
    m.blinkNames = []
    m.blinkTimer = invalid
    if m.config.christmasBlink.Count() = 0 then return
    strip = m.top.findNode("townStrip")
    stripW = m.sections * 1920
    for n = 0 to m.config.christmasBlink.Count() - 1
        rect = m.config.christmasBlink[n]
        for k = 1 to 2
            addBlink(strip, rect, rect[0], "blink_" + n.ToStr() + "_" + k.ToStr() + "_")
            if rect[0] < 1920 then addBlink(strip, rect, rect[0] + stripW, "blink_" + n.ToStr() + "_" + k.ToStr() + "_")
        end for
    end for
    m.blinkTimer = m.top.createChild("Timer")
    m.blinkTimer.duration = 0.45
    m.blinkTimer.repeat = true
    m.blinkTimer.observeField("fire", "onBlinkTick")
end sub

sub addBlink(strip as object, rect as object, x as integer, name as string)
    p = strip.createChild("Poster")
    p.width = rect[2]
    p.height = rect[3]
    p.translation = [x, rect[1]]
    p.visible = false
    m.blinkPosters.Push(p)
    m.blinkNames.Push(name)
end sub

' Shows the blinking lights in December at dusk and night, when there are
' blink images for the season the ground shows, and hides them otherwise.
sub updateBlink()
    if m.blinkTimer = invalid then return
    on = false
    if m.christmas and m.period <> "day"
        for each s in m.config.christmasSeasons
            if s = m.ground then on = true
        end for
    end if
    for i = 0 to m.blinkPosters.Count() - 1
        p = m.blinkPosters[i]
        if on
            p.uri = "pkg:/images/" + m.blinkNames[i] + m.ground + "_" + m.period + ".png"
            p.visible = Rnd(2) = 1
        else
            p.visible = false
        end if
    end for
    if on
        m.blinkTimer.control = "start"
    else
        m.blinkTimer.control = "stop"
    end if
end sub

' Turns about one in four of the blink posters on or off, picked at random,
' so the lights blink at random.
sub onBlinkTick()
    for each p in m.blinkPosters
        if Rnd(4) = 1 then p.visible = not p.visible
    end for
end sub
