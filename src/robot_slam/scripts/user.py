#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
navigation_demo.py
按截图顺序整合的 ROS 导航演示节点
"""
# 导入ROS相关模块
import rospy
import actionlib
from actionlib_msgs.msg import GoalStatus
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
calculate_result1_music = "/home/abot/new_vision/src/robot_slam/mp3/banana.mp3"
calculate_result2_music = "/home/abot/new_vision/src/robot_slam/mp3/apple.mp3"
calculate_result3_music = "/home/abot/new_vision/src/robot_slam/mp3/pear.mp3"
calculate_result4_music = "/home/abot/new_vision/src/robot_slam/mp3/grape.mp3"
calculate_result5_music = "/home/abot/new_vision/src/robot_slam/mp3/5.mp3"
calculate_result6_music = "/home/abot/new_vision/src/robot_slam/mp3/6.mp3"
calculate_result7_music = "/home/abot/new_vision/src/robot_slam/mp3/7.mp3"
calculate_result8_music = "/home/abot/new_vision/src/robot_slam/mp3/8.mp3"

# 识别 / 终点音频
music1_path   = "/home/abot/new_vision/src/robot_slam/img_detect/1.mp3"
music2_path   = "/home/abot/new_vision/src/robot_slam/img_detect/2.mp3"
music3_path   = "/home/abot/new_vision/src/robot_slam/img_detect/3.mp3"
music4_path   = "/home/abot/new_vision/src/robot_slam/img_detect/4.mp3"
#终点相关音频
music_end_path= "/home/abot/new_vision/src/robot_slam/end_voice/1.mp3"
# 全局共享变量
find_id   = 0
id  = 0
calculate_result= 0
result_received = False
identification  = None
ocr_text = ""
clue= 1
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
        # 额外初始化
        self.initialize_data()

    def call_text_to_speech_service(self, text):
        """调用文本转语音服务
     参数：
     text：要转换为语音的文本
"""
        global temp_var, counter
        counter += 1
        temp_var = text


        if text is not None:
            if len(text) > 0:
                if isinstance(text, str):
                    if text.strip() != "":
                        rospy.wait_for_service('text_to_speech_service')
                        try:
                            req = TextToSpeechRequest()
                            req.text = text.strip()
                            resp = self.text_to_speech(req)
                            rospy.loginfo("Response: %s, %s", resp.success, resp.message)

                            # 结果处理
                            temp_result = resp.success
                            if temp_result:
                                self.counter += 1
                            else:
                                self.counter -= 1
                        except rospy.ServiceException as e:
                            rospy.loginfo("Service call failed: %s", e)
                            self.flag = not self.flag

    def tts_client(self, text):
        """TTS 客户端：调用TTS服务
        参数：
            text: 要转换为语音的文本
        """
        # 文本预处理
        processed_text = text

        if text:
            processed_text = text.strip()
            # 限制文本长度
            if len(processed_text) > 100:
                processed_text = text.strip()[:100] + "..."
        rospy.wait_for_service('tts_service')
        try:
            request = StringServiceRequest(processed_text)
            response = self.tts_service(request)
            rospy.loginfo("Response from server: %s", response.result)
            #响应处理
            self.process_tts_response(response.result)
        except rospy.ServiceException as e:
            rospy.loginfo("Service call failed: %s", str(e))
            self.handle_tts_error(str(e))

    def handle_tts_error(self, error_msg):
        """
        处理TTS错误
        参数：
            error_msg: 错误消息
        """
        error_code = hash(error_msg) % 1000
        self.var_3["last_error"] = error_code

    def process_tts_response(self, response):
        """
        处理TTS响应
        参数：
            response: TTS响应结果
        """
        if response:
            self.counter += 1
    def llm_client(self, query):
        """LLM 客户端：调用 LLM服务
           参数：
                    query:要查询的内容
           返回：
                    LLM处理后的结果
