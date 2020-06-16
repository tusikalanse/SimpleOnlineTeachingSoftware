import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import *
from ffmpy3 import FFmpeg
from multiprocessing import Process
import filter
import os, subprocess, time, signal

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

def start(video, audio):
    inputstream = "video=" + video
    if (audio != "不使用音频"):
        inputstream = inputstream + ":audio=" + audio
    ff = FFmpeg(
        inputs={inputstream:"-rtbufsize 2048M -f dshow"},
        outputs={"rtmp://129.211.56.193:1935/live/test":" -pix_fmt yuv420p -codec:v libx264 -bf 0 -g 300 -f flv"}
    )
    return ff.cmd

class outerprocess(object):
    def __init__(self):
        super().__init__()
        self.process = None
    def start(self, args):
        self.p = subprocess.Popen(start(*args), shell=True, stdout=sys.stdout, stderr=sys.stderr)
    def end(self):
        os.kill(self.p.pid, signal.CTRL_C_EVENT)

out = outerprocess()

class CallHandler(QObject):
    @pyqtSlot()
    def getdevices(self):
        videos, audios = get_devices()
        for video in videos:
            view.page().runJavaScript("addvideo(\"" + video + "\")")
        for audio in audios:
            view.page().runJavaScript("addaudio(\"" + audio + "\")")
        view.page().runJavaScript("addaudio(\"" + "不使用音频" + "\")")
        # view.page().runJavaScript('uptext("hello, Pythongjhkkkk");')
        # print('call received')
 
    @pyqtSlot(str)
    def startlive(self, device):
        # print(device)
        video, audio = device.split(',')
        video = video.strip()
        audio = audio.strip()
        out.start((video, audio))
        # p = Process(target=startlive.start, args=(video, audio))
        # p.start()
    
    @pyqtSlot()
    def endlive(self):
        out.end()
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = QWebEngineView()
    channel = QWebChannel()
    handler = CallHandler()
    channel.registerObject('pyjs', handler)##前者是str，后者是一个QObject（里面放着需要调用的函数）
    view.page().setWebChannel(channel)
    view.setWindowTitle("直播 demo")
    view.load(QUrl(r'file:///C:/Users/wanghao/Desktop/在家上课/综合项目实践/SimpleOnlineTeachingSoftware/user/index.html'))
    view.show()
    app.exit(app.exec_())

    # app = QApplication(sys.argv)
    # view = QWebEngineView()
    # channel = QWebChannel()
    # handler = CallHandler()
    # channel.registerObject('pyjs', handler)##前者是str，后者是一个QObject（里面放着需要调用的函数）
    # view.page().setWebChannel(channel)
    # url_string = "file:///C:/Users/wanghao/Desktop/在家上课/综合项目实践/实验3/test/test.html"
    # view.load(QUrl(url_string))
    # view.show()
    # sys.exit(app.exec_())