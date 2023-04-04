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
sql="create table `tappay_list`(`tappay_id` int auto_increment primary key comment 'tappay ID',`tappay_number` int,`member_id` int,`order_number_list` varchar(255),`status` int,`name` varchar(255),`email` varchar(255),`phone` varchar(255))"
mycursor.execute(sql)
print("建立 table 名稱為 tappay_list ")
mycursor.close()
connector.close()