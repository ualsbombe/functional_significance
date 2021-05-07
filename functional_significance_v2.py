#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 13:29:45 2020

@author: lau
v0 relies on the QUEST staircase - since it works with continuous values which
are not possible with the current generator, we go to an up/down staircase in
v1
we also add the idea from Robert where the last stimulus appears "on time" to
not have to deal with the issue of "local timelocking". The trial_type
"last jittered" has been added
v2 relies on the Psi staircase after talking with Niia and Nicolas - a 2AFC
staircase is used for the staircasing part. A tutorial is also added
"""

#%% IMPORTS AND SET-UP
from subprocess import check_output
from random import uniform, randint, shuffle
from psychopy.clock import getTime, CountdownTimer, MonotonicClock
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
    window_size = (2400, 1300)
    fullscr = False
elif user == b'stimpc-08\n':
    from triggers import setParallelData ## only works at Skejby
    send_triggers = True
    device_path = '/dev'
    window_size = (1920, 1080)
    fullscr = True
else:
    raise NameError('The current user: ' + str(user) + \
                    ' has not been prepared')
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
    experiment_info = dict(subject='0001', test_fast=False, run_staircase=True,
                           run_detection=False, auto_respond=False,
                           target_current='staircased_value',
                           performance_target=0.85, language='danish',
                           present_feedback=True)

## add current_time
now = datetime.now()
datetime_string = now.strftime("%Y_%m_%d_%H%M%S")
experiment_info['datetime'] = datetime_string

dialogue = gui.DlgFromDict(experiment_info, fixed=['datetime'])
if dialogue.OK:
    misc.toFile(parameter_file, experiment_info)
else:
    core.quit()

#%% STAIRCASE

## Psi staircase

staircase = data.PsiHandler(nTrials=40,
                            intensRange=[1.0, 10.0],
                            alphaRange=[1.0, 10.0],
                            betaRange=[0.1, 1],
                            intensPrecision=0.1,
                            alphaPrecision=0.1,
                            betaPrecision=0.1,
                            delta=0.02)

#%% IN- AND OUTPUT FILES

subject = experiment_info['subject']

practice_filename  = join('..', 'data', subject + '_' + datetime_string + \
                          '_practice.csv')
staircase_filename = join('..', 'data', subject + '_' + datetime_string + \
                          '_staircase.csv')
data_filename      = join('..', 'data', subject + '_' + datetime_string + \
                          '_data.csv')
detection_filename = join('..', 'data', subject + '_' + datetime_string + \
                           '_detection.csv')
code_filename      = join('..', 'intensity_codes.csv')

#%% ENGLISH AND DANISH TEXTS

text_dict = dict()
text_dict['staircase_response'] = dict()
text_dict['detection_response'] = dict()
text_dict['experiment_response'] = dict()
text_dict['staircase_instructions'] = dict()
text_dict['detection_instructions'] = dict()
text_dict['experiment_instructions'] = dict()
text_dict['experiment_thank_you'] = dict()

english_texts = [
                'When did you receive an electric shock?\n' + \
                'Left: First time\n' + \
                'Right: Second time',

                'Did you receive an electric shock?\n' + \
                'Left: Yes\n' + \
                'Right: No',

                'Did you receive an electric shock?\n' + \
                'Left: Yes\n' + \
                'Right: No',

                'The staircase session is about to begin:\n\n' + \
                'Press a button to continue!',

                'The detection session is about to begin:\n\n' + \
                'Press a button to continue!',

                'The experiment session is about to begin:\n\n' + \
                'Press a button to continue!',

                'Thank you for participating in this experiment!' + \
                '\n\nPlease wait!\n'  + \
                'The experimenter will get you out shortly.'
                ]

danish_texts  = [
                'Hvornår fik du stød?\n' + \
                'Venstre: Første gang\n' + \
                'Højre: Anden gang',

                'Fik du stød?\n' + \
                'Venstre: Ja\n' + \
                'Højre: Nej',

                'Fik du stød?\n' + \
                'Venstre: Ja\n' + \
                'Højre: Nej',

                'Nu påbegyndes kalibreringssessionen:\n\n' + \
                'Tryk på en knap for at fortsætte!',

                'Nu påbegyndes detektionssessionen:\n\n' + \
                'Tryk på en knap for at fortsætte!',

                'Nu påbegyndes selve eksperimentet:\n\n' + \
                'Tryk på en knap for at fortsætte!',

                'Tak for din deltagelse!' + \
                '\n\nLig stille et øjeblik endnu\n'  + \
                'Den forsøgsansvarlige henter dig ganske straks.'
                ]
for text_index, text in enumerate(text_dict):
    text_dict[text]['danish'] = danish_texts[text_index]
    text_dict[text]['english'] = english_texts[text_index]


# break text is handled in check_for_break

#%% CREATE WINDOW AND VISUAL STIMULI

window = visual.Window(window_size, monitor='testMonitor', units='norm',
                       fullscr=fullscr)

fixation = visual.TextStim(window, '+', pos=(0.0, 0.0))
staircase_indicator_text = visual.TextStim(window, '', pos=(0.0, 0.0))

instructions_text = visual.TextStim(window, '', pos=(0.0, 0.0))

#%% EXPERIMENT PARAMETERS

## initialized empty

former_jitter_ISI = None

## fixed value parameters
ISI  = 1.487 ## s
# time_before_response = 1.000 ## s
if experiment_info['test_fast']:
    ISI /= 1e3
jitter_beginning_trial = 3 ## trial when jitter is introduced
condition_list = [('weak', 0.00), ('omission', 0.00),
                  ('weak', 0.15), ('omission', 0.15)] ## conditions
n_condition_repetition = 1
n_target_trials = 150 ## number of target trials per condition
target_trial = 6 ## trial where target is presented
non_target_current_factor = 2.0 ## multiply staircased current for non-targets
n_breaks = 11 ## number of breaks during experiment
response_table = dict(hit=0, miss=0, false_alarm=0, correct_rejection=0,
                      correct=0, incorrect=0)

## trigger related (binaries)
stim_trigger_value = 2**0 ## current generator
position_trigger_values = (2**1, 2**2, 2**3)
jitter_trigger_values = (2**4, 2**5)
weak_target_trigger_value = 2**6
omission_trigger_value = 2**7
trigger_duration = 0.010 ## s


## combination variables
n_omissions = n_target_trials // 2 # // integer division
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

def reset_response_table_counters(response_table, All=False):
    if All:
        response_table = dict(hit=0, miss=0, false_alarm=0, correct_rejection=0,
                      correct=0, incorrect=0)
    else:
        response_table['correct'] = 0
        response_table['incorrect'] = 0
        
    return response_table

def check_for_break(n_sequence, n_sequences, n_breaks, break_counter,
                    break_text, language, response_table, present_feedback):

    experiment_progress = (n_sequence) // (n_sequences // (n_breaks + 1))
    if experiment_progress > break_counter:

        accuracy = response_table['correct'] / \
            (response_table['correct'] + response_table['incorrect'])
        accuracy_string =  str(round(100 * accuracy)) + ' %'        


        if language == 'english':
            string = 'It is time for a short break\n' + \
                'This is break no.: ' + str(break_counter + 1) + ' out of ' + \
                    str(n_breaks) + ' breaks.'
            if present_feedback:
                string += '\n\nFeedback:\nYou got ' + accuracy_string + \
            ' correct during this session'
        elif language == 'danish':
            string = 'Nu holder vi en kort pause\n' + \
                'Dette er pause nummer: ' + \
                    str(break_counter + 1) + ' ud af ' + \
                    str(n_breaks) + ' pauser.'
            if present_feedback:
                string += '\n\nFeedback:\nDu svarede rigtigt ' + \
                    accuracy_string + ' af gangene.'
        break_text.setText(string)
        break_text.draw()
        window.flip()

        print('Break number: ' + str(break_counter + 1) + ' out of ' + \
              str(n_breaks) + ' breaks.\nCheck with subject before ' + \
              'returning.\n(Press "return" to carry on)')
        print(response_table)
        response_table = reset_response_table_counters(response_table)
        input()
        window.flip()
        break_counter += 1
    return break_counter, response_table

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
       trial_type == 'omission' or trial_type == 'last_jittered':
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
    elif n_trial > jitter_beginning_trial and (n_trial + 1) < target_trial:
        trial_type = 'jittered'
        former_trial_type = 'jittered'
        difference = correct_ISI(former_jitter_ISI, ISI, countdown_timer)
    elif n_trial > jitter_beginning_trial and (n_trial + 1) == target_trial:
        trial_type = 'last_jittered'
        former_trial_type = 'jittered'
        difference = correct_ISI(former_jitter_ISI, ISI, countdown_timer)
    elif n_trial == target_trial:
        trial_type = target_type
        former_trial_type = 'last_jittered'

    return trial_type, former_trial_type, difference

def get_position_trigger_value(position_trigger_values, n_trial,
                               n_trials_sequence):

    modulus = n_trial % ((n_trials_sequence - 1) // 2)
    position_trigger_value = position_trigger_values[modulus]

    return position_trigger_value

def get_trigger_value(stim_trigger_value, position_trigger_value,
                      jitter_trigger_values, weak_target_trigger_value,
                      omission_trigger_value, trial_type, jitter_proportion):

    if jitter_proportion < 0.075:
        jitter_trigger_value = jitter_trigger_values[0]
    else:
        jitter_trigger_value = jitter_trigger_values[1]

    if trial_type == 'regular':
        trigger_value = stim_trigger_value + position_trigger_value
    elif trial_type == 'jittered' or trial_type == 'last_jittered':
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
    elif trial_type == 'last_jittered' and former_trial_type == 'jittered':
        if difference is None:
            this_ISI = ISI
        else:
            this_ISI = ISI - difference
    elif trial_type == 'weak' or trial_type == 'omission':
        this_ISI = ISI

    return this_ISI

def get_staircased_current(staircase_filename):
    with open(staircase_filename, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            pass
    current = float(row[0])
    return current

def adjust_current_strength(target_current, non_target_current_factor,
                            trial_type, former_trial_type, port):

    non_target_current = round(target_current * non_target_current_factor, 1)
    if port is not None:
        integer_part_max_current = int(modf(non_target_current)[1])
        integer_part_min_current = int(modf(target_current)[1])
        # decimal_part_min_current = round(modf(target_current)[0], 1)
        decimal_part_max_current = round(modf(non_target_current)[0], 1)

        if not port.is_open:
            port.open()
        ## we need to dial up the current - max 1 mA per step
        if trial_type == 'regular' and former_trial_type == 'target':
            for intensity in range(integer_part_min_current,
                                    integer_part_max_current + 1):
                if intensity == integer_part_min_current:
                    intensity_code = intensity_codes[str(intensity + \
                                                  decimal_part_max_current)]
                else:
                    intensity_code = intensity_codes[str(intensity + \
                                                    decimal_part_max_current)]
                port.write(intensity_code)
        ## dialling down - can be done in one step
        elif trial_type == 'weak':
            intensity_code = intensity_codes[str(target_current)]
            port.write(intensity_code)
    if trial_type == 'weak': ## FIXME read off actual value instea
        return target_current
    elif trial_type == 'omission':
        return None
    else:
        return non_target_current

def trigger_current_generator(trigger_value, trigger_duration, ISI,
                              countdown_timer, begin_time, trial_type,
                              port, send_triggers, print_time=True,
                              print_trigger=True):
    if print_time:
        begin_trial = getTime()
    if print_trigger:
        print(trigger_value)

    ## send triggers precisely
    countdown_timer.reset(ISI) ## wait ISI
    while countdown_timer.getTime() > 0:
        pass
    ## send pulse serially
    if trial_type != 'omission':
        if port is not None:
            if not port.is_open:
                port.open()
            port.write(b'?*A,S$C0#') # send pulse
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


def present_response_options(window, stimulus, staircase=False, suppress=False):
    ##FIXME resopnse triggers
    this_response = None
    if experiment_info['auto_respond']:
        this_response = 'yes'
    stimulus.draw()
    window.flip()
    clock = MonotonicClock()
    while this_response is None:
        all_keys = event.waitKeys()
        for this_key in all_keys:
            if this_key == 'z' or this_key == '2':
                if staircase:
                    this_response = 'first'
                else:
                    this_response = 'yes'
            elif this_key == 'm' or this_key == '3':
                if staircase:
                    this_response = 'second'
                else:
                    this_response = 'no'
            elif this_key == 'q':
                window.close()
                core.quit()
        event.clearEvents('mouse')
    response_time = clock.getTime()
    window.flip()

    return this_response, response_time

def categorize_responses(response, trigger_value, response_table):
    if trigger_value == 144 or trigger_value == 160: ## omission
        if response == 'yes':
            categorization = 'false_alarm'
        elif response == 'no':
            categorization = 'correct_rejection'
    elif trigger_value == 81 or trigger_value == 97:
        if response == 'yes':
            categorization = 'hit'
        elif response == 'no':
            categorization = 'miss'
    response_table[categorization] += 1
    if categorization == 'correct_rejection' or categorization == 'hit':
        response_table['correct'] += 1
    elif categorization == 'false_alarm' or categorization == 'miss':
        response_table['incorrect'] += 1
    
    return response_table        
    
def present_instructions(window, text, text_dict, language):
    string = text_dict[language]
    text.setText(string)
    text.draw()
    window.flip()
    this_response = None
    if experiment_info['auto_respond']:
        this_response = 'yes'
    while this_response is None:
        all_keys = event.waitKeys()
        for this_key in all_keys:
            if this_key == 'z' or this_key == 'm' or \
               this_key == '2' or this_key == '3':
                this_response = 'continue'
            elif this_key == 'q':
                window.close()
                core.quit()
        event.clearEvents('mouse')
    window.flip()

def present_thank_you_screen(window, text, text_dict, language):
    string = text_dict[language]
    text.setText(string)
    text.draw()
    window.flip()
    this_response = None
    if experiment_info['auto_respond']:
        window.close()
        core.quit()
    while this_response is None:
        all_keys = event.waitKeys()
        for this_key in all_keys:
            if this_key == 'q':
                window.close()
                core.quit()
        event.clearEvents('mouse')
    window.flip()
        

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
            print('Found device at address: ' + address)
            return address
    address = None
    return address

def wait_ISI(ISI):
    ## wait an ISI
    countdown_timer.reset(ISI)
    while countdown_timer.getTime() > 0:
        pass

def set_inital_generator_values(port_address, starting_current,
                                intensity_codes):
    starting_current = np.round(float(starting_current), 1)
    if port_address is not None:
        duration_code = b'?L,10$D9#' ## 100 µs
        trigger_delay_code = b'?D,1$A0#' ## 0 µs
        intensity_1_code = b'?I,10$D6#' ## 1 mA (resetting)

        port = serial.Serial(port=port_address, baudrate=38400, timeout=1)
        port.write(duration_code)
        port.write(trigger_delay_code)
        port.write(intensity_1_code)

        this_range = np.linspace(1, starting_current,
                                 num=(starting_current - 1) *10 +1)
        # print(this_range)
        dial_counter = 0
        for intensity in this_range:
            this_insensity_string = str(float(np.round(intensity, 1)))
            this_intensity = intensity_codes[this_insensity_string]
            port.write(this_intensity)
            wait_ISI(0.006) # waiting is needed for dialling all the steps
            # print(this_insensity_string)
            dial_counter += 1
            if dial_counter > 7: ## you can only dial up 8 steps at a time
                port.close()
                port.open()
                dial_counter = 0


    else:
        print('Ports not opened')
        port = None
    return port

def write_staircase_csv(filename, this_increment, this_response, trial_number,
                        response_time):
    if not exists(filename):
        csv_file = open(filename, mode='w')
        csv_file.writelines('current,response,trial_number,response_time\n')
        csv_file.close()

    csv_file = open(filename, mode='a')
    csv_file.writelines(str(this_increment) + ',' + this_response + ',' + \
                        str(trial_number) + ',' + str(response_time) + ',\n')
    csv_file.close()

def update_current_in_staircase(port, port_address, intensity_codes,
                                new_current, former_current):
    if port_address is not None:
        if not port.is_open:
            port.open()

        if new_current > former_current:
            num = 10
            this_range = np.linspace(former_current, new_current, num)
        elif new_current < former_current:
            num = 10
            this_range = np.linspace(former_current, new_current, num)
        else:
            this_range = np.arange(new_current, new_current)
        print(this_range)

        for intensity in this_range:
            this_insensity_string = str(float(np.round(intensity, 1)))
            this_intensity = intensity_codes[this_insensity_string]
            wait_ISI(0.005)
            port.write(this_intensity)
        port.write(b'?*A,S$C0#') # pulse

def present_text(text, string, window):
    text.setText(string)
    text.draw()
    window.flip()

def staircase_intensity(staircase, intensity_codes, port_address,
                        ISI, window, response_text, staircase_filename,
                        text_dict, language):

    string = text_dict[language]
    response_text.setText(string)

    stimulus_positions = ['first', 'second']


    for new_current_index, new_current in enumerate(staircase):
        new_current = round(new_current, 1)

        if len(staircase.intensities) > 1:
            former_current = np.round(staircase.intensities[-2], 1)
        else:
            former_current = new_current
            port = set_inital_generator_values(port_address, new_current,
                                   intensity_codes)
        print('New current: ' + str(new_current) + ' mA')
        print('Former current: ' + str(former_current) + ' mA')

        stimulus_chooser = stimulus_positions[randint(0, 1)]

        wait_ISI(ISI)

        if stimulus_chooser == 'first':
            present_text(staircase_indicator_text, '1', window)
            update_current_in_staircase(port, port_address, intensity_codes,
                                        new_current, former_current)
            wait_ISI(ISI / 4)
            window.flip()
            wait_ISI(ISI / 4)
            present_text(staircase_indicator_text, '2', window)
        elif stimulus_chooser == 'second':
            present_text(staircase_indicator_text, '1', window)
            wait_ISI(ISI / 4)
            window.flip()
            wait_ISI(ISI / 4)
            present_text(staircase_indicator_text, '2', window)
            update_current_in_staircase(port, port_address, intensity_codes,
                                        new_current, former_current)

        wait_ISI(ISI)

        this_response, response_time = present_response_options(window,
                                                 response_text,
                                                 staircase=True)
        if this_response == 'first' and stimulus_chooser == 'first':
            staircase_response = 1
        elif this_response == 'second' and stimulus_chooser == 'second':
            staircase_response = 1
        else:
            staircase_response = 0
        print(staircase_response)
        staircase.addResponse(staircase_response)
        write_staircase_csv(staircase_filename, new_current, this_response,
                            new_current_index, this_response)

    return staircase

def write_data_csv(filename, this_trigger_value, this_current, this_response,
                   sequence_time, experiment_time, performance_target,
                   trial_number, sequence_number, block_number,
                   response_time):

    sequence_number = sequence_number - 25 * block_number

    if not exists(filename):
        csv_file = open(filename, mode='w')
        csv_file.writelines('trigger,current,response,trial_time,' + \
                            'experiment_time,performance_target,' + \
                            'trial_number,sequence_number,block_number,' + \
                            'response_time,\n')
        csv_file.close()

    csv_file = open(filename, mode='a')
    csv_file.writelines(str(this_trigger_value) + ',' + str(this_current) + \
                        ',' + this_response + ',' + \
                        str(sequence_time) + ',' + str(experiment_time) + \
                        ',' + str(performance_target) + ',' + \
                        str(trial_number) + ',' + str(sequence_number) + \
                        ',' + str(block_number) + ',' + str(response_time) + \
                        ',\n')
    csv_file.close()

def write_detection_csv(filename, current, this_trial_type, this_response,
                        performance_target, trial_number, response_time):
    if not exists(filename):
        csv_file = open(filename, mode='w')
        csv_file.writelines('current,trial_type,response,' + \
                            'performance_target,trial_number,response_time,\n')
        csv_file.close()

    csv_file = open(filename, mode='a')
    csv_file.writelines(str(current) + ',' + this_trial_type + ',' + \
                        this_response + ',' + str(performance_target) + \
                        ',' + str(trial_number) + ',' + str(response_time) + \
                        ',\n')
    csv_file.close()

## this function was written as an afterthought and is almost in isolation
## from the other functions FIXME: incorporate it into the rest of the script
def run_detection_session(filename, current, intensity_codes, port_address,
                          n_trials, staircase, experiment_info, text_dict,
                          response_text):

    language = experiment_info['language']
    string = text_dict[language]
    response_text.setText(string)

    countdown_timer.reset(ISI)
    while countdown_timer.getTime() > 0:
        pass
    if current == 'staircased_value':
        current = \
np.round(staircase.estimateThreshold(experiment_info['performance_target']), 1)


    port = set_inital_generator_values(port_address, current,
                                   intensity_codes)
    if port_address is not None:
        if not port.is_open:
            port.open()
        max_int = int(modf(current)[1])
        for intensity in range(1, max_int + 1):
            frac = round(modf(current)[0], 1)
            intensity_code = intensity_codes[str(intensity + frac)]
            port.write(intensity_code)

    else:
        return

    trial_types = ['weak', 'weak', 'omission', 'omission']

    for trial_index in range(n_trials):

        modulus = trial_index % len(trial_types)
        if modulus == 0:
            shuffle(trial_types)
        this_trial_type = trial_types[modulus]

        if this_trial_type == 'weak':
            port.write(b'?*A,S$C0#') # pulse
        elif this_trial_type == 'omission':
            pass

        this_response, response_time = \
            present_response_options(window, response_text)
        countdown_timer.reset(ISI)
        while countdown_timer.getTime() > 0:
            pass

        write_detection_csv(filename, current, this_trial_type, this_response,
                            experiment_info['performance_target'], trial_index,
                            response_time)

#%% PRACTICE SESSION

#%% STAIRCASE SESSION

port_address = find_serial_device(device_path)
intensity_codes = get_intensity_codes(code_filename)

if experiment_info['run_staircase']:
    present_instructions(window, instructions_text,
                        text_dict['staircase_instructions'],
                        experiment_info['language'])
    staircase = staircase_intensity(staircase, intensity_codes,
                                    port_address, ISI, window,
                                    instructions_text,
                                    staircase_filename,
                                    text_dict['staircase_response'],
                                    experiment_info['language'])

#%% DETECTION SESSION

if experiment_info['run_detection']:
    present_instructions(window, instructions_text,
                        text_dict['detection_instructions'],
                        experiment_info['language'])
    run_detection_session(detection_filename, 'staircased_value',
                        intensity_codes, port_address, n_trials=50,
                        staircase=staircase, experiment_info=experiment_info,
                        text_dict=text_dict['detection_response'],
                        response_text=instructions_text)

#%% EXPERIMENT SESSION
# should this be run with a single intensity, or adapt throughout?


if experiment_info['target_current'] == 'staircased_value':
    target_current = \
np.round(staircase.estimateThreshold(experiment_info['performance_target']), 1)
else:
    target_current = float(experiment_info['target_current'])
non_target_current = non_target_current_factor * target_current
port = set_inital_generator_values(port_address,
                non_target_current,
                intensity_codes)
present_instructions(window, instructions_text,
                    text_dict['experiment_instructions'],
                    experiment_info['language'])

experiment_begin_time = getTime()

for n_sequence in range(n_sequences):
    break_counter, response_table = \
                                    check_for_break(n_sequence, n_sequences,
                                    n_breaks,
                                    break_counter, instructions_text,
                                    experiment_info['language'],
                                    response_table,
                                    experiment_info['present_feedback'])
    fixation.draw()
    window.flip()
    countdown_timer.reset(0.250)
    while countdown_timer.getTime() > 0:
        pass
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
        print(former_trial_type)
        ## adjust current strength
        if (trial_type == 'regular' and former_trial_type == 'target') or \
            (trial_type == 'weak' or trial_type == 'omission'):
            this_current = adjust_current_strength(target_current,
                                                   non_target_current_factor,
                                                   trial_type,
                                                   former_trial_type, port)
        if trial_type != 'omission':
            print('The current applied was: ' + str(this_current) + ' mA')

        ## apply jitter
        jitter_ISI = apply_jitter(jitter_proportion, ISI)
        # print(jitter_ISI)
        ## get trigger value
        position_trigger_value = \
            get_position_trigger_value(position_trigger_values, n_trial,
                                       n_trials_sequence)
        trigger_value = get_trigger_value(stim_trigger_value,
                                          position_trigger_value,
                                          jitter_trigger_values,
                                          weak_target_trigger_value,
                                          omission_trigger_value, trial_type,
                                          jitter_proportion)
        ## get ISI
        this_ISI = get_trial_ISI(trial_type, former_trial_type, ISI,
                                  jitter_ISI, difference)
        ## trigger current generator and get timing
        sequence_time = trigger_current_generator(trigger_value,
                                                  trigger_duration, this_ISI,
                                                  countdown_timer,
                                                  sequence_begin_time,
                                                  trial_type, port,
                                                  send_triggers)
        experiment_time = getTime() - experiment_begin_time

        ## has to be last in trial loop
        if (n_trial + 1) == n_trials_sequence:
            instructions_text.setText(text_dict['experiment_response'][experiment_info['language']])
            this_response, response_time = \
                present_response_options(window, instructions_text,
                                        suppress=True)
            response_table = categorize_responses(this_response, trigger_value,
                                              response_table)
        else:
            this_response = 'None'
            response_time = 'None'

        write_data_csv(data_filename, trigger_value, this_current,
                       this_response,
                       sequence_time, experiment_time,
                       experiment_info['performance_target'],
                       n_trial, n_sequence, break_counter, response_time)
        print('\n')
        former_jitter_ISI = get_former_jitter_ISI(trial_type, jitter_ISI)

present_thank_you_screen(window, instructions_text,
                        text_dict['experiment_thank_you'],
                        experiment_info['language'])
