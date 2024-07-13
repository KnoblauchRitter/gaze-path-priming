import os
import glob
import time
import random
import pandas as pd
import json
from psychopy import gui, core, visual, event
from psychopy_visionscience.noise import NoiseStim
from psychopy.iohub.client import launchHubServer


window_size = [1920, 1080]

# paths to visual stimuli
img_dir = os.path.join(os.getcwd(), "stimuli_material", "exp_stim")
img_list = glob.glob(os.path.join(img_dir, "*.png"))
instruction_img_ALLF = os.path.join(os.getcwd(), "instructions_image_ALLF.png")
instruction_img_AFLL = os.path.join(os.getcwd(), "instructions_image_AFLL.png")

sortorder =  [0,8,1,9,2,10,3,11,4,12,5,13,6,14,7,15]
img_list_temp = [img_list[i] for i in sortorder]
sorted_img_list = img_list_temp + img_list_temp

# constants 
BACKGROUND_COLOR = [128, 128, 128]
RGB_GREY = [128, 128, 128]
MAX_TRIALS = 32
MAX_BLOCKS = 7
trial_dur = 6000
trial_keys = ["a", "f"]

# Generate Window
win = visual.Window((window_size[0], window_size[1]),
                    units="pix",
                    fullscr=True,
                    allowGUI=False,
                    colorSpace="rgb255",
                    color=BACKGROUND_COLOR
                    )

win.setMouseVisible(False)

# liste an Noise Samples generieren (Range = Anzahl an samples)
noise_list = []

for i in range(50):
    noise = NoiseStim(
        win=win, 
        name="noise", 
        units="pix",
        size=(2048, 2048),
        noiseType="Filtered",
        noiseFractalPower="-1",
        texRes=1024, 
        interpolate=True,
        blendmode="avg",
        opacity=0.1,
        contrast=1
        )
    noise_list.append(noise)

# supervisor input
supervisor_input = gui.Dlg(title="Participant Data", pos=(0, 0))
supervisor_input.addField('sub_id')
supervisor_input.addField('age')
supervisor_input.addField('glasses', choices=["Yes", "No"])
supervisor_input.addField('sex', choices=["Male", "Female"])
supervisor_input.addField('handedness', choices=["Right", "Left"])
supervisor_input.addField('response_buttons', choices=["AF_LL", "AL_LF"])
supervisor_input.show()

# if supervisor_input.OK:
#    print(supervisor_input)

sub_id = supervisor_input.data[0]
age = supervisor_input.data[1]
glasses = supervisor_input.data[2]
sex = supervisor_input.data[3]
dominant_hand = supervisor_input.data[4]
response_buttons = supervisor_input.data[5]

# Load in Gaze Path Data as List
with open("gazepathdata.json", "rb") as file_path:
    gpdata = json.load(file_path)


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

def counterbalance_paths(listing,prefix, gaze_path_list):
    for j in range(1,9):
        image_cur = prefix + str(j);
        sublist = []
        for i in listing:
            if(i[2][0] == image_cur):
                sublist.append(i)
        sublist = random.sample(sublist, 2)
        for x in sublist:
            gaze_path_list.append(x)
    return gaze_path_list

def present_text(window_instance,
                 text="If you are read this, \n please inform the experimentor!",
                 text_size=0.075,
                 continue_bool=None,
                 text_position=(0., 0.),
                 unit="norm",
                 continue_keys=["a", "l"]):
    
    text_stim = visual.TextStim(window_instance, 
                                height=text_size, 
                                units=unit, 
                                pos=text_position)
    
    text_stim.setText(text)
    text_stim.draw()
    window_instance.flip()
    
    if continue_bool == True:
        #core.wait(2.)
        event.waitKeys(keyList=continue_keys)
    elif continue_bool == False:
        core.wait(2.)

    return None

def present_image(window_instance,
                  img_in,
                  continue_bool=None,
                  image_position=(0., 0.),
                  continue_keys=["a", "f"]):
    
    image_stim = visual.ImageStim(window_instance,
                                  image=img_in,
                                  pos=image_position)
    image_stim.draw()
    window_instance.flip()
    
    if continue_bool == True: 
        #core.wait(2.)
        event.waitKeys(maxWait=float("inf"), keyList=continue_keys)
    elif continue_bool == False:
        core.wait(2.)

    return None

