# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 14:26:40 2014

@author: lau
"""

#==============================================================================
# DETERMINE OPERATING SYSTEM
#==============================================================================

import platform
sys = platform.system()

#==============================================================================
# LIBRARIES
#==============================================================================

if sys == 'Linux':
    function_library = '/home/lau/Dropbox/VanderbiltNashville/' + \
                        'experiment/psychopy_code/'
    
    save_library = '/home/lau/Dropbox/VanderbiltNashville/' + \
                    'experiment/data_files/'
                    
    target_font_type = 'digitalk'
    
    font_files = []
elif sys == 'Darwin':
    function_library = '/Users/lau/Desktop/psychopy_code/'
    
    save_library = '/Users/lau/Desktop/psychopy_code/data/'
    
    target_font_type = 'digitalk mono'
    
    font_files = ['/Users/lau/Library/Fonts/digitalk-mono.ttf']

#==============================================================================
# IMPORTS
#==============================================================================
import os
os.chdir(function_library)                    
import exp_functions_v2 as func
from psychopy import monitors, visual, data
import numpy as np


#==============================================================================
# MONITOR AND WINDOW PARAMETERS
#==============================================================================
monitor_width = 35 ## cm
monitor_distance = 45 ## cm
window_size = (1024, 768) ## pixels
background_color = (0, 0, 0 )


#==============================================================================
# EXPERIMENT PARAMETERS AND EXPERIMENT DIALOGUE                             
#==============================================================================
pickle_name = 'last_parameters.pickle'
exp_info = func.create_parameter_pickle_and_present_experiment_dialogue(
                                                                pickle_name)
default_text_height = 2.5    

full_screen = exp_info['full_screen']
pd_check = exp_info['pd_check']
seed = exp_info['seed']

seed_n = func.set_seed(seed)

#==============================================================================
# CREATE A WINDOW
#==============================================================================

monitor = monitors.Monitor('testMonitor', width=monitor_width,
                              distance=monitor_distance)
window = visual.Window(size=window_size, monitor=monitor, units='deg',
                       color=background_color, fullscr=full_screen)

                                                            
#==============================================================================
# WELCOME AND INSTRUCTION TEXT PARAMETERS                                                                
#==============================================================================

ins_col = (1, 1, 1)
ins_pos = (0, 0)
ins_height = 1
ins_resp = 'space'
ins_wrap_width = 40
ins_language = 'english'
      
#==============================================================================
# STIMULI PARAMETERS
#==============================================================================
blocked_design = exp_info['blocked_design']
ntrials = exp_info['ntrials']
repeat_n_times = exp_info['repeat_n_times']
automatic_responding = exp_info['automatic_responding']


task_settings = ['quadruplet', 'pairs', 'singles']
subject = exp_info['subject']
date = data.getDateStr()
even_digits = [2, 4, 6, 8]
odd_digits = [3, 5, 7, 9]
target_types = ['even', 'even', 'odd', 'odd']
combinations = []
for ndigits in range(1, 5):
    combinations.append(func.create_digit_lists(even_digits, odd_digits,
                                                ndigits))

all_target_nframes = range(1, 7)
all_target_nframes = range(2, 4) ## for follow up testing

parameter_dict_task = {'task': task_settings}

parameter_dict_quadruplet = {'combination': range(len(combinations[3])),
                             'target_types': target_types,
                             'target_nframes': all_target_nframes}
parameter_dict_pairs = {'combination': range(len(combinations[1])),
                         'target_types': target_types,
                         'target_nframes': all_target_nframes}                         
parameter_dict_singles = {'combination': range(len(combinations[0])),
                       'target_types': target_types,
                       'target_nframes': all_target_nframes}                         

parameter_dicts = {'task': parameter_dict_task,
                   'quadruplet': parameter_dict_quadruplet,
                   'pairs': parameter_dict_pairs,
                   'singles': parameter_dict_singles}
                   
task_counters = {'task': 0, 'quadruplet': 0, 'pairs': 0,
                 'singles': 0}                   
                                           	
#==============================================================================
# TASK SETTINGS
#==============================================================================
ts_col = (1, 1, 1)
ts_pos = (0, 0)                
ts_height = default_text_height
ts_resp = 'space'
ts_font = target_font_type
cue_last_trial = None ## set after each trial at the end of the trial loop
task_last_trial = None ## as above

#==============================================================================
# FIXATION
#==============================================================================
fix= '+'
fix_nframes = 30
fix_color = (-1, -1, -1)
fix_pos = (0, 0)
fix_height = default_text_height 
                                  
#==============================================================================
# DELAY
#==============================================================================
delay_nframes = 30

#==============================================================================
# TARGET
#==============================================================================
target_jitter = 0.5
target_color = (0.1, 0.1, 0.1)
target_pos = (0, 0)
target_height = 2.5
target_font = target_font_type
                                      
#==============================================================================
# MASK
#==============================================================================
mask_nframes = 30
mask_nlines = 250
mask_line_color = (1, 1, 1)
mask_line_width = 4 
mask_mu = 0
mask_sigma = 6

#==============================================================================
# OBJECTIVE RESPONSE           
#==============================================================================
o_resp_keys = ['e', 'o']
text_height = default_text_height
text_color = (1, 1, 1)
text_pos = (0, 0)

#==============================================================================
# SUBJECTIVE RESPONSE
#==============================================================================
modality = 'visual'
s_resp_keys = ['1', '2', '3', '4']
s_resp_names = ['No Experience', 'Weak Glimpse', 'Almost Clear Experience',
                'Clear Experience']
box_positions_x = list(np.linspace(start=-20, stop=20, num=len(s_resp_keys)))
box_position_y = 0
box_height = 2
box_width = 5
box_color = (-1, -1, -1)
number_color = (-1, -1, -1)
number_height = default_text_height
description_color = (-1, -1, -1)
description_height = 1
description_position_y = -2
show_answer_nframes = 1
show_box_color = (1, 1, 1)
box_fill_color = (1, 1, 1)
#==============================================================================
# CREATE THE FIXED STIMULI
#==============================================================================

fix_stim = func.create_fixation_stimulus(fix, fix_color, fix_pos, fix_height,
                                         window)
even_stimuli = func.create_target_stimuli(even_digits, target_font,
                                          target_color, target_pos,
                                          target_height, font_files, window)
odd_stimuli = func.create_target_stimuli(odd_digits, target_font, target_color,
                                         target_pos, target_height, font_files,
                                             window)
response_prompt = func.create_subjective_response_screen(
                                        s_resp_keys, s_resp_names,
                                        box_positions_x, box_position_y,
                                        box_height, box_width, box_color,
                                        number_color, number_height,
                                        description_color, description_height,
                                        description_position_y, window,
                                        modality)
                                        
objective_response_screen = func.create_objective_response_screen(
                                        text_height, text_color,
                                        text_pos, window)
                                        
pd_stim = func.create_photodiode_stimulus(window)                                        


#==============================================================================
# PRESENT WELCOME AND INSTRUCTIONS SCREEN
#==============================================================================

func.present_instructions('welcome', ins_col, ins_pos, ins_height, ins_resp,
                          ins_wrap_width, ins_language, automatic_responding,
                          window)

func.present_instructions('welcome2', ins_col, ins_pos, ins_height, ins_resp,
                          ins_wrap_width, ins_language, automatic_responding,
                          window)


#==============================================================================
# PRACTICE LOOP
#==============================================================================

n_practice_trials = 18
func.pratice_run(n_practice_trials, ts_col, ts_pos, ts_height, ts_resp,
                 ts_font, fix, fix_nframes, fix_color, fix_pos, fix_height,
                 delay_nframes, target_jitter, target_color, target_pos,
                 target_height, target_font, mask_nframes, mask_nlines, 
                 mask_line_color, mask_line_width, mask_mu, mask_sigma,
                 o_resp_keys, text_height, text_color, text_pos, modality,
                 s_resp_keys, s_resp_names, box_positions_x, box_position_y,
                 box_height, box_width, box_color, number_color, number_height,
                 description_color, description_height, description_position_y,
                 show_answer_nframes, show_box_color, box_fill_color, window,
                 even_digits, odd_digits, font_files, combinations,
                 automatic_responding, subject, date, save_library, pd_check,
                 seed_n)


func.present_instructions('welcome3', ins_col, ins_pos, ins_height, ins_resp,
                          ins_wrap_width, ins_language, automatic_responding,
                          window)

#==============================================================================
# TRIAL LOOP
#==============================================================================
ntrials = exp_info['ntrials']
nblocks = exp_info['nblocks']
nblock = 1
trial_type = 'experiment'
for ntrial in xrange(ntrials):
    
    #==========================================================================
    # DETERMINE WHETHER A BREAK IS COMING UP         
    #==========================================================================
    
    if ntrial % (ntrials / nblocks) == 0 and ntrial != 0:
        func.present_breaks(nblock, nblocks, ins_col, ins_pos, ins_height,
                            ins_resp, ins_wrap_width, ins_language,
                            automatic_responding, window)
        nblock += 1                                  
    
    #==========================================================================
    # CONTROLLING BALANCING OF PARAMETERS         
    #==========================================================================

    parameter_dicts = func.balance_and_randomize(parameter_dicts,
                                                 task_counters, blocked_design,
                                                 repeat_n_times, ntrial,
                                                 task_settings)
                                              
    #==========================================================================
    # CHOOSE THE STIMULUS OF THIS TRIAL
    #==========================================================================
    trial_parameters_dicts = func.set_parameters_for_all_tasks(parameter_dicts,
                                                               task_counters)
    target_type, target_nframes, even_digit, odd_digit, task, \
        current_combination = \
        func.set_parameters_for_trial(trial_parameters_dicts, combinations)
    task_counters = func.count_trials_per_task(task, task_counters)
    task_setting_stim = func.create_task_setting_stimulus(task, combinations,
                                                          current_combination,
                                                          ts_col, ts_pos,
                                                          ts_height, ts_font,
                                                          window)

    target_stimulus, jitter_x, jitter_y = \
                func.choose_target_stimulus(target_type,
                                            even_digit, odd_digit,
                                            even_digits, odd_digits,
                                            even_stimuli, odd_stimuli,
                                            target_jitter)
    
    mask_stimulus = func.create_mask_stimulus(mask_nlines, mask_line_color,
                                              mask_mu, mask_sigma,
                                              mask_line_width,
                                              window)
                                     
    
    #==========================================================================
    # PRESENTATION PROCEDURE
    #==========================================================================
    time = data.getDateStr()
    func.warn_if_cue_changes(current_combination, cue_last_trial, task,
                             task_last_trial, ntrial)
    func.present_task_setting_stimulus(task_setting_stim, ts_resp, window,
                                       automatic_responding)
    func.present_fixation_stimulus(fix_stim, fix_nframes, window)
    func.present_delay(delay_nframes, window)
    func.present_target_stimulus(target_stimulus, target_nframes, pd_check,
                                 pd_stim, window)
    func.present_mask_stimulus(mask_stimulus, mask_nframes, window)
    func.present_objective_response_screen(objective_response_screen, window)
    objective_response, rt_objective = func.get_objective_response(o_resp_keys,
                                                          automatic_responding)
    func.present_subjective_response_screen(response_prompt, modality,
                                            window)
    subjective_response, rt_subjective = func.get_subjective_response(
                                                        s_resp_keys,
                                                        automatic_responding)
    func.show_subjective_response(response_prompt,
                                  show_answer_nframes, subjective_response,
                                  box_positions_x, box_position_y, box_height,
                                  box_width, show_box_color, box_fill_color,
                                  number_color, number_height, modality, window
                                  )
                                      
                                  
    #==========================================================================
    # WRITE DATA TO CSV FILE                              
    #==========================================================================                          
    data_dict = {'subject': subject, 'date': time,
                 'obj.resp': objective_response,
                 'rt.obj': rt_objective, 'pas': subjective_response,
                 'rt.subj': rt_subjective, 'target.type': target_type,
                 'target.frames': target_nframes, 'task': task,
                 'trial': ntrial,
                 'even.digit': even_digit,
                 'odd.digit': odd_digit, 'target.contrast': target_color[0],
                 'jitter.x': jitter_x, 'jitter.y': jitter_y,
                 'cue': current_combination, 'trial.type': trial_type,
                 'seed': seed_n}
    filename = save_library + subject + '_' + date + '.csv'    
    func.write_data_to_csv(data_dict, filename)

    #==========================================================================
    #  STORE INFORMATION FROM THIS TRIAL TO THE NEXT TRIAL
    #==========================================================================
    
    cue_last_trial = current_combination
    task_last_trial = task

#==============================================================================
# TRIAL LOOP FINISHES
#==============================================================================
func.present_instructions('thank_you', ins_col, ins_pos, ins_height, ins_resp,
                          ins_wrap_width, ins_language, automatic_responding,
                          window)
                          
window.close()                          