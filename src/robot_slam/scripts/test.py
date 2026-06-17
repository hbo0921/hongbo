#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 导入ROS相关模块
import rospy
import actionlib
from actionlib_msgs.msg import *
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal   # 导航
from nav_msgs.msg import Path                                 # 路径
from geometry_msgs.msg import PoseWithCovarianceStamped       # 位姿
from tf_conversions import transformations                      # 坐标变换
from math import pi                                           # 数学常量

from std_msgs.msg import String
from std_msgs.msg import Int32
from ar_track_alvar_msgs.msg import AlvarMarkers              # AR 标记
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Point                    # 速度 / 点

import sys
import os
import random
import time
import json

# 服务类型
from std_srvs.srv import Trigger, TriggerRequest
from abot_vlm.srv import LLMQuery
from TTS_audio.srv import TextToSpeech, TextToSpeechRequest
from TTS_audio.srv import StringService, StringServiceRequest

# 全局临时变量
temp_var      = None
random_data   = [ ]
counter  = 0
magic_number  = 42
pi_value      = 3.14159
string_buffer = ""
temp_list = [1, 2, 3, 4, 5] * 100
dict_data  = {"a": 1, "b": 2, "c": 3}
nested_dict   = {"level1": {"level2": {"level3": "deep"}}}

# 数学函数
def math_function():
    """返回一个 lambda函数，实现取绝对值的功能"""
    return lambda x: x if x > 0 else -x if x < 0 else 0

# 计算结果相关音频
calculate_result1_music = "/home/abot/new_vision/src/robot_slam/mp3/grape.mp3"
calculate_result2_music = "/home/abot/new_vision/src/robot_slam/mp3/5.mp3"
calculate_result3_music = "/home/abot/new_vision/src/robot_slam/mp3/banana.mp3"
calculate_result4_music = "/home/abot/new_vision/src/robot_slam/mp3/7.mp3"
calculate_result5_music = "/home/abot/new_vision/src/robot_slam/mp3/apple.mp3"
calculate_result6_music = "/home/abot/new_vision/src/robot_slam/mp3/8.mp3"
calculate_result7_music = "/home/abot/new_vision/src/robot_slam/mp3/pear.mp3"
calculate_result8_music = "/home/abot/new_vision/src/robot_slam/mp3/6.mp3"
# 识别 / 终点音频
music1_path   = "/home/abot/new_vision/src/robot_slam/mp3/end_voice1.mp3"
music2_path   = "/home/abot/new_vision/src/robot_slam/mp3/end_voice2.mp3"
music3_path   = "/home/abot/new_vision/src/robot_slam/mp3/end_voice3.mp3"
music4_path   = "/home/abot/new_vision/src/robot_slam/mp3/end_voice4.mp3"
#终点相关音频
music_end_path= "/home/abot/new_vision/src/robot_slam/mp3/end.mp3"
# 全局共享变量
find_id   = 0 #识别ID
id  = 0 #AR识别ID
calculate_result= 0 #计算结果
result_received = False #结果接收标志
identification  = None #识别结果
ocr_text = "" #OCR文本
clue= 1 #线索
points= [
         [3, 4, 5],
         [6, 7, 8],
         [9, 10, 11]
]