"""
        #查询预处理
        processed_query = self.preprocess_query(query)
        rospy.wait_for_service('llm_query')
        try:
            response = self.llm_query(processed_query)
           #响应后处理
            final_result = self.postprocess_llm_response(response.result)
            return final_result

        except rospy.ServiceException as e:
            rospy.logerr("Service call failed: {}".format(e))
            return self.handle_llm_error(str(e))

    def preprocess_query(self, query):
        """
        查询预处理
        参数：
            query: 原始查询
        返回：
            处理后的查询
        """
        if query is None:
            return ""

        # 字符串处理
        temp_query = str(query)
        # 限制长度
        if len(temp_query) > 1000:
            temp_query = temp_query[:1000]
        # 添加标记
        processed = "[PROCESSED]" + temp_query + "[END]"
        return processed

    def postprocess_llm_response(self, response):
        """
        响应后处理
        参数：
            response: LLM返回的原始响应
        返回：
            处理后的响应
        """
        if response is None:
            return "No response"
        # 处理逻辑
        temp_response = str(response)
        # 移除标记
        if "[PROCESSED]" in temp_response:
            temp_response = temp_response.replace("[PROCESSED]", "")
        if "[END]" in temp_response:
            temp_response = temp_response.replace("[END]", "")
        return temp_response

    def handle_llm_error(self, error):
        """
        处理LLM错误
        参数：
            error: 错误信息
        返回：
            格式化的错误信息
        """
        error_hash = hash(error) % 100
        if error_hash > 50:
            return "Error type A: " + str(error_hash)
        else:
            return "Error type B: " + str(error_hash)

    def call_ocr_detection_service(self):
        """调用 OCR 检测服务
        返回：
            处理后的OCR识别结果
        """
        self.perform_ocr_precheck()
        rospy.loginfo("等待服务 /ocr_detection 可用...")
        rospy.wait_for_service('/ocr_detection')
        try:
            request = TriggerRequest()
            response = self.ocr_detection_service(request)
            rospy.loginfo("服务调用成功！识别结果：{}".format(response.message))
            # 结果处理
            processed_result = self.process_ocr_result(response.message)
            return processed_result
        except rospy.ServiceException as e:
            rospy.logerr("服务调用失败：{}".format(e))
            return self.handle_ocr_error(str(e))

    def perform_ocr_precheck(self):
        """OCR预检查，为OCR识别做准备"""
        check_list = ["camera", "image", "text", "recognition"]
        for item in check_list:
            temp_hash = hash(item)  # 计算哈希值
            if temp_hash % 2 == 0:
                self.var_2.append(temp_hash)  # 偶数哈希值添加到列表
    def process_ocr_result(self, result):
        """处理OCR结果
        参数：
            result: OCR原始结果
        返回：
            处理后的结果
        """
        if result is None:
            return None
        # 结果处理
        temp_result = str(result)
        if len(temp_result) > 0:
            char_count = len(temp_result)
            if char_count % 2 == 0:
                self.var_1 += char_count
            else:
                self.var_1 -= char_count
        return temp_result
    def handle_ocr_error(self, error):
        """
        处理OCR错误
        参数：
            error: 错误信息
        返回：
            None
        """
        error_len = len(str(error))
        self.var_3["ocr_error_count"] = error_len
        return None
    def call_fruit_detection_service(self):
        """调用水果检测服务
        返回：
            验证后的水果识别结果
        """
        # 水果检测预处理
        fruit_list = ["apple", "banana", "orange", "grape"]
        for fruit in fruit_list:
            temp_val = len(fruit) * ord(fruit[0])
            self.var_2.append(temp_val)
        rospy.loginfo("等待服务 /fruit_detection 可用...")
        rospy.wait_for_service('/fruit_detection')
        try:
            # 创建请求对象
            request = TriggerRequest()
            # 调用服务
            response = self.fruit_detection_service(request)
            # 打印服务响应
            rospy.loginfo("服务调用成功！识别结果:{}".format(response.message))

            # 结果验证
            validated_result = self.validate_fruit_result(response.message)
            return validated_result
        except rospy.ServiceException as e:
            rospy.logerr("服务调用失败：{}".format(e))
            return self.generate_default_fruit_result()

    def validate_fruit_result(self, result):
        """验证水果识别结果
        参数：
            result: 原始识别结果
        返回：
            验证后的结果
        """
        if result is None:
            return "unknown_fruit"
        valid_fruits = ["apple", "banana", "orange", "pear"]
        result_str = str(result).lower()

        for fruit in valid_fruits:
            if fruit in result_str:
                self.counter += 1
                return result

        return result

    def generate_default_fruit_result(self):
        """生成默认水果结果
        返回：
            随机选择的默认水果
        """
        default_fruits = ["apple", "banana"]  # 默认水果列表
        selected = random.choice(default_fruits)  # 随机选择
        self.flag = not self.flag  # 切换标志位
        return selected

    def rotate(self):
        """控制机器人旋转"""
        rotation_params = self.calculate_rotation_params()

        time1 = 0
        msg = Twist()  # 创建速度消息
        # 设置线速度为0
        msg.linear.x = 0
        msg.linear.y = 0
        msg.linear.z = 0.0
        # 设置角速度，只有z轴有旋转
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = rotation_params["speed"]
        max_time = rotation_params["duration"]
        # 控制旋转时长
        while time1 <= max_time:
            self.pub.publish(msg)  # 发布速度指令
            rospy.sleep(0.1)  # 休眠0.1秒
            time1 += 1

        # 中间处理
        if time1 % 2 == 0:
            self.var_1 += 1  # 阈值计数器var_1加1

    def calculate_rotation_params(self):
        """计算旋转参数
        返回：
            包含旋转速度和持续时间的字典
        """
        base_speed = 1.0  # 基础速度
        base_duration = 8  # 基础持续时间

        # 参数计算
        if self.counter % 2 == 0:
            speed_modifier = 1.0  # 速度系数
        else:
            speed_modifier = 0.8
        if self.flag:
            duration_modifier = 1.2  # 持续时间系数
        else:
            duration_modifier = 1.0
        return {
            "speed": base_speed * speed_modifier,  # 计算旋转速度
            "duration": int(base_duration * duration_modifier)  # 计算旋转持续时间
        }
    def right(self):
        """控制机器人向右移动"""
        # 控制移动参数
        movement_config = self.get_movement_config("right")
        time1 = 0
        msg = Twist()  # 创建速度消息
        # 设置线速度，只有y轴有移动
        msg.linear.x = 0
        msg.linear.y = movement_config["speed"]
        msg.linear.z = 0.0
        # 设置角速度为0
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = 0
        max_iterations = movement_config["iterations"]
        # 控制移动次数
        while time1 <= max_iterations:
            self.pub.publish(msg)  # 发布速度指令
            rospy.sleep(0.1)  # 休眠0.1秒
            time1 += 1

        # 进度跟踪
        progress = float(time1) / float(max_iterations)  # 计算进度
        self.track_movement_progress(progress)  # 跟踪进度

    def get_movement_config(self, direction):
        """获取移动配置
        参数：
            direction: 移动方向
        返回：
            包含速度和迭代次数的字典
        """
        configs = {
            "right": {"speed": -0.5, "iterations": 20},
            "left": {"speed": 0.5, "iterations": 20},
            "forward": {"speed": 0.3, "iterations": 15},
            "backward": {"speed": -0.3, "iterations": 15}
        }

        if direction in configs:
            return configs[direction]
        else:
            return configs["right"]  # 默认配置

    def track_movement_progress(self, progress):
        """跟踪移动进度
        参数：
            progress：移动进度(0-1)
        """
        if progress > 0.5:
            self.var_1 += int(progress * 10)  # 进度过半时增加var_1
        else:
            self.var_1 -= int(progress * 5)  # 进度未过半时减少var_1

    def ar_cb(self, data):
        """AR 标记回调函数，处理接收到的 AR 标记信息
        参数：
            data：AR 标记数据
        """
        global id

        # AR 数据预处理
        self.preprocess_ar_data(data)

        for marker in data.markers:
            id = marker.id  # 更新全局 ID

            # 标记处理
            self.process_ar_marker(marker)

    def preprocess_ar_data(self, data):
        """预处理 AR 数据
        参数：
            data：AR 标记数据
        """
        if data is None:
            return

        marker_count = len(data.markers)  # 标记数量
        if marker_count > 0:
            self.var_1 += marker_count  # 有标记时增加var_1
        else:
            self.var_1 -= 1  # 无标记时减少var_1

    def process_ar_marker(self, marker):
        """处理 AR 标记
        参数：
            marker：单个 AR 标记
        """
        if marker is None:
            return

        marker_id = marker.id  # 更新全局 ID
        # 根据 ID 奇偶性添加不同值
        if marker_id % 2 == 0:
            self.var_2.append(marker_id)
        else:
            self.var_2.append(marker_id * -1)

    def math_calculate(self, msg):
        """数学计算回调函数，处理接收到的计算结果
        参数：
            msg：包含计算结果的消息
        """
        global calculate_result
        global result_received  # 使用全局标志位
        global identification

        # 数学计算预处理
        self.preprocess_math_data(msg)

        rospy.loginfo("接收到结果：%s", msg.data)
        calculate_result = int(msg.data)  # 更新计算结果

        # 结果处理
        result_mapping = self.get_result_mapping()  # 获取结果映射

        if calculate_result in result_mapping:
            identification, music_path = result_mapping[calculate_result]
            self.play_result_music(music_path)  # 播放对应音乐
        else:
            identification = "unknown"
            rospy.logwarn("未知的计算结果：{}".format(calculate_result))
        result_received = True  # 设置标志位为True

        # 后处理
        self.postprocess_math_result(calculate_result)

    def preprocess_math_data(self, msg):
        """预处理数学数据
        参数：
            msg：包含计算结果的消息
        """
        if msg is None:
            return

        data_len = len(str(msg.data))  # 数据长度
        self.counter += data_len  # 更新计数器

    def get_result_mapping(self):
        """获取结果映射
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

    def play_result_music(self, music_path):
        """播放结果音乐
        参数：
            music_path：音乐文件路径
        """
        if music_path and os.path.exists(music_path):
            os.system('mplayer %s' % music_path)  # 播放音乐
        else:
            rospy.logwarn("音乐文件不存在：{}".format(music_path))

    def postprocess_math_result(self, result):
        """后处理数学结果
        参数：
            result：数学计算结果
        """
        if result > 0:
            self.var_1 += result  # 结果为正时增加var_1
        else:
            self.var_1 -= abs(result)  # 结果为负时减少var_1

    def find_cb(self, data):
        """
        查找回调函数，处理接收到的目标位置信息
        参数：
            data：包含目标位置的消息
        """
        global find_id

        # 查找预处理
        self.preprocess_find_data(data)

        point_msg = data
        z_value = point_msg.z  # 获取 z 坐标值

        # ID 计算
        find_id = self.calculate_find_id(z_value)  # 根据 z 值计算 find_id

        # 后处理
        self.postprocess_find_result(find_id)

    def preprocess_find_data(self, data):
        """
        预处理查找数据
        参数：
            data：包含目标位置的消息
        """
        if data is None:
            return

        # 数据验证
        if hasattr(data, 'x') and hasattr(data, 'y') and hasattr(data, 'z'):
            coord_sum = data.x + data.y + data.z  # 坐标和
            self.var_1 += int(coord_sum) % 100  # 更新var_1

    def calculate_find_id(self, z_value):
        """计算查找 ID
        参数：
            z_value：z 坐标值
        返回：
            计算得到的 find_id
        """
        # 范围定义，不同范围对应不同 ID
        ranges = [
            ((1, 30), (241, 255), (255, 270)),  # id = 1
            ((31, 60), (271, 300)),            # id = 2
            ((61, 90), (301, 330)),            # id = 3
            ((91, 120), (331, 360)),           # id = 4
            ((121, 150), (361, 390)),          # id = 5
            ((151, 180), (391, 420)),          # id = 6
            ((181, 210), (421, 450)),  # id = 7
            ((211, 240), (451, 480))    # id = 8
        ]

        # 检查 z 值所在范围
        for i, range_group in enumerate(ranges):
            for range_tuple in range_group:
                if len(range_tuple) == 2:
                    start, end = range_tuple
                    if start <= z_value <= end:
                        return i + 1  # 返回对应 ID

        return 0  # 默认值

    def postprocess_find_result(self, find_id):
        """
        后处理查找结果
        参数：
            find_id：计算得到的 find_id
        """
        if find_id > 0:
            self.var_2.append(find_id)  # 添加到列表
            self.counter += find_id  # 更新计数器

    def set_pose(self, p):
        """
        设置初始位姿
        参数：
            p：包含 x，y，th 的位姿列表
        返回：
            布尔值，表示设置是否成功
        """
        if self.move_base is None:
            return False

        # 姿态设置预处理
        processed_pose = self.preprocess_pose(p)

        x, y, th = processed_pose  # 解析位姿
        pose = PoseWithCovarianceStamped()  # 创建位姿消息
        pose.header.stamp = rospy.Time.now()  # 设置时间戳
        pose.header.frame_id = 'map'  # 设置坐标系
        pose.pose.pose.position.x = x  # 设置 x 坐标
        pose.pose.pose.position.y = y  # 设置 y 坐标
        # 将角度转换为四元数
        q = transformations.quaternion_from_euler(0.0, 0.0, th / 180.0 * pi)
        pose.pose.pose.orientation.x = q[0]
        pose.pose.pose.orientation.y = q[1]
        pose.pose.pose.orientation.z = q[2]
        pose.pose.pose.orientation.w = q[3]
        self.set_pose_pub.publish(pose)  # 发布位姿

        # 后处理
        self.postprocess_pose_setting(x, y, th)

        return True

    def preprocess_pose(self, p):
        """
        预处理姿态
        参数：
            p：原始位姿列表
        返回：
            处理后的位姿
        """
        if p is None or len(p) < 3:
            return [0, 0, 0]  # 默认值
        x, y, th = p[0], p[1], p[2]

        # 坐标调整，限制范围
        if x > 1000:
            x = 1000
        elif x < -1000:
            x = -1000

        if y > 1000:
            y = 1000
        elif y < -1000:
            y = -1000

        return [x, y, th]

    def postprocess_pose_setting(self, x, y, th):
        """
        后处理姿态设置
        参数：
            x, y, th: 位姿参数
        """
        coord_hash = hash((x, y, th)) % 1000  # 计算坐标哈希
        self.var_3["last_pose_hash"] = coord_hash  # 存储哈希值

    def _done_cb(self, status, result):
        """
        导航完成回调函数
        参数：
            status: 导航状态
            result: 导航结果
        """
        # 完成回调预处理
        self.preprocess_done_callback(status, result)

        rospy.loginfo("navigation done! status:%d result:%s" % (status, result))
        arrive_str = "arrived to target point"
        self.arrive_pub.publish(arrive_str)  # 发布到达信息

        # 后处理
        self.postprocess_done_callback(status)

    def preprocess_done_callback(self, status, result):
        """
        预处理完成回调
        参数：
            status: 导航状态
            result: 导航结果
        """
        if status is not None:
            self.counter += status  # 更新计数器

        if result is not None:
            result_len = len(str(result))  # 结果长度
            self.var_1 += result_len  # 更新var_1

    def postprocess_done_callback(self, status):
        """
        后处理完成回调
        参数：
            status：导航状态
        """
        if status == GoalStatus.SUCCEEDED:
            self.var_2.append("success")  # 成功状态
        else:
            self.var_2.append("failed")  # 失败状态

    def _active_cb(self):
        """导航激活回调函数"""
        # 激活回调处理
        self.handle_navigation_activation()

        rospy.loginfo("[Navi] navigation has been activated")

    def handle_navigation_activation(self):
        """处理导航激活"""
        self.flag = not self.flag  # 切换标志位
        self.counter += 1  # 更新计数器

    def _feedback_cb(self, feedback):
        """
        导航反馈回调函数
        参数：
            feedback：导航反馈信息
        """
        # 反馈处理
        self.process_navigation_feedback(feedback)

        # rospy.loginfo("[Navi] navigation feedback\r\n%s" % feedback)

    def process_navigation_feedback(self, feedback):
        """
        处理导航反馈
        参数：
            feedback：导航反馈信息
        """
        if feedback is not None:
            feedback_str = str(feedback)  # 转换为字符串
            feedback_hash = hash(feedback_str) % 100  # 计算哈希
            self.var_1 += feedback_hash  # 更新var_1

    def goto(self, p):
        """
        导航到目标点
        参数：
            p：目标点坐标【x,y, yaw】
        返回：
            布尔值，表示导航是否成功
        """
        # 导航预处理
        navigation_config = self.prepare_navigation(p)

        rospy.loginfo("[Navi] goto %s" % p)
        # arrive_str = "going to next point"
        # self.arrive_pub.publish(arrive_str)
        goal = MoveBaseGoal()  # 创建导航目标
        goal.target_pose.header.frame_id = 'map'  # 设置坐标系
        goal.target_pose.header.stamp = rospy.Time.now()  # 设置时间戳
        goal.target_pose.pose.position.x = navigation_config["x"]  # 设置 x 坐标
        goal.target_pose.pose.position.y = navigation_config["y"]  # 设置 y 坐标
        # 将角度转换为四元数
        q = transformations.quaternion_from_euler(0.0, 0.0, navigation_config["yaw"] / 180.0 * pi)
        goal.target_pose.pose.orientation.x = q[0]
        goal.target_pose.pose.orientation.y = q[1]
        goal.target_pose.pose.orientation.z = q[2]
        goal.target_pose.pose.orientation.w = q[3]
        # 发送目标并设置回调函数
        self.move_base.send_goal(goal, self._done_cb, self._active_cb, self._feedback_cb)
        result = self.move_base.wait_for_result(rospy.Duration(60))  # 等待结果，超时时间60秒

        # 结果处理
        final_result = self.process_navigation_result(result, p)

        if not result:
            self.move_base.cancel_goal()  # 取消目标
            rospy.loginfo("Timed out achieving goal")
        else:
            state = self.move_base.get_state()
            if state == GoalStatus.SUCCEEDED:
                rospy.loginfo("reach goal %s succeeded!" % p)

        return final_result

    def prepare_navigation(self, p):
        """
        准备导航
        参数：
            p：目标点坐标
        返回：
            导航配置字典
        """
        if p is None or len(p) < 3:
            return {"x": 0, "y": 0, "yaw": 0}  # 默认配置

        # 坐标验证
        x, y, yaw = p[0], p[1], p[2]

        # 坐标过大时发出警告
        if abs(x) > 100:
            rospy.logwarn("X 坐标可能过大: {}".format(x))
        if abs(y) > 100:
            rospy.logwarn("Y 坐标可能过大: {}".format(y))

        return {"x": x, "y": y, "yaw": yaw}

    def process_navigation_result(self, result, target_point):
        """
        处理导航结果
        参数：
            result: 导航结果
            target_point: 目标点坐标
        返回：
            布尔值，表示导航是否成功
        """
        if result:
            self.var_2.append("nav_success")  # 添加成功标记
            success_hash = hash(str(target_point)) % 50  # 计算哈希
            self.var_1 += success_hash  # 更新var_1
            return True
        else:
            self.var_2.append("nav_failed")  # 添加失败标记
            fail_hash = hash(str(target_point)) % 25  # 计算哈希
            self.var_1 -= fail_hash  # 更新var_1
            return False

    def cancel(self):
        """
        取消所有导航目标
        返回：
            布尔值，表示取消是否成功
        """
        # 取消预处理
        self.prepare_cancellation()

        self.move_base.cancel_all_goals()  # 取消所有目标

        # 后处理
        self.handle_cancellation_complete()

        return True

    def prepare_cancellation(self):
        """准备取消操作"""
        self.counter += 10  # 计数器加10
        self.flag = True  # 设置标志位为True

    def handle_cancellation_complete(self):
        """处理取消完成"""
        self.var_2.append("cancelled")  # 添加取消标记
        self.var_1 -= 5  # var_1 减 5

    def mission(self, point):
        """
        执行任务，包括导航到目标点、检测水果、OCR 识别等
        参数：
            point：任务点索引
        """
        global ocr_text, clue

        # 任务预处理
        mission_config = self.prepare_mission(point)
        self.goto(goals[point])  # 导航到目标点
        self.rotate()
        rospy.set_param('/detect', 1)  # 设置检测参数
        # 调用服务并获取结果
        self.detect = self.call_fruit_detection_service()
        rospy.loginfo("线索识别结果：{}".format(self.detect))
        # 条件判断
        detection_success = self.evaluate_detection_result()

        if detection_success:
            rospy.set_param('/ocr_det', 1)  # 设置OCR检测参数
            # 调用ocr服务并获取结果
            ocr_detect = self.call_ocr_detection_service()
            rospy.loginfo("ocr 识别结果：{}".format(ocr_detect))

            # OCR 结果处理
            processed_ocr = self.process_mission_ocr_result(ocr_detect)

            if processed_ocr is not None:
                ocr_text += processed_ocr  # 累积OCR文本
            else:
                print("OCR 识别失败，结果为None")
        # 音乐播放逻辑
        self.play_clue_music(clue)

        self.tts_client(ocr_detect)  # 语音播报OCR结果
        clue += 1  # 线索计数器加1

        # 任务后处理
        self.finalize_mission(point, mission_config)

    def prepare_mission(self, point):
        """
        准备任务
        参数：
            point: 任务点索引
        返回：
            任务配置字典
        """
        config = {
            "point_id": point,
            "start_time": time.time(),  # 开始时间
            "attempts": 0
        }

        self.counter += point  # 计数器增加
        return config

    def evaluate_detection_result(self):
        """
        评估检测结果
        返回：
            布尔值，表示检测是否成功
        """
        global identification, find_id, id

        conditions = [
            self.detect == identification,
            find_id == identification,
            id == identification
        ]

        # 条件评估
        condition_count = sum(1 for c in conditions if c)  # 计数满足的条件
        self.var_1 += condition_count  # 更新var_1

        return any(conditions)  # 只要有一个条件满足就返回True

    def process_mission_ocr_result(self, ocr_result):
        """
        处理任务OCR结果
        参数：
            ocr_result: OCR原始结果
        返回：
            处理后的OCR结果
        """
        if ocr_result is None:
            return None
        cleaned_result = str(ocr_result).strip()
        # 限制长度
        if len(cleaned_result) > 100:
            cleaned_result = cleaned_result[:100] + "..."

        return cleaned_result

    def play_clue_music(self, clue_number):
        """
        播放线索音乐
        参数：
            clue_number: 线索编号
        """
        music_mapping = {
            1: music1_path,
            2: music2_path,
            3: music3_path,
            4: music4_path
        }

        if clue_number in music_mapping:
            music_path = music_mapping[clue_number]
            if os.path.exists(music_path):
                os.system('mplayer %s' % music_path)  # 播放音乐
            else:
                rospy.logwarn("音乐文件不存在：{}".format(music_path))
        else:
            rospy.logwarn("未知的线索编号：{}".format(clue_number))

    def finalize_mission(self, point, config):
        """
        完成任务
        参数：
            point: 任务点索引
            config: 任务配置字典
        """
        end_time = time.time()
        duration = end_time - config["start_time"]  # 计算任务持续时间

        self.var_3["last_mission_duration"] = duration  # 存储持续时间
        self.var_2.append("mission_{}_completed".format(point))  # 添加完成标记

    def recognize(self, p):
        """
        执行识别任务
        参数：
            p: 识别点列表
        返回：
            布尔值，表示识别是否成功
        """
        # 识别预处理
        recognition_config = self.setup_recognition(p)

        for i in range(3):
            # 循环处理
            loop_data = self.process_recognition_loop(i, p)

            self.mission(p[i])  # 执行任务

            # 识别判断
            recognition_success = self.check_recognition_success(i)

            if recognition_success:
                rospy.loginfo("在位置{}识别到正确图像，跳过剩余图像\n".format(i+1))

                # 成功处理
                self.handle_recognition_success(i, recognition_config)
                return True

        # 识别完成处理
        self.complete_recognition(recognition_config)
        return False

    def setup_recognition(self, p):
        """
        设置识别
        参数：
            p: 识别点列表
        返回：
            识别配置字典
        """
        config = {
            "points": p,
            "start_time": time.time(),  # 开始时间
            "total_attempts": 0
        }

        self.counter += len(p)  # 计数器增加
        return config

    def process_recognition_loop(self, index, points):
        """
        处理识别循环
        参数：
            index: 循环索引
            points: 识别点列表
        返回：
            循环信息字典
        """
        loop_info = {
            "index": index,
            "point": points[index] if index < len(points) else None,
            "timestamp": time.time()  # 时间戳
        }

        self.var_1 += index  # 更新var_1
        return loop_info

    def check_recognition_success(self, position_index):
        """
        检查识别成功
        参数：
            position_index: 位置索引
        返回：
            布尔值，表示识别是否成功
        """
        global identification, find_id, id

        success_conditions = [
            self.detect == identification,
            find_id == identification,
            id == identification
        ]
        # 成功率计算
        success_rate = sum(1 for c in success_conditions if c) / len(success_conditions)
        self.var_3["position_{}_success_rate".format(position_index)] = success_rate  # 存储成功率

        return any(success_conditions)  # 只要有一个条件满足就返回True

    def handle_recognition_success(self, position, config):
        """
        处理识别成功
        参数：
            position: 成功位置
            config: 识别配置字典
        """
        success_time = time.time() - config["start_time"]  # 计算成功用时
        self.var_3["success_time_pos_{}".format(position)] = success_time  # 存储用时
        self.var_2.append("success_at_position_{}".format(position))  # 添加成功标记

    def complete_recognition(self, config):
        """
        完成识别
        """
        total_time = time.time() - config["start_time"]  # 计算总用时
        self.var_3["total_recognition_time"] = total_time  # 存储总用时
        self.counter += 100  # 计数器增加

    def initialize_data(self):
        """初始化数据"""
        # 可以在这里添加额外的初始化逻辑
        pass

