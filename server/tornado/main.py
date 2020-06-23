import tornado.web
import tornado.websocket
import os
import json
import time
import asyncio
import sys
import sql
import pymysql
import hashlib

conn = pymysql.connect(host='yourdatabaseserver', port=3306, user='yourdatabaseserveruser', passwd='yourdatabaseserverpassword', db='yourdatabasename')
cursor = conn.cursor()
liveList = dict()
messageRecord = dict()

class fileWriter(object):
    filelist = dict()
    def open(self, CID, addr):
        if CID in self.filelist.keys():
            return
        f = open(addr, "w")
        self.filelist[CID] = f
    def write(self, CID, msg):
        f = self.filelist[CID]
        f.write(msg)
        f.write('\n')
    def close(self, CID):
        f = self.filelist[CID]
        f.close()
        self.filelist.pop(CID)

class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("login.html")
    def post(self):
        UID = self.get_argument("UID")
        password = self.get_argument("password")
        flag = sql.queryUser(conn, cursor, UID, password)
        if flag == 0:
            self.render("error.html", info={"Content" : "出错了", 
                                            "info" : "用户名或密码错误，请重新输入，正在跳转至登录界面...请稍候",
                                            "timeout" : 3,
                                            "url" : "/login"})
        else:
            self.render("student.html", UID=UID, courselist=sql.queryCourseStudent(conn, cursor, UID))

class RegisterHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("register.html")
    def post(self):
        UID = self.get_argument("UID")
        password = self.get_argument("password")
        flag = sql.newUser(conn, cursor, UID, password)
        if flag == 0:
            self.render("error.html", info={"Content" : "注册失败", 
                                            "info" : "用户名已注册，正在跳转至注册界面...请稍候",
                                            "timeout" : 3,
                                            "url" : "/register"})
        else:
            self.render("success.html", info={"Content" : "注册成功", 
                                            "info" : "注册成功! 正在跳转至登录界面...请稍候",
                                            "timeout" : 3,
                                            "url" : "/login"})

class StudentHandler(tornado.web.RequestHandler):
    def get(self):
        UID = self.get_argument("UID")
        self.render("student.html", UID=UID, courselist=sql.queryCourseStudent(conn, cursor, UID))
    def post(self):
        pass

class TeacherHandler(tornado.web.RequestHandler):
    def get(self):
        UID = self.get_argument("UID")
        self.render("teacher.html", UID=UID, courselist=sql.queryCourseTeacher(conn, cursor, UID))
    def post(self):
        pass

class ModifyPasswordHandler(tornado.web.RequestHandler):
    def get(self):
        UID = self.get_argument("UID")
        self.render("modifypassword.html", UID=UID)
    def post(self):
        UID = self.get_argument("UID")
        password = self.get_argument("password")
        newpassword = self.get_argument("newpassword")
        newpassword2 = self.get_argument("newpassword2")
        if newpassword != newpassword2:
            self.render("error.html", info={"Content" : "出错了", 
                                            "info" : "两次输入的新密码不一致, 请重新输入, 正在跳转至密码修改界面...请稍候",
                                            "timeout" : 3,
                                            "url" : "/modifypassword?UID=%s" % UID})
        else:
            flag = sql.queryUser(conn, cursor, UID, password)
            if flag == 0:
                self.render("error.html", info={"Content" : "出错了", 
                                            "info" : "密码错误，请重新输入，正在跳转至密码修改界面...请稍候",
                                            "timeout" : 3,
                                            "url" : "/modifypassword?UID=%s" % UID})
            else:
                flag = sql.userUpdatePassword(conn, cursor, UID, newpassword)
                if flag == 0:
                    self.render("error.html", info={"Content" : "出错了", 
                                            "info" : "系统错误，请稍后再试，正在跳转至密码修改界面...请稍候",
                                            "timeout" : 3,
                                            "url" : "/modifypassword?UID=%s" % UID})
                else:
                    self.render("success.html", info={"Content" : "注册成功", 
                                                "info" : "修改成功! 正在跳转至登录界面...请稍候",
                                                "timeout" : 3,
                                                "url" : "/login"})

