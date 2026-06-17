#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import rospy
import math
import actionlib
import serial
import time
from std_msgs.msg import String
from actionlib_msgs.msg import *
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseWithCovarianceStamped
from tf_conversions import transformations
from math import pi
from std_msgs.msg import String
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
from ar_track_alvar_msgs.msg import AlvarMarkers
from geometry_msgs.msg import Point
import dynamic_reconfigure.client
import threading 
import rosnode
import subprocess
from geometry_msgs.msg import Twist
id = 0
find_id = 0
music_path0 = ["/home/abot/310117/src/robot_slam/mp3/1.mp3", "/home/abot/310117/src/robot_slam/mp3/2.mp3",
               "/home/abot/310117/src/robot_slam/mp3/3.mp3", "/home/abot/310117/src/robot_slam/mp3/4.mp3",
               "/home/abot/310117/src/robot_slam/mp3/5.mp3", "/home/abot/310117/src/robot_slam/mp3/6.mp3",
               "/home/abot/310117/src/robot_slam/mp3/7.mp3", "/home/abot/310117/src/robot_slam/mp3/8.mp3"]
music_path1 = ["/home/abot/310117/src/robot_slam/mp3/01.mp3", "/home/abot/310117/src/robot_slam/mp3/02.mp3",
               "/home/abot/310117/src/robot_slam/mp3/03.mp3", "/home/abot/310117/src/robot_slam/mp3/04.mp3",
               "/home/abot/310117/src/robot_slam/mp3/05.mp3", "/home/abot/310117/src/robot_slam/mp3/06.mp3",
               "/home/abot/310117/src/robot_slam/mp3/07.mp3", "/home/abot/310117/src/robot_slam/mp3/08.mp3",
               "/home/abot/310117/src/robot_slam/mp3/09.mp3"]
# 初始化节点
#rospy.init_node('d_pose_subscriber', anonymous=True)
# 定义全局变量
D_pose = None
D_pose = 520
def callback(data):
    global D_pose
    D_pose = data.data  # 假设消息类型为String
    rospy.loginfo("Received data: %s", D_pose)

def listener():
    # 订阅名为D_model的话题
    rospy.Subscriber('D_model', String, callback)
    rospy.spin()  # 保持节点运行

