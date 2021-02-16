import pymysql

def connect_to_db():
    #连接数据库
    db = pymysql.connect(host = "localhost", port =3306, user = "root", passwd = "yongfufan", db = "data")


    #使用cursor()方法创建一个游标对象
    cursor = db.cursor()

    #使用execute()方法执行SQL语句
    cursor.execute("SELECT * FROM flow")

    #使用fetall()获取全部数据
    data = cursor.fetchall()

    #打印获取到的数据
    print(data)

    #关闭游标和数据库的连接
    cursor.close()
    db.close()