def draw_fixation(window_instance,
                  fixation_position=(1, 1)):
    
    fixation = visual.ShapeStim(window_instance,
                                pos=fixation_position,
                                vertices=((0, -15), (0, 15), (0,0), (-15,0), (15, 0)),
                                lineWidth=3,
                                closeShape=False,
                                lineColor="black")
    fixation.draw()
    window_instance.update()
    core.wait(1.5)
    
    return None

def draw_red_cross(window_instance):   
    
    red_cross = visual.ShapeStim(window_instance,
                                vertices=((0, -20), (0, 20), (0,0), (-20,0), (20, 0)),
                                lineWidth=7,
                                closeShape=False,
                                lineColor="red",
                                ori=45)
    red_cross.draw()
    window_instance.update()
    core.wait(2.0)
    return None

def draw_circle(window_instance):
    
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
                  noise_list,
                  noise_sync=0):
    timer= core.Clock()
    
    dotfixation_stim = visual.Circle(window_instance,
                                     radius=10,
                                     lineColor="green",
                                     fillColor="red"
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
                 noise_sync = 0
                ):
    
    timer = core.Clock()
    #remove first 3 entries with path type/viewerid/imgNr for easier handling
    print("gazepathinfunktion davor", gaze_path_input)
    gaze_path_input = gaze_path_input[3:]
    print("gazepathinfunktion danach", gaze_path_input)
    for gaze_coordinates in gaze_path_input:
        dotfixation_stim = visual.Circle(window_instance,
                                        radius=10,
                                        lineColor="green",
                                        fillColor="red",
                                        pos=gaze_coordinates[0]
                                        )
        timer.reset()
        fix_dur  = gaze_coordinates[1]/1000
        #add buffer to fixations
        fix_dur =  fix_dur + 0.2
        
        while timer.getTime() < fix_dur :
            # + 9 oder  + 19 fuer entweder 10 oder 20 samples
            for i in range(noise_sync , noise_sync + 19): 
                noise_list[(i%(len(noise_list)))].draw()
            noise_sync +=1

            dotfixation_stim.draw()
            window_instance.flip() 
    
    return noise_sync

