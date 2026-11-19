' The airplane that flies across the sky.
' These subs run in the scope of MainScene (see MainScene.xml), so they
' share m with MainScene.brs.

' Starts a flight, or waits again if the weather is bad for flying.
sub onPlaneTimer()
    if m.precipKind <> "" or m.fog.visible or m.storm or m.upside
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
