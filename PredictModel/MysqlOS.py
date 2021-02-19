import pymysql

class SQLOS(object):
    def connect_to_db():
        #连接数据库
        connection = pymysql.connect(host = "localhost", port =3306, user = "root", passwd = "yongfufan", db = "data")
        return connection
    
    def  