class JoinHandler(tornado.web.RequestHandler):
    def get(self):
        UID = self.get_argument("UID")
        self.render("join.html", UID=UID)
    def post(self):
        UID = self.get_argument("UID")
        CID = int(self.get_argument("CID"))
        flag = sql.queryCourse(conn, cursor, CID)
        if flag == 0:
            self.render("error.html", info={"Content" : "出错了", 
                                            "info" : "不存在编号为%d的课程，正在跳转至加入课程界面...请稍候" % CID,
                                            "timeout" : 3,
                                            "url" : "/join?UID=%s" % UID})
        else:
            flag = sql.newCourseStudent(conn, cursor, CID, UID)
            if flag == 0:
                self.render("error.html", info={"Content" : "出错了", 
                                            "info" : "系统错误，请稍后再试，正在跳转至加入课程界面...请稍候",
                                            "timeout" : 3,
                                            "url" : "/join?UID=%s" % UID})
            else:
                (CID, name, TUID, info) = sql.queryCourseInfo(conn, cursor, CID)
                self.render("success.html", info={"Content" : "加入成功", 
                                                "info" : "您已成功加入%s.正在跳转至该课程界面...请稍候" % name,
                                                "timeout" : 3,
                                                "url" : "/course?CID=%d&UID=%s" % (CID, UID)})

class CreateHandler(tornado.web.RequestHandler):
    def get(self):
        UID = self.get_argument("UID")
        self.render("create.html", UID=UID)
    def post(self):
        UID = self.get_argument("UID")
        name = self.get_argument("name")
        info = self.get_argument("info")
        CID = sql.countCourse(conn, cursor) + 1
        flag = sql.newCourse(conn, cursor, CID, name, UID, info)
        if flag == 0:
            self.render("error.html", info={"Content" : "出错了", 
                                            "info" : "系统错误，请稍后再试，正在跳转至创建课程界面...请稍候",
                                            "timeout" : 3,
                                            "url" : "/create?UID=%s" % UID})
        else:
            self.render("success.html", info={"Content" : "创建成功", 
                                                "info" : "您已成功创建%s.正在跳转至该课程界面...请稍候" % name,
                                                "timeout" : 3,
                                                "url" : "/course?CID=%d&UID=%s" % (CID, UID)})

class CourseHandler(tornado.web.RequestHandler):
    def get(self):
        UID = self.get_argument("UID")
        CID = int(self.get_argument("CID"))
        result = sql.queryCourseInfo(conn, cursor, CID)
        name = result[1]
        TUID = result[2]
        intro = result[3]
        if UID == TUID:
            self.render("courseteacher.html", UID=UID, CID=CID, name=name, TUID=TUID, intro=intro)
        else:
            isLiving = CID in liveList.keys()
            self.render("coursestudent.html", UID=UID, CID=CID, name=name, TUID=TUID, intro=intro, isLiving=isLiving)
    def post(self):
        pass

class ResourceHandler(tornado.web.RequestHandler):
    def get(self):
        UID = self.get_argument("UID")
        CID = int(self.get_argument("CID"))
        result = sql.queryCourseInfo(conn, cursor, CID)
        name = result[1]
        TUID = result[2]
        resourceList = sql.queryResource(conn, cursor, CID)
        if UID == TUID:
            self.render("resourceteacher.html", UID=UID, CID=CID, name=name, TUID=TUID, resourceList=resourceList)
        else:
            self.render("resourcestudent.html", UID=UID, CID=CID, name=name, TUID=TUID, resourceList=resourceList)
    def post(self):
        pass

