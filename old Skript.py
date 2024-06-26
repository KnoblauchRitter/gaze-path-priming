# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 08:40:46 2024

@author: Denny Krempin
"""

import os
import glob
from psychopy import gui, core, visual, event, iohub
import time
import random
import csv
import numpy as np
from psychopy.tools import monitorunittools
import pandas
import json
from psychopy.iohub.client import launchHubServer
from psychopy.iohub.constants import EyeTrackerConstants
from psychopy.tools import monitorunittools
from psychopy.iohub.util import hideWindow, showWindow

# paths to visual stimuli
img_dir = os.getcwd() + '//stimuli_material//exp_stim//'
img_list = glob.glob(img_dir + '*.png')
instruction_img_ALLF = os.getcwd() + '//instructions_image_ALLF'
instruction_img_AFLL = os.getcwd() + '//instructions_image_AFLL'

# constants 
BACKGROUND_COLOR = [128, 128, 128]
RGB_GREY = [128, 128, 128]
max_trials = len(img_list)
max_blocks = 2
trial_dur = 6000
continue_key = ['l']
trial_keys = ['a', 'l']

# supervisor input
supervisor_input = gui.Dlg(title='Participant Data',
                           pos=(0, 0))
supervisor_input.addField('Probanden-ID:')
supervisor_input.addField('Alter:')
supervisor_input.addField('Dominant eye', choices=['Right', 'Left'])
supervisor_input.addField('Glasses:', choices=['Yes', 'No'])
supervisor_input.addField('Sex:', choices=['Male', 'Female'])
supervisor_input.addField('Handednes:', choices=['Right', 'Left'])
supervisor_input.addField('Response Buttons:', choices=['AF_LL', 'AL_LF'])
supervisor_input.show()

sub_id = supervisor_input.data[0]
age = supervisor_input.data[1]
dominant_eye = supervisor_input.data[2]
glasses = supervisor_input.data[3]
sex = supervisor_input.data[4]
dominant_hand = supervisor_input.data[5]
response_buttons = supervisor_input.data[6]

# Generate Window
win = visual.Window((1000, 1080),
                    units='pix',
                    fullscr=False,
                    allowGUI=False,
                    colorSpace='rgb255',
                    color=BACKGROUND_COLOR
                    )

win.setMouseVisible(False)


# Load in Gaze Path Data as List
with open('gazepathdata.json', 'rb') as fp:
        gaze_path_list = json.load(fp)

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

#######################################################
##########           Functions           ##############
#######################################################


def present_text(window_instance,
                 text = 'Standardsatz',
                 text_size = 0.075,
                 waitforpress = True,
                 text_position = (0., 0.),
                 unit='norm',
                 continue_key= 'l'):
    
    text_stim = visual.TextStim(window_instance, 
                                height=text_size, 
                                units=unit, 
                                pos=text_position)
    
    text_stim.setText(text)
    text_stim.draw()
    window_instance.flip()
    
    if waitforpress == True:
        event.waitKeys(keyList=['l'])
    else:
        core.wait(2)

    return None

def present_image(window_instance,
                img_input,
                waitforpress = True,
                image_position=(0., 0.),
                continue_key= 'l'):
    
    image_stim = visual.ImageStim(window_instance,
                                  image=img_input,
                                  pos=image_position)
    image_stim.draw()
    window_instance.flip()
    
    if waitforpress == True:
        event.waitKeys(keyList=['l'])
    else:
        core.wait(2)

    return None

def draw_fixation(window_instance,
                  fixation_position=(1, 1)):
    
    fixation = visual.ShapeStim(window_instance,
                                pos=fixation_position,
                                vertices=((0, -15), (0, 15), (0,0), (-15,0), (15, 0)),
                                lineWidth=3,
                                closeShape=False,
                                lineColor='black')
    fixation.draw()
    window_instance.update()
    core.wait(2.0)
    
    return None

def draw_red_cross (window_instance):   
    
    red_cross = visual.ShapeStim(window_instance,
                                vertices=((0, -20), (0, 20), (0,0), (-20,0), (20, 0)),
                                lineWidth=7,
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

def present_noise(window_instance,
                  noise_sync = 0):
    
   timer= core.Clock()
   
   
   dotfixation_stim = visual.Circle(window_instance,
                                    radius = 10,
                                    lineColor = 'green',
                                    fillColor = 'red',
                                    pos = (1, 1)
                                    )
   
   timer.reset()
   while timer.getTime() < 1:
        for i in range(noise_sync , noise_sync + 19): 
            noise_list[(i%(len(noise_list)))].draw()
        noise_sync +=1
           
        dotfixation_stim.draw()
        window_instance.flip() 
        core.wait(0.012)
    
   return noise_sync

def present_gaze(window_instance,
                gaze_path_input,
                continue_key='space',
                noise_sync = 0
                ):
    
   timer = core.Clock()
   #remove first entry with path type for easier handling
   gaze_path_input = gaze_path_input[1:-1]
   
   for i in gaze_path_input:
       
       dotfixation_stim = visual.Circle(window_instance,
                                        radius = 10,
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
    
   return noise_sync

def present_jitter(window_instance,
                fix_position,
                noise_sync,
                continue_key='space'
                ):
   timer= core.Clock()
   
   
   dotfixation_stim = visual.Circle(window_instance,
                                    radius = 10,
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
    
   return noise_sync

def present_img(window_instance,
                img_input,
                noise_sync,
                fix_position,
                continue_key='space'):
   
   pos_list_x = [-150,0,150]
   pos_list_y = [-150,0,150]
   fix_position = (fix_position[0],fix_position[1])
        
   face_pos = fix_position
   while face_pos == fix_position:
       face_pos = (fix_position[0]+random.choice(pos_list_x),fix_position[1]+random.choice(pos_list_y))


   dotfixation_stim = visual.Circle(window_instance,
                                    radius = 10,
                                    lineColor = 'green',
                                    fillColor = 'red',
                                    pos = fix_position)
   
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
           opacity=0.08*actual
           
       if actual > 6: 
           done = True
           RT = 6
           opacity=0.08*actual
   
   # Answer Logic based on set Response Buttons
   
   if response_buttons == 'AF_LL':
       if keypress == ['a'] and 'face' in img_input or keypress == ['l'] and 'L' in img_input:
           draw_circle(win)
           return ['Correct', RT, opacity]
       else: 
           if RT == 6:
               present_text(win, 'Sie haben keine Taste Gedrückt', waitforpress = False)
               return ['No Answer', RT, opacity]
           draw_red_cross(win)    
           return ['False', RT, opacity]
       
   elif response_buttons == 'AL_LF':
       if keypress == ['a'] and 'L' in img_input or keypress == ['l'] and 'face' in img_input:
           draw_circle(win)
           return ['Correct', RT, opacity]
       else: 
           if RT == 6:
               present_text(win, 'Sie haben keine Taste Gedrückt', waitforpress = False)
               return ['No Answer', RT, opacity]
           draw_red_cross(win)    
           return ['False', RT, opacity]
    

   
def gen_file(sub_id):
    
    output_path = os.getcwd() + f'/output/sub-{sub_id}'
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    behav_data = pandas.DataFrame({'sub_id' : [], 
                              'age' : [],
                              'sex' : [],
                              'dominant_hand': [],
                              'dominant_eye': [],
                              'glasses' : [],
                              'block' : [],
                              'trial' : [],
                              'onset' : [],
                              'duration' : [],
                              'gaze_path_type' : [],
                              'congruency' : [],
                              'reaction_time' : [],
                              'opacity':[],
                              'accuracy' : [],
                              'responsebuttons': [],
                              'fixamount' : [],
                              'presentedfixations' : []})
    
    file_path = output_path + f'/sub-{sub_id}.tsv'
    return behav_data, file_path

def collect_responses(sub_id,
                      age,
                      sex,
                      dominant_hand,
                      dominant_eye,
                      glasses,
                      block,
                      trial,
                      onset,
                      duration,
                      typeofpath,
                      congruency,
                      reaction_time,
                      opacity,
                      accuracy,
                      responsebuttons,
                      fixamount,
                      presentedfixations):
    
    trial_column = pandas.DataFrame({'sub_id' : [sub_id], 
                                 'age' : [age],
                                 'sex' : [sex],
                                 'glasses' : [glasses],
                                 'dominant_hand' : [dominant_hand],
                                 'dominant_eye' : [dominant_eye],
                                 'block' : [block],
                                 'trial' : [trial],
                                 'onset' : [onset],
                                 'duration' : [duration],
                                 'gaze_path_type' : [typeofpath],
                                 'congruency' : [congruency],
                                 'reaction_time' : [reaction_time],
                                 'opacity' : [opacity],
                                 'accuracy' : [accuracy],
                                 'responsebuttons' : [responsebuttons],
                                 'fixamount' : [fixamount],
                                 'presentedfixations' : [presentedfixations]})
    return trial_column

#######################################################
##########        Start Experiment       ##############
#######################################################


    
def start_experiment(win,
                     image_list,
                     trial_num):
   
  sub_data, file_path = gen_file(sub_id) 
  global_timer = core.Clock()
  
  if response_buttons == 'ALLF':
    present_image(win,instruction_img_ALLF)
  else:
    present_image(win,instruction_img_AFLL)

  for block in range(max_blocks):
      
      tracker.sendMessage(f"EVT_START BLOCKnr {block}")
      if block == 0:
          present_text(window_instance = win,
                   text = 'Starting with Block 1',
                   waitforpress = False,
                   continue_key = ['l'])
      else:
          present_text(window_instance = win,
                   text = f'Block {block+1}: Take a small break \n To continue press any key',
                   waitforpress = True,
                   continue_key = ['l'])
      
      shuffled_img_list = random.sample(img_list, len(img_list))
      shuffled_gaze_path_list = random.sample(gaze_path_list, len(gaze_path_list))

      for trial in range(max_trials):
            tracker.setRecordingState(True)
            tracker.sendMessage(f"EVT_START TRIALnr {trial}")
            onset = global_timer.getTime()
            draw_fixation(window_instance=win,
                         fixation_position=(0, 0))
            
            noise_sync = present_noise(win)
            
            gaze_path_temp = shuffled_gaze_path_list[trial][0:random.randint(3,5)]
            noise_sync = present_gaze(window_instance = win, 
                                      gaze_path_input = gaze_path_temp)
            
            #  gaze_path_temp[-1][0] = last Fixation Position
            noise_sync = present_jitter(window_instance = win, 
                                        fix_position = gaze_path_temp[-1][0],
                                        noise_sync = noise_sync)


            [answer, RT, opacity] = present_img( win, 
                                        shuffled_img_list[trial],
                                        noise_sync,
                                        gaze_path_temp[-1][0])
            
            tracker.setRecordingState(False)
            tracker.sendMessage(f"EVT_END TRIALnr {trial}")
            
            trial_duration = onset - global_timer.getTime()
            
            if 'F'== gaze_path_temp[0] and 'face' in shuffled_img_list[trial] or 'L'== gaze_path_temp[0] and 'L' in shuffled_img_list[trial]:
                congruency = 1
            else:
                congruency = 0
            
            typeofpath = gaze_path_temp[0]
            
            
            sub_data = sub_data.append(collect_responses(sub_id=sub_id,
                                                         age=age,
                                                         sex=sex,
                                                         dominant_hand= dominant_hand,
                                                         dominant_eye= dominant_eye,
                                                         glasses=glasses,
                                                         block=block+1,
                                                         trial=trial+1,
                                                         onset= onset,
                                                         duration = trial_duration,
                                                         typeofpath = typeofpath,
                                                         congruency = congruency,
                                                         reaction_time=RT,
                                                         opacity = opacity,
                                                         accuracy= answer,
                                                         responsebuttons = response_buttons,
                                                         fixamount = (len(gaze_path_temp) - 1)),
                                                         presentedfixations = gaze_path_temp)           
            
            try:
                sub_data.to_csv(file_path, 
                                index=False,
                                sep='\t')
            except:
                print(f'Error saving file: {file_path}')
            
            present_ITI(window_instance=win,
                        duration=2) 
        
      tracker.sendMessage(f"EVT_END BLOCKnr {block}")
            
start_experiment(win, img_list, max_trials)

tracker.setRecordingState(False)
tracker.setConnectionState(False)
io.quit()

present_text(window_instance = win,
             text = 'Vielen dank für die Teilnahme etc.',
             waitforpress = False,
             continue_key = continue_key)

win.close()