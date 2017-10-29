import time
from pytz import timezone
from datetime import datetime, timedelta
import datetime
import requests
import csv, json

f = open('token.txt','r')
token_dict = json.load(f)

base_url_s = "https://internal-apigw.central.arubanetworks.com/"
base_url = "http://internal-apigw.central.arubanetworks.com/"

#### Refresh_API_Token ####
def refresh_token():
    client_id = token_dict['client_id']
    client_secret = token_dict['client_secret']
    refresh_token = token_dict['refresh_token']
    url = base_url_s+"oauth2/token?client_id="+client_id+"&client_secret="+client_secret+"&refresh_token="+refresh_token+"&grant_type=refresh_token"

    response = requests.request("POST", url)
    token_dict['refresh_token'] = response.json()['refresh_token']
    token_dict['access_token'] = response.json()['access_token']
    access_token = response.json()['access_token']
    f = open('token.txt', 'w')
    json.dump(token_dict, f)
    f.close()
    return access_token

#### Get Total Clients ####
def total_client(access_token):
    url = base_url+"monitoring/v1/clients/count?access_token="+access_token
    s = requests.session()
    r = s.request("POST", url)
    epoch_time = r.json()['samples'][35]['timestamp']   
    jst = datetime.datetime.fromtimestamp(epoch_time) + timedelta(hours=9)
    
    timestamp = jst.strftime("%Y/%m/%d %H:%M:%S")
    client = r.json()['samples'][35]['client_count']   
    return (timestamp,client)

#### Get Application List ####
def application_list(access_token,now):
    week = now + datetime.timedelta(weeks=-1)
    week_unix = int(time.mktime(week.timetuple()))
    url = base_url+"apprf/v1/applications?access_token="+access_token+"&from_timestamp="+str(week_unix)
    s = requests.session()
    r = s.request("POST", url)
    application = []
    percent = []
    for i in range(5):
        application.insert(i,r.json()['result'][i]['name'])   
        percent.insert(i,r.json()['result'][i]['percent_usage']) 
    return (application,percent)

#### Top N Client ####
def top_client(access_token,now):
    week = now + datetime.timedelta(weeks=-1)
    week_unix = int(time.mktime(week.timetuple()))
    url = base_url+"monitoring/v1/clients/bandwidth_usage/topn?access_token="+access_token+"&from_timestamp="+str(week_unix)
    s = requests.session()
    r = s.request("POST", url)
    client_name = []
    usage = []
    for i in range(5):
        client_name.insert(i,r.json()['clients'][i]['name'])
        rx_usage = r.json()['clients'][i]['rx_data_bytes']   
        tx_usage = r.json()['clients'][i]['tx_data_bytes']   
        total_usage = round((rx_usage + tx_usage)/10**9,2)
        usage.insert(i,total_usage)
    return (client_name,usage)

#### AP Status ####
def ap_status(access_token):
    url = base_url+"monitoring/v1/aps?access_token="+access_token+"&status=Up"
    s = requests.session()
    r = s.request("POST", url)
    up_count = r.json()['count']

    url = base_url+"monitoring/v1/aps?access_token="+access_token+"&status=Down"
    s = requests.session()
    r = s.request("POST", url)
    down_count = r.json()['count']
    
    return (up_count,down_count)



