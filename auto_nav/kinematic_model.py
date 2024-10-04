import numpy as np

class robot_model():

    def __init__(self, wheel_radius, l_r):
        self.r = wheel_radius
        self.l_r = l_r  #  Distance between any wheel and center of the robot along the linear axis

    def kinematic_model(self, state, input, dt):  #  Four wheeled differential robot with right and left wheels with same input command

        ''' Initialize Inputs '''
        x, y, theta = state # x, y, theta -- pos of robot
        v1, v2 = input  #  vi -- angular velocity of wheel i

        ''' Compute pos '''
        x += (v1 + v2) * self.r/2 * np.cos(theta) * dt
        y += (v1 + v2) * self.r/2 * np.sin(theta) * dt
        theta += (v1 - v2) * (self.r/(2 * self.l_r)) * dt

        ''' Output '''
        return (x, y, theta)
