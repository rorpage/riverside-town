' The cars that drive along the street, and the car parked at the gas
' station.
' These subs run in the scope of MainScene (see MainScene.xml), so they
' share m with MainScene.brs.

sub buildCars()
    m.cars = {}
    m.laneBusy = { near: "", far: "" }
    ' The time, in milliseconds on m.clock, when each lane can take a car again
    m.laneReadyAt = { near: 0, far: 0 }
    m.clock = CreateObject("roTimespan")
    for each def in m.carDefs
        makeCar(def)
    end for
end sub

sub makeCar(def as object)
    name = def.name
    car = m.nearLane.createChild("Group")
    car.id = name + "_car"
    car.visible = false

    body = car.createChild("Poster")
    body.uri = "pkg:/images/car_" + name + ".png"
    body.width = def.w
    body.height = def.h

    ' Wheel spin: one full turn per (2 * pi * radius) pixels of road
    spin = m.top.createChild("Animation")
    spin.id = name + "_spin"
    spin.repeat = true
    spin.easeFunction = "linear"
    spin.duration = 2 * 3.14159 * def.r / def.ground
    wheels = []
    interps = []
    i = 0
    for each w in def.wheels
        wheel = car.createChild("Poster")
        wheel.id = name + "_wheel" + i.ToStr()
        wheel.uri = wheelUri(def)
        wheel.width = def.r * 2
        wheel.height = def.r * 2
        wheel.translation = [w[0] - def.r, w[1] - def.r]
        wheel.scaleRotateCenter = [def.r, def.r]
        interp = spin.createChild("FloatFieldInterpolator")
        interp.key = [0.0, 1.0]
        interp.keyValue = [0.0, -6.28318]
        interp.fieldToInterp = wheel.id + ".rotation"
        wheels.Push(wheel)
        interps.Push(interp)
        i = i + 1
    end for

    move = m.top.createChild("Animation")
    move.id = name + "_move"
    move.repeat = false
    move.easeFunction = "linear"
    moveInterp = move.createChild("Vector2DFieldInterpolator")
    moveInterp.key = [0.0, 1.0]
    moveInterp.fieldToInterp = car.id + ".translation"
    move.observeField("state", "onCarMoveState")

    timer = m.top.createChild("Timer")
    timer.id = name + "_timer"
    timer.repeat = false
    timer.duration = 1 + Rnd(6)
    if isSpecial(def) then timer.duration = m.specialFirstMin + Rnd(m.specialFirstMore)
    timer.observeField("fire", "onCarTimer")
    timer.control = "start"

    m.cars[name] = { def: def, node: car, body: body, wheels: wheels, interps: interps, move: move, moveInterp: moveInterp, spin: spin, timer: timer, lane: "" }
end sub

' The wheel image for a car. Special cars have their own wheels.
function wheelUri(def as object) as string
    if isSpecial(def) then return "pkg:/images/wheel_" + def.name + ".png"
    return "pkg:/images/wheel.png"
end function

' True for a special car: one with special: true in allCars
function isSpecial(def as object) as boolean
    return def.DoesExist("special")
end function

function carNameFromId(id as string) as string
    return Left(id, Instr(1, id, "_") - 1)
end function

sub onCarTimer(event as object)
    spawnCar(carNameFromId(event.getNode()))
end sub