def present_jitter(window_instance,
                fix_position,
                noise_sync
                ):
    timer= core.Clock()
    
    dotfixation_stim = visual.Circle(
        window_instance,
        radius=10,
        lineColor="green",
        fillColor = "red",
        pos=fix_position
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
    
    return noise_sync, rand_jitter

def present_trial_img(window_instance,
                      img_input,
                      noise_sync,
                      fix_position, 
                      trial_key_list_in=None):
    
    pos_list_x = [-150,0,150]
    pos_list_y = [-150,0,150]
    fix_position = (fix_position[0],fix_position[1])
    

    face_pos = fix_position
    while face_pos == fix_position:
        face_pos = (fix_position[0]+random.choice(pos_list_x),fix_position[1]+random.choice(pos_list_y))
    
    # start timer 
    start_time = time.process_time()

    dotfixation_stim = visual.Circle(
        window_instance,
        radius=10,
        lineColor="green",
        fillColor="red",
        pos=fix_position
    )
    timer = core.Clock()
    done = False
    timer.reset()
    event.clearEvents()
    
    while done == False:
        actual = timer.getTime()
        
        image_stim = visual.ImageStim(
            window_instance,
            image=img_input,
            pos=face_pos,
            opacity=0.08*actual
        )
       
        # + 9 oder  + 19 fuer entweder 10 oder 20 samples
        for i in range(noise_sync , noise_sync + 19):
            noise_list[(i%(len(noise_list)))].draw()
        noise_sync +=1
               
        image_stim.draw()
        dotfixation_stim.draw()
        window_instance.flip()
        
        
        keypress = event.getKeys(keyList=trial_key_list_in)

        if ("a" in keypress) or ("f" in keypress):
            done = True
            opacity=0.08*actual
            
        if actual > 6: 
           done = True
           opacity=0.08*actual
    
    if response_buttons == "AF_LL":
        if keypress == ["a"] and "F" in img_input or keypress == ["f"] and "L" in img_input:
            reaction_time = (time.process_time() - start_time)
            draw_circle(win)
            return "correct", reaction_time, opacity, keypress
        elif keypress == ["f"] and "F" in img_input or keypress == ["a"] and "L" in img_input:
            reaction_time = (time.process_time() - start_time)
            draw_red_cross(win)    
            return "incorrect", reaction_time, opacity, keypress
        elif keypress == []: # return has switched from None to []
            reaction_time = (time.process_time() - start_time)
            present_text(
                win,
                text="You did not respond within time!",
                continue_bool=False
                )
            return "incorrect", reaction_time, opacity, keypress
        
    if response_buttons == "AL_LF":
        if keypress == ["f"] and "F" in img_input or keypress == ["a"] and "L" in img_input:
            reaction_time = (time.process_time() - start_time)
            draw_circle(win)
            return "correct", reaction_time, opacity, keypress
        elif keypress == ["a"] and "F" in img_input or keypress == ["f"] and "L" in img_input:
            reaction_time = (time.process_time() - start_time)
            draw_red_cross(win)    
            return "incorrect", reaction_time, opacity, keypress
        elif keypress == []: # return has switched from None to []
            reaction_time = (time.process_time() - start_time)
            present_text(
                win,
                text="You did not respond within time!",
                continue_bool=False
                )
            return "incorrect", reaction_time, opacity, keypress
    
def gen_file(sub_id_in):
    output_path = os.path.join(os.getcwd(), "output", f"sub-{sub_id_in}")
    output_f_path =os.path.join(output_path, f"sub-{sub_id_in}.tsv")
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)
    
    behav_data = {"sub_id" : [], 
                  "age" : [],
                  "sex" : [],
                  "dominant_hand": [],
                  "glasses" : [],
                  "block_num" : [],
                  "trial_num" : [],
                  "onset" : [],
                  "gaze_path_type" : [],
                  "congruency" : [],
                  "jitter" : [],
                  "reaction_time" : [],
                  "button_pressed" : [],
                  "opacity": [],
                  "accuracy" : [],
                  "response_buttons": [],
                  "fix_num" : [],
                  "presented_img" : [],
                  "image_type" : [], 
                  "presented_fixations" : [],
                  "sourceid" : [],
                  "premature_keypress": []
        }

    return behav_data, output_f_path

