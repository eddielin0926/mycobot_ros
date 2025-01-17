#!/usr/bin/env python

from __future__ import print_function

import rospy

import sys
import copy
import moveit_commander

from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import JointState
from moveit_msgs.msg import RobotState

from mycobot_communication.srv import MoverService, MoverServiceResponse, MoveToPoseServiceResponse

joint_names = ['joint2_to_joint1', 'joint3_to_joint2', 'joint4_to_joint3', 'joint5_to_joint4', 'joint6_to_joint5', 'joint6output_to_joint6']

# Between Melodic and Noetic, the return type of plan() changed. moveit_commander has no __version__ variable, so checking the python version as a proxy
if sys.version_info >= (3, 0):
    def planCompat(plan):
        return plan[1]
else:
    def planCompat(plan):
        return plan
    
        
"""
    Given the start angles of the robot, plan a trajectory that ends at the destination pose.
"""
def plan_trajectory(move_group, destination_pose, start_joint_angles): 
    current_joint_state = JointState()
    current_joint_state.name = joint_names
    current_joint_state.position = start_joint_angles

    moveit_robot_state = RobotState()
    moveit_robot_state.joint_state = current_joint_state
    move_group.set_start_state(moveit_robot_state)

    end_effector_link = move_group.get_end_effector_link()

    move_group.set_pose_target(destination_pose, end_effector_link)
    plan = move_group.plan()

    if not plan:
        exception_str = """
            Trajectory could not be planned for a destination of {} with starting joint angles {}.
            Please make sure target and destination are reachable by the robot.
        """.format(destination_pose, destination_pose)
        raise Exception(exception_str)

    return planCompat(plan)


"""
    Creates a pick and place plan using the four states below.
    
    1. Pre Grasp - position gripper directly above target object
    2. Grasp - lower gripper so that fingers are on either side of object
    3. Pick Up - raise gripper back to the pre grasp position
    4. Place - move gripper to desired placement position

    Gripper behaviour is handled outside of this trajectory planning.
        - Gripper close occurs after 'grasp' position has been achieved
        - Gripper open occurs after 'place' position has been achieved

    https://github.com/ros-planning/moveit/blob/master/moveit_commander/src/moveit_commander/move_group.py
"""
def plan_pick_and_place(req: MoverService):
    response = MoverServiceResponse()

    # Initialize the scene object to monitor changes in the external environment
    scene = moveit_commander.PlanningSceneInterface()
    rospy.sleep(1)

    # Initialize self.arm group in the robotic arm that needs to be controlled by move group
    group_name = "arm_group"
    move_group = moveit_commander.MoveGroupCommander(group_name)

    # Get the name of the terminal link
    end_effector_link = move_group.get_end_effector_link()
    rospy.loginfo(end_effector_link)

    # Set the reference coordinate system used for the target position
    reference_frame = "world"
    move_group.set_pose_reference_frame(reference_frame)

    # Allow replanning when motion planning fails
    move_group.allow_replanning(True)

    # Set the allowable error of position (unit: meter) and attitude (unit: radian)
    move_group.set_goal_position_tolerance(0.01)
    move_group.set_goal_orientation_tolerance(0.05)
    
    current_robot_joint_configuration = [ 
        req.joints_input.joint_1, 
        req.joints_input.joint_2,
        req.joints_input.joint_3,
        req.joints_input.joint_4,
        req.joints_input.joint_5,
        req.joints_input.joint_6,
    ]

    # Pre grasp - position gripper directly above target object
    pre_grasp_pose = plan_trajectory(move_group, req.pick_pose, current_robot_joint_configuration)
    
    # If the trajectory has no points, planning has failed and we return an empty response
    if not pre_grasp_pose.joint_trajectory.points:
        return response

    previous_ending_joint_angles = list(pre_grasp_pose.joint_trajectory.points[-1].positions)

    # Grasp - lower gripper so that fingers are on either side of object
    pick_pose = copy.deepcopy(req.pick_pose)
    pick_pose.position.z -= 0.05  # Static value coming from Unity, TODO: pass along with request
    grasp_pose = plan_trajectory(move_group, pick_pose, previous_ending_joint_angles)
    
    if not grasp_pose.joint_trajectory.points:
        return response

    previous_ending_joint_angles = grasp_pose.joint_trajectory.points[-1].positions

    # Pick Up - raise gripper back to the pre grasp position
    pick_up_pose = plan_trajectory(move_group, req.pick_pose, previous_ending_joint_angles)
    
    if not pick_up_pose.joint_trajectory.points:
        return response

    previous_ending_joint_angles = pick_up_pose.joint_trajectory.points[-1].positions

    # Place - move gripper to desired placement position
    place_pose = plan_trajectory(move_group, req.place_pose, previous_ending_joint_angles)

    if not place_pose.joint_trajectory.points:
        return response

    # If trajectory planning worked for all pick and place stages, add plan to response
    response.trajectories.append(pre_grasp_pose)
    response.trajectories.append(grasp_pose)
    response.trajectories.append(pick_up_pose)
    response.trajectories.append(place_pose)

    move_group.clear_pose_targets()

    return response


"""
    Creates a plan to move the arm to the desired pose.

    https://github.com/ros-planning/moveit/blob/master/moveit_commander/src/moveit_commander/move_group.py
"""
def plan_move_to_pose(req):
    response = MoveToPoseServiceResponse()

    group_name = "arm_group"
    move_group = moveit_commander.MoveGroupCommander(group_name)

    current_robot_joint_configuration = [ 
        req.joints_input.joint_1, 
        req.joints_input.joint_2,
        req.joints_input.joint_3,
        req.joints_input.joint_4,
        req.joints_input.joint_5,
        req.joints_input.joint_6,
    ]

    # Target pose
    target_pose = plan_trajectory(move_group, req.pick_pose, current_robot_joint_configuration)
    
    # If the trajectory has no points, planning has failed and we return an empty response
    if not target_pose.joint_trajectory.points:
        return response

    response.trajectories.append(target_pose)

    return response


def moveit_server():
    moveit_commander.roscpp_initialize(sys.argv)
    rospy.init_node('mycobot_moveit_server')

    s = rospy.Service('mycobot_moveit', MoverService, plan_pick_and_place)
    #s2 = rospy.Service('mycobot_moveit', MoveToPoseService, plan_move_to_pose)

    rospy.loginfo("mycobot_moveit_server ready to plan")
    rospy.spin()


if __name__ == "__main__":
    moveit_server()
