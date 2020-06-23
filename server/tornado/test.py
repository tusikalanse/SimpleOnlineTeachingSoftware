# import tornado.ioloop
# import tornado.web
# import pymysql
 
# conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='A[8,XIWTYdX5ibJh', db='OnlineTeaching')
# cursor = conn.cursor()

# temp = "select UID from user"
# effect_row = cursor.execute(temp)
# result = cursor.fetchall()


import tornado.web
import tornado.ioloop
import tornado.httpserver
import os
import asyncio
import sys
if sys.platform == 'win32':
	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
class UpFileHandler(tornado.web.RequestHandler):
    #tornado.httputil.HTTPFile对象三个属性
    #1.filename文件名
    #2.body文件内部实际内容
    #3.type文件的类型
    def get(self, *args, **kwargs):
        self.write('<!DOCTYPE html>\
                    <html lang="en">\
                    <head>\
                        <meta charset="UTF-8">\
                        <title>Title</title>\
                    </head>\
                    <body>\
                        <form action="fileup" method="post" enctype="multipart/form-data">\
                            <input type="file" name="file1">\
                            <input type="file" name="file2">\
                            <input type="submit" value="shangchuan">\
                        </form>\
                    </body>\
                    </html>')
        #write里面内容是一个简单的完整页面，为了博客方便，放在了一起，建议分开
    def post(self, *args, **kwargs):
        #查看上传文件的完整格式，files以字典形式返回
        #{'file1':
        #[{'filename': '新建文本文档.txt', 'body': b'61 60 -83\r\n-445 64 -259', 'content_type': 'text/plain'}],
        #'file2':
        filesDict=self.request.files
        for inputname in filesDict:
            #第一层循环取出最外层信息，即input标签传回的name值
            #用过filename键值对对应，取出对应的上传文件的真实属性
            http_file=filesDict[inputname]
            for fileObj in http_file:
                #第二层循环取出完整的对象
                #取得当前路径下的upfiles文件夹+上fileObj.filename属性(即真实文件名)
                filePath=os.path.join(os.path.dirname(__file__),"save",fileObj.filename)
                with open(filePath,'wb') as f:
                     f.write(fileObj.body)
        self.write('上传成功')
if __name__ == '__main__':
    app=tornado.web.Application(
        [(r'/fileup',UpFileHandler)])
    httpserver=tornado.httpserver.HTTPServer(app)
    httpserver.bind(8000)
    httpserver.start()
    tornado.ioloop.IOLoop.instance().start()