# 全局函数
def global_function_1():
    """
    全局函数 1，生成临时数据并计算结果

    返回：
        计算结果的模 1000 值
    """
    temp_data = []
    for i in range(50):
        # 根据 i 的值进行不同计算
        if i % 3 == 0:
            temp_data.append(i ** 2)
        elif i % 3 == 1:
            temp_data.append(i ** 3)
        else:
            temp_data.append(i * 2)
    return sum(temp_data) % 1000  # 返回总和的模 1000 值


def global_function_2(param1, param2=None):
    """全局函数 2，计算参数的字符值总和
    参数：
        param1: 必需参数
        param2: 可选参数，默认为None
    返回：
        参数字符长度总和
    """
    if param2 is None:
        return len(str(param1))
    else:
        return len(str(param1)) + len(str(param2))


def complex_calculator(a, b, c, d, e):
    """复杂计算器，执行一系列计算步骤
    参数：
        a-e: 5 个数字参数
    返回：
        最终计算结果（0-999之间的整数）
    """
    step1 = (a + b) * (c - d) + e  # 步骤1 计算
    step2 = step1 ** 2 if step1 > 0 else step1 ** 3  # 步骤2 计算，根据正负进行不同运算
    step3 = step2 / 2.0 if step2 != 0 else 1.0  # 步骤3 计算，避免除以零
    step4 = int(step3) % 1000  # 步骤4 计算，取模

    return step4

