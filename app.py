from flask import *

app=Flask(
	__name__)

app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
from mysql.connector import pooling
import json

#載入&實例化jwt
from flask_jwt_extended import create_access_token, jwt_required,set_access_cookies,decode_token,get_jwt_identity,unset_jwt_cookies,JWTManager,create_refresh_token,set_refresh_cookies
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = "this-is-a-key-in-taipeidAttractionsProgram"  #設定jwt密鑰
# jwt.init_app(app)


mydbPool=pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=3,
    host="localhost",
    user="root",
    password="123456789",
    buffered=True
)
print("連上資料庫")

# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

# 註冊一個新的會員
@app.post("/api/user")
def signNewMember():
	name=request.form["name"]
	email=request.form["email"]
	password=request.form["password"]
	print(name)
	if(name=="" or email=="" or password==""):
		inputIsNone={"error": True,"message": "name、email、password shouldn't be empty"}
		return inputIsNone,400
	connector=mydbPool.get_connection()
	mycursor=connector.cursor()
	mycursor.execute("use taipeiAttractions")
	try:
		sql = "select * from member where email = %s"
		mycursor.execute(sql,(email,))
		getUserInfoFromTable=mycursor.fetchone()
		if(getUserInfoFromTable != None):
			responseJs={"error": True,"message": "email is used"}
			connector.commit()
			mycursor.close()
			connector.close()
			print("1")
			return responseJs,400
		sql="insert into member(name,email,password) values (%s,%s,%s)"
		val=(name,email,password)
		mycursor.execute(sql,val)
		connector.commit()
		mycursor.close()
		connector.close()
		print("0000")
		responseJs={"ok":True}
		return responseJs,200
	except:
		connector.commit()
		mycursor.close()
		connector.close()
		print("999")
		responseJs={"error":True,"message":"註冊時發生錯誤，請重新輸入"}
		return responseJs,500

# 取得當前登入的會員資訊
@app.get("/api/user/auth")
def getSigninMemberData():
	try:
		token=request.cookies["token"]
	except:
		print("沒有cookie，名為token")
		return "null",200
	# 驗證token是否有被竄改
	try:
		# 將token解密，取出存放在payload內的資訊
		eee=decode_token(token)
		info={"data":eee["data"]}
		return info,200
	except:
		return "token 驗證失敗",422

# 登入會員帳戶
@app.put("/api/user/auth")
def login():
	passwordIndex=3
	print(request.data)
	print(request.form["email"])
	email=request.form["email"]
	password=request.form["password"]
	connector=mydbPool.get_connection()
	mycursor=connector.cursor()
	mycursor.execute("use taipeiAttractions")
	try:
		sql="select * from member where email = %s"
		mycursor.execute(sql,(email,))
		getDataFromMemberTable=mycursor.fetchone()
		mycursor.close()
		connector.close()
		print(getDataFromMemberTable)
		if(getDataFromMemberTable==None):
			errorInfo={ "error":True,"message":" account is not active , please register an account first"}
			return errorInfo,500
		if(getDataFromMemberTable[passwordIndex]==password):
			clientInfo={"data":{"id":getDataFromMemberTable[0],"name":getDataFromMemberTable[1],"email":getDataFromMemberTable[2]}}
			# 將標頭內的set-cookie用來將jwt存到cookie中			
			resp=jsonify({"ok": True})
			print(resp)
			# 將clientInfo作為附加資訊存入以jwt嘉蜜的token內
			access_token = create_access_token(identity=getDataFromMemberTable[1],additional_claims=clientInfo)
			# token=access_token
			# refresh_token= create_refresh_token(identity=email)
			# set_access_cookies(resp,access_token,max_age=604800)
			# set_refresh_cookies(resp,refresh_token)
			resp.set_cookie(key="token",value=access_token,max_age=604800)
			return resp,200
		else:
			errorInfo={"error": True,"message": "password is wrong , please try again"}
			return errorInfo,400
	except:
		errorInfo={ "error":True,"message":"Internal Server Error"}
		return errorInfo,500

#登出帳戶
@app.delete("/api/user/auth")
def logout():
	# 將cookie中的jwt移除
	resp=jsonify({'ok':True})
	resp.delete_cookie(key="token")
	resp.delete_cookie(key="access_token_cookie")
	resp.delete_cookie(key="refresh_token_cookie")
	return resp,200