class navigation_demo:
    def __init__(self):
        self.set_pose_pub = rospy.Publisher('/initialpose', PoseWithCovarianceStamped, queue_size=5)
        self.ar_sub = rospy.Subscriber('/ar_pose_marker', AlvarMarkers, self.ar_cb)
        self.ar_sub = rospy.Subscriber('/object_position', Point, self.find_cb)
        
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        self.move_base.wait_for_server(rospy.Duration(60))

        self.global_inflation_client = dynamic_reconfigure.client.Client("/move_base/global_costmap/inflation_layer",
                                                                         timeout=30)
        self.local_inflation_client = dynamic_reconfigure.client.Client("/move_base/local_costmap/inflation_layer",
                                                                        timeout=30)

    def update_inflation_radius(self, global_radius, local_radius):
        # 更新全局成本地图的膨胀系数
        global_config = {"inflation_radius": global_radius}
        global_costmap_client.update_configuration(global_config)
        # 更新局部成本地图的膨胀系数
        local_config = {"inflation_radius": local_radius}
        local_costmap_client.update_configuration(local_config)

        rospy.loginfo("Updated global inflation radius to: %f", global_radius)
        rospy.loginfo("Updated local inflation radius to: %f", local_radius)

    def ar_cb(self,data):
        global id 
        for marker in data.markers:
            id = marker.id
        print(id)

    def find_cb(self, data):
        global find_id
        point_msg = data
        find_id = int((point_msg.z - 1) // 100 + 1)
#        print(find_id)

    def set_pose(self, p):
        if self.move_base is None:
            return False

        x, y, th = p

        pose = PoseWithCovarianceStamped()
        pose.header.stamp = rospy.Time.now()
        pose.header.frame_id = 'map'
        pose.pose.pose.position.x = x
        pose.pose.pose.position.y = y
        q = transformations.quaternion_from_euler(0.0, 0.0, th/180.0*pi)
        pose.pose.pose.orientation.x = q[0]
        pose.pose.pose.orientation.y = q[1]
        pose.pose.pose.orientation.z = q[2]
        pose.pose.pose.orientation.w = q[3]

        self.set_pose_pub.publish(pose)
        return True

    def _done_cb(self, status, result):
        rospy.loginfo("navigation done! status:%d result:%s"%(status, result))

    def _active_cb(self):
        rospy.loginfo("[Navi] navigation has be actived")

    def _feedback_cb(self, feedback):
        msg = feedback
        #rospy.loginfo("[Navi] navigation feedback\r\n%s"%feedback)

    def goto(self, p):
        rospy.loginfo("[Navi] goto %s"%p)
        goal = MoveBaseGoal()

        goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = p[0]
        goal.target_pose.pose.position.y = p[1]
        q = transformations.quaternion_from_euler(0.0, 0.0, p[2]/180.0*pi)
        goal.target_pose.pose.orientation.x = q[0]
        goal.target_pose.pose.orientation.y = q[1]
        goal.target_pose.pose.orientation.z = q[2]
        goal.target_pose.pose.orientation.w = q[3]

        self.move_base.send_goal(goal, self._done_cb, self._active_cb, self._feedback_cb)
        result = self.move_base.wait_for_result(rospy.Duration(60))
        if not result:
            self.move_base.cancel_goal()
            rospy.loginfo("Timed out achieving goal")
        else:
            state = self.move_base.get_state()
            if state == GoalStatus.SUCCEEDED:
                rospy.loginfo("reach goal %s succeeded!"%p)
        return True

    def cancel(self):
        self.move_base.cancel_all_goals()
        return True
a=[1,4,7,10,13]#四个识别点
b=[2,3,5,6,8,9,11,12]#所有的任务点
c=[1,2,3,4,5,6,7,8]#识别的八个数
d=['1','2','3','4','5','6','7','8']#大模型返回的八个字符串类
if __name__ == "__main__":
    rospy.init_node('navigation_demo',anonymous=True)
    global_costmap_client = dynamic_reconfigure.client.Client("/move_base/global_costmap/inflation_layer", timeout=30)
    local_costmap_client = dynamic_reconfigure.client.Client("/move_base/local_costmap/inflation_layer", timeout=30)
    goalListX = rospy.get_param('~goalListX', '2.0, 2.0,2.0')
    goalListY = rospy.get_param('~goalListY', '2.0, 4.0,2.0')
    goalListYaw = rospy.get_param('~goalListYaw', '0, 90.0,2.0')
    listener_thread = threading.Thread(target=listener)
    listener_thread.daemon = True
    listener_thread.start()	

    goals = [[float(x), float(y), float(yaw)] for (x, y, yaw) in zip(goalListX.split(","),goalListY.split(","),goalListYaw.split(","))]
    print ('Please 1 to continue: ')
    input = raw_input()
    r = rospy.Rate(1)
    r.sleep()
    navi = navigation_demo()
    navi.goto(goals[0])#0点
    navi.goto(goals[1])#1点
    rospy.sleep(5)
    for i in range(0,5):
        rospy.sleep(5)
        if id in c or find_id in c:  # 在列表C中遍历
            t = id if id in c else find_id 
            os.system('mplayer %s' % music_path0[t-1])
            navi.goto(goals[b[t-1]])  # 2点
            os.system('mplayer %s' % music_path1[t-1])
            if i == 4:
                navi.goto(goals[a[i-1]])  # 终点前的一个带点
                navi.update_inflation_radius(0, 0)#动态调参，膨胀系数归0
                navi.goto(goals[a[i]]) #终点
                os.system('mplayer %s' % music_path1[8])#播报终点
            else:
                navi.goto(goals[a[i+1]])
        else:
            rospy.set_param('/top_view_shot_node/im_flag', 1)
            print(D_pose)
            for f,n in enumerate(d):
                if D_pose ==n:
                    os.system('mplayer %s' % music_path0[f])
                    navi.goto(goals[b[f]])  
                    os.system('mplayer %s' % music_path1[f])
                    if i == 4:
                             navi.goto(goals[a[i]])  # 终点前的一个点,也是八点
                             navi.update_inflation_radius(0, 0)  # 动态调参，膨胀系数归0
                             navi.goto(goals[a[i]])  # 终点
                             os.system('mplayer %s' % music_path1[8])  # 播报终点
                    else:
                            navi.goto(goals[a[i+1]])
    while not rospy.is_shutdown():
        r.sleep()