' Sends a car across the screen. Only one car uses a lane at a time so faster
' cars never drive through slower ones, and a lane stays empty for 1 to 10
' seconds after a car leaves it. If no lane is free, the car tries again in
' half a second.
' Near lane: full size. Far lane: slightly smaller.
' With driveOn "right" in the settings, the near lane drives left to right and
' the far lane right to left. With "left", the directions are the other way
' around. A car that drives right to left uses a mirrored copy of the car image
' instead of a negative scale, because Roku does not draw spinning children
' correctly inside a mirrored (negative scale) group.
sub spawnCar(name as string)
    c = m.cars[name]
    free = []
    now = m.clock.TotalMilliseconds()
    for each laneName in ["near", "far"]
        if m.laneBusy[laneName] = "" and now >= m.laneReadyAt[laneName] then free.Push(laneName)
    end for
    if free.Count() = 0
        c.timer.duration = 0.5
        c.timer.control = "start"
        return
    end if

    lane = free[Rnd(free.Count()) - 1]
    m.laneBusy[lane] = name
    c.lane = lane
    d = c.def
    car = c.node
    car.getParent().removeChild(car)

    if lane = "near"
        s = 1.0
        groundY = 1072
        m.nearLane.appendChild(car)
        facingLeft = (m.config.driveOn = "left")
    else
        s = 0.86
        groundY = 1002
        m.farLane.appendChild(car)
        facingLeft = (m.config.driveOn <> "left")
    end if
    if facingLeft
        speed = d.ground + m.cameraSpeed   ' moving against the scroll direction looks faster
        fromX = 1960
        toX = -d.w - 40
    else
        speed = d.ground - m.cameraSpeed   ' moving with the scroll direction looks slower
        fromX = -d.w - 40
        toX = 1960
    end if

    car.scaleRotateCenter = [d.w / 2, d.h / 2]
    car.scale = [s, s]

    ' Make the car face its direction of travel: swap the body image, move the wheels to the
    ' mirrored positions, and reverse the spin direction.
    suffix = ""
    turn = -6.28318
    if facingLeft
        suffix = "_left"
        turn = 6.28318
    end if
    c.body.uri = "pkg:/images/car_" + d.name + suffix + ".png"
    for i = 0 to c.wheels.Count() - 1
        wx = d.wheels[i][0]
        if facingLeft then wx = d.w - wx
        c.wheels[i].translation = [wx - d.r, d.wheels[i][1] - d.r]
        c.wheels[i].rotation = 0
        c.interps[i].keyValue = [0.0, turn]
    end for
    y = groundY - d.h / 2 - (d.bottom - d.h / 2) * s
    c.moveInterp.keyValue = [[fromX, y], [toX, y]]
    c.move.duration = Abs(toX - fromX) / speed
    car.translation = [fromX, y]
    car.visible = true
    c.spin.control = "start"
    c.move.control = "start"
end sub

sub onCarMoveState(event as object)
    if event.getData() <> "stopped" then return
    name = carNameFromId(event.getNode())
    c = m.cars[name]
    if c = invalid then return
    if c.lane = "" then return
    c.node.visible = false
    c.spin.control = "stop"
    m.laneBusy[c.lane] = ""
    m.laneReadyAt[c.lane] = m.clock.TotalMilliseconds() + m.laneGapMin + Rnd(m.laneGapMax - m.laneGapMin + 1) - 1
    c.lane = ""
    c.timer.duration = 2 + Rnd(7)
    if isSpecial(c.def) then c.timer.duration = m.specialWaitMin + Rnd(m.specialWaitMore)
    c.timer.control = "start"
end sub

' Parks a randomly chosen car, facing a random direction, at the gas station.
' Special cars never park there.
' parkedCarX in the settings is the center of the parking space in townStrip
' coordinates, or -1 if the town has no gas station. The car is a child of
' townStrip, so it scrolls with the town. The wheels do not spin.
sub parkCar()
    regular = []
    for each def in m.carDefs
        if not isSpecial(def) then regular.Push(def)
    end for
    if m.config.parkedCarX < 0 or regular.Count() = 0 then return
    d = regular[Rnd(regular.Count()) - 1]
    facingLeft = Rnd(2) = 2
    ' The strip starts at screen y = 550, and the station ground is at screen y = 898.
    addParkedCar(d, facingLeft, m.config.parkedCarX, "parked_car")
    ' Town section 0 is shown twice in the strip, so a car parked there is
    ' added to the second copy too
    if m.config.parkedCarX < 1920 then addParkedCar(d, facingLeft, m.config.parkedCarX + m.sections * 1920, "parked_car_copy")
end sub

sub addParkedCar(d as object, facingLeft as boolean, centerX as integer, id as string)
    s = 0.78
    groundY = 898 - 550
    car = m.top.findNode("townStrip").createChild("Group")
    car.id = id
    car.scale = [s, s]
    car.translation = [centerX - d.w * s / 2, groundY - d.bottom * s]

    suffix = ""
    if facingLeft then suffix = "_left"
    body = car.createChild("Poster")
    body.uri = "pkg:/images/car_" + d.name + suffix + ".png"
    body.width = d.w
    body.height = d.h
    for each w in d.wheels
        wx = w[0]
        if facingLeft then wx = d.w - wx
        wheel = car.createChild("Poster")
        wheel.uri = wheelUri(d)
        wheel.width = d.r * 2
        wheel.height = d.r * 2
        wheel.translation = [wx - d.r, w[1] - d.r]
    end for
end sub
