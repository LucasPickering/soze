#SingleInstance, force

Command = wsl.exe curl -XPOST -H 'Content-Type: application/json' http://riolu/api/{1}/normal -d '{2}'

; LED and LCD off
^!+X::
    Run, % Format(Command, "led", "{""mode"": ""off""}"),, Hide
    Run, % Format(Command, "lcd", "{""mode"": ""off""}"),, Hide
    return

; LCD Clock
^!+C::
    Run, % Format(Command, "lcd", "{""mode"": ""clock""}"),, Hide
    return

; LED Fade
^!+N::
    Run, % Format(Command, "led", "{""mode"": ""fade""}"),, Hide
    return
