#!/usr/bin/env python

from math import pi, sqrt, atan2, cos, sin
import numpy as np

import rospy
import tf
from std_msgs.msg import Empty
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist, Pose2D

##class(controller)
class Controller:
    def __init__(self, P=0.0, D=0.0, set_point=0):
        self.Kp = P
        self.Kd = D
        self.set_point = set_point # reference (desired value)
        self.previous_error = 0

    def update(self, current_value):
        # calculate P_term and D_term ??
        error = self.set_point - current_value
        P_term = self.Kp * error
        D_term = self.Kd * (error - self.previous_error)
        self.previous_error = error
        return P_term + D_term

    def setPoint(self, set_point):
        self.set_point = set_point
        self.previous_error = 0
    
    def setPD(self, P=0.0, D=0.0):
        self.Kp = P
        self.Kd = D


##class(Turlebot)
class Turtlebot():
    def __init__(self):
        rospy.init_node("turtlebot_move")
        rospy.loginfo("Press Ctrl + C to terminate")
        self.vel_pub = rospy.Publisher("cmd_vel_mux/input/navi", Twist, queue_size=10)
        self.rate = rospy.Rate(10)

        # reset odometry to zero
        self.reset_pub = rospy.Publisher("mobile_base/commands/reset_odometry", Empty, queue_size=10)
        for i in range(10):
            self.reset_pub.publish(Empty())
            self.rate.sleep()
        
        # subscribe to odometry
        self.pose = Pose2D()
        self.logging_counter = 0
        self.trajectory = list()
        self.odom_sub = rospy.Subscriber("odom", Odometry, self.odom_callback)

        try:
            self.run()
        except rospy.ROSInterruptException:
            rospy.loginfo("Action terminated.")
        finally:
            # save trajectory into csv file
            np.savetxt('trajectory.csv', np.array(self.trajectory), fmt='%f', delimiter=',')


    def run(self):
        # add your code here to adjust your movement based on 2D pose feedback
        # Use the Controller


        vel = Twist()
	th = 0.03

        #1.Straight line
        vel.linear.x = 0.5
        vel.angular.z = 0
	control = Controller(1,0,0)
	control.setPoint(0)
        #while not rospy.is_shutdown():  # uncomment to use while loop
        while abs(self.pose.x-4) > th:
            	pose_x = self.pose.x
            	pose_y = self.pose.y
		vel.angular.z = control.update(self.pose.theta)
		self.vel_pub.publish(vel)
		self.rate.sleep()
	
	#2.rotation
        vel.linear.x = 0
        vel.angular.z = 0.5
	control = Controller(1,0,0)
	control.setPoint(pi/2)
        #while not rospy.is_shutdown():  # uncomment to use while loop
        while abs(self.pose.theta-pi/2) > th:
            	pose_x = self.pose.x
            	pose_y = self.pose.y
		vel.angular.z = control.update(self.pose.theta)
		self.vel_pub.publish(vel)
		self.rate.sleep()

        #3.Straight line
        vel.linear.x = 0.5
        vel.angular.z = 0
	control.setPoint(pi/2)
        #while not rospy.is_shutdown():  # uncomment to use while loop
        while abs(self.pose.y-4) > th:
            	pose_x = self.pose.x
            	pose_y = self.pose.y
		vel.angular.z = control.update(self.pose.theta)
		self.vel_pub.publish(vel)
		self.rate.sleep()

	#4.rotation
        vel.linear.x = 0
        vel.angular.z = 0.5
	control = Controller(1,0,0)
	control.setPoint(pi)
        #while not rospy.is_shutdown():  # uncomment to use while loop
        while abs(self.pose.theta-pi) > th:
            	pose_x = self.pose.x
            	pose_y = self.pose.y
		vel.angular.z = control.update(self.pose.theta)
		self.vel_pub.publish(vel)
		self.rate.sleep()

 	#5.Straight line
        vel.linear.x = 0.5
        vel.angular.z = 0
	control.setPoint(pi)
        #while not rospy.is_shutdown():  # uncomment to use while loop
        while abs(self.pose.x) > th:
            	pose_x = self.pose.x
            	pose_y = self.pose.y
		vel.angular.z = control.update(self.pose.theta)
		self.vel_pub.publish(vel)
		self.rate.sleep()

	#6.rotation
        vel.linear.x = 0
        vel.angular.z = 0.5
	control = Controller(1,0,0)
	control.setPoint(-pi/2)
        #while not rospy.is_shutdown():  # uncomment to use while loop
        while abs(self.pose.theta+pi/2) > th:
            	pose_x = self.pose.x
            	pose_y = self.pose.y
		vel.angular.z = control.update(self.pose.theta)
		self.vel_pub.publish(vel)
		self.rate.sleep()

 	#7.Straight line
        vel.linear.x = 0.5
        vel.angular.z = 0
	control.setPoint(-pi/2)
        #while not rospy.is_shutdown():  # uncomment to use while loop
        while abs(self.pose.y) > th:
            	pose_x = self.pose.x
            	pose_y = self.pose.y
		vel.angular.z = control.update(self.pose.theta)
		self.vel_pub.publish(vel)
		self.rate.sleep()

	


	pass
       



    def odom_callback(self, msg):
        # get pose = (x, y, theta) from odometry topic
        quarternion = [msg.pose.pose.orientation.x,msg.pose.pose.orientation.y,\
                    msg.pose.pose.orientation.z, msg.pose.pose.orientation.w]
        (roll, pitch, yaw) = tf.transformations.euler_from_quaternion(quarternion)
        self.pose.theta = yaw
        self.pose.x = msg.pose.pose.position.x
        self.pose.y = msg.pose.pose.position.y

        # logging once every 100 times (Gazebo runs at 1000Hz; we save it at 10Hz)
        self.logging_counter += 1
        if self.logging_counter == 100:
            self.logging_counter = 0
            self.trajectory.append([self.pose.x, self.pose.y])  # save trajectory
            # display (x, y, theta) on the terminal
            rospy.loginfo("odom: x=" + str(self.pose.x) +\
                ";  y=" + str(self.pose.y) + ";  theta=" + str(yaw))


if __name__ == '__main__':
    whatever = Turtlebot()
