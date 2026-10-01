"""controller_bbr controller."""

# Code for BBR Controller
# Author: Christopher Mitchell 
# Date: 08/11/2023
# Language: Python 
# version 1.15

# Code for the Required Imports
from controller import Robot
from datetime import datetime
import math
import numpy as np
import time

class Controller:
    def __init__(self, robot):
        ###### Lines 20 - 60 Edited from Lab 1 code ######
        # Robot Parameters
        self.robot = robot
        self.time_step = 32 # ms
        self.max_speed = 1 # m/s

        # Enable motors
        self.left_motor = self.robot.getDevice('left wheel motor')
        self.right_motor = self.robot.getDevice('right wheel motor')
        
        # Set Motor Positions
        self.left_motor.setPosition(float('inf'))
        self.right_motor.setPosition(float('inf'))
        
        # Set Velocities
        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)
        self.velocity_left = 0
        self.velocity_right = 0

        # Initialise & Enable Proximity and Light Sensors
        self.proximity_sensors = []
        self.light_sensors = []

        for i in range(8):
            self.proximity_sensors.append(self.robot.getDevice('ps' + str(i)))
            if (i in [4,5,6,7]):
                self.light_sensors.append(self.robot.getDevice('ls' + str(i)))
                self.light_sensors[i-4].enable(self.time_step)

            self.proximity_sensors[i].enable(self.time_step)

        # Initialise & Enable Ground Sensors
        self.left_ir = self.robot.getDevice('gs0')
        self.left_ir.enable(self.time_step)
        self.center_ir = self.robot.getDevice('gs1')
        self.center_ir.enable(self.time_step)
        self.right_ir = self.robot.getDevice('gs2')
        self.right_ir.enable(self.time_step)

        # Data
        self.inputs = []
        self.inputsPrevious = []
        ######

        ###### Coded by Christopher & Chris
        # Object count
        self.object_count = 0

        # Flags
        self.flag_turn = 0
        self.beacon_flag = 0
        self.object_detected = 0
        
        # Flags for action if back at line after avoiding obstacle
        self.back_at_line = 1
        self.object_was_detected = 1

        # Flag for route A or B
        self.routeA_turn = 0
        self.routeB_turn = 0
        ######

    ###### Lines 84 - 202 Coded By Chris & Christopher 
    # Main movement code
    def movement(self):
        if (len(self.inputs)>1):
            
            # Ground sensors
            gs_left = self.inputs[0]
            gs_center = self.inputs[1]
            gs_right = self.inputs[2]

            # Proximity sensors
            prox_sens = self.inputs[3:-4]

            # Detect object
            if (np.max(prox_sens) > 200):
            
                # Object detected
                print("Obstale Detected")
                self.back_at_line = 0
                self.object_detected = 1
                self.object_was_detected = 1

            else:
                self.object_detected = 0
            

            # If at end of line then turn
            if (self.flag_turn):
                print("Arrived at Fork in the Path")
                
                # if beacon on the turn left
                if (self.beacon_flag):                  
                    self.velocity_left = -0.15
                    self.velocity_right = 0.15

                # if beacon off turn right
                else:                    
                    self.velocity_left = 0.15
                    self.velocity_right = -0.15

                if (np.sum(self.inputs[0:3]) < 1000):
                    if (self.object_count in [2]):
                        self.beacon_flag = not self.beacon_flag
                        self.object_count = 0

                    self.flag_turn = 0
            
            else:
                # Object detection, move right
                if (self.object_detected):
                    if (self.routeA_turn):
                        self.velocity_left = 1
                        self.velocity_right = 0.8
                    else:
                        self.velocity_left = 0.8
                        self.velocity_right = 1

                # Back at line
                elif (self.back_at_line == 0):
                    # Check if we found a line and previously an object was detected
                    if (np.sum(self.inputs[0:3]) < 1000 and self.object_was_detected):
                        
                        # reset values
                        self.back_at_line = 1
                        self.object_was_detected = 0

                        # How many objects are cleared
                        self.object_count += 1

                        # Flip again if cleared 2 obstacles (is a bug thats why we need here)
                        if (self.object_count in [2]):
                            self.beacon_flag = not self.beacon_flag
                    
                        self.beacon_flag = not self.beacon_flag
                        
                    else:
                        # If taking route A then take a right path around object
                        if (self.routeA_turn):
                            print("Beacon is on - Taking Route A")
                            self.velocity_left = 0.7
                            self.velocity_right = 1

                        # elif taking route B then take a left path around object
                        elif (self.routeB_turn):
                            print("Beacon is off - Taking Route B")
                            self.velocity_left = 1
                            self.velocity_right = 0.7

                else:
                    # Check end of line
                    if (np.sum(self.inputs[0:3]) > 1500):
                        print("End of line")
                        self.flag_turn = 1

                    else:
                        # Line following
                        print("Following the Line")
                        # if left turn right
                        if (gs_left > gs_center and gs_left > gs_right):
                            self.velocity_left = 1
                            self.velocity_right = 0.5
                        # if center keep moving
                        elif (gs_center > gs_left and gs_center > gs_right):
                            self.velocity_left = 1
                            self.velocity_right = 1
                        # if right turn left
                        elif (gs_right > gs_center and gs_right > gs_left):
                            self.velocity_left = 0.5
                            self.velocity_right = 1

        # if beacon on, turn flag on and route A
        if (0 in self.inputs[-4:]):            
            self.beacon_flag = 1
            self.routeA_turn = 1

        # else turn route B on
        else:            
            self.routeB_turn = 1

        # Setting Motor Velocities
        self.left_motor.setVelocity(self.velocity_left)
        self.right_motor.setVelocity(self.velocity_right)
        ######

    ###### Lines 206 - 222 Edited from Lab 2 code    
    def run_robot(self):
        while self.robot.step(self.time_step) != -1:
            # Read ground sensors
            self.inputs = []
            self.inputs.append(self.left_ir.getValue())
            self.inputs.append(self.center_ir.getValue())
            self.inputs.append(self.right_ir.getValue())

            # Read distance sensors
            for i in range(8):
                self.inputs.append(self.proximity_sensors[i].getValue())

            # Read light sensors
            for i in range(4):
                self.inputs.append(self.light_sensors[i].getValue())
            
            self.movement()
            ######

if __name__ == "__main__":
    my_robot = Robot()
    controller = Controller(my_robot)
    controller.run_robot()
