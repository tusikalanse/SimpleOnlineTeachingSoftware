from ffmpy3 import FFmpeg
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import QWebChannel

import subprocess
from multiprocessing import Process
import re
import json
import os
import sys

#设备名称
class Equipment:
    def __init__(self):
        s = ''
        p = subprocess.Popen('ffmpeg -list_devices true -f dshow -i dummy', shell=False, encoding='utf-8',
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        s += p.stdout.read()
        c = s.split('DirectShow video devices')
        c = c[1].split('DirectShow audio devices')
        include = re.findall(r'\"([^@\"]*)\"', c[0])
        self.video = []
        for i in include:
            if i != 'screen-capture-recorder':
                self.video.append(i)

        self.audio = re.findall(r'\"([^@\"]*)\"', c[1])

    def get(self):
        return self.video, self.audio

#交互对象
class InteractObj(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtSlot(result=str)
    def getequppment(self):
        a, b = Equipment().get()
        message = {
            'vedio': a,
            'audio': b
        }
        return json.dumps(message)

    @pyqtSlot(str, str, str)
    def start(self, vedio, audio, screen):
        p1 = Process(target=run, args=(vedio, audio, screen,))
        p1.start()
        return


channel = QWebChannel()
interactObj = InteractObj()

#主窗口
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("mainwindow")
        self.setGeometry(5, 30, 1355, 730)

        self.browser = QWebEngineView()
        self.browser.load(QUrl('http://129.211.89.206/'))
        channel.registerObject("obj", interactObj)
        self.browser.page().setWebChannel(channel)

        self.setCentralWidget(self.browser)


#
def run(vedio, audio, screen):
    print(vedio, audio, screen)
    a = dict()
    if vedio != '不开启':
        a['video=' + vedio] = '-f dshow '
    else:
        if screen != '不开启':
            a['video=screen-capture-recorder'] = '-f dshow '
    if audio != '不开启':
        a['audio=' + audio] = '-f dshow '
    print(a)

    ff = FFmpeg(inputs=a,
                outputs={
                    'rtmp://129.211.89.206:8080/myapp/yuzhidi': '-vcodec libx264 -preset:v ultrafast -tune:v zerolatency -f flv'})
    ff.run()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()

    win.show()
    app.exit(app.exec())