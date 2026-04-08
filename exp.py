import subprocess
import time



# open_windows = subprocess.check_output(["wmctrl", "-l"], text=True)
# if "Remote Desk" not in open_windows:
#     print(open_windows)    
# from pynput.keyboard import Key, Controller

# window_name = "Music"
# output = subprocess.check_output(["wmctrl", "-l"], text=True)
# for row in output.split("\n"):
#     if window_name in row:
#         window = row.split()[0]

# subprocess.check_output(["xdotool", "windowactivate", window], text=True)
# subprocess.check_output(["xdotool", "key", "ctrl+alt+g"], text=True)
# subprocess.check_output(["xdotool", "key", "ctrl+alt+0xff53"], text=True)
# subprocess.check_output(["xdotool", "key", "ctrl+alt+f"], text=True)
h = subprocess.Popen(
    ["ls non_existent_file;"],
    shell=True, stdout=subprocess.DEVNULL)
ret = h.wait()


print("HTHISI ", ret)
# print(h)

# window_name = "Remote Desktop"
# subprocess.run(["pkill", "-9", '-f', "remote-desktop-profile" ], text=True)
# # _ = [subprocess.run(["wmctrl", "-c", window]) for window in open_windows if window_name in window]

# vncviewer_proc = subprocess.Popen(
#     ["firefox", "--new-window", "-P", 'remote-desktop-profile', "https://192.168.50.181:8080/remote.html"]
# )
# time.sleep(1)

# windows = subprocess.check_output(["wmctrl", "-l"], text=True)
# max_tries = 10
# active_window = None
# while window_name not in windows or max_tries < 1:
#     time.sleep(0.5)
#     windows = subprocess.check_output(["wmctrl", "-l"], text=True)
#     max_tries -= 1
# if active_window is None:
#     print ("WÖÖÖÖ")
# print(windows.split("\n"))

# active_window = [window for window in windows.split("\n") if "Remote Desktop" in window][0]
# subprocess.run(["xdotool", "windowactivate", active_window])
# time.sleep(0.2)
# subprocess.run(["xdotool", "key", "ctrl+alt+g"])
# subprocess.run(["xdotool", "key", "ctrl+alt+0xff53"])
# subprocess.run(["xdotool", "key", "ctrl+alt+f"])