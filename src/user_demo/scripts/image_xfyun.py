#!/usr/bin/env python3
#!coding=utf-8
import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time  # 使用 websocket-client 库
import websocket
import threading
#from __future__ import print_function
import os
import rospy
import roslib
import sys
from sensor_msgs.msg import Image
import numpy as np
from cv_bridge import CvBridge
#import imageio

#from std_msgs.msg import String
import cv2
#cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

#appid = "e4101dd1"    #填写控制台中获取的 APPID 信息
#api_secret = "ODM0OGMwOWFmNGNjYzk4MzZjMDUzYTFk"   #填写控制台中获取的 APISecret 信息
#api_key = "006b11e2081be0d88c389e1d5c08feae"    #填写控制台中获取的 APIKey 信息

#imagedata = open("./img7.jpg", 'rb').read()

#imageunderstanding_url = "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"  # 云端环境的服务地址
#text = [{"role": "user", "content": str(base64.b64encode(imagedata), 'utf-8'), "content_type": "image"}]

class Ws_Param(object):
    def __init__(self, APPID, APIKey, APISecret, imageunderstanding_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(imageunderstanding_url).netloc
        self.path = urlparse(imageunderstanding_url).path
        self.ImageUnderstanding_url = imageunderstanding_url

    def create_url(self):
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = 'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        url = self.ImageUnderstanding_url + '?' + urlencode(v)
        return url

class ImageUnderstandingClient:
    def __init__(self, appid, api_key, api_secret, imageunderstanding_url):
        self.appid = appid
        self.api_key = api_key
        self.api_secret = api_secret
        self.imageunderstanding_url = imageunderstanding_url
        self.answer = ""

    def on_error(self, ws, error):
        print("### error:", error)

    def on_close(self, ws, one, two):
        print(" ")
        ws.close_event.set()  # 设置事件，通知主线程连接已关闭

    def on_open(self, ws):
        thread.start_new_thread(self.run, (ws,))

    def run(self, ws, *args):
        data = json.dumps(self.gen_params(question=ws.question))
        ws.send(data)

    def on_message(self, ws, message):
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误： {code}, {data}')
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            print(content, end="")
            self.answer += content
            if status == 2:
                ws.close()

    def gen_params(self, question):
        data = {
            "header": {
                "app_id": self.appid
            },
            "parameter": {
                "chat": {
                    "domain": "image",
                    "temperature": 0.5,
                    "top_k": 4,
                    "max_tokens": 2028,
                    "auditing": "default"
                }
            },
            "payload": {
                "message": {
                    "text": question
                }
            }
        }
        return data

    def process_question(self, hy, input_text="这个题的答案是多少"):
        imagedata = open(hy, 'rb').read()
        question = self.checklen(self.getText("user", input_text))
        print("调用视觉大模型结果为：", end="")
        self.main(question)

    def getText(self, role, content):
        jsoncon = {}
        jsoncon["role"] = role
        jsoncon["content"] = content
        text.append(jsoncon)
        return text

    def getlength(self, text):
        length = 0
        for content in text:
            temp = content["content"]
            leng = len(temp)
            length += leng
        return length

    def checklen(self, text):
        while (self.getlength(text[1:]) > 8000):
            del text[1]
        return text

    def main(self, question):
        wsParam = Ws_Param(self.appid, self.api_key, self.api_secret, self.imageunderstanding_url)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close, on_open=self.on_open)
        ws.question = question
        ws.close_event = threading.Event()  # 创建事件对象
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        ws.close_event.wait()  # 等待事件被设置
def callback(msg):
    print("Received image with dimensions: %dx%d" , (msg.width, msg.height))
    cv_image = CvBridge.imgmsg_to_cv2(np.array(msg.data),desired_encoding="bgr8")
 
        # Save the image to a file
    filename = "image_1.jpg"
    cv2.imwrite(filename, cv_image)
   
   
    imageunderstanding_url = "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"  # 云端环境的服务地址
    text = [{"role": "user", "content": str(base64.b64encode(msg.data), 'utf-8'), "content_type": "image"}]
    client = ImageUnderstandingClient("e4101dd1", "ODM0OGMwOWFmNGNjYzk4MzZjMDUzYTFk", "006b11e2081be0d88c389e1d5c08feae", imageunderstanding_url)
    client.process_question(hy=b)

if __name__ == '__main__':
    rospy.init_node('webcam display', anonymous=True)
    rospy.Subscriber('/usb_cam/image_raw', Image, callback)
    rospy.spin()
    
   
              

       
