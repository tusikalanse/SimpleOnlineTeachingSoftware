from ffmpy3 import FFmpeg
from collections import OrderedDict
import filter

# ff = FFmpeg(
#     inputs={"video=screen-capture-recorder:audio=麦克风阵列 (Conexant SmartAudio HD)":"-rtbufsize 2048M -f dshow",
#             "video=Integrated Camera":"-rtbufsize 512M -f dshow"},
#     outputs={"rtmp://129.211.56.193:1935/live/test":"-filter_complex [1:v]scale=480:320[camera];[0:v][camera]overlay=(main_w-overlay_w):(main_h-overlay_h)  -pix_fmt yuv420p -codec:v libx264 -bf 0 -g 300 -f flv"}
# )

def get_devices():
    string = open("fff.txt", "w")
    ff = FFmpeg(
        inputs={'dummy': "-list_devices true -f dshow"},
    )
    try:
        stdout, stderr = ff.run(stderr=string)
    except:
        pass
    string.close()
    string = open("fff.txt", "r", encoding="utf-8")
    return filter.filter(string.read())

if __name__ == "__main__":
    get_devices()