def start_experiment(
        window_instance,
        sub_id_in,
        img_list_in,
        input_keys,
        gaze_path_list_in,
        response_buttons_in,
        MAX_BLOCKS_IN, 
        MAX_TRIALS_IN):
    
    sub_data, file_path = gen_file(sub_id_in)
    
    #Block Counterbalance 
    gaze_paths_faces = gaze_path_list_in[0:143]
    gaze_paths_leafs = gaze_path_list_in[144:268]
    #gaze_path_list = 32 Einträge je 2 von jedem Typ (F0x, L0x)
    gaze_path_list = counterbalance_paths(gaze_paths_faces,'F0',[])
    gaze_path_list = counterbalance_paths(gaze_paths_leafs,'L0',gaze_path_list)
    
    if response_buttons_in == "AL_LF":
        instr_img = instruction_img_ALLF
    elif response_buttons_in == "AF_LL":
        instr_img = instruction_img_AFLL

    # present instruction image
    present_image(
        window_instance, 
        img_in=instr_img,
        continue_bool=True,
        continue_keys=["f"]
        )

    # start the global timer after the instruction
    global_timer = core.Clock()

    for block in range(MAX_BLOCKS_IN):
        
        tracker.sendMessage(f"EVT_START BLOCKnr {block}")

        #shuffle order of trials, while keeping the counterbalance structure
        combined_list = list(zip(gaze_path_list, img_list_in))
        random.shuffle(combined_list)
        gaze_path_list, shuffled_img_list = zip(*combined_list)
        
        if block == 0:
            block_str = "Block 1: \n To start the experiment press the left or right button!"
        else:
            block_str = f"Block {block + 1}: Take a small break ... \n To continue press left or right button!"
        
        present_text(window_instance,
                     text=block_str,
                     continue_bool=True,
                     continue_keys=input_keys)
        
        
        
        

        for trial in range(MAX_TRIALS_IN):
            onset = global_timer.getTime()
            tracker.setRecordingState(True)
            tracker.sendMessage(f"EVT_START TRIALnr {trial}")

            draw_fixation(
                window_instance, 
                fixation_position=(0, 0)
                )
            
            noise_sync = present_noise(window_instance, noise_list)
            
            ###### obacht!!!!!
            gaze_path_temp = gaze_path_list[trial][0:random.randint(6,8)]
            

            print(gaze_path_temp)
            noise_sync = present_gaze(window_instance, 
                                      gaze_path_input=gaze_path_temp)
            
            # gaze_path_temp[-1][0] = last Fixation Position
            noise_sync, jitter = present_jitter(window_instance, 
                                                fix_position=gaze_path_temp[-1][0],
                                                noise_sync=noise_sync)

            # get pressed keys bevore the actual task
            premature_keypress = event.getKeys()
            if premature_keypress == []:
                premature_keypress = ["no early input"]
            
            sub_response, reaction_time, opacity, button_pressed = present_trial_img(window_instance, 
                                                                                     shuffled_img_list[trial],
                                                                                     noise_sync,
                                                                                     gaze_path_temp[-1][0],
                                                                                     trial_key_list_in=input_keys
                                                                                        )
            
            
            tracker.setRecordingState(False)
            tracker.sendMessage(f"EVT_END TRIALnr {trial}")

            
            # section to make output more readable
            type_path = gaze_path_temp[0]
            if type_path == ["L"]:
                type_path = "leaf"
            elif type_path == ["F"]:
                type_path = "face"

            image_type = shuffled_img_list[trial].split("/")[-1]
            if "F" in image_type:
                image_type = "face"
            elif "L" in image_type:
                image_type = "leaf"
                
            if type_path == "face" and "F" in shuffled_img_list[trial] or type_path == "leaf" and "L" in shuffled_img_list[trial]:
                congruency = "congruent"
            else:
                congruency = "incongruent"
            
            presented_fixations = gaze_path_temp[3:]
            
            if button_pressed == []:
                button_pressed = "no_response"
            
            sub_data["sub_id"].append(sub_id_in)
            sub_data["age"].append(age)
            sub_data["sex"].append(sex)
            sub_data["dominant_hand"].append(dominant_hand)
            sub_data["glasses"].append(glasses)
            sub_data["block_num"].append(block + 1)
            sub_data["trial_num"].append(trial + 1)
            sub_data["onset"].append(onset)
            sub_data["gaze_path_type"].append(type_path)
            sub_data["congruency"].append(congruency)
            sub_data["jitter"].append(jitter)
            sub_data["reaction_time"].append(reaction_time)
            sub_data["button_pressed"].append(button_pressed[0])
            sub_data["opacity"].append(opacity)
            sub_data["accuracy"].append(sub_response)
            sub_data["response_buttons"].append(response_buttons)
            sub_data["fix_num"].append(len(gaze_path_temp) - 3)
            sub_data["presented_img"].append(shuffled_img_list[trial].split("/")[-1])
            sub_data["image_type"].append(image_type)
            sub_data["presented_fixations"].append(presented_fixations)
            sub_data["sourceid"].append(gaze_path_temp[1])
            sub_data["premature_keypress"].append(premature_keypress)
            
            present_ITI(window_instance, duration=1)

            try:
                sub_data_out = pd.DataFrame(sub_data)
                sub_data_out.to_csv(file_path, index=False, sep="\t", mode="w")
            except:
                raise Exception(f"Error saving file at: {file_path}")

        tracker.sendMessage(f"EVT_END BLOCKnr {block}")


# start the actual experiment
start_experiment(window_instance=win, 
                 sub_id_in=sub_id,
                 img_list_in=sorted_img_list, 
                 input_keys=trial_keys,
                 gaze_path_list_in=gpdata,
                 response_buttons_in=response_buttons,
                 MAX_BLOCKS_IN=MAX_BLOCKS,
                 MAX_TRIALS_IN=MAX_TRIALS
                 )

tracker.setRecordingState(False)
tracker.setConnectionState(False)
io.quit()

present_text(window_instance=win,
             text="Thank you for your participation in the experiment! \n The experimenter will contact you shortly.",
             waitforpress=True,
             continue_keys=trial_keys)

win.close()





