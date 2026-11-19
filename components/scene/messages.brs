' Birthdays and messages: the texts to show today on the banner the airplane
' tows and on the marquee sign. They come from birthdays and messages in
' town.json, and the network settings file can replace either list (see
' external.brs).
' These subs run in the scope of MainScene (see MainScene.xml), so they
' share m with MainScene.brs.

' Returns the texts to show today at place, "banner" or "marquee": the
' birthdays first, then the messages, in the order they are listed.
' A birthday on 02-29 shows on February 28 in years without February 29.
function currentMessages(place as string) as object
    return messagesOn(todayText(), place)
end function

' The texts to show at place on the day today, written as "2026-11-19"
function messagesOn(today as string, place as string) as object
    year = Val(Left(today, 4))
    monthDay = Right(today, 5)
    leap = (year MOD 4 = 0 and year MOD 100 <> 0) or year MOD 400 = 0
    out = []
    for each b in m.config.birthdays
        if showsAt(b["where"], place)
            d = b["date"]
            if d = monthDay or (d = "02-29" and monthDay = "02-28" and not leap)
                if b["text"] <> invalid
                    out.Push(b["text"])
                else
                    out.Push("Happy birthday, " + b["name"] + "!")
                end if
            end if
        end if
    end for
    for each msg in m.config.messages
        if showsAt(msg["where"], place)
            started = msg["from"] = invalid or today >= msg["from"]
            ended = msg["until"] <> invalid and today > msg["until"]
            if started and not ended then out.Push(msg["text"])
        end if
    end for
    return out
end function

' True if a text with this "where" value shows at place. A text with no
' "where" value shows at both places.
function showsAt(where as dynamic, place as string) as boolean
    if where = invalid or where = "both" then return true
    return where = place
end function

' Today's date as "2026-11-19", in the Roku's time zone
function todayText() as string
    dt = CreateObject("roDateTime")
    dt.ToLocalTime()
    return dt.GetYear().ToStr() + "-" + twoDigits(dt.GetMonth()) + "-" + twoDigits(dt.GetDayOfMonth())
end function

function twoDigits(n as integer) as string
    if n < 10 then return "0" + n.ToStr()
    return n.ToStr()
end function

' Prints today's texts to the debug console.
sub printMessages()
    print "Messages today: banner " + FormatJson(currentMessages("banner")) + ", marquee " + FormatJson(currentMessages("marquee"))
end sub
