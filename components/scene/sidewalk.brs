' The animals, the bikes, and the street lamps on the sidewalk, and the bikes
' beside the radio station. The animals and the bikes are hidden while it
' rains or snows, and the bikes are also hidden in winter (see updateOutside).
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
    pet.visible = m.precipKind = ""
    m.outsidePosters.Push(pet)
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

' The bikes in the bike racks. bikes in the settings has the [x, y] of each
' rack's bike image, bike_rack_<n>.png, in townStrip coordinates (BIKE_BOX in
' tools/riverside/buildings.py). The racks themselves are part of the town
' image. The bikes are added before the animals, so the animals are in front
' of them. Town section 0 is shown twice in the strip, so bikes there are
' added to the second copy too.
sub buildBikes()
    strip = m.top.findNode("townStrip")
    stripW = m.sections * 1920
    n = 0
    for each spot in m.config.bikes
        uri = "pkg:/images/bike_rack_" + n.ToStr() + ".png"
        addBikes(strip, uri, spot[0], spot[1], 184, 70)
        if spot[0] < 1920 then addBikes(strip, uri, spot[0] + stripW, spot[1], 184, 70)
        n = n + 1
    end for
end sub

function addBikes(strip as object, uri as string, x as integer, y as integer, w as integer, h as integer) as object
    bikes = strip.createChild("Poster")
    bikes.uri = uri
    bikes.width = w
    bikes.height = h
    bikes.translation = [x, y]
    bikes.visible = bikesOut()
    m.bikePosters.Push(bikes)
    return bikes
end function

' The two bikes beside the radio station. radioBikes in the settings is
' [x, y, width, height] of radio_bikes_<period>.png in hills strip
' coordinates, or empty if there are none. Hills tile A is at x = 0 and again
' at x = 5760, so there are bikes in both copies. Called before applyScene(),
' which sets the image for the time of day.
sub buildRadioBikes()
    m.radioBikes = []
    spot = m.config.radioBikes
    if spot.Count() < 4 then return
    strip = m.top.findNode("hillsStrip")
    for i = 0 to 1
        m.radioBikes.Push(addBikes(strip, "", spot[0] + i * m.layerWidths.hills, spot[1], spot[2], spot[3]))
    end for
end sub

' Hides the animals and the bikes while it rains or snows, and shows them
' at other times. The bikes are also hidden in winter (the ground is winter
' in winter and while snow is falling). applyScene() calls it when the
' weather or the season changes.
sub updateOutside()
    outside = m.precipKind = ""
    for each poster in m.outsidePosters
        poster.visible = outside
    end for
    showBikes = bikesOut()
    for each poster in m.bikePosters
        poster.visible = showBikes
    end for
    for each poster in m.radioBikes
        poster.uri = "pkg:/images/radio_bikes_" + m.period + ".png"
    end for
end sub

function bikesOut() as boolean
    return m.precipKind = "" and m.ground <> "winter"
end function

' The street lamps. lamps in the settings is the x of each lamp post in
' townStrip coordinates. The lamps are separate posters, added after the
' parked car, the bikes, and the animals, so the animals walk behind them. Town section 0
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
