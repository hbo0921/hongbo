#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AR码识别测试脚本
用于单独验证AR码识别功能
"""
import rospy
from ar_track_alvar_msgs.msg import AlvarMarkers

class ARRecognitionTester:
    def __init__(self):
        rospy.init_node('ar_recognition_tester', anonymous=True)
        rospy.loginfo("AR码识别测试节点启动...")
        
        # 订阅AR标记话题
        self.ar_sub = rospy.Subscriber('/ar_pose_marker', AlvarMarkers, self.ar_cb)
        
        # 统计信息
        self.total_messages = 0
        self.detected_markers = {}
        self.last_marker_id = None
        
        rospy.loginfo("等待AR识别数据...")
        rospy.loginfo("请将AR标记放在摄像头前...")
    
    def ar_cb(self, data):
        """AR标记回调函数"""
        self.total_messages += 1
        
        # 检查是否有标记
        if len(data.markers) == 0:
            if self.total_messages % 10 == 0:  # 每10条消息打印一次
                rospy.loginfo("未检测到AR标记...")
            return
        
        # 处理检测到的标记
        for marker in data.markers:
            marker_id = marker.id
            position = marker.pose.pose.position
            orientation = marker.pose.pose.orientation
            
            # 记录统计信息
            if marker_id not in self.detected_markers:
                self.detected_markers[marker_id] = {
                    'count': 0,
                    'first_detected': rospy.Time.now()
                }
            
            self.detected_markers[marker_id]['count'] += 1
            self.last_marker_id = marker_id
            
            # 打印详细信息
            rospy.loginfo("=" * 60)
            rospy.loginfo("检测到AR标记!")
            rospy.loginfo("标记ID: %d", marker_id)
            rospy.loginfo("位置: x=%.3f, y=%.3f, z=%.3f", 
                         position.x, position.y, position.z)
            rospy.loginfo("姿态: x=%.3f, y=%.3f, z=%.3f, w=%.3f",
                         orientation.x, orientation.y, 
                         orientation.z, orientation.w)
            rospy.loginfo("检测次数: %d", self.detected_markers[marker_id]['count'])
            rospy.loginfo("置信度: %.2f", marker.confidence)
            rospy.loginfo("坐标系: %s", data.header.frame_id)
            rospy.loginfo("=" * 60)
    
    def print_statistics(self):
        """打印统计信息"""
        rospy.loginfo("\n" + "=" * 60)
        rospy.loginfo("AR识别统计信息:")
        rospy.loginfo("总接收消息数: %d", self.total_messages)
        rospy.loginfo("检测到的标记数量: %d", len(self.detected_markers))
        
        if len(self.detected_markers) > 0:
            rospy.loginfo("\n检测到的标记详情:")
            for marker_id, info in self.detected_markers.items():
                rospy.loginfo("  标记ID %d: 检测到 %d 次", 
                             marker_id, info['count'])
        
        if self.last_marker_id is not None:
            rospy.loginfo("\n最后检测到的标记ID: %d", self.last_marker_id)
        
        rospy.loginfo("=" * 60 + "\n")
    
    def run(self):
        """运行测试"""
        rate = rospy.Rate(1)  # 1Hz
        
        while not rospy.is_shutdown():
            # 每秒打印一次统计信息
            if self.total_messages > 0 and self.total_messages % 10 == 0:
                self.print_statistics()
            
            rate.sleep()
        
        # 退出时打印最终统计
        self.print_statistics()

if __name__ == '__main__':
    try:
        tester = ARRecognitionTester()
        tester.run()
    except rospy.ROSInterruptException:
        pass