#取得景點資料列表
@app.get("/api/attractions/")
def getAttractionsInformation():
	page=request.args.get("page",0)
	keyword=request.args.get("keyword","")
	print("page = " + str(page))
	print("keyword = "+keyword)
	connector=mydbPool.get_connection()
	mycursor=connector.cursor()
	mycursor.execute("use taipeiAttractions")
	first=int(page)*12
	dataCounts=13
	try:
		if(keyword != ""):
			sql="select * from taipeiAttractionsData where cat=%s or name like %s limit %s,%s"
			catKeyword=keyword
			nameKeyword ="%" + keyword + "%"
			mycursor.execute(sql,(catKeyword,nameKeyword,first,dataCounts))
		if(keyword ==""):
			sql="select * from taipeiAttractionsData limit %s,%s"
			mycursor.execute(sql,(first,dataCounts))
		findInDataBase=mycursor.fetchall()
		mycursor.close()
		connector.close()
		listData=[]
		print(len(findInDataBase))
		for i in range(len(findInDataBase)):
			imageList=findInDataBase[i][13].split("http")
			respUrl=[]
			for j in range(0,len(imageList)):
				if(imageList[j][-3:].lower()=="jpg"):
					respUrl.append("http"+imageList[j])
			data={"id": findInDataBase[i][0],
				"name": findInDataBase[i][3],
				"category": findInDataBase[i][10],
				"description": findInDataBase[i][16],
				"address": findInDataBase[i][18],
				"transport": findInDataBase[i][2],
				"mrt": findInDataBase[i][7],
				"lat": findInDataBase[i][5],
				"lng": findInDataBase[i][15],
				"images":respUrl}
			listData.append(data)
		nextpage=int(page)+1
		resp={"nextPage":nextpage,"data":listData}
		print(type(resp))
		return resp,200
	except:
		mycursor.close()
		connector.close()
		resp={"error":True,"message":"something error in using database"}
		return jsonify(resp),500


#取得指定id資料
@app.get("/api/attraction/<int:id>")
def getDataWithId(id):
	connector=mydbPool.get_connection()
	mycursor=connector.cursor()
	mycursor.execute("use taipeiAttractions")
	sql="select * from taipeiAttractionsData where id = %s"
	try:
		mycursor.execute(sql,(id,))
		findInDataBase=mycursor.fetchone()
		mycursor.close()
		connector.close()
		if(findInDataBase != None):
			imageList=findInDataBase[13].split("http")
			respUrl=[]
			for j in range(1,len(imageList)):
				if(imageList[j][-3:].lower()=="jpg"):
					respUrl.append("http"+imageList[j])				
			data={"id": findInDataBase[0],
				"name": findInDataBase[3],
				"category": findInDataBase[10],
				"description": findInDataBase[16],
				"address": findInDataBase[18],
				"transport": findInDataBase[2],
				"mrt": findInDataBase[7],
				"lat": findInDataBase[5],
				"lng": findInDataBase[15],
				"images":respUrl}
			resp={"data":data}
			# resp=str(resp)
			print(type(resp))
			return resp,200
		else:
			return jsonify({"error":True,"message":"此id無資料"}),400
	except:
		mycursor.close()
		connector.close()
		return jsonify({"error":True,"message":"伺服器錯誤"}),500

#取得所有景點分類列表
@app.get("/api/categories")
def getCategoriesList():
	connector=mydbPool.get_connection()
	mycursor=connector.cursor()
	mycursor.execute("use taipeiAttractions")
	sql="select cat from taipeiAttractionsData"
	try:
		mycursor.execute(sql)
		catList=mycursor.fetchall()
		mycursor.close()
		connector.close()
		resultCatList=[]
		print(type(catList[0][0]))
		print(catList[0])
		for x in catList:
			if x[0] not in resultCatList:
				resultCatList.append(x[0])
		resp={"data":resultCatList}
		print(type(resp))
		return jsonify(resp),200
	except:
		mycursor.close()
		connector.close()
		return jsonify({"error":True,"message":"伺服器錯誤"}),500
# @app.get("api/test")
# def test():
# 	return 

app.run(host="0.0.0.0",port=8888)