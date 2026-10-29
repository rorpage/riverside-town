' Downloads current weather plus today's sunrise and sunset from Open-Meteo.
' Network calls must run in a Task node, not on the render thread.

sub init()
    m.top.functionName = "fetchWeather"
end sub

sub fetchWeather()
    url = "https://api.open-meteo.com/v1/forecast"
    url = url + "?latitude=" + m.top.lat + "&longitude=" + m.top.lon
    url = url + "&current=temperature_2m,weather_code,is_day"
    url = url + "&daily=sunrise,sunset&forecast_days=1"
    url = url + "&temperature_unit=" + m.top.unit + "&timezone=auto"

    xfer = CreateObject("roUrlTransfer")
    xfer.SetCertificatesFile("common:/certs/ca-bundle.crt")
    xfer.InitClientCertificates()
    xfer.SetUrl(url)
    body = xfer.GetToString()

    data = ParseJson(body)
    if data = invalid or data.current = invalid
        print "WeatherTask: request failed or returned unexpected data"
        m.top.result = { ok: false }
        return
    end if

    result = {
        ok: true
        temp: data.current.temperature_2m
        code: data.current.weather_code
        isDay: data.current.is_day
        sunrise: ""
        sunset: ""
    }
    if data.daily <> invalid and data.daily.sunrise <> invalid and data.daily.sunrise.Count() > 0
        result.sunrise = data.daily.sunrise[0]
        result.sunset = data.daily.sunset[0]
    end if
    m.top.result = result
end sub
