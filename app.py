from flask import *

app=Flask(
	__name__)

app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
from mysql.connector import pooling
import json
import datetime
import requests


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

@app.route("/test")
def layout():
	return render_template("layout.html")

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
		tokenUser=request.cookies["tokenUser"]
	except:
		print("沒有cookie，名為tokenUser")
		return "null",200
	# 驗證token是否有被竄改
	try:
		# 將token解密，取出存放在payload內的資訊
		eee=decode_token(tokenUser)
		info={"data":eee["data"]}
		print(tokenUser)
		print(eee)
		return info,200
	except:
		return "tokenUser 驗證失敗",422

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
			access_tokenUser = create_access_token(identity=getDataFromMemberTable[1],additional_claims=clientInfo)
			# token=access_token
			# refresh_token= create_refresh_token(identity=email)
			# set_access_cookies(resp,access_token,max_age=604800)
			# set_refresh_cookies(resp,refresh_token)
			resp.set_cookie(key="tokenUser",value=access_tokenUser,max_age=3600)

			return resp,200
		else:
			errorInfo={"error": True,"message": "password is wrong , please try again"}
			return errorInfo,400
	except:
		errorInfo={ "error":True,"message":"Internal Server Error"}
		return errorInfo,501


#登出帳戶
@app.delete("/api/user/auth")
def logout():
	# 將cookie中的jwt移除
	resp=jsonify({'ok':True})
	resp.delete_cookie(key="tokenUser")
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


# 取得預定行程
@app.get("/api/booking")
def getUnconfirmedItinerary():
	if(request.cookies.__contains__("tokenUser")):
		try:
			tokenUser=request.cookies["tokenUser"]
			dataInCookie=decode_token(tokenUser)
			id=dataInCookie["data"]["id"]
			connector=mydbPool.get_connection()
			mycursor=connector.cursor()
			mycursor.execute("use taipeiAttractions")
			print("11")
			sql="select * from orderList inner join taipeiAttractionsData on orderList.order_id = taipeiAttractionsData.id where member_id = %s and paid is null"

			val=id
			print("22")
			mycursor.execute(sql,(val,))
			nopaidList=mycursor.fetchall()
			print("33")
			connector.commit()
			mycursor.close()
			connector.close()
			if(len(nopaidList)==0):
				return "null",200
			resList=[]
			for i in nopaidList:
				image=i[20].split("http")
				info={
					"attraction":{
						"id":i[1],
						"name":i[10],
						"address":i[25],
						"image":"http"+image[1]
					},
					"order_id":i[0],
					"date":i[3].isoformat(),
					"time":i[4],
					"price":i[5],
					"paid":i[6]
				}
				print(type(i[3]))
				resList.append(info)
			resp={"data":resList}			
			# return resList[0],200
			print(resp)
			return resp,200
		except:
			connector.commit()
			mycursor.close()
			connector.close()
			errorInfo={"error":True,"message":"伺服器發生錯誤，讀取db失敗"}
			return errorInfo,400
	else:
		errorInfo={"error": True,"message": "尚未登入，請先登入帳號"}
		return errorInfo,403


#建立新的預定行程
@app.post("/api/booking")
def buildNewItinerary():
	try:
		if(not request.cookies.__contains__("tokenUser")):
			print("沒有cookie，名為tokenUser")
			errorInfo={"error":True,"message":"請先登入帳號"}
			return errorInfo,403
		# 將tokenUser解密，取出存放在payload內的資訊
		tokenUser=request.cookies["tokenUser"]
		dataInCookie=decode_token(tokenUser)
		name=dataInCookie["data"]["name"]
		id=dataInCookie["data"]["id"]
		email=dataInCookie["data"]["email"]

		time=request.form["time"]
		date=request.form["date"]
		price=request.form["price"]
		attractionId=request.form["attractionId"]
		# paid=request.form["paid"]
		print(attractionId)
		try:
			connector=mydbPool.get_connection()
			mycursor=connector.cursor()
			mycursor.execute("use taipeiAttractions")
			sql="insert into orderList(attraction_id,member_id,date,time,price) values (%s,%s,%s,%s,%s)"
			val=(attractionId,id,date,time,price)
			mycursor.execute(sql,val)
			connector.commit()
			mycursor.close()
			connector.close()
			print(val)
			return {"ok":True},200
		except:
			connector.commit()
			mycursor.close()
			connector.close()
			errorInfo={"error":True,"nessage":"寫入db時發生錯誤"}
			return errorInfo,400
	except:
		# resp=jsonify({'ok':True})
		# resp.delete_cookie(key="tokenUser")
		errorInfo=jsonify({"error":True,"message":"伺服器錯誤"})
		errorInfo.delete_cookie(key="tokenUser")

		return errorInfo,500


