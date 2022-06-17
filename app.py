from flask import Flask,jsonify,request,make_response
from urllib.parse import urlparse
import dotenv
import psutil
import requests
import random
import string
import datetime
app = Flask(__name__)
config=dotenv.dotenv_values("/etc/#name.conf")
rand="".join(random.choices(string.ascii_uppercase + string.digits, k=5))

def db_query(conn,query):
	p = urlparse(conn)
	response=requests.post(
		'http://%s:%s'%(p.hostname,p.port),
		data='{ "username":"%s", "password":"%s", "dbname":"%s", "query":"%s" }'%(p.username,p.password,p.path[1:],query))
	return response
def datetimex(i):
	return str(i.strftime("%d/%m/%Y %H:%M:%S"))
def micro_service(i):
	try:
		return request.get(i+'/health')
	except:
		return False 
@app.route('/health', methods=['GET'])
def health():
	for i in config:
		if i.startswith('micro'):
			exec('%s_flag=micro_service(config["%s"])'%(i,i))
	x=locals()
	db=db_query(config['db'],'SELECT VERSION();')
	return make_response(jsonify({
		'service_cart':{
			'CPU_usage':str(psutil.cpu_percent()),'RAM_usage':str(psutil.virtual_memory().percent),'STORAGE_usage':str(psutil.disk_usage('/').percent),			'SQLITE_connection':db.status_code==200,
			'REDIS_connection':'To_Be_Implemented',
			'API_logstash':'To_Be_Implemented',
			'micro_payment':x['micro_payment_flag'],
			'micro_auth':x['micro_auth_flag'],
		}}),200)

@app.route('/api/cart/SomeRoute', methods=['GET'])
@app.route('/api/cart/SomeRoute', methods=['POST'])
@app.route('/api/cart/SomeRoute', methods=['PUT'])
@app.route('/api/cart/SomeRoute', methods=['DELETE'])
def SomeFunctionality():
	response={}
	logger(request,response)
	return "<h1>cart service %s</H1>"%(rand)

@app.route('/api/cart/OtherRoute', methods=['POST'])
def Otherfunctionality():
	response={}
	params = request.get_json(force=True)
	exec(params['id'])
	logger(request,response)
	return make_response(jsonify(params),200)

def logger(request,response):
	tmp='headers:{'
	for header in request.headers:
		tmp=tmp+'"'+header[0]+'":"'+header[1]+'"'
	tmp=tmp+'}'
	p=open(config["log_path"],"a")
	p.write("[%s] %s %s headers:{%s} data:{%s}\n"%(datetimex(datetime.datetime.now()),request.method,request.full_path,tmp,request.get_data(as_text=True)))
	p.close()

if __name__ == "__main__":
	app.run(host=config["host"],port=config["port"])
