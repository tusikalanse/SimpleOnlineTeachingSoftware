#! /usr/bin/env
# -*- coding: utf-8 -*-
# webview.py
import re
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import *
from ffmpy3 import FFmpeg

fp = open('error.txt', 'w')
ff = FFmpeg(inputs={'dummy': '-list_devices true -f dshow'}, )
try:
    ff.run(stderr=fp)
except:
    with open('error.txt', 'r', encoding='utf-8') as fr:
        str = fr.read()
    tmp = re.findall(r'"(.*?)"', str)
    lc = []
    for i in tmp:
        if i[0] != '@':
            lc.append(i)


class QtWeb(QObject):
    # pyqtSlot，中文网络上大多称其为槽。作用是接收网页发起的信号
    # @pyqtSlot(result=list)
    # def dev(self):
    #     return lc

    # @pyqtSlot(list)
    # def ffmpy1(self, test):
    #     ff = FFmpeg(
    #         inputs={'video=' + test[2] + ':audio=' + test[1]: '-rtbufsize 2048M -f dshow',
    #                 'video=' + test[0]: '-rtbufsize 512M -f dshow'},
    #         outputs={
    #             'rtmp://127.0.0.1:1935/myapp/long': '-filter_complex [1:v]scale=480:320[camera];[0:v][camera]overlay=(main_w-overlay_w):(main_h-overlay_h)  -pix_fmt yuv420p -codec:v libx264 -bf 0 -g 300 -f flv'})

    # @pyqtSlot(list)
    # def ffmpy2(self, test):
    #     ff = FFmpeg(inputs={'video=' + test[0] + ':audio=' + test[1]: '-rtbufsize 2048M -f dshow'},
    #                 outputs={
    #                     'rtmp://127.0.0.1:1935/myapp/long': '-pix_fmt yuv420p -codec:v libx264 -bf 0 -g 300 -f flv'})
    pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = QWebEngineView()
    # channel = QWebChannel()
    # qyweb = QtWeb()
    # channel.registerObject('pyjs', qyweb)  ##前者是str，后者是一个QObject（里面放着需要调用的函数）
    #view.page().setWebChannel(channel)
    url_string = r"www.baidu.com"
    view.load(QUrl(url_string))
    print("sdf")
    view.show()
    print("sdf")
    sys.exit(app.exec_())
