#!/usr/bin/env python
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

id = 0
find_id = 0

music_path1 = "/home/abot/zbbxq/src/robot_slam/mp3/1.mp3"
music_path2 = "/home/abot/zbbxq/src/robot_slam/mp3/2.mp3"
music_path3 = "/home/abot/zbbxq/src/robot_slam/mp3/3.mp3"
music_path4 = "/home/abot/zbbxq/src/robot_slam/mp3/4.mp3"
music_path5 = "/home/abot/zbbxq/src/robot_slam/mp3/5.mp3"
music_path6 = "/home/abot/zbbxq/src/robot_slam/mp3/6.mp3"
music_path7 = "/home/abot/zbbxq/src/robot_slam/mp3/7.mp3"
music_path8 = "/home/abot/zbbxq/src/robot_slam/mp3/8.mp3"

music_path01 = "/home/abot/zbbxq/src/robot_slam/mp3/01.mp3"
music_path02 = "/home/abot/zbbxq/src/robot_slam/mp3/02.mp3"
music_path03 = "/home/abot/zbbxq/src/robot_slam/mp3/03.mp3"
music_path04 = "/home/abot/zbbxq/src/robot_slam/mp3/04.mp3"
music_path05 = "/home/abot/zbbxq/src/robot_slam/mp3/05.mp3"
music_path06 = "/home/abot/zbbxq/src/robot_slam/mp3/06.mp3"
music_path07 = "/home/abot/zbbxq/src/robot_slam/mp3/07.mp3"
music_path08 = "/home/abot/zbbxq/src/robot_slam/mp3/08.mp3"

music_path9  = "/home/abot/zbbxq/src/robot_slam/mp3/09.mp3"

class navigation_demo:
    def __init__(self):
        self.set_pose_pub = rospy.Publisher('/initialpose', PoseWithCovarianceStamped, queue_size=5)
        self.ar_sub = rospy.Subscriber('/ar_pose_marker', AlvarMarkers, self.ar_cb)
        self.ar_sub = rospy.Subscriber('/object_position', Point, self.find_cb)
        
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        self.move_base.wait_for_server(rospy.Duration(60))

    def ar_cb(self,data):
        global id 
        for marker in data.markers:
            id = marker.id
        print(id)

    def find_cb(self, data):
        global find_id
        point_msg = data
        find_id = int((point_msg.z - 1) // 10 + 1)
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
    
if __name__ == "__main__":
    
    rospy.init_node('navigation_demo',anonymous=True)
#    rospy.init_node('dynamic_reconfigure_client')
    client1 = dynamic_reconfigure.client.Client("/move_base/global_costmap/inflation_layer/")
    client2 = dynamic_reconfigure.client.Client("/move_base/local_costmap/inflation_layer/")
    #client3 = dynamic_reconfigure.client.Client("/move_base/recovery_behavior_enabled/")
    #client3.update_configuration({"recovery_behavior_enabled":flase})    
    #client4 = dynamic_reconfigure.client.Client("/move_base/global_costmap/obstacle_layer/obstacle_range/")

    goalListX = rospy.get_param('~goalListX', '2.0, 2.0,2.0')
    goalListY = rospy.get_param('~goalListY', '2.0, 4.0,2.0')
    goalListYaw = rospy.get_param('~goalListYaw', '0, 90.0,2.0')

    goals = [[float(x), float(y), float(yaw)] for (x, y, yaw) in zip(goalListX.split(","),goalListY.split(","),goalListYaw.split(","))]
    print ('Please 1 to continue: ')
    input = raw_input()
    r = rospy.Rate(1)
    r.sleep()
    navi = navigation_demo()
    navi.goto(goals[0])
    navi.goto(goals[1])
    rospy.sleep(4)

    if id == 1 or find_id ==1:
        os.system('mplayer %s' % music_path1) 
        navi.goto(goals[2])  
        os.system('mplayer %s' % music_path01)
#       rospy.sleep(2)
#       navi.goto(goals[14])
        navi.goto(goals[4])
    if id == 2 or find_id ==2:
        os.system('mplayer %s' % music_path2)
	navi.goto(goals[3])  
        os.system('mplayer %s' % music_path02)
#       rospy.sleep(2)
#       navi.goto(goals[15])
        navi.goto(goals[4])

    rospy.sleep(4)
    if id == 3 or find_id ==3:
        os.system('mplayer %s' % music_path3) 
        navi.goto(goals[5])  
        os.system('mplayer %s' % music_path03)
#       rospy.sleep(2)
#       navi.goto(goals[20])
#       navi.goto(goals[21])
        navi.goto(goals[7])
    if id == 4 or find_id ==4:
	os.system('mplayer %s' % music_path4)
	navi.goto(goals[6])  
        os.system('mplayer %s' % music_path04)
#       rospy.sleep(2)
#       navi.goto(goals[22])   
#       navi.goto(goals[17])   
        navi.goto(goals[8])

    rospy.sleep(4)
    if id == 5 or find_id ==5:
        os.system('mplayer %s' % music_path5) 
        navi.goto(goals[9])  
        os.system('mplayer %s' % music_path05)
#       rospy.sleep(2)
#       navi.goto(goals[23])
#       navi.goto(goals[16])
        navi.goto(goals[12])

    if id == 6 or find_id ==6:
	os.system('mplayer %s' % music_path6)
	navi.goto(goals[9])  
        os.system('mplayer %s' % music_path06)
#       rospy.sleep(2)  
#       navi.goto(goals[18])
        navi.goto(goals[12])   
  
    rospy.sleep(4)
    if id == 7 or find_id ==7:
        os.system('mplayer %s' % music_path7) 
        navi.goto(goals[13])  
        os.system('mplayer %s' % music_path07)
#       rospy.sleep(2)
        while not rospy.is_shutdown():
            client1.update_configuration({"inflation_radius":0.0})
            client2.update_configuration({"inflation_radius":0.0})
         #   client4.update_configuration({"obstacle_range":0.0})
            rospy.sleep(1)   
            navi.goto(goals[14])	    
            
	    os.system('mplayer %s' % music_path9)
	    break

    if id == 8 or find_id ==8:
	os.system('mplayer %s' % music_path8)
	navi.goto(goals[13])  
        os.system('mplayer %s' % music_path08)
#        rospy.sleep(2)
        while not rospy.is_shutdown():
            client1.update_configuration({"inflation_radius":0.0})
            client2.update_configuration({"inflation_radius":0.0})
          #  client4.update_configuration({"obstacle_range":0.0})
            rospy.sleep(1)   	
            navi.goto(goals[15])	        
           
	    os.system('mplayer %s' % music_path9)
	    break
        

    while not rospy.is_shutdown():
	r.sleep()
