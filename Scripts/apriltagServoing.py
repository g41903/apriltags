#!/usr/bin/env python
"""
A responsible racecar driver.
"""

import rospy
from std_msgs.msg import Bool, Duration
from ackermann_msgs.msg import AckermannDriveStamped
from visual_servoing.msg import CameraObjectsStamped
from nav_msgs.msg import Odometry
import numpy as np
import threading
from apriltags.msg import AprilTagDetections


from rospyext import *

class ApriltagDriverNode(Node):
    side = 1
    lost = True
    look = True
    cone_pose_rel = None

    gain_angle = Param(float, default=-.8)
    
    
    pub = rospy.Publisher('/vesc/ackermann_cmd_mux/input/navigation', AckermannDriveStamped, queue_size=10)
    pub_def = rospy.Publisher('/vesc/ackermann_cmd_mux/input/default', AckermannDriveStamped, queue_size=10)

    @Subscriber('/apriltags/detections', AprilTagDetections, queue_size=1)
    def sub_cone(self, msg):
        #print msg.detections[0].pose
        print msg.detections[0].pose.position.x
        #if x>0.01, it turns right
        x_position=msg.detections[0].pose.position.x
        
        cmd = AckermannDriveStamped()
        cmd.drive.speed = 2.0
        cmd.drive.steering_angle=-(x_position-0.01)*1.5
        self.pub.publish(cmd)
        self.pub_def.publish(cmd)
    """
        if not msg.objects:
            if not self.lost:
                self.side *= -1
                self.lost = True
                rospy.loginfo('Going around cone to ' + ('left' if self.side == -1 else 'right'))
                self.look = False
                t = threading.Timer(5.0, self.look_release)
                t.start()
        else:
            if self.look:
                cone = msg.objects[0]
                self.cone_pose_rel = (cone.center.x, cone.center.z)
                if self.lost: rospy.loginfo("Cone at: " + str(self.cone_pose_rel))
                self.lost = False

    @Subscriber('/apriltags/detections',ApriltagDetection)
    def sub_apriltags(self,msg):
        print msg

    def look_release(self):
        rospy.loginfo('looking again')
        self.look = True

    @Timer(rospy.Duration(.1))
    def timer_callback(self, event):
        cmd = AckermannDriveStamped()
        

        target_x = 0.1 + 0.5 * self.side
        if not self.lost:
            cmd.drive.steering_angle = self.gain_angle*(self.cone_pose_rel[0] - target_x)
            rospy.loginfo('steering angle: %f, t: %f', cmd.drive.steering_angle, target_x)
        else:
            cmd.drive.steering_angle = -.03+.14*self.side
            rospy.loginfo('steering angle: %f, lost', cmd.drive.steering_angle)
        cmd.drive.speed = .3
        if self.cone_pose_rel == None:
            cmd.drive.speed = 0   

        #0.1
        cmd.drive.speed = .3
        cmd.drive.steering_angle=.3
        print steering_angle
        #self.pub.publish(cmd)
        self.pub_def.publish(cmd)
"""

if __name__ == '__main__':
    rospy.init_node("apriltagdriver")
    node = ApriltagDriverNode()
    rospy.on_shutdown(lambda: node.on_shutdown())
    rospy.spin()