class DeleteResourceHandler(tornado.web.RequestHandler):
    def get(self):
        UID = self.get_argument("UID")
        CID = int(self.get_argument("CID"))
        RID = int(self.get_argument("RID"))
        result = sql.queryResourceInfo(conn, cursor, RID)
        if not result:
            self.render("error.html", info={"Content" : "出错了", 
                                            "info" : "该资源已被删除，正在跳转至课程资源界面...请稍候",
                                            "timeout" : 3,
                                            "url" : "/resource?UID=%s&CID=%d" % (UID, CID)})
            return
        addr = result[2]
        command = "rm download/" + addr
        flag = sql.deleteResource(conn, cursor, RID)
        if flag == 0:
            self.render("error.html", info={"Content" : "出错了", 
                                            "info" : "系统错误，请稍后再试，正在跳转至课程资源界面...请稍候",
                                            "timeout" : 3,
                                            "url" : "/resource?UID=%s&CID=%d" % (UID, CID)})
        else:
            os.system(command)
            self.render("success.html", info={"Content" : "删除成功", 
                                                "info" : "您已成功删除该资源.正在跳转至课程资源界面...请稍候",
                                                "timeout" : 3,
                                                "url" : "/resource?UID=%s&CID=%d" % (UID, CID)})

class ReplayHandler(tornado.web.RequestHandler):
    def get(self):
        UID = self.get_argument("UID")
        CID = int(self.get_argument("CID"))
        result = sql.queryCourseInfo(conn, cursor, CID)
        name = result[1]
        TUID = result[2]
        replayList = sql.queryReplay(conn, cursor, CID)
        if UID == TUID:
            self.render("replayteacher.html", UID=UID, CID=CID, name=name, TUID=TUID, replayList=replayList)
        else:
            self.render("replaystudent.html", UID=UID, CID=CID, name=name, TUID=TUID, replayList=replayList)
    def post(self):
        pass

class DeleteReplayHandler(tornado.web.RequestHandler):
    def get(self):
        UID = self.get_argument("UID")
        CID = int(self.get_argument("CID"))
        BID = int(self.get_argument("BID"))
        result = sql.queryReplayInfo(conn, cursor, BID)
        if not result:
            self.render("error.html", info={"Content" : "出错了", 
                                            "info" : "该回放已被删除，正在跳转至课程回放界面...请稍候",
                                            "timeout" : 3,
                                            "url" : "/replay?UID=%s&CID=%d" % (UID, CID)})
            return
        addr = result[2]
        command = "rm videos/" + addr
        flag = sql.deleteReplay(conn, cursor, BID)
        if flag == 0:
            self.render("error.html", info={"Content" : "出错了", 
                                            "info" : "系统错误，请稍后再试，正在跳转至课程回放界面...请稍候",
                                            "timeout" : 3,
                                            "url" : "/replay?UID=%s&CID=%d" % (UID, CID)})
        else:
            os.system(command)
            command = command + ".txt"
            os.system(command)
            self.render("success.html", info={"Content" : "删除成功", 
                                                "info" : "您已成功删除该回放.正在跳转至课程回放界面...请稍候",
                                                "timeout" : 3,
                                                "url" : "/replay?UID=%s&CID=%d" % (UID, CID)})

class UploadHandler(tornado.web.RequestHandler):
    def get(self):
        UID = self.get_argument("UID")
        CID = int(self.get_argument("CID"))
        result = sql.queryCourseInfo(conn, cursor, CID)
        name = result[1]
        self.render('upload.html', UID=UID, CID=CID, name=name)
 
    def post(self, *args, **kwargs):
        UID = self.get_argument("UID")
        CID = int(self.get_argument("CID"))
        RID = sql.maxResource(conn, cursor)[0] + 1
        name = self.get_argument("name")
        file = self.request.files.get('file', None)[0]
        ext = file["filename"]
        idx = ext.rfind(".")
        if idx == -1:
            ext = ''
        else:
            ext = ext[idx:]
        hl = hashlib.md5()
        hl.update(str(RID).encode(encoding='utf-8'))
        filename = hl.hexdigest() + ext
        path = os.path.join("download", filename)
        flag = sql.newResource(conn, cursor, RID, name, filename, CID)
        if flag == 0:
            self.render("error.html", info={"Content" : "出错了", 
                                            "info" : "系统错误，请稍后再试，正在跳转至课程资源界面...请稍候",
                                            "timeout" : 3,
                                            "url" : "/resource?UID=%s&CID=%d" % (UID, CID)})
        else:
            with open(path, 'wb') as up:
                up.write(file["body"])
            self.render("success.html", info={"Content" : "上传成功", 
                                                "info" : "您已成功上传.正在跳转至课程资源界面...请稍候",
                                                "timeout" : 3,
                                                "url" : "/resource?UID=%s&CID=%d" % (UID, CID)})

