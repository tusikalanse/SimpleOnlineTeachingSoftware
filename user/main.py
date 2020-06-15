import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import *
import get_devices
import startlive
from multiprocessing import Process

class outerprocess(object):
    def __init__(self):
        super().__init__()
        self.process = None
    def start(self, args):
        self.process = Process(target=startlive.start, args=args)
        self.process.daemon = True
        self.process.start()
    def end(self):
        self.process.kill()

out = outerprocess()

class CallHandler(QObject):
    @pyqtSlot()
    def getdevices(self):
        videos, audios = get_devices.get_devices()
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
    view.load(QUrl(r'file:///C:/Users/wanghao/Desktop/在家上课/综合项目实践/实验3/client/index.html'))
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