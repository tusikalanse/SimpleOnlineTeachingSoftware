import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import *
from PyQt5.QtGui import QDesktopServices
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

def start(video, audio, UID, CID):
    inputstream = ""
    if (video != "不使用视频"):
        inputstream = "video=" + video
    if (audio != "不使用音频"):
        if inputstream != "":
            inputstream = inputstream + ":"
        inputstream = inputstream + "audio=" + audio
    if inputstream == "":
        return ""
    outputstream = "rtmp://yournginxserver:1935/live/" + CID + "_" + UID
    ff = FFmpeg(
        inputs={inputstream:"-rtbufsize 2048M -f dshow"},
        outputs={outputstream:" -pix_fmt yuv420p -codec:v libx264 -bf 0 -g 300 -vf scale=640:360 -f flv"}
    )
    return ff.cmd

class outerprocess(object):
    def __init__(self):
        super().__init__()
        self.running = False
        self.process = None
    def start(self, args):
        self.running = True
        self.p = subprocess.Popen(start(*args), shell=True, stdout=sys.stdout, stderr=sys.stderr)
    def end(self):
        if self.running == True:
            os.kill(self.p.pid, signal.CTRL_C_EVENT)
            self.running = False

out = outerprocess()

class CallHandler(QObject):
    @pyqtSlot()
    def getdevices(self):
        videos, audios = get_devices()
        view.page().runJavaScript("addvideo(\"" + "不使用视频" + "\")")
        view.page().runJavaScript("addaudio(\"" + "不使用音频" + "\")")
        for video in videos:
            view.page().runJavaScript("addvideo(\"" + video + "\")")
        for audio in audios:
            view.page().runJavaScript("addaudio(\"" + audio + "\")")

        # view.page().runJavaScript('uptext("hello, Pythongjhkkkk");')
        # print('call received')
 
    @pyqtSlot(str)
    def startlive(self, device):
        # print(device)
        out.end()
        video, audio, UID, CID = device.split(',')
        video = video.strip()
        audio = audio.strip()
        UID = UID.strip()
        CID = CID.strip()
        if video == "不使用视频" and audio == "不使用音频":
            return
        out.start((video, audio, UID, CID))
        # p = Process(target=startlive.start, args=(video, audio))
        # p.start()
    
    @pyqtSlot()
    def endlive(self):
        out.end()

    @pyqtSlot()
    def whiteboard(self):
        QDesktopServices.openUrl(QUrl(r'http://yourwebserver:8888/whiteboard'))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = QWebEngineView()
    channel = QWebChannel()
    handler = CallHandler()
    channel.registerObject('pyjs', handler)##前者是str，后者是一个QObject（里面放着需要调用的函数）
    view.page().setWebChannel(channel)
    view.setWindowTitle("1727405048 直播系统")
    #view.load(QUrl(r'file:///C:/Users/wanghao/Desktop/在家上课/综合项目实践/SimpleOnlineTeachingSoftware/user/index.html'))
    view.load(QUrl(r'http://yourwebserver:8888'))
    view.show()
    app.exit(app.exec_())