class DownloadHandler(tornado.web.RequestHandler):
    def get(self, filename):
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=%s' % filename)
        path = os.path.join("download", filename)
        with open(path, 'rb') as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                self.write(data)
        self.finish()

class WatchHandler(tornado.web.RequestHandler):
    def get(self):
        UID = self.get_argument("UID")
        CID = int(self.get_argument("CID"))
        BID = int(self.get_argument("BID"))
        result = sql.queryReplayInfo(conn, cursor, BID)
        addr = result[2]
        name = result[1]
        f = open("videos/" + addr + ".txt", 'r')
        lines = f.readlines()
        f.close()
        self.render("watch.html", UID=UID, CID=CID, BID=BID, addr=addr, name=name, records=lines)
    def post(self):
        pass

class VideoHandler(tornado.web.RequestHandler):
    def get(self):
        addr = self.get_argument("addr")
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=%s' % "addr")
        path = os.path.join("videos", addr)
        with open(path, 'rb') as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                self.write(data)
        self.finish()

class BeforeLiveHandler(tornado.web.RequestHandler):
    def get(self):
        CID = int(self.get_argument("CID"))
        UID = self.get_argument("UID")
        result = sql.queryCourseInfo(conn, cursor, CID)
        name = result[1]
        TUID = result[2]
        if UID == TUID:
            self.render("beforelive.html", UID=UID, CID=CID, name=name)
        else:
            self.render("error.html", info={"Content" : "出错了",
                                            "info" : "只有课程的创建者才能直播,正在跳转至课程界面,请稍候",
                                            "timeout" : 3,
                                            "url" : "/course?CID=%d&UID=%s" % (CID, UID)})
    def post(self):
        UID = self.get_argument("UID")
        CID = int(self.get_argument("CID"))
        lessonName = self.get_argument("lessonName")
        liveList[CID] = lessonName
        result = sql.queryCourseInfo(conn, cursor, CID)
        TUID = result[2]
        BID = sql.maxReplay(conn, cursor)[0] + 1
        ext = ".flv"
        hl = hashlib.md5()
        hl.update(str(BID).encode(encoding='utf-8'))
        filename = hl.hexdigest() + ext
        path = os.path.join("videos", filename)
        sql.newReplay(conn, cursor, BID, lessonName, filename, CID)
        path = path + ".txt"
        self.application.writer.open(CID, path)
        self.render("liveteacher.html", UID=UID, CID=CID, TUID=TUID, lessonName=lessonName)

class EndLiveHandler(tornado.web.RequestHandler):
    def get(self):
        UID = self.get_argument("UID")
        CID = int(self.get_argument("CID"))
        lessonName = self.get_argument("lessonName")
        liveList.pop(CID)
        BID = int(sql.queryReplayID(conn, cursor, lessonName)[0])
        ext = ".flv"
        hl = hashlib.md5()
        hl.update(str(BID).encode(encoding='utf-8'))
        filename = hl.hexdigest() + ext
        path = os.path.join("videos", filename)
        # flag = sql.newReplay(conn, cursor, BID, lessonName, filename, CID)
        command = "mv videos/%d_%s.flv videos/%s" % (CID, UID, filename)
        self.application.writer.close(CID)
        os.system(command)
        command = "rm videos/" + str(CID) + "_* -f"
        os.system(command)
        result = sql.queryCourseInfo(conn, cursor, CID)
        name = result[1]
        TUID = result[2]
        intro = result[3]
        self.render("courseteacher.html", UID=UID, CID=CID, name=name, TUID=TUID, intro=intro)

class LiveStudentHandler(tornado.web.RequestHandler):
    def get(self):
        UID = self.get_argument("UID")
        CID = int(self.get_argument("CID"))
        result = sql.queryCourseInfo(conn, cursor, CID)
        TUID = result[2]
        lessonName = liveList[CID]
        self.render("livestudent.html", UID=UID, CID=CID, TUID=TUID, lessonName=lessonName, users=self.application.ChatHome.getUserList(CID))