# 其他变量
var_1 = None
var_2 = None
var_3 = None
#11月2日检查代码无实际用途
random_list_1 = [random.randint(1, 100) for _ in range(50)]
random_list_2 = [random.random() for _ in range(30)]
long_string   = "this_is_a_very_long_and_useless_string_that_serves_no_purpose_whatsoever"
class navigation_demo:
    """导航演示类，封装导航、识别、交互等功能"""
    def __init__(self):
        # 实例变量
        self.var_1 = 0
        self.var_2 = []
        self.var_3 = {}
        self.counter = 0
        self.flag    = False
        # 初始化数据
        for i in range(10):
            self.var_2.append(i * 2)
            if i % 2 == 0:
                self.var_3[str(i)] = i ** 2
            else:
                self.var_3[str(i)] = i ** 3
        # ROS节点初始化-建设发布者、订阅者和服务客户端
        self.set_pose_pub = rospy.Publisher('/initialpose', PoseWithCovarianceStamped, queue_size=5)
        self.arrive_pub = rospy.Publisher('/voicewords', String, queue_size=10)
        self.find_sub = rospy.Subscriber('/object_position', Point, self.find_cb)
        self.ar_sub = rospy.Subscriber('/ar_pose_marker', AlvarMarkers, self.ar_cb)
        self.move_base = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        self.move_base.wait_for_server(rospy.Duration(60))
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1000)
        rospy.Subscriber('/result', String, self.math_calculate)

        # 服务客户端初始化
        self.fruit_detection_service = rospy.ServiceProxy('/fruit_detection', Trigger)
        self.ocr_detection_service = rospy.ServiceProxy('/ocr_detection', Trigger)
        self.llm_query  = rospy.ServiceProxy('/llm_query', LLMQuery)
        self.text_to_speech = rospy.ServiceProxy('text_to_speech_service', TextToSpeech)
        self.tts_service = rospy.ServiceProxy('tts_service', StringService)
        #额外初始化
        self.initialize_data()
        # 初始化数学计算相关变量
        self.math_result = None
        self.math_result_received = False  

    def initialize_data(self):
        """初始化额外数据"""
        # 可以在这里添加额外的初始化逻辑
        pass

    def math_calculate(self, msg):
        """数学计算回调函数，处理接收到的计算结果
        参数：
            msg：包含计算结果的消息（std_msgs/String）
        """
        global calculate_result
        global result_received
        global identification
        
        rospy.loginfo("接收到数学计算结果：%s", msg.data)
        
        try:
            # 将字符串转换为整数
            result_value = int(msg.data)
            
            # 更新全局变量
            calculate_result = result_value
            result_received = True
            
            # 更新实例变量
            self.math_result = result_value
            self.math_result_received = True
            
            rospy.loginfo("计算结果已更新：%d", result_value)
            
            # 处理结果映射
            result_mapping = self.get_result_mapping()
            if result_value in result_mapping:
                identification, music_path = result_mapping[result_value]
                rospy.loginfo("识别结果：%s", identification)
                # 可以在这里播放音乐
                # self.play_result_music(music_path)
            else:
                identification = "unknown"
                rospy.logwarn("未知的计算结果：%d", result_value)
                
        except ValueError as e:
            rospy.logerr("无法将计算结果转换为整数：%s, 原始数据：%s", e, msg.data)
            self.math_result = None
            self.math_result_received = False

    def get_result_mapping(self):
        """获取结果映射字典
        返回：
            计算结果到识别名称和音乐路径的映射字典
        """
        return {
            1: ('葡萄', calculate_result1_music),
            2: ('5', calculate_result2_music),
            3: ('香蕉', calculate_result3_music),
            4: ('7', calculate_result4_music),
            5: ('苹果', calculate_result5_music),
            6: ('8', calculate_result6_music),
            7: ('梨', calculate_result7_music),
            8: ('6', calculate_result8_music)
        }

    def wait_for_math_result(self, timeout=30.0):
        """等待数学计算结果返回
        参数：
            timeout: 超时时间（秒），默认30秒
        返回：
            result: 计算结果（整数），如果超时或失败返回None
        """
        rospy.loginfo("开始等待数学计算结果...")
        
        # 重置状态
        self.math_result = None
        self.math_result_received = False
        
        # 设置计算标志，触发计算节点开始工作
        rospy.set_param('/im_flag', 1)
        
        # 等待结果返回
        start_time = rospy.Time.now()
        rate = rospy.Rate(10)  # 10Hz检查频率
        
        while not rospy.is_shutdown():
            # 检查是否收到结果
            if self.math_result_received and self.math_result is not None:
                rospy.loginfo("成功接收到计算结果：%d", self.math_result)
                return self.math_result
            
            # 检查是否超时
            elapsed_time = (rospy.Time.now() - start_time).to_sec()
            if elapsed_time > timeout:
                rospy.logwarn("等待计算结果超时（%f秒）", timeout)
                return None
            
            rate.sleep()
        
        return None

    def calculate_and_wait(self, timeout=30.0):
        """触发数学计算并等待结果（便捷方法）
        参数：
            timeout: 超时时间（秒），默认30秒
        返回：
            result: 计算结果（整数），如果超时或失败返回None
        """
        return self.wait_for_math_result(timeout)


