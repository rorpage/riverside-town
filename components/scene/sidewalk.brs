' The animals and the street lamps on the sidewalk.
' These subs run in the scope of MainScene (see MainScene.xml), so they
' share m with MainScene.brs.

' Places the animals from the settings at random spots on the sidewalk when
' the screensaver starts. They are children of townStrip, so they scroll with
' the town. Town section 0 is shown twice in the strip, so an animal there is
' added to the second copy too. Each animal stays at least 140 px from the
' others, if there is room.
sub placeAnimals()
    ' The animals' feet are at screen y = 924, in the middle of the sidewalk.
    ' The strip starts at screen y = 550.
    feetY = 924 - 550
    stripW = m.sections * 1920
    strip = m.top.findNode("townStrip")
    used = []
    for each a in m.config.pets
        x = 0
        for tries = 1 to 50
            x = 40 + Rnd(stripW - 120)
            clear = true
            for each u in used
                if Abs(u - x) < 140 or stripW - Abs(u - x) < 140 then clear = false
            end for
            if clear then exit for
        end for
        used.Push(x)
        addAnimal(strip, a, x, feetY)
        if x < 1920 then addAnimal(strip, a, x + stripW, feetY)
    end for
end sub

' An animal with night: true in the settings also has an image ending in
' _night, which is shown at night. applyScene() calls updateAnimals() when the
' time of day changes.
sub addAnimal(strip as object, a as object, x as integer, feetY as integer)
    pet = strip.createChild("Poster")
    pet.uri = "pkg:/images/" + a.image + ".png"
    pet.width = a.w
    pet.height = a.h
    pet.translation = [x, feetY - a.h]
    if a.DoesExist("night")
        if a.night = true
            m.nightAnimals.Push({ poster: pet, image: a.image })
            updateAnimals(m.period)
        end if
    end if
end sub

sub updateAnimals(period as string)
    suffix = ""
    if period = "night" then suffix = "_night"
    for each a in m.nightAnimals
        a.poster.uri = "pkg:/images/" + a.image + suffix + ".png"
    end for
end sub

' The street lamps. lamps in the settings is the x of each lamp post in
' townStrip coordinates. The lamps are separate posters, added after the
' parked car and the animals, so the animals walk behind them. Town section 0
' is shown twice in the strip, so a lamp there is added to the second copy
' too. The lamp image is 72 x 168 pixels, with the post 36 pixels from its left
' edge and its top at screen y = 772 (LAMP_BOX in tools/riverside/buildings.py).
sub buildLamps()
    strip = m.top.findNode("townStrip")
    stripW = m.sections * 1920
    for each x in m.config.lamps
        addLamp(strip, x)
        if x < 1920 then addLamp(strip, x + stripW)
    end for
    updateLamps()
end sub

sub addLamp(strip as object, x as integer)
    lamp = strip.createChild("Poster")
    lamp.width = 72
    lamp.height = 168
    lamp.translation = [x - 36, 772 - 550]
    m.lampPosters.Push(lamp)
end sub

' The lamps are lit at dusk and night, have snow on top in winter, and have
' a wreath in December
sub updateLamps()
    name = "street_lamp_"
    if m.christmas then name = name + "christmas_"
    if m.ground = "winter" then name = name + "winter_"
    for each lamp in m.lampPosters
        lamp.uri = "pkg:/images/" + name + m.period + ".png"
    end for
end sub
