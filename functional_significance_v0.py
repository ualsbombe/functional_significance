#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 13:29:45 2020

@author: lau
v0 relies on the QUEST staircase - since it works with continuous values which
are not possible with the current generator, we go to an up/down staircase in v1
"""


#%% IMPORTS AND SET-UP
from subprocess import check_output
from random import uniform, randint, shuffle
from psychopy.clock import getTime, CountdownTimer
from psychopy import visual, misc, core, gui, event, data
from datetime import datetime
from os.path import join, exists
from os import listdir
import numpy as np
import csv
import serial
from math import modf

user = check_output('uname -n', shell=True)
if user == b'lau\n': ## find name of meg stim computer
    print('triggers.py not imported')
    send_triggers = False
    device_path = '/dev'
    run_detection = True
else:
    from triggers import setParallelData ## only works at Skejby
    send_triggers = True
    device_path = '' ## FIXME
    run_detection = False
    
## FIXME
## FIND ROBERT'S COMMENT REMOVING THE LOCAL/NORMAL PROBLEM

# helper functions

def decimal_ceil(a, precision=0):
    return np.round(a + 0.5 * 10**(-precision), precision)

def decimal_floor(a, precision=0):
    return np.round(a - 0.5 * 10**(-precision), precision)

#%% GUI FOR PARAMETERS

parameter_file = 'staircase_parameters.pickle'

try:
    experiment_info = misc.fromFile(parameter_file)
except:
    experiment_info = dict(subject='0001',test_fast=False)

## add current_time
now = datetime.now()
datetime_string = now.strftime("%Y_%m_%d_%H%M%S")
experiment_info['datetime'] = datetime_string

dialogue = gui.DlgFromDict(experiment_info, fixed=['datetime'])    
if dialogue.OK:
    misc.toFile(parameter_file, experiment_info)
else:
    core.quit()
    
#%% IN- AND OUTPUT FILES

subject = experiment_info['subject']

practice_filename  = join('.', 'data', subject + '_' + datetime_string + \
                          '_practice.csv')
staircase_filename = join('.', 'data', subject + '_' + datetime_string + \
                          '_staircase.csv')
data_filename      = join('.', 'data', subject + '_' + datetime_string + \
                          '_data.csv')
detection_filename = join('.', 'data', subject + '_' + datetime_string + \
                           '_detection.csv.')                          
code_filename      = join('.', 'intensity_codes.csv')

#%% CREATE WINDOW AND VISUAL STIMULI

window = visual.Window((2400, 1300), monitor='testMonitor', units='norm')

fixation = visual.TextStim(window, '+', pos=(0,0))
response_text = visual.TextStim(window, 'Did you perceive a touch?\n' + \
                                        'Press left for yes\n' + \
                                        'Press right for no', pos=(0.5, 0.0))

#%% EXPERIMENT PARAMETERS

## initialized empty

former_jitter_ISI = None

## fixed value parameters
ISI  = 1.487 ## s
if experiment_info['test_fast']:
    ISI /= 1e3
jitter_beginning_trial = 3 ## trial when jitter is introduced
condition_list = [('weak', 0.00), ('omission', 0.00),
                  ('weak', 0.15), ('omission', 0.15)] ## conditions
n_condition_repetition = 2
n_target_trials = 150 ## number of target trial per condition
target_trial = 6 ## trial where target is presented
n_breaks = 6 ## number of breaks during experiment

## trigger related (binaries)
stim_trigger_value = 2**0 ## current generator
position_trigger_values = (2**1, 2**2, 2**3)
jitter_trigger_value = 2**4
weak_target_trigger_value = 2**5
omission_trigger_value = 2**6
trigger_duration = 0.010 ## s

## staircase related
starting_ampere = 5.0 # mA
staircase = data.QuestHandler(startVal=starting_ampere, startValSd=4,
                              pThreshold=2/3, nTrials=12,
                              gamma=0.01)

## combination variables
n_omissions = n_target_trials // 2
n_weak_targets = n_target_trials // 2
condition_list_experiment = condition_list.copy() * n_condition_repetition
n_trials_sequence = target_trial + 1
n_jitter_conditions = len(condition_list) 
n_sequences = n_omissions * n_jitter_conditions
break_interval = n_sequences // n_breaks
jitter_trial = target_trial - jitter_beginning_trial

## counters
break_counter = 0 ## counting the number of breaks
countdown_timer = CountdownTimer()

#%% FUNCTIONS

def check_for_break(n_sequence, n_sequences, n_breaks, break_counter):
    
    experiment_progress = n_sequence // (n_sequences // (n_breaks + 1))
    if experiment_progress > break_counter:
        print('Break number: ' + str(break_counter + 1) + ' out of ' + \
              str(n_breaks) + ' breaks.\nCheck with subject before ' + \
              'returning.\n(Press "return" to carry on)')
        input()
        break_counter += 1
    return break_counter
    
def apply_jitter(jitter_proportion, ISI):
    
    if jitter_proportion == 0:
        jitter_ISI = ISI
    else:
        this_proportion = uniform(0, jitter_proportion)
        if randint(0, 1):
            this_proportion *= -1
        jitter_ISI = ISI * (1 + this_proportion)
    return jitter_ISI

def counterbalance_target_trials(condition_list_experiment, n_sequence):
    
    modulus = n_sequence % len(condition_list_experiment)
    if modulus == 0:
        shuffle(condition_list_experiment)
    target_type, jitter_proportion = condition_list_experiment[modulus]
    
    return condition_list_experiment, target_type, jitter_proportion

def get_former_jitter_ISI(trial_type, jitter_ISI):
    
    if trial_type == 'jittered' or trial_type == 'weak' or \
        trial_type == 'omission':
        former_jitter_ISI = jitter_ISI
    elif trial_type == 'regular':
        former_jitter_ISI = None
        
    return former_jitter_ISI
                  
def correct_ISI(former_jitter_ISI, ISI, countdown_timer):
    
    if former_jitter_ISI < ISI:
        to_correct = ISI - former_jitter_ISI
        countdown_timer.reset(to_correct) ## wait till to_correct s has passed
        while countdown_timer.getTime() > 0: 
            pass
        print(str(round(to_correct, 4)) + ' seconds were corrected')
        difference = None
    else:
        difference = former_jitter_ISI - ISI
        
    return difference

def get_trial_type(n_trial, jitter_beginning_trial, target_trial,
                   target_type, former_jitter_ISI, ISI, countdown_timer):
    
    difference = None ## resetting
    if n_trial == 0:
        trial_type = 'regular'
        former_trial_type = 'target'
    elif n_trial > 0 and n_trial < jitter_beginning_trial:
        trial_type = 'regular'
        former_trial_type = 'regular'
    elif n_trial == jitter_beginning_trial:
        trial_type = 'jittered'
        former_trial_type = 'regular'
    elif n_trial > jitter_beginning_trial and n_trial < target_trial:
        trial_type = 'jittered'
        former_trial_type = 'jittered'
        difference = correct_ISI(former_jitter_ISI, ISI, countdown_timer)
    elif n_trial == target_trial:
        trial_type = target_type
        former_trial_type = 'jittered'
        difference = correct_ISI(former_jitter_ISI, ISI, countdown_timer)
    
    return trial_type, former_trial_type, difference

def get_position_trigger_value(position_trigger_values, n_trial,
                               n_trials_sequence):
    
    modulus = n_trial % ((n_trials_sequence - 1) // 2)
    position_trigger_value = position_trigger_values[modulus]
    
    return position_trigger_value

def get_trigger_value(stim_trigger_value, position_trigger_value,
                      jitter_trigger_value, weak_target_trigger_value,
                      omission_trigger_value, trial_type):
    
    if trial_type == 'regular':
        trigger_value = stim_trigger_value + position_trigger_value
    elif trial_type == 'jittered':
        trigger_value = stim_trigger_value + position_trigger_value + \
                        jitter_trigger_value
    elif trial_type == 'weak':
        trigger_value = stim_trigger_value + weak_target_trigger_value + \
                        jitter_trigger_value
    elif trial_type == 'omission':
        trigger_value = omission_trigger_value + jitter_trigger_value
        
    return trigger_value

def get_trial_ISI(trial_type, former_trial_type, ISI, jitter_ISI, difference):
    
    if trial_type == 'regular':
        this_ISI = ISI
    elif trial_type == 'jittered' and former_trial_type == 'regular':
        this_ISI = jitter_ISI
    elif trial_type == 'jittered' and former_trial_type == 'jittered':
        if difference is None:
            this_ISI = jitter_ISI
        else:
            this_ISI = jitter_ISI - difference
    elif trial_type == 'weak' or trial_type == 'omission':
        if difference is None:
            this_ISI = ISI
        else:
            this_ISI = ISI - difference
            
    return this_ISI

def trigger_current_generator(trigger_value, trigger_duration, ISI,
                              countdown_timer, begin_time, send_triggers,
                              print_time=True,
                              print_trigger=True):
    if print_time:
        begin_trial = getTime()
    if print_trigger:
        print(trigger_value)
        
    ## send triggers precisely
    countdown_timer.reset(ISI) ## wait ISI
    while countdown_timer.getTime() > 0:
        pass
    if send_triggers: ## raise trigger
        setParallelData(trigger_value)
    countdown_timer.reset(trigger_duration) ## wait trigger duration
    while countdown_timer.getTime() > 0:
        pass
    if send_triggers: ## lower trigger
        setParallelData(0)
    
    if print_time:
        print(str(round(getTime() - begin_trial, 4)) + ' seconds elapsed')
    new_time = getTime() - begin_time
    
    return new_time

def present_response_options(window, stimulus): ## visual or auditory
    ##FIXME resopnse triggers
    stimulus.draw()
    window.flip()
    this_response = None
    while this_response is None:
        all_keys = event.waitKeys()
        for this_key in all_keys:
            if this_key == 'z':
                this_response = 'yes'
            elif this_key == 'm':
                this_response = 'no'
            elif this_key == 'q':
                window.close()
                core.quit()
        event.clearEvents('mouse')
    window.flip()
    
    return this_response
        
def present_feedback(): ## should we do this - maybe during practice
    pass

def get_intensity_codes(code_filename):
    code_dict = dict()
    with open(code_filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader, None)
        for line in csv_reader:
            code = line[0].encode()
            intensity = round(float(line[1].replace(',', '.')), 1)
            code_dict[str(intensity)] = code
    return code_dict

def find_serial_device(device_path):
    devices = listdir(device_path)
    for device in devices:
        if 'ttyUSB' in device:
            address = join(device_path, device)
            return address
    address = None
    return address
    

def set_inital_generator_values(port_address, starting_ampere, intensity_codes):
    if port_address is not None:
        duration_code = b'?L,10$D9#' ## 100 ??s
        trigger_delay_code = b'?D,1$A0#' ## 0 ??s
        
        port = serial.Serial(port=port_address, baudrate=38400, timeout=1)
        port.write(duration_code)    
        port.write(trigger_delay_code)

        for intensity in range(1, int(starting_ampere + 1)):
            if intensity > 8: ## you can only dial up 8 steps at a time
                port.close()
                port.open()
            this_insensity_string = str(float(intensity))
            this_intensity = intensity_codes[this_insensity_string]
            port.write(this_intensity)

        port.readline()
        port.close()

        return port
    else:
        print('Ports not opened')

def write_staircase_csv(filename, this_current, this_increment, this_response):
    if not exists(filename):
        csv_file = open(filename, mode='w')
        csv_file.writelines('current,current_staircase,response,\n')
        csv_file.close()

    csv_file = open(filename, mode='a')
    csv_file.writelines(str(this_current) + ',' + str(this_increment) + ',' + \
                        this_response + ',\n')
    csv_file.close()       

def staircase_intensity(port, staircase, intensity_codes, port_address,
                        ISI, window, response_text, staircase_filename):

    for this_increment_index, this_increment in enumerate(staircase):
        if this_increment_index == 0:
            rounded_increment = round(this_increment, 1)
        else:
            if staircase_response:
                # make it harder
                rounded_increment = decimal_floor(this_increment, precision=1) 
            else:
                # make it easier
                rounded_increment = decimal_ceil(this_increment, precision=1)
        print(this_increment)
        print(rounded_increment)
        intensity_code = intensity_codes[str(rounded_increment)]
        if port_address is not None:
            port.open()
            # port.write(b'?*R$52#') # standby
            # port.write(b'?*W$57#') # wakeup
            port.write(intensity_code)
            port.write(b'?*A,S$C0#') # pulse
            port.readline()
            port.close()
            
        this_response = present_response_options(window, response_text)
        if this_response == 'yes':
            staircase_response = 1
        elif this_response == 'no':
            staircase_response = 0
        print(staircase_response)
        staircase.addResponse(staircase_response)
        write_staircase_csv(staircase_filename, rounded_increment,
                            this_increment, this_response)

        ## wait an ISI
        countdown_timer.reset(ISI)
        while countdown_timer.getTime() > 0:
            pass
            
    return staircase

def write_data_csv(filename, this_trigger_value, this_response, sequence_time,
                   experiment_time):
    if not exists(filename):
        csv_file = open(filename, mode='w')
        csv_file.writelines('trigger,response,trial_time,experiment_time,\n')
        csv_file.close()
        
    csv_file = open(filename, mode='a')
    csv_file.writelines(str(this_trigger_value) + ',' + this_response + ',' + \
                        str(sequence_time) + ',' + str(experiment_time) + \
                            ',\n')
    csv_file.close()

def write_detection_csv(filename, current, this_trial_type, this_response):
    if not exists(filename):
        csv_file = open(filename, mode='w')
        csv_file.writelines('current,trial_type,response,\n') 
        csv_file.close()

    csv_file = open(filename, mode='a')
    csv_file.writelines(str(current) + ',' + this_trial_type + ',' + \
                        this_response + ',\n')
    csv_file.close()

def run_detection_session(filename, current, intensity_codes, port_address,
                          n_trials, staircase_filename):
    if current == 'staircased_value':
        with open(staircase_filename, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                pass
        current = float(row[0])


    if port_address is not None:
        max_int = int(modf(current)[1])
        for intensity in range(1, max_int + 1):
            frac = round(modf(current)[0], 1)
            intensity_code = intensity_codes[str(intensity + frac)]
            port.open()
            port.write(intensity_code)
            port.readline()
            port.close()
    else:
        return

    trial_types = ['weak', 'weak', 'omission', 'omission']

    for trial_index in range(n_trials):

        modulus = trial_index % len(trial_types)
        if modulus == 0:
            shuffle(trial_types)
        this_trial_type = trial_types[modulus]

        if this_trial_type == 'weak':
            port.open()
            port.write(b'?*A,S$C0#') # pulse
            port.readline()
            port.close()
        elif this_trial_type == 'omission':
            port.open()
            port.write(b'')
            port.readline()
            port.close()

        this_response = present_response_options(window, response_text)
        countdown_timer.reset(ISI)
        while countdown_timer.getTime() > 0:
            pass

        write_detection_csv(filename, current, this_trial_type, this_response)

#%% PRACTICE SESSION

#%% STAIRCASE SESSION

port_address = find_serial_device(device_path)
intensity_codes = get_intensity_codes(code_filename)
port = set_inital_generator_values(port_address, starting_ampere,
                                   intensity_codes)
staircase = staircase_intensity(port, staircase, intensity_codes, port_address,
                                ISI, window, response_text, staircase_filename)

#%% DETECTION SESSION

run_detection_session(detection_filename, 'staircased_value', intensity_codes,
                      port_address, n_trials=20,
                      staircase_filename=staircase_filename)

#%% EXPERIMENT SESSION
# should this be run with a single intensity, or adapt throughout?

experiment_begin_time = getTime()

for n_sequence in range(n_sequences):
    print('This is sequence: ' + str(n_sequence + 1) + ' out of: ' + \
          str(n_sequences) + ' sequences.\n')
    sequence_begin_time = getTime()
    
    ## find target and jitter for sequence
    condition_list_experiment, target_type, jitter_proportion = \
        counterbalance_target_trials((condition_list_experiment), n_sequence)
    print('Target is: ' + target_type + ' and jitter is: ' + \
          str(jitter_proportion) + '\n')
        
    ## loop through trials of sequence
    for n_trial in range(n_trials_sequence):
        print('This is trial: ' + str(n_trial + 1) + ' out of: ' + \
              str(n_trials_sequence) + ' trials.')
        ## get trial type
        trial_type, former_trial_type, difference = \
            get_trial_type(n_trial, jitter_beginning_trial, target_trial,
                           target_type, former_jitter_ISI, ISI,
                           countdown_timer)
        print(trial_type)
        ## apply jitter
        jitter_ISI = apply_jitter(jitter_proportion, ISI)
        # print(jitter_ISI)
        ## get trigger value
        position_trigger_value = \
            get_position_trigger_value(position_trigger_values, n_trial,
                                       n_trials_sequence)
        trigger_value = get_trigger_value(stim_trigger_value,
                                          position_trigger_value,
                                          jitter_trigger_value,
                                          weak_target_trigger_value,
                                          omission_trigger_value, trial_type)
        ## get ISI
        this_ISI = get_trial_ISI(trial_type, former_trial_type, ISI,
                                  jitter_ISI, difference)
        ## trigger current generator and get timing
        sequence_time = trigger_current_generator(trigger_value,
                                                  trigger_duration, this_ISI,
                                                  countdown_timer,
                                                  sequence_begin_time,
                                                  send_triggers)
        experiment_time = getTime() - experiment_begin_time
        
        ## has to be last in trial loop
        if (n_trial + 1) == n_trials_sequence:
            this_response = present_response_options(window, response_text)
        else:
            this_response = 'None'
        write_data_csv(data_filename, trigger_value, this_response,
                       sequence_time, experiment_time)
        print('\n')
        former_jitter_ISI = get_former_jitter_ISI(trial_type, jitter_ISI)