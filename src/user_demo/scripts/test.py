import rospy
from sensor_msgs.msg import Image 
from cv_bridge import CvBridge 
import cv2 

class take_pho: 
	def __init__(self): 

		rospy.init_node('take_pho', anonymous=True) 
		self.bridge = CvBridge() 
		self.image_subscriber = rospy.Subscriber('/usb_cam/image_raw', Image, self.image_callback) 

	def image_callback(self, msg):
		cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8') 
		cv2.imshow("Camera Image", cv_image) 
		cv2.imwrite("test.jpg",cv_image)
		cv2.waitKey(1) 

if __name__ == '__main__': 
	try: 
		camera_subscriber = take_pho() 
		rospy.spin() 
	except rospy.ROSInterruptException: 
		cv2.destroyAllWindows()
