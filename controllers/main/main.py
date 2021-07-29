"""
Possible values of 1-st argument role: 
forward, goalkeeper, penalty_Shooter, penalty_Goalkeeper, run_test
Possible values of 2-nd argument: 1-8
Possible values of 3-rd argument: [0.0, 0.0, 0.0]
"""

import sys
import os
import math
import json
import time

current_work_directory = os.getcwd()
current_work_directory = current_work_directory.replace('\\', '/')
current_work_directory += '/'
SIMULATION = 4                       # 0 - Simulation without physics, 
                                     # 1 - Simulation synchronous with physics, 
                                     # 3 - Simulation streaming with physics
                                     # 4 - Simulation in Webots

sys.path.append( current_work_directory + 'Soccer/')
sys.path.append( current_work_directory + 'Soccer/Motion/')
sys.path.append( current_work_directory + 'Soccer/Localisation/')
sys.path.append( current_work_directory)
        
from class_Glob import Glob
from class_Local import *
from strategy import Player
from class_Motion_Webots_inner import Motion_sim as Motion
from launcher import *


arguments = sys.argv
role = arguments[1]
second_pressed_button = int(arguments[2])
initial_coord = list(eval(arguments[3]))
team = int(arguments[4])
player_number = int(arguments[5])
is_goalkeeper = bool(arguments[6])


receiver = init_gcreceiver(team, player, is_goalkeeper)
for i in range(5):
    if receiver.team_state != None:
        player_super_cycle()
    else: 
        print('Game Controller Receiver returns "None"')
        time.sleep(1)

print('Player is going to play without Game Controller')
glob = Glob(SIMULATION, current_work_directory)
glob.pf_coord = initial_coord
motion = Motion(glob)
motion.sim_Start()
motion.direction_To_Attack = -initial_coord[2]
motion.activation()
local = Local(motion, glob, coord_odometry = initial_coord)
motion.local = local
local.coordinate_record(odometry = True)
motion.falling_Flag = 0
player = Player(role, second_pressed_button, glob, motion, local)
player.play_game()


