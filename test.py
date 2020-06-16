import sys, os, subprocess, time, signal
s = '''ffmpeg -f dshow -i video="screen-capture-recorder" -pix_fmt yuv420p -codec:v libx264 -bf 0 -g 300 -f mp4 1727405048demo4.mp4'''

p = subprocess.Popen(s, shell=True, stdout=sys.stdout, stderr=sys.stderr)

time.sleep(5)

os.kill(p.pid, signal.CTRL_C_EVENT)
