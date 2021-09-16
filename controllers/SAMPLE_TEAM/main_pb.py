"""
The module is designed by team Robokit of Phystech Lyceum and team Starkit
of MIPT under mentorship of Azer Babaev.
The module is designed for creating players' dashboard and alternating between 
team game with Game Controller or individual play without Game Controller.
"""
"""
The module must be used for running with arguments of command line:
Order of arguments: port, team_id, robot_color, robot_number, role, second_pressed_button, initial_coord
all arguments have to be transferred as str values with following type assignmet to other types:
int: port  - TCP port of communication with player.exe, must be defined in team.json
int: team_id  - value between 60 -127, must be appointed by human referee
str: robot_color - can be 'red' or 'blue', defined in game.json
int: robot_number - from 1 to 5. Must be defined in team.json
str: role  - initial role of player in game. Possible values of role argument:
             'forward', 'goalkeeper', 'penalty_Shooter', 'penalty_Goalkeeper', 'run_test'
int: second_pressed_button  - possible values of 2-nd argument: 1-8. 
                            At real robot second pressed button number is used to choose mode of role 
list: initial_coord - initial localization and orientation values of robot transferred to controller
                      by human handler of real robot or by auto-referee to controllor in simulation. 
                      Elenets of list: [float: x, float: y, float: yaw]. x and y - coordinates expressed in m.
                      yaw - orientation of robot in radians.
"""

import sys
import os
import math
import json
import time
import wx
import threading
from pathlib import Path

current_work_directory = Path.cwd()

SIMULATION = 4                       # 0 - Simulation without physics in Coppelia, 
                                     # 1 - Simulation synchronous with physics in Coppelia, 
                                     # 2 - used for real robot
                                     # 3 - Simulation streaming with physics in Coppelia
                                     # 4 - Simulation in Webots

from Soccer.Localisation.class_Glob import Glob
from Soccer.Localisation.class_Local import *
from Soccer.strategy import Player
from Soccer.Motion.class_Motion_Webots_PB import Motion_sim
from launcher_pb import *
sys.path.append(str(current_work_directory.parent/'player'))
from communication_manager_robokit import CommunicationManager

with open('../referee/game.json', "r") as f:
    game_data = json.loads(f.read())

with open('../referee/' + game_data['red']['config'], "r") as f:
    team_1_data = json.loads(f.read())

with open('../referee/' + game_data['blue']['config'], "r") as f:
    team_2_data = json.loads(f.read())



class Falling:
    def __init__(self):
        self.Flag = 0

class Pause:
    def __init__(self):
        self.Flag = False
global pause
pause = Pause()

def main_procedure():
    global pause
    Port = sys.argv[1]
    print('port =', Port)
    robot = CommunicationManager(1, '127.0.0.1', int(Port), team_color=sys.argv[3].upper(), player_number = int(sys.argv[4]), time_step = 15)
    #sensors = {"left_knee_sensor": 15, "right_knee_sensor": 15, "left_ankle_pitch_sensor": 15, "right_ankle_pitch_sensor": 15,
    #          "right_hip_pitch_sensor": 15, "left_hip_pitch_sensor": 15,  "gps_body": 15,"head_pitch_sensor": 15,
    #          "head_yaw_sensor": 15, "imu_body": 5, "recognition": 15}
    #sensors = {"gps_body": 15,"imu_body": 5}#, "recognition": 5}
    #robot.enable_sensors(sensors)
    #th0 = threading.Thread(target=robot.run)
    #th0.start()
    #th0.join
    falling = Falling()

    team_id = int(sys.argv[2])
    role = sys.argv[5]
    print('role =', role)
    if team_id > 0:
        robot_color = sys.argv[3]
        robot_number = int(sys.argv[4])
        player_super_cycle(falling, team_id, robot_color, robot_number, SIMULATION, current_work_directory, robot, pause)

    second_pressed_button = int(sys.argv[6])
    initial_coord = eval(sys.argv[7])
    print(initial_coord)
    print('Player is going to play without Game Controller')
    glob = Glob(SIMULATION, current_work_directory)
    glob.pf_coord = initial_coord
    motion = Motion_sim(glob, robot, None, pause)
    motion.sim_Start()
    motion.direction_To_Attack = -initial_coord[2]
    motion.activation()
    local = Local(motion, glob, coord_odometry = initial_coord)
    motion.local = local
    local.coordinate_record(odometry = True)
    motion.falling_Flag = 0
    player = Player(role, second_pressed_button, glob, motion, local)
    player.play_game()
    sys.exit(0)


class RedirectText(object):
    def __init__(self,aWxTextCtrl):
        self.out = aWxTextCtrl

    def write(self,string):
        self.out.WriteText(string)




class Main_Panel(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(Main_Panel, self).__init__(*args, **kwargs)
        #self.main_procedure()
        self.InitUI()
        wx.CallLater(1000, self.main_procedure)

    def main_procedure(self):
        t1 = threading.Thread( target = main_procedure, args=())
        t1.setDaemon(True)
        t1.start()

    def InitUI(self):
        self.console_Panel = wx.Panel(self)
        panel = wx.Panel(self.console_Panel)
        self.log = wx.TextCtrl(self.console_Panel, -1, style=wx.TE_MULTILINE) #|wx.TE_READONLY) #|wx.HSCROLL)
        log_box = wx.BoxSizer(wx.VERTICAL)
        log_box.Add(panel,0,wx.TOP)
        log_box.Add(self.log, proportion = 1, flag=wx.EXPAND|wx.BOTTOM|wx.TOP)
        self.console_Panel.SetSizer(log_box)
        redir = RedirectText(self.log)
        sys.stdout = redir

        hbox = wx.BoxSizer()
        sizer = wx.GridSizer(1, 2, 2, 2)

        btn1 = wx.Button(panel, label='Exit')
        btn2 = wx.Button(panel, label='Pause')

        sizer.AddMany([btn1, btn2])

        hbox.Add(sizer, 0, wx.TOP)
        panel.SetSizer(hbox)


        btn1.Bind(wx.EVT_BUTTON, self.ShowMessage1)
        btn2.Bind(wx.EVT_BUTTON, self.ShowMessage2)

        self.SetSize((300, 200))
        robot_color = sys.argv[3]
        robot_number = sys.argv[4]
        title = 'Team ' + robot_color + ' player '+ robot_number
        self.SetTitle(title)
        width, height = wx.GetDisplaySize().Get()
        if robot_color == 'red':
            x_position = width - 300 * (5- int(robot_number))
        else:
            x_position = width - 300 * (3- int(robot_number))
        self.SetPosition((x_position, height -225))
        #self.Centre()

    def ShowMessage1(self, event):
        print('Exit button pressed')
        sys.stdout = sys.__stdout__
        sys.exit(0)

    def ShowMessage2(self, event):
        global pause
        if pause.Flag:
            pause.Flag = False
        else:
            pause.Flag = True
        print('Pause button pressed')


def main():
    app = wx.App()
    ex = Main_Panel(None)
    ex.Show()
    app.MainLoop()

main()


