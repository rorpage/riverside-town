' The text on the theater marquees. Each theater in the town has a text area
' on its marquee board (marquees in the settings: x and y in townStrip
' coordinates, the width, the height, and the theater's own text, from
' marquee_area() in tools/riverside/buildings.py). A label over that area
' shows today's birthdays and messages for the marquee
' (currentMessages("marquee") in messages.brs), one at a time, each for
' m.marqueeHold seconds. When there are none, it shows the theater's own text.
' The text is in capital letters, like the letters on a real marquee.
' These subs run in the scope of MainScene (see MainScene.xml), so they
' share m with MainScene.brs.

sub buildMarquee()
    m.marqueeLabels = []
    m.marqueeDefs = []
    m.marqueeIndex = 0
    if m.config.marquees.Count() = 0 then return
    ' Text sizes, largest first. MARQUEE_SIZES in buildings.py has the same
    ' sizes, for the previews.
    m.marqueeSizes = [30, 26, 22, 18, 15]
    m.marqueeFonts = []
    for each size in m.marqueeSizes
        font = CreateObject("roSGNode", "Font")
        font.uri = "font:BoldSystemFontFile"
        font.size = size
        m.marqueeFonts.Push(font)
    end for

    strip = m.top.findNode("townStrip")
    fadeOut = m.top.createChild("Animation")
    fadeOut.id = "marqueeFadeOut"
    fadeOut.duration = 0.4
    fadeOut.repeat = false
    fadeIn = m.top.createChild("Animation")
    fadeIn.id = "marqueeFadeIn"
    fadeIn.duration = 0.4
    fadeIn.repeat = false
    n = 0
    for each d in m.config.marquees
        ' Town section 0 is shown twice in the strip, so a theater there gets
        ' a label in the second copy too
        xs = [d["x"]]
        if d["x"] < 1920 then xs.Push(d["x"] + m.sections * 1920)
        for each x in xs
            label = strip.createChild("Label")
            label.id = "marquee" + n.ToStr() + "_text"
            label.translation = [x, d["y"]]
            label.width = d["w"]
            label.height = d["h"]
            label.wrap = true
            label.horizAlign = "center"
            label.vertAlign = "center"
            label.color = "0x1F2A33FF"
            m.marqueeLabels.Push(label)
            m.marqueeDefs.Push(d)
            for each pair in [[fadeOut, [1.0, 0.0]], [fadeIn, [0.0, 1.0]]]
                interp = pair[0].createChild("FloatFieldInterpolator")
                interp.key = [0.0, 1.0]
                interp.keyValue = pair[1]
                interp.fieldToInterp = label.id + ".opacity"
            end for
            n = n + 1
        end for
    end for
    m.marqueeFadeOut = fadeOut
    m.marqueeFadeIn = fadeIn
    fadeOut.observeField("state", "onMarqueeFaded")
    m.marqueeNext = []
    for i = 0 to m.marqueeLabels.Count() - 1
        text = marqueeText(i)
        m.marqueeNext.Push(text)
        setMarqueeText(m.marqueeLabels[i], text, m.marqueeDefs[i])
    end for
    makeTimer(m.marqueeHold, "onMarqueeTick")
end sub

' The text that label number i shows now
function marqueeText(i as integer) as string
    texts = currentMessages("marquee")
    if texts.Count() = 0 then texts = [m.marqueeDefs[i]["text"]]
    return UCase(texts[m.marqueeIndex MOD texts.Count()])
end function

' Moves to the next text. If any label's text changes, the labels fade out,
' change, and fade back in.
sub onMarqueeTick()
    m.marqueeIndex = m.marqueeIndex + 1
    changed = false
    for i = 0 to m.marqueeLabels.Count() - 1
        m.marqueeNext[i] = marqueeText(i)
        if m.marqueeNext[i] <> m.marqueeLabels[i].text then changed = true
    end for
    if changed then m.marqueeFadeOut.control = "start"
end sub

sub onMarqueeFaded(event as object)
    if event.getData() <> "stopped" then return
    for i = 0 to m.marqueeLabels.Count() - 1
        setMarqueeText(m.marqueeLabels[i], m.marqueeNext[i], m.marqueeDefs[i])
    end for
    m.marqueeFadeIn.control = "start"
end sub

' Shows text in the largest size at which it fits the text area, split into
' lines at spaces. A size fits when its lines, each 1.2 times the size apart,
' fit in the height, and every line fits in the width. This is the same rule
' as marquee_lines() in tools/riverside/buildings.py. At the smallest size,
' a line that still does not fit is cut off with "...".
sub setMarqueeText(label as object, text as string, d as object)
    words = text.Split(" ")
    lines = []
    for k = 0 to m.marqueeSizes.Count() - 1
        font = m.marqueeFonts[k]
        most = Int(d["h"] / (m.marqueeSizes[k] * 1.2))
        if most < 1 then most = 1
        lines = []
        fits = true
        for each word in words
            if word <> ""
                if lines.Count() > 0 and measureText(lines[lines.Count() - 1] + " " + word, font) <= d["w"]
                    lines[lines.Count() - 1] = lines[lines.Count() - 1] + " " + word
                else
                    if measureText(word, font) > d["w"] then fits = false
                    lines.Push(word)
                end if
            end if
        end for
        if fits and lines.Count() <= most then exit for
    end for
    label.font = font
    label.maxLines = lines.Count()
    joined = ""
    for i = 0 to lines.Count() - 1
        if i > 0 then joined = joined + Chr(10)
        joined = joined + lines[i]
    end for
    label.text = joined
end sub