class WhiteBoardHandler(tornado.web.RequestHandler):
    def get(self):
        # UID = self.get_argument("UID")
        # CID = int(self.get_argument("CID"))
        # lessonName = self.get_argument("lessonName")
        self.render("whiteboard.html")

class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("test.html")
    def post(self):
        pass

class ChatHome(object):
    clients = {}
    def getUserList(self, CID):
        if CID not in self.clients.keys():
            return []
        res = []
        for user in self.clients[CID]:
            res.append(user.get_argument("UID"))
        return res
    def addClient(self, newClient):
        CID = int(newClient.get_argument("CID"))
        className = newClient.get_argument("lessonName")
        UID = newClient.get_argument("UID")
        if CID not in self.clients.keys():
            self.clients[CID] = []
        self.clients[CID].append(newClient)
        message = {
            "time" : time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "source" : "system",
            "message": "{} 加入课堂 {}".format(UID, CID)
        }
        self.trigger(CID, message)

    def deleteClient(self, leftClient):
        CID = int(leftClient.get_argument("CID"))
        className = leftClient.get_argument("lessonName")
        UID = leftClient.get_argument("UID")
        self.clients[CID].remove(leftClient)
        message = {
            "time" : time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "source" : "system",
            "message": "{} 离开课堂".format(UID)
        }
        self.trigger(CID, message)

    def sendMessage(self, sender, msg):
        CID = int(sender.get_argument("CID"))
        className = sender.get_argument("lessonName")
        UID = sender.get_argument("UID")
        message = {
            "time" : time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "source" : UID,
            "message": msg,
        }
        self.trigger(CID, message)

    def trigger(self, CID, msg):
        if CID in messageRecord.keys():
            messageRecord[CID].append(msg)
        else:
            messageRecord[CID] = [msg]
        for client in self.clients[CID]:
            client.write_message(json.dumps(msg))
        
class newClient(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True
    def open(self):
        className = self.get_argument("lessonName")
        message = {
            "time" : time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "source" : "system",
            "message": "欢迎加入 {}".format(className)
        }
        self.write_message(json.dumps(message))
        self.application.ChatHome.addClient(self)
    
    def on_close(self):
        self.application.ChatHome.deleteClient(self)
    
    def on_message(self, message):
        CID = int(self.get_argument("CID"))
        UID = self.get_argument("UID")
        if message != "开启直播1234567890" and message != "关闭直播1234567890":
            self.application.writer.write(CID, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " " + UID)
            self.application.writer.write(CID, message)
        self.application.ChatHome.sendMessage(self, message)

class Application(tornado.web.Application):
    def __init__(self):
        self.ChatHome = ChatHome()
        self.writer = fileWriter()
        handlers = [
            (r"/", LoginHandler),
            (r"/login", LoginHandler),
            (r"/register", RegisterHandler),
            (r"/student", StudentHandler),
            (r"/teacher", TeacherHandler),
            (r"/modifypassword", ModifyPasswordHandler),
            (r"/join", JoinHandler),
            (r"/create", CreateHandler),
            (r"/course", CourseHandler),
            (r"/resource", ResourceHandler),
            (r"/deleteresource", DeleteResourceHandler),
            (r"/replay", ReplayHandler),
            (r"/deletereplay", DeleteReplayHandler),
            (r'/upload', UploadHandler),
            (r'/download/(.*)', DownloadHandler),
            (r'/videos', VideoHandler),
            (r'/watch', WatchHandler),
            (r'/beforelive', BeforeLiveHandler),
            (r'/endlive', EndLiveHandler),
            (r"/newClient", newClient),
            (r'/livestudent', LiveStudentHandler),
            (r'/whiteboard', WhiteBoardHandler),
            (r"/test", TestHandler),
        ]
        settings = {
            'template_path': 'html',
            'static_path': 'static'
        }
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    server = tornado.httpserver.HTTPServer(Application())
    server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