# 刪除目前的預定行程
@app.delete("/api/booking")
def deleteThisItinerary():
	try:
		if(not request.cookies.__contains__("tokenUser")):
			print("沒有cookie，名為tokenUser")
			errorInfo={"error":True,"message":"請先登入帳號"}
			return errorInfo,403
		tokenUser=request.cookies["tokenUser"]
		dataInCookie=decode_token(tokenUser)
		memberId=dataInCookie["data"]["id"]
		orderId=request.form["order_id"]
		connector=mydbPool.get_connection()
		mycursor=connector.cursor()
		mycursor.execute("use taipeiAttractions")
		sql="delete from orderList where order_id = %s and member_id = %s"
		val=(orderId,memberId)
		mycursor.execute(sql,val)
		connector.commit()
		mycursor.close()
		connector.close()
		return {"ok":True},200

	except:
		return "伺服器發生錯誤",400

# 建立新的訂單，並完成付款程序
import json
import requests
@app.post("/api/orders")
def orderToTappay():
	try:
		if(not request.cookies.__contains__("tokenUser")):
			print("沒有cookie，名為tokenUser")
			errorInfo={"error":True,"message":"請先登入帳號"}
			return errorInfo,403
		tokenUser=request.cookies["tokenUser"]
		try:
			dataInCookie=decode_token(tokenUser)
		except:
			errorInfo=jsonify({"error":True,"message":"tokenUser過期，請重新登入"})
			errorInfo.delete_cookie(key="tokenUser")
			return errorInfo,404

		memberId=dataInCookie["data"]["id"]
		prime=request.json["prime"]
		orderIdList=request.json["order"]["trip"]
		userName=request.json["order"]["contact"]["name"]
		userEmail=request.json["order"]["contact"]["email"]
		userPhoneNumber=request.json["order"]["contact"]["phone"]
		amount=0
		connector=mydbPool.get_connection()
		mycursor=connector.cursor()
		mycursor.execute("use taipeiAttractions")
		print("11")
		sql="select * from orderList where member_id = %s"
		val=memberId
		print("22")
		mycursor.execute(sql,(val,))
		userAllOrderList=mycursor.fetchall()
		print("33")
		connector.commit()
		mycursor.close()
		connector.close()
		orderIdListStr=""
		for i in userAllOrderList:
			if i[0] in orderIdList :
				orderIdListStr=orderIdListStr+str(i[0])+","
				amount=amount+i[5]
				print(amount)

		url="https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
		headers={
			'Content-Type': 'application/json',
			'x-api-key': 'partner_GhEedd0oFO42dBxPBp7qWJzRM6Qb6V4h5WPnKkDw0PbYRlTofSamRqEq'
		}
		post_data = {
			"prime":prime,
			"partner_key": "partner_GhEedd0oFO42dBxPBp7qWJzRM6Qb6V4h5WPnKkDw0PbYRlTofSamRqEq",
			"merchant_id": "webber0971_ESUN",
			"amount": amount,
			"currency": "TWD",
			"details": orderIdListStr,
			"cardholder": {
				"phone_number": userPhoneNumber,
				"name": userName,
				"email": userEmail
			},
			"remember": False
		}
		post_data=json.dumps(post_data)
		r=requests.post(url,headers=headers,data=post_data).json()
		res=""
		if(r["msg"] == "Success") :
			# 更改orderList的paid狀態
			try:
				connector=mydbPool.get_connection()
				mycursor=connector.cursor()
				mycursor.execute("use taipeiAttractions")
				print("11")
				orderNumberList=" ".join([str(elem) for elem in orderIdList])
				print(orderNumberList)
				# for i in orderNumberList:
				# 	print(i)
				sql="update orderList set paid = %s where order_id = %s"
				print("iii")
				if(r["order_number"]==""):
					r["order_number"]=123456789				
				for i in orderIdList :
					print("ppp")
					val= (r["order_number"],i)
					mycursor.execute(sql,val)
					connector.commit()
				# 儲存tappay訂單資訊
				print("kkk")
				print(r["order_number"])
				sql="insert into tappay_list(tappay_number,member_id,order_number_list,status,name,email,phone) values (%s,%s,%s,%s,%s,%s,%s)"
				val=(r["order_number"],memberId,orderNumberList,r["status"],userName,userEmail,userPhoneNumber)			
				mycursor.execute(sql,val)
				connector.commit()
				mycursor.close()
				connector.close()
				res={
					"data":{
						"number":r["order_number"],
						"payment":{
							"status":r["status"],
							"message":r["msg"]
						}
					}
				}
				print("訂單編號"+str(r["order_number"])+"已成功存入tappay_list table")
				return res,200
			except:	
				mycursor.close()
				connector.close()
				return {"error":True,"message":"伺服器db發生錯誤"},506
		if(r["msg"] != "Success") :
			try:
				res={
					"data":{
						"payment":{
							"status":r["status"],
							"message":r["msg"]
						}
					}
				}
				return {"error":True,"data":res,"message":r["msg"]},401
			except:
				mycursor.close()
				connector.close()
				res={"error":True,"message":r["msg"]}
				return res,400
	except:
		return "伺服器發生錯誤",500

