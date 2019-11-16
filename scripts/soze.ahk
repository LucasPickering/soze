Command = wsl.exe curl -XPOST -H 'Content-Type: application/json' "http://riolu/api/lcd/normal"

^+X::
    Run, %Command% -d '{"mode": "off"}'
    return

^+C::
    Run, %Command% -d '{"mode": "clock"}'
    return
