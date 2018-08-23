######################################
# 系统模块
######################################
import urllib.request
import json


######################################
# 获取 IP 地址的城市
######################################
def get_ip_location(ip):
    url = "http://ip.taobao.com/service/getIpInfo.php?ip="
    data = urllib.request.urlopen(url + ip).read().decode("utf-8")
    datadict=json.loads(data)

    for oneinfo in datadict:
        if "code" == oneinfo:
            if datadict[oneinfo] == 0:
                county = datadict["data"]["county"]
                if county != '内网IP':
                    country = datadict["data"]["country"]
                    provience = datadict["data"]["region"]
                    city = datadict["data"]["city"]
                    address = country +' '+ provience +' '+ city
                else:
                    address = 'Unknown'
                return address























