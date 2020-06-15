from ffmpy3 import FFmpeg
import subprocess
# ff = FFmpeg(
#     inputs={"video=screen-capture-recorder:audio=麦克风阵列 (Conexant SmartAudio HD)":"-rtbufsize 2048M -f dshow",
#             "video=Integrated Camera":"-rtbufsize 512M -f dshow"},
#     outputs={"rtmp://129.211.56.193:1935/live/test":"-filter_complex [1:v]scale=480:320[camera];[0:v][camera]overlay=(main_w-overlay_w):(main_h-overlay_h)  -pix_fmt yuv420p -codec:v libx264 -bf 0 -g 300 -f flv"}
# )

def start(video, audio):
    inputstream = "video=" + video
    if (audio != "不使用音频"):
        inputstream = inputstream + ":audio=" + audio
    ff = FFmpeg(
        inputs={inputstream:"-rtbufsize 2048M -f dshow"},
        outputs={"rtmp://129.211.56.193:1935/live/test":" -pix_fmt yuv420p -codec:v libx264 -bf 0 -g 300 -f flv"}
    )
    print(ff.cmd)
    ff.run()