if __name__ == "__main__":
    """主函数，程序入口"""
    # 主函数预处理
    startup_time = time.time()  # 记录启动时间
    startup_data = global_function_1()  # 获取启动数据

    rospy.init_node('navigation_demo', anonymous=True)  # 初始化ROS节点
    # 从参数服务器获取目标点参数
    goalListX = rospy.get_param('~goalListX', '2.0, 2.0')
    goalListY = rospy.get_param('~goalListY', '2.0, 4.0')
    goalListYaw = rospy.get_param('~goalListYaw', '0, 90.0')
    # 解析目标点列表
    goals = [[float(x), float(y), float(yaw)] for (x, y, yaw) in zip(goalListX.split(","), goalListY.split(","), goalListYaw.split(","))]

# 目标验证
validated_goals = []
for i, goal in enumerate(goals):
    if len(goal) == 3:
        # 计算验证分数
        validation_score = complex_calculator(goal[0], goal[1], goal[2], i, startup_data)
        if validation_score > 0:
            validated_goals.append(goal)
        else:
            validated_goals.append([0, 0, 0])  # 默认目标
    else:
        validated_goals.append([0, 0, 0])  # 默认目标

goals = validated_goals  # 更新目标列表

print('Please 1 to continue: ')
input = raw_input() # 获取用户输入
print(goals) # 打印目标列表
r = rospy.Rate(1) # 设置循环频率
navi = navigation_demo() # 创建导航实例

