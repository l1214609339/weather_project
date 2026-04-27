import requests
import json
import pymysql
import pandas as pd
import os
import hmac
import urllib.parse
import time
import base64
import hashlib
from datetime import datetime





class Weather:

    def __init__(self):

        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir,"config.json")
        with open(json_path,"r",encoding="utf-8") as f:
            self.json_content = json.load(f)
        
        self.api_key = self.json_content["api_key"]
        self.location_id = self.json_content["location_id"]

        self.url = f"https://{self.json_content['api_host']}/v7/weather/now"

        self.params = {
            "location":self.location_id,
            "key":self.api_key
        }

        self.ding_Webhook = self.json_content["Webhook"]
        self.ding_secret = self.json_content["secret"]
        self.ding_access_token = self.json_content["access_token"]

        self.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    def send_ding_message(self,content):

        timestamp = str(round(time.time()*1000))
        timestamp_secret = f"{timestamp}\n{self.ding_secret}"
        secret_en = self.ding_secret.encode('utf-8')
        timestamp_secret_en = timestamp_secret.encode('utf-8')
        hmac_code = hmac.new(secret_en,timestamp_secret_en,digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code).decode())


        params = {
            "access_token":self.ding_access_token,
            "timestamp":timestamp,
            "sign":sign
        }

        headers = {
            "Content-Type":"application/json"
        }

        data = {
            "msgtype":"text",
            "text":{"content":content}
        }
        try:
            response = requests.post(self.ding_Webhook,params=params,headers=headers,json=data,timeout=10)        
            print(json.loads(response.text))
        
        except Exception as e:
            print(f"{self.current_time} 钉钉发送异常：{str(e)}")

    def address_pool(self):

        url_link = self.json_content["link"]
        ip_add = requests.get(url_link).text.strip()
        return ip_add

    def start_get(self):
        # proxy = {
        #     "https": self.address_pool()
        # }

        for num in range(3):
            try:
                response = requests.get(self.url,params=self.params)
                break
            except Exception as e:
                print(f"{self.current_time} 第{num+1}次请求异常: {str(e)}")
                self.send_ding_message(f"{self.current_time} 第{num+1}次请求异常: {str(e)}")
                continue
        if response.status_code == 200:
            data = json.loads(response.text)
            if data["code"] == "200":
                data_now = data["now"]
                self.Date_time = data_now["obsTime"]
                self.Temp = data_now["temp"]
                self.FeelsLike = data_now["feelsLike"]
                self.Text = data_now["text"]
                self.Wind360 = data_now["wind360"]
                self.WindDir = data_now["windDir"]
                self.WindScale = data_now["windScale"]
                self.WindSpeed = data_now["windSpeed"]
                self.Humidity = data_now["humidity"]
                self.Precip = data_now["precip"]
                self.Pressure = data_now["pressure"]
                self.Vis = data_now["vis"]
                self.Cloud = data_now["cloud"]
                self.Dew = data_now["dew"]  
                data_dict = {
                    "ObsTime":[self.Date_time],
                    "Temp":[self.Temp],
                    "FeelsLike":[self.FeelsLike],
                    "Text": [self.Text],
                    "Wind360": [self.Wind360],
                    "WindDir": [self.WindDir],
                    "WindScale": [self.WindScale],
                    "WindSpeed": [self.WindSpeed],
                    "Humidity": [self.Humidity],
                    "Precip": [self.Precip],
                    "Pressure": [self.Pressure],
                    "Vis": [self.Vis],
                    "Cloud": [self.Cloud],
                    "Dew": [self.Dew]
                    }
                return data_dict

        else:
            print(f'{self.current_time} 请求失败，状态码：{response.status_code}')
            self.send_ding_message(f'{self.current_time} 请求失败，状态码：{response.status_code}')

    def data_treating(self,data_dict):

        column = ["ObsTime","Temp","FeelsLike","Text","Wind360","WindDir","WindScale","WindSpeed","Humidity","Precip","Pressure","Vis","Cloud", "Dew"]
        data = pd.DataFrame(
            data_dict,columns=column
        )
        
        data = data.dropna(subset=["ObsTime"])
        data = data.drop_duplicates(subset=["ObsTime"],keep="last")
        data[["ObsTime","time"]] = data["ObsTime"].str.split('T',expand=True)
        self.data_content = [data.iloc[0,:].tolist()]
        data["ObsTime"] = pd.to_datetime(data["ObsTime"])
        data["Precip"] = data["Precip"].astype("float")
        data["Temp"] = data["Temp"].astype("int")
        return data
        
    def save_data(self,data):
        try:
            with pd.ExcelWriter(self.json_content["excel_path"],engine="openpyxl") as writer:
                data.to_excel(writer,index=False,sheet_name="Sheet1")
        except Exception as e:
            print(f"保存Excel失败：{str(e)}")
            self.send_ding_message(f"保存Excel失败：{str(e)}")
        try:
            with pymysql.connect(
                host=self.json_content["db_host"],
                port=self.json_content["db_port"],
                user=self.json_content["db_user"],
                password=self.json_content["db_password"],
                database=self.json_content["db_name"],
                charset="utf8mb4"
            ) as con:
                print('连接数据库成功')
                with con.cursor() as cursor:
                    cteate_tb = '''
                        create table if not exists weather_data (
                            ObsTime DATETIME,
                            Temp INT,
                            FeelsLike VARCHAR(20),
                            Text VARCHAR(50),
                            Wind360 VARCHAR(10),
                            WindDir VARCHAR(10),
                            WindScale VARCHAR(10),
                            WindSpeed VARCHAR(20),
                            Humidity VARCHAR(10),
                            Precip FLOAT,
                            Pressure VARCHAR(10),
                            Vis VARCHAR(20),
                            Cloud VARCHAR(10),
                            Dew VARCHAR(20),
                            Time VARCHAR(50)
                        );
                    '''
                    cursor.execute(cteate_tb)
                    print(self.data_content)
                    data_insert = '''
                        insert into weather_data (
                            ObsTime, Temp, FeelsLike, Text, Wind360, WindDir, WindScale,
                            WindSpeed, Humidity, Precip, Pressure, Vis, Cloud, Dew, time
                        ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    '''
                    cursor.executemany(data_insert,self.data_content)
                    con.commit()
                    self.send_ding_message(f'{self.current_time} 天气采集成功,当前温度是{self.Temp}')
        except Exception as e:
            print(f'连接数据库失败{str(e)}')
            self.send_ding_message(f'连接数据库失败{str(e)}')

if __name__ == '__main__':
    Weathers = Weather()
    start_gets = Weathers.start_get()
    data_treatings = Weathers.data_treating(start_gets)
    save_datas = Weathers.save_data(data_treatings)
    