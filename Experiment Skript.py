# -*- coding: utf-8 -*-
"""
Created on Mon May 13 14:26:39 2024

@author: Denny Krempin
"""

import os
import glob
from psychopy import gui, core, visual, event, iohub
import time
import random
import csv
import numpy as np
from psychopy.iohub.client import launchHubServer
from psychopy.iohub.constants import EyeTrackerConstants
from psychopy.tools import monitorunittools
from psychopy.iohub.util import hideWindow, showWindow


# paths to visual stimuli
img_dir = os.getcwd() + '//stimuli_material//exp_stim//'
img_list = glob.glob(img_dir + '*.png')

# constants 
BACKGROUND_COLOR = [128, 128, 128]
RGB_GREY = [128, 128, 128]
max_trials = len(img_list)
max_blocks = 2
trial_dur = 6000
continue_key = 'space'
trial_keys = ['a', 'l']

# Generate Window
win = visual.Window((1920, 1080),
                    units='pix',
                    fullscr=True,
                    allowGUI=False,
                    colorSpace='rgb255',
                    color=BACKGROUND_COLOR
                    )

win.setMouseVisible(False)

# parameter:
gaze_path_list = [[["face"],[(0.2, 0.3), 1600], [(0.1, -0.4), 1200], [(0.2, 0.1), 1100]],
                  [["house"],[(0.2, -0.5), 800], [(-0.2, 0.4), 1350], [(0.1, -0.3), 1200]],
                  [["face"],[(-0.2, -0.4), 1200], [(0.4, -0.2), 900], [(-0.4, 0.3), 1900], [(0.2, 0.3), 1750]],
                  [["face"],[(0.3, -0.5), 800], [(-0.2, 0.1), 1000], [(-0.3, -0.1), 1400]],
                  [["house"],[(-0.2, 0.2), 1400], [(-0.3, 0.3), 1500], [(-0.2, -0.1), 900], [(-0.3, -0.1), 900]],
                  [["house"],[(0.4, 0.1), 1800], [(-0.1, -0.2), 1150], [(0.4, 0.3), 1700]],
                  [["face"],[(-0.1, 0.3), 1550], [(0.1, -0.3), 1350], [(0.1, 0.4), 2000], [(0.1, -0.2), 1100]]]

instructions = {'instructions_1' : 'Welcome to our experiment' \
    'continuekey = Spacebar ...'}

# liste an Noise Samples generieren (Range = Anzahl an samples)
noise_list = []

for i in range(10):
    noise = visual.NoiseStim(win=win, 
                       name = 'noise', 
                       units = 'pix',
                       size = (1024, 1024),
                       noiseType='Filtered',
                       noiseFractalPower='-1',
                       texRes=1024, interpolate=True,
                       blendmode = 'avg',
                       opacity = 0.1,
                       contrast = 1) 
    
    noise_list.append(noise)

#######################################################
##########      EYETRACKER SETUP         ##############
#######################################################
TRACKER = 'eyelink'
devices_config = dict()
eyetracker_config = dict(name='tracker')
if TRACKER == 'mouse':
    eyetracker_config['calibration'] = dict(screen_background_color=BACKGROUND_COLOR)
    devices_config['eyetracker.hw.mouse.EyeTracker'] = eyetracker_config
elif TRACKER == 'eyelink':
    eyetracker_config['model_name'] = 'EYELINK 1000 DESKTOP'
    eyetracker_config['runtime_settings'] = dict(sampling_rate=1000, track_eyes='RIGHT')
    eyetracker_config['calibration'] = dict(screen_background_color=BACKGROUND_COLOR)
    devices_config['eyetracker.hw.sr_research.eyelink.EyeTracker'] = eyetracker_config

CALIBRATION_SETTINGS = {
                        'unit_type':'pix',
                        'color_type':'rgb255',
                        'target_attributes':dict(outer_diameter=42,
                                                inner_diameter=11,
                                                target_duration=1,
                                                target_delay = 2
                                                ),
                        'screen_background_color':RGB_GREY
                    }

iohub_config = {'eyetracker.hw.sr_research.eyelink.EyeTracker':
                    {
                    'name':'tracker',
                    'model_name':'EYELINK 1000 DESKTOP',
                    'calibration':CALIBRATION_SETTINGS
                    }
                }

io = launchHubServer(window=win, **iohub_config)
io.clearEvents()
tracker = io.getDevice('tracker')

# run eyetracker calibration
tracker.sendCommand('calibration_area_proportion = 0.65 0.65')
tracker.sendCommand('validation_area_proportion = 0.65 0.65')
result = tracker.runSetupProcedure()
print("Calibration returned: ", result)

