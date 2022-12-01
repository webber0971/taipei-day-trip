from flask import *

app=Flask(
	__name__)

app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
from mysql.connector import pooling
import json

#載入&實例化jwt
from flask_jwt_extended import *
jwt = JWTManager()
app.config["JWT-SECRET-KEY"] = "this-is-a-key-in-taipeidAttractionsProgram"  #設定jwt密鑰
jwt.init_app(app)


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
	if(name | email | password == None):
		inputIsNone={"error": True,"message": "name、email、password shouldn't be empty"}
		return inputIsNone,400
	connector=mydbPool.get_connection()
	mycursor=connector.cursor()
	try:
		sql = "select email from member where email =%s"
		mycursor.execute(sql,(email,))
		getNameFromTable=mycursor.fetchone()
		if(getNameFromTable != None):
			responseJs={"error": True,"message": "email is used"}
			connector.commit()
			mycursor.close()
			connector.close()
			return responseJs,400
		sql="insert into member(name,email,password) values (%s,%s,%s)"
		val=(name,email,password)
		mycursor.execute(sql,val)
		connector.commit()
		mycursor.close()
		connector.close()
		responseJs={"ok":True},200
		return responseJs
	except:
		connector.commit()
		mycursor.close()
		connector.close()
		responseJs={"error":True,"message":"註冊時發生錯誤，請重新輸入"},500

# 取得當前登入的會員資訊
@app.get("/api/user/auth")
def getSigninMemberData():
	if "email" in session:
		email=session["email"]
		connector=mydbPool.get_connection()
		mycursor=connector.cursor()
		try:
			sql = "select (id,name,email) from member where email = %s"
			mycursor.execute(sql,(email,))
			memberData=mycursor.fetchone()
			mycursor.close()
			connector.close()
			print(memberData)
			return memberData,200
		except:
			mycursor.close()
			connector.close()
			return "null",200
	else:
		return "null",200

# 登入會員帳戶
@app.put("/api/user/ayth")
def login():
	email=request.form["email"]
	password=request.form["password"]
	connector=mydbPool.get_connection()
	mycursor=connector.cursor()
	sql="select * from member where email = %s"
	try:
		mycursor.execute(sql,(email,))
		getDataFromMemberTable=mycursor.fetchone()
		mycursor.close()
		connector.close()
		print(getDataFromMemberTable)
		if(getDataFromMemberTable==None):
			return jsonify({"error": True,"message": "email or password is wrong , please try again"}),400
		if(getDataFromMemberTable["password"]==password):
			# resp.set_cookie("access_token")
			# 將標頭內的set-cookie用來將jwt存到cookie中			
			resp=jsonify({"ok": True})
			access_token = create_access_token(identity=email)
			refresh_token= create_refresh_token(identity=email)
			set_access_cookies(resp,access_token,max_age=604800)
			set_refresh_cookies(resp,refresh_token)
			
			resp.set_cookie(key="token",value=access_token,max_age=604800)
			return resp,200
	except:
		return jsonify({ "error":True,"message":"server error"}),500

#登出帳戶
@app.delete("/api/user/auth")
def logout():
	# 將cookie中的jwt移除
	resp=jsonify({'ok':True})
	unset_jwt_cookies(resp)
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
		print(len(findInDataBase))
		listData=[]
		for i in range(len(findInDataBase)):
			data={"id": findInDataBase[i][0],
				"name": findInDataBase[i][3],
				"category": findInDataBase[i][10],
				"description": findInDataBase[i][16],
				"address": findInDataBase[i][18],
				"transport": findInDataBase[i][2],
				"mrt": findInDataBase[i][7],
				"lat": findInDataBase[i][5],
				"lng": findInDataBase[i][15],
				"images":findInDataBase[i][13]}
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
			data={"id": findInDataBase[0],
				"name": findInDataBase[3],
				"category": findInDataBase[10],
				"description": findInDataBase[16],
				"address": findInDataBase[18],
				"transport": findInDataBase[2],
				"mrt": findInDataBase[7],
				"lat": findInDataBase[5],
				"lng": findInDataBase[15],
				"images":findInDataBase[13]}
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