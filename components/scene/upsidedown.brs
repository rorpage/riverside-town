' The Upside Down in October (extras.upside_down in town.json): a dark
' version of the town with vines, specks that float up the screen, and red
' lightning every 7 seconds. There are no cars, animals, or airplane, and no
' sun, moon, or stars.
' These subs run in the scope of MainScene (see MainScene.xml), so they
' share m with MainScene.brs.

' True in October when the town has the Upside Down images (upsideDown in
' the settings). m.upsideOverride can force it on or off.
function upsideDownTime() as boolean
    if not m.config.upsideDown then return false
    if m.upsideOverride <> "" then return m.upsideOverride = "on"
    dt = CreateObject("roDateTime")
    dt.ToLocalTime()
    return dt.GetMonth() = 10
end function

sub buildUpsideDown()
    m.upsideSkyFlash = m.top.findNode("upsideSkyFlash")
    m.upsideBolt = m.top.findNode("upsideBolt")
    m.upsideFlash = m.top.findNode("upsideFlash")
    m.upsideFlashAnim = m.top.findNode("upsideFlashAnim")
    m.upsideSkyKeys = m.top.findNode("upsideSkyKeys")
    m.upsideBoltKeys = m.top.findNode("upsideBoltKeys")
    m.upsideFrontKeys = m.top.findNode("upsideFrontKeys")
    m.spores = m.top.findNode("spores")
    m.sporesAnimA = m.top.findNode("sporesAnimA")
    m.sporesAnimB = m.top.findNode("sporesAnimB")
    m.upsideTimer = m.top.createChild("Timer")
    m.upsideTimer.duration = m.upsideLightningEvery
    m.upsideTimer.repeat = true
    m.upsideTimer.observeField("fire", "onUpsideLightning")
end sub

' Shows or hides everything that changes in the Upside Down. applyScene()
' sets the images; this sub does the rest.
sub updateUpsideDown()
    on = m.upside
    m.farLane.visible = not on
    m.nearLane.visible = not on
    for each node in m.upsideHidden
        node.visible = not on
    end for
    m.spores.visible = on
    if on
        m.sporesAnimA.control = "start"
        m.sporesAnimB.control = "start"
        m.upsideTimer.control = "start"
        ' A flight that already started ends now (see onPlaneState)
        if m.plane.visible then m.planeAnim.control = "stop"
    else
        m.sporesAnimA.control = "stop"
        m.sporesAnimB.control = "stop"
        m.upsideTimer.control = "stop"
        m.upsideFlashAnim.control = "stop"
        m.upsideSkyFlash.opacity = 0
        m.upsideBolt.opacity = 0
        m.upsideFlash.opacity = 0
    end if
end sub

' One lightning flash. It is a different random pattern each time: two to
' four bright pulses with short dark gaps, with one of the bolt images at a
' random place in the clouds. The sky flash goes up to
' m.upsideSkyMax, the flash over everything to m.upsideFrontMax, and the bolt
' to fully visible.
sub onUpsideLightning()
    if not m.upside then return
    m.upsideBolt.uri = "pkg:/images/bolt_" + (Rnd(3) - 1).ToStr() + ".png"
    ' The bolt starts in the clouds and its lower end goes behind the mountains
    m.upsideBolt.translation = [40 + Rnd(1400), 100 + Rnd(40)]
    total = m.upsideFlashAnim.duration
    times = [0.0]
    levels = [0.0]
    t = 0.0
    pulses = 1 + Rnd(3)
    for i = 1 to pulses
        t = t + 0.04 + Rnd(0) * 0.22
        peak = 0.55 + Rnd(0) * 0.45
        hold = 0.04 + Rnd(0) * 0.12
        times.Append([t, t + 0.03, t + 0.03 + hold, t + 0.07 + hold])
        levels.Append([0.0, peak, peak * 0.4, 0.0])
        t = t + 0.07 + hold
    end for
    times.Push(total)
    levels.Push(0.0)
    keys = []
    sky = []
    front = []
    for i = 0 to times.Count() - 1
        keys.Push(times[i] / total)
        sky.Push(levels[i] * m.upsideSkyMax)
        front.Push(levels[i] * m.upsideFrontMax)
    end for
    m.upsideFlashAnim.control = "stop"
    m.upsideSkyKeys.key = keys
    m.upsideSkyKeys.keyValue = sky
    m.upsideBoltKeys.key = keys
    m.upsideBoltKeys.keyValue = levels
    m.upsideFrontKeys.key = keys
    m.upsideFrontKeys.keyValue = front
    m.upsideFlashAnim.control = "start"
end sub
