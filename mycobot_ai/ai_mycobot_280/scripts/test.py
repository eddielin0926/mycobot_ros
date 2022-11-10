# -*- coding: utf-8 -*-
from pymycobot.mycobot import MyCobot
from pymycobot.genre import Angle
from pymycobot import PI_PORT, PI_BAUD  # 当使用树莓派版本的mycobot时，可以引用这两个变量进行MyCobot初始化
import time

mc = MyCobot("/dev/ttyACM0", 115200)
# mc = MyCobot("/dev/ttyUSB0", 115200)
# mc = MyCobot("/dev/ttyAMA0", 1000000)

# mc.send_angles([0,0,0,0,0,0], 25)
# print(mc.get_angles())
# mc.send_angles([-7.11, -6.94, -55.01, -24.16, 0.0, -15], 20)
# time.sleep(4)
# print(mc.get_angles())

# mc.send_coords([120.8, -134.4, 258.0, -172.72, -5.31, -109.09], 30, 1) # red bucket
# time.sleep(4)

# mc.send_coords([18.8, -7.91, -54.49, -23.02, -0.79, -14.76], 30, 1) # green bucket
# time.sleep(4)

# mc.send_coords([124.7, 145.3, 250.4, -173.5, -2.23, -11.7], 30, 1) # above the blue bucket
# time.sleep(4)

# mc.send_coords([14.6, 175.9, 250.4, -177.42, -0.08, 25.93], 30, 1)  # abobe the gray bucket
# time.sleep(4)

# mc.send_angles([-7.11, -6.94, -55.01, -24.16, 0, -15], 20, 0)
# mc.send_angles([1.4, 0, -53.61, -33.39, -3.51, -20.3],20)
# time.sleep(3)

# mc.send_coords([145.3, -11.2, 126.6, 179.87, -3.78, -62.75], 30, 1)
# time.sleep(6)


# mc.release_all_servos()
# mc.release_servo(3)
# mc.set_servo_calibration(3)
# time.sleep(1)
# while True:
#   print("angles:%s"% mc.get_angles())
#   print("coords:%s"% mc.get_coords())
#   print("\n")
move_coords = [
            [136.8, -133.4, 260.2, -171.72, -3.88, -107.09],  # above the red bucket
            [221.8, -116.4, 271.2, -147.53, -6.21, -99.91], # green
            [117.7, 164.3, 259.4, -168.25, -2.25, -6.92], # blue
            [11.8, 162.5, 260.3, -167.54, -1.78, 29.4], # gray
        ]

move_angles = [
        [-7.11, -6.94, -55.01, -24.16, 0, -15],  # init the point
        [-12.56, -45, -0.49, -7.02, -4.79, -5.76],  # point to grab 
    ]

mc.send_coords(move_coords[1], 20, 1)
# mc.send_angles(move_angles[1],20)
time.sleep(2)
print(mc.get_angles())
print(mc.get_coords())