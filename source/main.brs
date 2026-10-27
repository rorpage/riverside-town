' Riverside Town screensaver
' Roku calls RunScreenSaver() when the screensaver starts.
' A screensaver must not define Main(); if it does, Roku treats it as a normal
' app and does not list it under Settings > Theme > Screensavers.

sub RunScreenSaver()
    screen = CreateObject("roSGScreen")
    port = CreateObject("roMessagePort")
    screen.SetMessagePort(port)
    screen.CreateScene("MainScene")
    screen.Show()
    while true
        msg = Wait(0, port)
        if Type(msg) = "roSGScreenEvent" and msg.IsScreenClosed() then return
    end while
end sub
