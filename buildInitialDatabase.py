import json
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
try:
    sql="create database taipeiAttractions"
    mycursor.execute(sql)
    print("建立初始的database")
except:
    sql="drop database taipeiAttractions"
    mycursor.execute(sql)
    print("刪除舊的database")
    sql="create database taipeiAttractions"
    mycursor.execute(sql)
    print("建立新的database名稱為taipeiAttractions")
mycursor.execute("show databases")
# for i in mycursor:
#     print(i)
mycursor.execute("use taipeiAttractions")
sql="create table `taipeiAttractionsData`(`id` int auto_increment primary key comment '獨立編號',`rate` int not null default '0' comment '分級',`direction` text,`name` varchar(255) comment '名稱',`date` date comment'日期',`longitude` char(255),`ref_wp` varchar(255),`mrt` varchar(255),`serial_no` varchar(255),`rowNumber` varchar(255),`cat` varchar(255),`memo_time` text,`poi` varchar(255),`file` text,`idpt` varchar(255),`latitude` varchar(255),`description` text,`avEnd` varchar(255),`address` varchar(255))"
mycursor.execute(sql)
print("建立新的table 名稱為 taipeiAttractionsData")
mycursor.execute("show tables")
print("---")
with open('./data/taipei-attractions.json',mode='r',encoding='utf-8') as file:
    data=file.read()
data=json.loads(data)
i = data['result']['results'][0]
for i in data['result']['results']:
    sql = "insert into taipeiAttractionsData (rate,direction,name,date,longitude,ref_wp,mrt,serial_no,rowNumber,cat,memo_time,poi,file,idpt,latitude,description,avEnd,address) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    val = (i['rate'],i['direction'],i['name'],i['date'],i['longitude'],i['REF_WP'],i['MRT'],i['SERIAL_NO'],i['RowNumber'],i['CAT'],i['MEMO_TIME'],i['POI'],i['file'],i['idpt'],i['latitude'],i['description'],i['avEnd'],i['address'])
    mycursor.execute(sql,val)
print("初始資料已輸入資料庫中")
connector.commit()
mycursor.close()
connector.close()