# 根據訂單編號取得訂單訊息，null表示沒有資料
@app.get("/api/orders/<int:orderNumber>")
def getOrderNumberInfo(orderNumber):
	try:
		if(not request.cookies.__contains__("tokenUser")):
			print("沒有cookie，名為tokenUser")
			errorInfo={"error":True,"message":"請先登入帳號"}
			return errorInfo,403
		tokenUser=request.cookies["tokenUser"]
		try:
			dataInCookie=decode_token(tokenUser)
		except:
			errorInfo=jsonify({"error":True,"message":"tokenUser過期，請重新登入"})
			errorInfo.delete_cookie(key="tokenUser")
			return errorInfo,404

		memberId=dataInCookie["data"]["id"]
		sql="select * from orderList inner join taipeiAttractionsData on orderList.order_id = taipeiAttractionsData.id where paid = %s and member_id = %s"
		val=(orderNumber,memberId)
		connector=mydbPool.get_connection()
		mycursor=connector.cursor()
		mycursor.execute("use taipeiAttractions")
		mycursor.execute(sql,val)
		dataInfo=mycursor.fetchall()

		sql="select * from tappay_list where tappay_number = %s"
		mycursor.execute(sql,val)
		userInfo=mycursor.fetchone()
		connector.commit()
		mycursor.close()
		connector.close()
		# print(dataInfo)
		print(userInfo)
		print(len(dataInfo))
		count=0
		tripList=[]
		price=0
		# res.append
		for i in dataInfo:
			attractionName="attraction"+str(count)
			imageUrl=i[20].split("https")
			print("---------")
			imageUrl1="https"+imageUrl[1]
			cell={
				attractionName:{
					"id":i[0],
					"name":i[10],
					"address":i[25],
					"image":imageUrl1,
					"date":i[3].isoformat(),
					"time":i[4]
				}
			}
			count=count+1
			tripList.append(cell)
			price=price+i[5]
			print(cell)
		res={
			"number":orderNumber,
			"price":price,
			"trip":tripList,
			"contact":{
				"name":userInfo[1],
				"email":userInfo[6],
				"phone":userInfo[7]
			},
			"status":userInfo[4]
		}

		return {"data":res},200
	except:
		return "伺服器發生錯誤",403




app.run(host="0.0.0.0",port=8888)