# reinitialise the HubServer to get rid of the display trouble
io.quit()
io = launchHubServer(window=win, **iohub_config)
tracker = io.getDevice('tracker')

tracker.setRecordingState(True)


# # So request to start trial has occurred...
#             # Clear the screen, start recording eye data, and clear all events
#             # received to far.


# self.hub.sendMessageEvent(text="TRIAL_START")
# self.hub.clearEvents('all')

# flip_time=window.flip()
#            self.hub.sendMessageEvent(text="TRIAL_END %d"%t,sec_time=flip_time)
#            tracker.setRecordingState(False)
#            self.hub.clearEvents('all')

# self.eyetracker.sendMessage("SESSION " + sess + " BLOCKID " + str(block_ind) + " TRIALID " + str(tr_ind))

#eyetracker.setRecordingState(True)
#self.eyetracker.sendMessage("Recording")

#io.clearEvents()
#disconnect_eyetracker()
# duration = self.master_clock.getTime() - onset
# self.eyetracker.sendMessage("SESSION " + sess + " BLOCKID " + str(block_ind) + " TRIALEND " + str(tr_ind))



#######################################################
##########           Functions           ##############
#######################################################


def present_text(window_instance,
                 text = 'Standardsatz',
                 text_size = 0.075,
                 waiting = True,
                 text_position = (0., 0.),
                 unit='norm',
                 continue_key='space'):
    
    text_stim = visual.TextStim(window_instance, 
                                height=text_size, 
                                units=unit, 
                                pos=text_position)
    
    text_stim.setText(text)
    text_stim.draw()
    window_instance.flip()
    
    if waiting == True:
        event.waitKeys(keyList=[continue_key])
    else:
        core.wait(2)

    return None

def draw_fixation(window_instance,
                  fixation_position=(1, 1)):
    
    fixation = visual.ShapeStim(window_instance,
                                pos=fixation_position,
                                vertices=((0, -0.04), (0, 0.04), (0,0), (-0.04,0), (0.04, 0)),
                                lineWidth=4,
                                closeShape=False,
                                lineColor='black')
    fixation.draw()
    window_instance.update()
    core.wait(2.0)
    
    return None

def draw_red_cross (window_instance):   
    
    red_cross = visual.ShapeStim(window_instance,
                                vertices=((0, -0.05), (0, 0.05), (0,0), (-0.05,0), (0.05, 0)),
                                lineWidth=8,
                                closeShape=False,
                                lineColor='red',
                                ori = 45)
    red_cross.draw()
    window_instance.update()
    core.wait(2.0)
    
    return None

def draw_circle(window_instance,position=(0.,0.)):
    
    big_circle = visual.Circle(win=win,
                                    units="pix",
                                    radius=18,
                                    fillColor=[-1, 0.00392156862745097, -1],
                                    lineColor=[-1, 0.00392156862745097, -1]
                                    )
    small_circle = visual.Circle(win=win,
                                    units="pix",
                                    radius=10,
                                    fillColor=[0, 0, 0],
                                    lineColor=[0, 0, 0]
                                    )
    
    big_circle.draw()
    small_circle.draw()
    window_instance.flip()
    core.wait(2.0)
    
    return None

def present_ITI(window_instance,
                duration=2.0):
    window_instance.update()
    core.wait(duration)
    
    return None

def present_gaze(window_instance,
                gaze_path_input,
                continue_key='space',
                noise_sync = 0
                ):
    
   timer = core.Clock()
   gaze_path_input = gaze_path_input[1:-1]
   
   for i in gaze_path_input:
       
       dotfixation_stim = visual.Circle(window_instance,
                                        radius = 0.02,
                                        lineColor = 'green',
                                        fillColor = 'red',
                                        pos = i[0]
                                        )
       
       timer.reset()
       fix_dur = i[1]/1000
       while timer.getTime() < fix_dur:
           # + 9 oder  + 19 fuer entweder 10 oder 20 samples
           for i in range(noise_sync , noise_sync + 19): 
               noise_list[(i%(len(noise_list)))].draw()
           noise_sync +=1
           
              
               
           dotfixation_stim.draw()
           window_instance.flip() 
           core.wait(0.024)
    #event.waitKeys(keyList=[continue_key])
    
   return noise_sync

