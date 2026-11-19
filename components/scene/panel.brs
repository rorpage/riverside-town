' The clock and weather panel in the top-right corner.
' These subs run in the scope of MainScene (see MainScene.xml), so they
' share m with MainScene.brs.

sub onClockTick()
    updateClock()
end sub

sub updateClock()
    dt = CreateObject("roDateTime")
    dt.ToLocalTime()
    h = dt.GetHours()
    mins = dt.GetMinutes()
    mm = mins.ToStr()
    if mins < 10 then mm = "0" + mm
    if m.config.clock24
        m.clockLabel.text = h.ToStr() + ":" + mm
        return
    end if
    suffix = "AM"
    if h >= 12 then suffix = "PM"
    h12 = h MOD 12
    if h12 = 0 then h12 = 12
    m.clockLabel.text = h12.ToStr() + ":" + mm + " " + suffix
end sub

' Moves the clock panel to its next position. It fades out, moves while it
' cannot be seen, and fades back in (infoMoveAnim in MainScene.xml).
sub onMoveInfo()
    oldSpot = m.info.translation
    m.infoIndex = (m.infoIndex + 1) MOD m.infoSpots.Count()
    newSpot = m.infoSpots[m.infoIndex]
    m.infoMove.keyValue = [oldSpot, oldSpot, newSpot, newSpot]
    m.infoMoveAnim.control = "start"
end sub
