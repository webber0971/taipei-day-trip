from flask import *
app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
from mysql.connector import pooling

#載入&實例化jwt
from flask_jwt_extended import create_access_token, jwt_required,set_access_cookies,unset_jwt_cookies,JWTManager
jwt = JWTManager()
app.config["JWT_SECRET_KEY"] = "this-is-a-key-in-taipeidAttractionsProgram"  #設定jwt密鑰
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


@app.route('/')
def index():
    
    AccountName="eee"
    add={"address":123,"time":"12:00"}
    access_token = create_access_token(identity=AccountName)
    resp=jsonify({"ok":True})
    print(AccountName)
    print(access_token)
    resp.set_cookie(key="hi",value=access_token,max_age=604800)
    return resp,200


@app.put("/api/user/ayth")
def login():
	passwordIndex=3
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
			return jsonify({"error": True,"message": "email or password is wrong , please try again"}),400
		if(getDataFromMemberTable[passwordIndex]==password):
			# resp.set_cookie("access_token")
			# 將標頭內的set-cookie用來將jwt存到cookie中			
			resp=jsonify({"ok": True})
			print(resp)
			access_token = create_access_token(identity="EEE")
			print(access_token)
			# refresh_token= create_refresh_token(identity=email)
			set_access_cookies(resp,access_token,max_age=604800)
			# set_refresh_cookies(resp,refresh_token)
			# resp.set_cookie(key="token",value=access_token,max_age=604800)
			return resp,200
	except:
		return jsonify({ "error":True,"message":"server error"}),500

app.run(port=3000)