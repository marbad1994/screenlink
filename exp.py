import subprocess
from pynput.keyboard import Key, Controller

window_name = "Music"
output = subprocess.check_output(["wmctrl", "-l"], text=True)
for row in output.split("\n"):
    if window_name in row:
        window = row.split()[0]


print(output)


print(window)
subprocess.check_output(["xdotool", "windowactivate", window], text=True)
subprocess.check_output(["xdotool", "key", "ctrl+alt+g"], text=True)
subprocess.check_output(["xdotool", "key", "ctrl+alt+0xff53"], text=True)
subprocess.check_output(["xdotool", "key", "ctrl+alt+f"], text=True)

