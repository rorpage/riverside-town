' The banner plane: a larger copy of the airplane that tows a banner with
' today's birthdays and messages (currentMessages("banner") in messages.brs).
' Each flight shows the next text, in turn. It does not fly when there is no
' text for today, or in rain, snow, fog, or thunderstorms. It flies whether
' or not the small airplane is turned on.
' These subs run in the scope of MainScene (see MainScene.xml), so they
' share m with MainScene.brs.
'
' The parts, in the bannerPlane group, for a plane flying right (from left
' to right): the banner, the rope, and the plane. For a plane flying left the
' order is the other way around, and the plane and the rope use their left
' images. The rope image is 84x64: its pole is 3 pixels from one end, on the
' front edge of the banner, and its other end is at the tail of the plane,
' 12 pixels in from the back of the plane image and 36 pixels below its top
' (banner_rope() in tools/riverside/sprites.py). The banner flies straight
' behind the plane: its center is at the same height as the tail.

sub startBanner()
    m.bannerPlane = m.top.findNode("bannerPlane")
    m.bannerStripe = m.top.findNode("bannerStripe")
    m.bannerCloth = m.top.findNode("bannerCloth")
    m.bannerLabel = m.top.findNode("bannerLabel")
    m.bannerRope = m.top.findNode("bannerRope")
    m.bannerBody = m.top.findNode("bannerBody")
    m.bannerStrobe = m.top.findNode("bannerStrobe")
    m.bannerAnim = m.top.findNode("bannerAnim")
    m.bannerMove = m.top.findNode("bannerMove")
    m.bannerStrobeAnim = m.top.findNode("bannerStrobeAnim")
    m.bannerAnim.observeField("state", "onBannerState")
    m.bannerLeft = false
    m.bannerIndex = 0
    m.bannerTimer = m.top.createChild("Timer")
    m.bannerTimer.repeat = false
    m.bannerTimer.observeField("fire", "onBannerTimer")
    m.bannerTimer.duration = m.bannerFirstMin + Rnd(m.bannerFirstMore)
    m.bannerTimer.control = "start"
    updateBannerImage()
end sub

' Starts a flight with the next text for today, or waits again if there is
' no text or the weather is bad for flying.
sub onBannerTimer()
    texts = currentMessages("banner")
    if texts.Count() = 0 or m.precipKind <> "" or m.fog.visible or m.storm
        scheduleBanner()
        return
    end if
    text = texts[m.bannerIndex MOD texts.Count()]
    m.bannerIndex = m.bannerIndex + 1
    m.bannerLeft = Rnd(2) = 2
    width = layoutBanner(text)

    y = 262 + Rnd(38)
    if m.bannerLeft
        ' Flying against the scroll direction looks faster
        fromX = 1940
        toX = -width - 20
        speed = m.bannerSpeed + m.layerSpeeds.near
    else
        fromX = -width - 20
        toX = 1940
        speed = m.bannerSpeed - m.layerSpeeds.near
    end if
    m.bannerMove.keyValue = [[fromX, y], [toX, y]]
    m.bannerAnim.duration = Abs(toX - fromX) / speed
    m.bannerPlane.translation = [fromX, y]
    m.bannerPlane.visible = true
    updateBannerImage()
    m.bannerAnim.control = "start"
end sub

sub onBannerState(event as object)
    if event.getData() <> "stopped" then return
    m.bannerPlane.visible = false
    m.bannerStrobeAnim.control = "stop"
    scheduleBanner()
end sub

sub scheduleBanner()
    m.bannerTimer.duration = m.bannerWaitMin + Rnd(m.bannerWaitMore)
    m.bannerTimer.control = "start"
end sub

' Sets the text and places the parts for the direction in m.bannerLeft.
' Returns the width of the whole group: the banner, the rope, and the plane.
function layoutBanner(text as string) as integer
    ' The label gets the width of the text, plus a little, so the text is
    ' never cut off with "...".
    m.bannerLabel.text = text
    textWidth = measureText(text, m.bannerLabel.font)
    if textWidth <= 0 then textWidth = Len(text) * 22
    m.bannerLabel.width = textWidth + 4
    bannerWidth = textWidth + 48

    if m.bannerLeft
        planeX = 0
        ropeX = 168 - 12
        bannerX = ropeX + 84 - 3
    else
        bannerX = 0
        ropeX = bannerWidth - 3
        planeX = ropeX + 84 - 12
    end if
    ' The banner is 60 pixels tall, from 6 to 66 pixels below the top of the
    ' plane image, so its center is level with the tail (y=36). The red
    ' stripes are 5 pixels tall, on the top and the bottom.
    m.bannerStripe.translation = [bannerX, 6]
    m.bannerStripe.width = bannerWidth
    m.bannerCloth.translation = [bannerX, 11]
    m.bannerCloth.width = bannerWidth
    m.bannerLabel.translation = [bannerX + 22, 6]
    m.bannerRope.translation = [ropeX, 4]
    m.bannerBody.translation = [planeX, 0]
    m.bannerPlaneX = planeX
    return bannerWidth + 237
end function

' Sets the images and colors for the direction and the time of day. The
' strobe on the tail blinks at dusk and night, and is larger and brighter at
' night, like the small airplane's.
sub updateBannerImage()
    if m.bannerPlane = invalid or m.period = invalid then return
    suffix = ""
    if m.bannerLeft then suffix = "_left"
    m.bannerBody.uri = "pkg:/images/plane_big" + suffix + "_" + m.period + ".png"
    m.bannerRope.uri = "pkg:/images/banner_rope" + suffix + "_" + m.period + ".png"
    colors = m.config.bannerColors[m.period]
    m.bannerStripe.color = colors["stripe"]
    m.bannerCloth.color = colors["cloth"]
    m.bannerLabel.color = colors["text"]

    ' The tail strobe's center is 16 pixels in from the back of the plane
    ' image and 6 pixels below its top.
    centerX = 16
    if m.bannerLeft then centerX = 168 - 16
    if m.bannerPlaneX <> invalid then centerX = centerX + m.bannerPlaneX
    size = 24
    m.bannerStrobe.uri = "pkg:/images/plane_strobe_big.png"
    if m.period = "night"
        size = 48
        m.bannerStrobe.uri = "pkg:/images/plane_strobe_big_night.png"
    end if
    m.bannerStrobe.width = size
    m.bannerStrobe.height = size
    m.bannerStrobe.translation = [centerX - size / 2, 6 - size / 2]
    if m.period = "day"
        m.bannerStrobeAnim.control = "stop"
        m.bannerStrobe.opacity = 0
    else if m.bannerPlane.visible
        m.bannerStrobeAnim.control = "start"
    end if
end sub
