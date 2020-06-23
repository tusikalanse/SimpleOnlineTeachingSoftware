import pymysql

conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='A[8,XIWTYdX5ibJh', db='OnlineTeaching')
cursor = conn.cursor()

def queryUser(db, p, uid, pswd):
    sql = "SELECT * FROM user WHERE UID = '%s' AND password = '%s'" % (uid, pswd)
    count = p.execute(sql)
    result = p.fetchall()
    return count == 1

def newUser(db, p, uid, pswd):
    sql = "SELECT * FROM user WHERE UID = '%s'" % uid
    count = p.execute(sql)
    if count != 0:
        return False
    sql = "INSERT INTO user(UID, password) VALUES('%s', '%s')" % (uid, pswd)
    try:
        p.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def userUpdatePassword(db, p, uid, newpswd):
    sql = "UPDATE user SET password = '%s' WHERE UID = '%s'" % (newpswd, uid)
    try:
        p.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def countCourse(db, p):
    sql = "SELECT count(*) FROM course"
    count = p.execute(sql)
    return p.fetchone()[0]

def queryCourse(db, p, cid):
    sql = "SELECT * FROM course WHERE CID = %d" % cid
    count = p.execute(sql)
    result = p.fetchall()
    return count == 1

def queryCourseInfo(db, p, cid):
    sql = "SELECT * FROM course WHERE CID = %d" % cid
    count = p.execute(sql)
    result = p.fetchone()
    return result

def newCourse(db, p, cid, name, uid, intro):
    sql = "INSERT INTO course(CID, name, UID, intro) VALUES(%d, '%s', '%s', '%s')" % (cid, name, uid, intro)
    try:
        p.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def newCourseTeacher(db, p, cid, uid):
    sql = "INSERT INTO course_teacher(CID, UID) VALUES(%d, '%s')" % (cid, uid)
    try:
        p.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def queryCourseTeacher(db, p, uid):
    sql = "SELECT CID, name FROM course WHERE UID = '%s'" % uid
    count = p.execute(sql)
    result = p.fetchall()
    return result

def newCourseStudent(db, p, cid, uid):
    sql = "INSERT INTO course_student(CID, UID) VALUES(%d, '%s')" % (cid, uid)
    try:
        p.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def queryCourseStudent(db, p, uid):
    sql = "SELECT course.CID, name FROM course, course_student WHERE course_student.UID = '%s' AND course.CID = course_student.CID" % uid
    count = p.execute(sql)
    result = p.fetchall()
    return result

def maxResource(db, p):
    sql = "SELECT max(RID) FROM resource"
    count = p.execute(sql)
    result = p.fetchone()
    return result

def newResource(db, p, rid, name, add, cid):
    sql = "INSERT INTO resource(RID, name, address, CID) VALUES(%d, '%s', '%s', %d)" % (rid, name, add, cid)
    try:
        p.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def queryResource(db, p, cid):
    sql = "SELECT RID, name, address FROM resource WHERE CID = %d" % cid
    count = p.execute(sql)
    result = p.fetchall()
    return result

def queryResourceInfo(db, p, rid):
    sql = "SELECT * FROM resource WHERE RID = %d" % rid
    count = p.execute(sql)
    result = p.fetchone()
    return result

def deleteResource(db, p, rid):
    sql = "DELETE FROM resource WHERE RID = %d" % rid
    try:
        p.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False


def maxReplay(db, p):
    sql = "SELECT max(BID) FROM replay"
    count = p.execute(sql)
    result = p.fetchone()
    return result

def queryReplayInfo(db, p, bid):
    sql = "SELECT * FROM replay WHERE BID = %d" % bid
    count = p.execute(sql)
    result = p.fetchone()
    return result

def queryReplay(db, p, cid):
    sql = "SELECT BID, name, address FROM replay WHERE CID = %d" % cid
    count = p.execute(sql)
    result = p.fetchall()
    return result

def newReplay(db, p, bid, name, add, cid):
    sql = "INSERT INTO replay(BID, name, address, cid) VALUES(%d, '%s', '%s', %d)" % (bid, name, add, cid)
    try:
        p.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def queryReplayID(db, p, name):
    sql = "SELECT BID FROM replay WHERE name='%s'" % name
    count = p.execute(sql)
    result = p.fetchone()
    return result

def deleteReplay(db, p, bid):
    sql = "DELETE FROM replay WHERE BID = %d" % bid
    try:
        p.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False

if __name__ == "__main__":
    print(countCourse(conn, cursor))
    print(queryCourseStudent(conn, cursor, "test"))
    print(queryReplay(conn, cursor, 1))