def present_jitter(window_instance,
                fix_position,
                noise_sync,
                continue_key='space'
                ):
   timer= core.Clock()
   
   
   dotfixation_stim = visual.Circle(window_instance,
                                    radius = 0.02,
                                    lineColor = 'green',
                                    fillColor = 'red',
                                    pos = fix_position
                                    )
   
   timer.reset()
   rand_jitter= random.uniform(1.0, 2.0) 
   while timer.getTime() < rand_jitter:
        for i in range(noise_sync , noise_sync + 19): 
            noise_list[(i%(len(noise_list)))].draw()
        noise_sync +=1
           
        dotfixation_stim.draw()
        window_instance.flip() 
        core.wait(0.012)
    #event.waitKeys(keyList=[continue_key])
    
   return noise_sync

def present_img(window_instance,
                img_input,
                noise_sync,
                fix_position,
                continue_key='space'):
   
   pos_list_x = [-0.4,0.4]
   pos_list_y = [-0.4,0,0.4]
   face_pos = (0,0)
   while face_pos == (0,0):
       face_pos = (fix_position[0]+random.choice(pos_list_x),fix_position[1]+random.choice(pos_list_y))
   
   dotfixation_stim = visual.Circle(window_instance,
                                    radius = 0.02,
                                    lineColor = 'green',
                                    fillColor = 'red',
                                    pos = fix_position
                                    )
   
   timer = core.Clock()
   done = False
   timer.reset()
   while done == False:    
       actual = timer.getTime()
       
       image_stim = visual.ImageStim(window_instance,
                                      image=img_input,
                                      pos=face_pos,
                                      opacity=0.08*actual)
       
       # + 9 oder  + 19 fuer entweder 10 oder 20 samples
       for i in range(noise_sync , noise_sync + 19): 
           noise_list[(i%(len(noise_list)))].draw()
       noise_sync +=1
               
       image_stim.draw()
       dotfixation_stim.draw()
       window_instance.flip()
       
       keypress = event.getKeys(keyList=trial_keys)
       
       if ('a' in keypress) or ('l' in keypress):
           done = True
           RT = actual
       if actual > 6: 
           done = True
           RT = 6
    
   # Gesicht rechts     
   if (((face_pos[0] > 0) and ('l' in keypress)) or ((face_pos[0] < 0) and ('a' in keypress))):
       draw_circle(win)
       return ['Correct', RT]
   else:
       if RT == 6:
           present_text(win, 'Sie haben keine Taste Gedrückt :(', waiting = False)
           return ['No Answer', RT]
       draw_red_cross(win)    
       return ['False', RT]
       

#######################################################
##########        Start Experiment       ##############
#######################################################
    
def start_experiment(win,
                     image_list,
                     trial_num):
    
  present_text(window_instance=win,
                   text=instructions,
                   waiting=True,                   
                   continue_key=continue_key)

  for block in range(max_blocks):
    
      tracker.sendMessage(f"EVT_START BLOCKnr {block}")
      present_text(window_instance = win,
                   text = f'Block {block+1}: machen sie eine Pause, zum Fortfahren Leertaste drücken',
                   waiting = True,
                   continue_key = continue_key)
      
      shuffled_img_list = random.sample(img_list, len(img_list))
      shuffled_gaze_path_list = random.sample(gaze_path_list, len(gaze_path_list))
     
      for trial in range(max_trials):
        
            tracker.setRecordingState(True)
            tracker.sendMessage(f"EVT_START TRIALnr {trial}")
            
            draw_fixation(window_instance=win,
                         fixation_position=(0, 0))
            
            noise_sync = present_gaze(window_instance = win, 
                                      gaze_path_input = shuffled_gaze_path_list[trial])
            
            #  shuffled_gaze_path_list[trial][-1][0] = last Fixation Position
            noise_sync = present_jitter(window_instance = win, 
                                        fix_position = shuffled_gaze_path_list[trial][-1][0],
                                        noise_sync = noise_sync)


            [answer, RT] = present_img( win, 
                                        shuffled_img_list[trial],
                                        noise_sync,
                                        shuffled_gaze_path_list[trial][-1][0])

            typeofpath = shuffled_gaze_path_list[trial][0]
            tracker.setRecordingState(False)
            present_ITI(window_instance=win,
                        duration=2) 
            tracker.sendMessage(f"EVT_END TRIALnr {trial}")
            
      tracker.sendMessage(f"EVT_END BLOCKnr {block}")

start_experiment(win, img_list, max_trials)

tracker.setRecordingState(False)
eyetracker.setConnectionState(False)
io.quit()

present_text(window_instance = win,
             instr_text = 'Vielen dank für die Teilnahme etc.',
             waiting = False,
             continue_key = continue_key)

win.close()





