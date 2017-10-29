from flask import Flask, request, jsonify
import requests
import myfunc
import time
from datetime import datetime,timedelta
import datetime

now = datetime.datetime.now()
unix_now = int(now.timestamp())

app = Flask(__name__)


@app.route("/", methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    resp = jsonify(process_request(req))
    return resp

def process_request(request_data):
    if "result" not in request_data:
        return {}
    message = "よくわかりません。"
    access_token = myfunc.refresh_token()

    city = request_data['result']['parameters']['geo-city']
#    date = request_data['result']['parameters']['date']
    data = request_data['result']['parameters']['data']
    

    if(city!="東京"):
        message = "その都市にはAPは設置されていません。"
        return {
                "data": {"slack": {"text":message}},
            }


#### Get Total Clients ####
    if(data=='total_client'):
        timestamp, client = myfunc.total_client(access_token)
        message = "端末数: {}, 日時:{}".format(client,timestamp)
    
#### Top Application ####
    elif(data=='application'):
        application, percent = myfunc.application_list(access_token,now)
        message ="" 
        for i in range(5):
            message = message+"{}位: {} : {}\n".format(i+1,application[i], percent[i])

#### Top client ####
    elif(data=='top_client'):
        client_name, usage = myfunc.top_client(access_token,now)
        message = ""
        for i in range(5):
            message = message+"{}位: {} : {}GB\n".format(i+1,client_name[i], usage[i])


#### AP Status ####
    elif(data=='ap_status'):
        up_count, down_count = myfunc.ap_status(access_token)
        message = "{}台のAPが稼働中、{}台のAPがダウンしています".format(up_count,down_count)

 
#    else:
 
    return {
            "data": {"slack": {"text":message}},
        }


if __name__ == "__main__":
    app.run(host='0.0.0.0')