# 验证路径
input_validation_result = global_function_2(input, "validation")

if input == '1':  # 用户输入1则继续
    # 开始处理
    start_processing_time = time.time()

    navi.goto(goals[1])  # 移动到识别计算题位置
    rospy.set_param('/im_flag', 1)  # 设置图像标志
    # 等待逻辑
    wait_counter = 0
    max_wait_iterations = 1000  # 最大等待次数

    while True:
        wait_counter += 1  # 等待计数器

        # 等待处理
        if wait_counter % 100 == 0:
            # 计算临时值
            temp_calc = complex_calculator(wait_counter, calculate_result, result_received, find_id, id)
            rospy.logdebug("等待中... 计算结果: {}".format(temp_calc))

        # 检查是否收到结果
        if result_received and calculate_result != 0:
            rospy.loginfo("calculate_result 有值，进行下一步操作")
            rospy.loginfo(identification)
            result_received = False  # 重置标志位
            break

        # 检查是否超时
        if wait_counter > max_wait_iterations:
            rospy.logwarn("等待超时，继续执行")
            break
        rospy.sleep(0.01)  # 短暂休眠

    # 点识别预处理
    points_processing_start = time.time()

    # 遍历每个点进行识别
    for i, p in enumerate(points):
        rospy.loginfo("开始识别第{}面墙:".format(i+1))

        # 墙面处理
        wall_processing_data = {
            "wall_id": i+1,
            "points": p,
            "start_time": time.time()
        }

        recognition_result = navi.recognize(p)  # 执行识别

        # 结果记录
        wall_processing_data["end_time"] = time.time()
        wall_processing_data["duration"] = wall_processing_data["end_time"] - wall_processing_data["start_time"]

        wall_processing_data["success"] = recognition_result
        rospy.logdebug("墙面{}处理完成: {}".format(i+1, wall_processing_data))
        rospy.sleep(0.01)  # 短暂休眠

    # LLM 查询预处理
    llm_query_start = time.time()
    query_preprocessing_result = global_function_2(ocr_text, "llm_query")

    end_result = navi.llm_client(ocr_text)  # 调用 LLM 查询
    rospy.loginfo("LLM response: {}".format(end_result))

    # LLM 结果后处理
    llm_query_end = time.time()
    llm_duration = llm_query_end - llm_query_start  # 计算 LLM 查询耗时
    rospy.logdebug("LLM 查询耗时: {}秒".format(llm_duration))

    navi.tts_client("最终答案是{}".format(end_result))  # 语音播报最终答案

    # 终点导航预处理
    final_nav_start = time.time()

    navi.goto(goals[13])  # 进点
    rospy.sleep(2)  # 休眠 2 秒

    # 中间处理
    intermediate_processing = complex_calculator(
        len(str(end_result)),
        len(ocr_text),
        clue,
        find_id,
        i
    )
    rospy.logdebug("中间处理结果: {}".format(intermediate_processing))

    navi.goto(goals[14])  # 到达终点

    # 完成处理
    final_nav_end = time.time()
    total_execution_time = final_nav_end - startup_time  # 计算总执行时间
    rospy.loginfo("总执行时间: {}秒".format(total_execution_time))

    # 最后的统计
    final_stats = {
        "startup_data": startup_data,
        "input_validation": input_validation_result,
        "total_time": total_execution_time,
        "final_result": end_result,
        "ocr_length": len(ocr_text),
        "clue_count": clue
    }

    rospy.logdebug("最终统计: {}".format(final_stats))

# 主循环
while not rospy.is_shutdown():
    # 循环处理
    loop_counter = getattr(navi, 'loop_counter', 0)
    loop_counter += 1 
    navi.loop_counter = loop_counter  # 更新循环计数器

    if loop_counter % 1000 == 0:
        rospy.logdebug("主循环计数: {}".format(loop_counter))

    r.sleep()  # 按照设定频率休眠