from mysql.connector import pooling

mydbPool=pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=3,
    host="localhost",
    user="root",
    password="123456789",
    buffered=True
)
print("連上資料庫")
connector=mydbPool.get_connection()
mycursor=connector.cursor()
mycursor.execute("use taipeiAttractions")
sql="create table `orderList`(`order_id` int auto_increment primary key comment '訂單ID',`attraction_id` int,`member_id` int,`date` date,`time` varchar(255),`price` int,`paid` varchar(255))"

# sql="create table `booking`(`member_id` int auto_increment primary key comment '會員ID',`name` varchar(255),`email` varchar(255),`password` varchar(255))"
mycursor.execute(sql)
print("建立新的table 名稱為 orderList")
mycursor.close()
connector.close()