' Downloads the network settings file (external_config_url in town.json) and
' keeps the last good copy in the Roku registry. components/scene/external.brs
' applies the settings. Network calls must run in a Task node, not on the
' render thread.
'
' What happens to the saved copy:
'   - A good download (status 200 and valid JSON) replaces it.
'   - A 404 or 410 means the file was removed on purpose. The saved copy is
'     deleted, and the scene goes back to the settings in the zip.
'   - Any other problem (no network, server down, invalid JSON) keeps it.
'   - It is used at startup only if it is from the same address and is not
'     older than keepDays.

sub init()
    m.top.functionName = "fetchConfig"
end sub

sub fetchConfig()
    if m.top.readSaved then m.top.saved = readSaved(m.top.url, m.top.keepDays)

    xfer = CreateObject("roUrlTransfer")
    port = CreateObject("roMessagePort")
    xfer.SetMessagePort(port)
    xfer.SetCertificatesFile("common:/certs/ca-bundle.crt")
    xfer.InitClientCertificates()
    xfer.SetUrl(m.top.url)
    if not xfer.AsyncGetToString()
        m.top.result = { status: "error", reason: "the request could not start" }
        return
    end if
    msg = wait(15000, port)
    if type(msg) <> "roUrlEvent"
        xfer.AsyncCancel()
        m.top.result = { status: "error", reason: "no answer after 15 seconds" }
        return
    end if

    code = msg.GetResponseCode()
    if code = 404 or code = 410
        deleteSaved()
        m.top.result = { status: "removed" }
        return
    end if
    if code <> 200
        ' Negative codes are network errors, for example -7 when the server
        ' does not accept the connection.
        m.top.result = { status: "error", reason: "response code " + code.ToStr() }
        return
    end if

    text = msg.GetString()
    data = ParseJson(text)
    if type(data) <> "roAssociativeArray"
        m.top.result = { status: "error", reason: "the file is not a valid JSON object" }
        return
    end if
    version = data["version"]
    if version <> invalid and GetInterface(version, "ifToStr") <> invalid and Val(version.ToStr()) > 1
        m.top.result = { status: "error", reason: "the file is version " + version.ToStr() + ", which this screensaver does not know" }
        return
    end if
    writeSaved(m.top.url, text)
    m.top.result = { status: "ok", data: data }
end sub

function registry() as object
    return CreateObject("roRegistrySection", "external_config")
end function

' Returns { data, saved } for the saved copy, or {} if there is none, it is
' from a different address, or it is older than keepDays.
function readSaved(url as string, keepDays as integer) as object
    sec = registry()
    if not sec.Exists("copy") then return {}
    copy = ParseJson(sec.Read("copy"))
    if type(copy) <> "roAssociativeArray" then return {}
    if copy["url"] <> url then return {}
    saved = copy["saved"]
    if saved = invalid then return {}
    now = CreateObject("roDateTime").AsSeconds()
    if now - saved > keepDays * 86400 then return {}
    data = ParseJson(copy["text"])
    if type(data) <> "roAssociativeArray" then return {}
    return { data: data, saved: saved }
end function

' The registry holds at most 16 KB for the whole app, so a larger file is not
' saved. It is still used while the screensaver runs.
sub writeSaved(url as string, text as string)
    if Len(text) > 12000
        print "ExternalConfigTask: the file is too large to save (over 12000 characters)"
        return
    end if
    now = CreateObject("roDateTime").AsSeconds()
    sec = registry()
    sec.Write("copy", FormatJson({ url: url, saved: now, text: text }))
    sec.Flush()
end sub

sub deleteSaved()
    sec = registry()
    if sec.Exists("copy")
        sec.Delete("copy")
        sec.Flush()
    end if
end sub
