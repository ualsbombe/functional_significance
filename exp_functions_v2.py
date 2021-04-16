# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 15:25:06 2014

@author: lau
"""

from psychopy import visual, event, core, gui, misc, sound, data
import random
import itertools

#==============================================================================
# EXPERIMENT PARAMETERS AND EXPERIMENT DIALOGUE                             
#==============================================================================
def create_parameter_pickle_and_present_experiment_dialogue(pickle_name):
    try:
        exp_info = misc.fromFile(pickle_name)
    except:
        exp_info = {'subject': 'code_test', 'ntrials': 5, 'nblocks': 2,
                    'blocked_design': True, 'full_screen': False,
                    'repeat_n_times': 12, 'automatic_responding': False,
                    'pd_check': False, 'seed': None}
    
    experiment_dialogue = gui.DlgFromDict(exp_info)
    
    if experiment_dialogue.OK:
        misc.toFile(pickle_name, exp_info)
    else:
        core.quit()
    return exp_info
    
def set_seed(seed):
    if seed == 'None':
        seed = None
    if seed is None:
        seed_n = random.sample(range(100000), 1)[0]
    else:
        seed_n = seed
    random.seed(seed_n)
    return seed_n
    
    
#==============================================================================
# WELCOME AND INSTRUCTIONS
#==============================================================================

def present_instructions(filename, color, pos, height, response_key,
                         wrap_width, language, automatic_responding, window):
    path = './stimuli/' + filename + '_' + language + '.txt'
    text_file = open(path, 'r')
    text = text_file.readlines()
    text = ''.join(text)
    text_stim = visual.TextStim(window, text, pos=pos, color=color,
                                height=height, wrapWidth=wrap_width)
    text_stim.draw()
    window.flip()
    no_response = True
    while no_response:
        key_list = event.getKeys(response_key)
        if len(key_list) or automatic_responding:
            no_response = False
    event.clearEvents()
    
def present_breaks(nblock, nblocks, color, pos, height, response_key,
                   wrap_width, language, automatic_responding, window):
    if language == 'english':
        text = 'You have now finished ' + str(nblock) + ' out of ' +  \
                str(nblocks) + ' blocks.\n\nTake a short break before you ' + \
                'continue!\n\n' + 'Press "space" when ready to do so!'
    elif language == 'danish':
        text = u'Du har netop afsluttet blok ' + str(nblock) + u' ud af ' + \
                str(nblocks) + u' blokke.\n\nTag en kort pause, før du går ' +\
                u'videre!\n\nTryk på "mellemrum", når du er klar igen!'
    else:
        raise NameError('language is not supported')
    text_stim = visual.TextStim(window, text, pos=pos, color=color,
                                height=height, wrapWidth=wrap_width)
    text_stim.draw()
    window.flip()
    no_response = True
    while no_response:
        key_list = event.getKeys(response_key)
        if len(key_list) or automatic_responding:
            no_response = False
    event.clearEvents()                         
    
    
    
#==============================================================================
# CREATING PARAMETER LISTS
#==============================================================================

def create_digit_lists(even_digits, odd_digits, ndigits):
    combinations_list = [ [], [] ]
    combinations_even = itertools.combinations(even_digits, ndigits)
    combinations_odd = itertools.combinations(odd_digits, ndigits)    
    
    for combinations in zip(combinations_even, combinations_odd):
        combinations_list[0].append(combinations[0])
        combinations_list[1].append(combinations[1])
        
    pairings = []
    for even_combination in combinations_list[0]:
        for odd_combination in combinations_list[1]:
            pairings.append(even_combination + odd_combination)
            
    return pairings
#==============================================================================
# CONTROLLING BALANCING OF PARAMETERS         
#==============================================================================
    

    
def balance_and_randomize(parameter_dicts, task_counters, blocked_design,
                          repeat_n_times, ntrial, task_settings):
    for parameter_dict in zip(parameter_dicts.values(), \
                                parameter_dicts.keys()):

        for parameter_value in parameter_dict[0].values():
            index = parameter_dict[0].values().index(parameter_value)
            for task_counter_key in task_counters.keys():
                key = parameter_dict[0].keys()[index]
                ## initial shuffling of combination
                if ntrial == 0 and key == 'combination' and \
                parameter_dict[1] == task_counter_key:
                    random.shuffle(parameter_value)
   
                ## reshuffle lists when they run out and initially

                if task_counters[task_counter_key] % \
                len(parameter_value) == 0 and parameter_dict[1] == \
                task_counter_key:
                    
                    last_value = parameter_value[-1]
                    ## not for combinations during blocked design though
                    if key == 'combination' and blocked_design:
                        pass
                    ## reset to original length
                    elif key == 'task' and blocked_design and \
                    parameter_dict[1] == 'task':
                        parameter_value = list(task_settings)
                        random.shuffle(parameter_value)
                        ## make sure that for blocked design that the same task
                        ## doesn't appear twice in a row
                        while last_value == parameter_value[0] and \
                        parameter_dict[1] == 'task':
                            random.shuffle(parameter_value)
                        parameter_dict[0][key] = list(parameter_value)

                        ## make repeats for task
                        if repeat_n_times > 1 and parameter_dict[1] == 'task':
                            parameter_value_copy = list(parameter_value)
        
                            for n in parameter_value_copy:
                                n_index = parameter_value_copy.index(n)
        
                                for m in xrange(repeat_n_times - 1):
                                    index_and_value = n_index * \
                                                            repeat_n_times
        
                                    parameter_value.insert(
                                        index_and_value,
                                        parameter_value[index_and_value])
                            
                            parameter_dict[0][key] = list(parameter_value)
                            
                            
                    elif key == 'target_nframes' and parameter_dict[1] == \
                    task_counter_key :
                        random.shuffle(parameter_value)
                        parameter_dict[0][key] = list(parameter_value)

                    elif key == 'target_types':
                        random.shuffle(parameter_value)
                        parameter_dict[0][key] = list(parameter_value)

                    
                ## make repeats for combinations 
                if key == 'combination' and blocked_design and \
                repeat_n_times > 1 and ntrial < 1 and \
                parameter_dict[1] == task_counter_key:
                    
                    parameter_value_copy = list(parameter_value)

                    for n in parameter_value_copy:
                        n_index = parameter_value_copy.index(n)

                        for m in xrange(repeat_n_times - 1):
                            index_and_value = n_index * \
                                                    repeat_n_times

                            parameter_value.insert(
                                index_and_value,
                                parameter_value[index_and_value])
              
                parameter_dict[0][key] = list(parameter_value)

    return parameter_dicts    
    
def create_photodiode_stimulus(window):
    stim = visual.Circle(window, 4, pos=(-20, 15), fillColor='white')
    return stim
    
#==============================================================================
# CHOOSE THE STIMULUS OF THIS TRIAL
#==============================================================================    

def set_parameters_for_all_tasks(parameter_dicts, task_counters):
    trial_parameter_dicts = parameter_dicts.copy()
    for trial_parameter_key in trial_parameter_dicts.keys():
        trial_parameter_dict = parameter_dicts[trial_parameter_key].copy()
        for trial_parameter_value in trial_parameter_dict.values():
            counter_index = trial_parameter_dict.values(). \
                                    index(trial_parameter_value)
            trial_parameter_index = task_counters[trial_parameter_key] % \
                                                    len(trial_parameter_value)
            key = trial_parameter_dict.keys()[counter_index]
            current_trial_parameter = trial_parameter_value \
                                        [trial_parameter_index]
            trial_parameter_dict[key] = current_trial_parameter
            trial_parameter_dicts[trial_parameter_key] = \
                                                    trial_parameter_dict
    return trial_parameter_dicts

def set_parameters_for_trial(trial_parameter_dicts, combinations):
    task = trial_parameter_dicts['task']['task']    
    trial_parameter_dict = trial_parameter_dicts[task]
    target_type = trial_parameter_dict['target_types']
    target_nframes = trial_parameter_dict['target_nframes']
    combination = trial_parameter_dict['combination']
    if task == 'quadruplet':
        even_digits = combinations[3][combination][:4]
        odd_digits = combinations[3][combination][4:]
    elif task == 'pairs':
        even_digits = combinations[1][combination][:2]
        odd_digits = combinations[1][combination][2:]
    elif task == 'singles':
        even_digits = combinations[0][combination][:1]
        odd_digits = combinations[0][combination][1:]
    else:
        raise NameError('det hele er noget lort')
    even_digit = random.sample(even_digits, 1)[0]   
    odd_digit = random.sample(odd_digits, 1)[0]
        
    return target_type, target_nframes, even_digit, odd_digit, task, \
            combination

def count_trials_per_task(task, task_counters):
    task_counters['task'] += 1    
    if task == 'quadruplet':
        task_counters['quadruplet'] += 1
    if task == 'pairs':
        task_counters['pairs'] += 1
    if task == 'singles':
        task_counters['singles'] += 1
    return task_counters     
    
#==============================================================================
# TASK SETTINGS
#==============================================================================
def create_task_setting_stimulus(task, combinations, current_combination,
                                 color, pos, height, font, window):

    if task == 'quadruplet':
        string = str(combinations[3][current_combination])    
        text = string[1] + string[4] + string[7] + string[10] + ' : ' + \
               string[13] + string[16] + string[19] + string[22]
    elif task == 'pairs':
        string = str(combinations[1][current_combination])    
        text = string[1] + string[4] + ' : ' + string[7] + string[10]
    elif task == 'singles':
        string = str(combinations[0][current_combination])    
        text = string[1] + ' : ' +  string[4]
    task_setting_stim = visual.TextStim(window, text, color=color,
                                        pos=pos, height=height, font=font)
    return task_setting_stim                                        


def warn_if_cue_changes(current_combination, cue_last_trial, task,
                        task_last_trial, ntrial):
    if ntrial != 0:
        
        if current_combination != cue_last_trial or task != task_last_trial:
            warning = sound.Sound(value='A', secs=0.5, octave=4,
                                  sampleRate=44100, bits=16, name='',
                                  autoLog=True)
            warning.play()
            core.wait(0.2)
            warning.play()
            core.wait(0.5)
            event.clearEvents()


def present_task_setting_stimulus(task_setting_stim, response_key, window,
                                  automatic_responding):
    task_setting_stim.draw()
    window.flip()
    no_response = True
    while no_response:
        key_list = event.getKeys(response_key)
        if len(key_list) or automatic_responding:
            no_response = False
    event.clearEvents()
               
#==============================================================================
# FIXATION
#==============================================================================

def create_fixation_stimulus(stimulus, color, pos, height, window):
    fixation_stim = visual.TextStim(window, stimulus, color=color, pos=pos,
                                    height=height)
    return fixation_stim

def present_fixation_stimulus(fixation_stim, nframes, window):
    for nframe in xrange(nframes):
        fixation_stim.draw()
        window.flip()
    event.clearEvents()
#==============================================================================
# DELAY
#==============================================================================
        
def present_delay(nframes, window):
    for nframe in xrange(nframes):
        window.flip()
    event.clearEvents()

        
#==============================================================================
# TARGET
#==============================================================================      

def create_target_stimuli(digits, font, color, pos, height, font_files,
                          window):
    stimuli = []
    for digit in digits:
        stim = visual.TextStim(window, text=digit, font=font, color=color,
                               pos=pos, height=height, fontFiles=font_files)
        stimuli.append(stim)
    return stimuli
    
def choose_target_stimulus(stim_type, even_digit, odd_digit, even_digits,
                           odd_digits, even_stimuli, odd_stimuli, jitter):
    jitter_x = random.uniform(-jitter, jitter)
    jitter_y = random.uniform(-jitter, jitter)
    if stim_type == 'even':
        index = even_digits.index(even_digit)
        target_digit = even_stimuli[index]
    elif stim_type == 'odd':
        index = odd_digits.index(odd_digit)
        target_digit = odd_stimuli[index]
    else:
        raise NameError('"stim_type" has to be either "odd" or "even"')
    target_digit.setPos((jitter_x, jitter_y))
    return target_digit, jitter_x, jitter_y
    
    
def present_target_stimulus(target_stimulus, nframes, pd_check, pd_stim,
                            window):
    for nframe in xrange(nframes):
        if pd_check:
           pd_stim.draw() 
        target_stimulus.draw()
        window.flip()
    event.clearEvents()
    
    
#==============================================================================
# MASK
#==============================================================================

def create_mask_stimulus(nlines, color, mu, sigma, line_width, window):
    lines = [None] * nlines
    for nline in range(nlines):
        line_start = (random.normalvariate(mu, sigma),
                      random.normalvariate(mu, sigma))
        line_end = (random.normalvariate(mu, sigma),
                    random.normalvariate(mu, sigma))
        lines[nline] = visual.Line(window, line_start, line_end,
                        lineColor=color, lineWidth=line_width)
    for line in lines:
        line.draw()
    mask = visual.BufferImageStim(window)
    window.clearBuffer()
    return mask
    
def present_mask_stimulus(mask, nframes, window):
    for nframe in range(nframes):
        mask.draw()
        window.flip()
    event.clearEvents()
    
#==============================================================================
# OBJECTIVE RESPONSE           
#==============================================================================
def create_objective_response_screen(text_height, text_color, text_pos,
                                     window):
    text = 'e : o'                                         
    text_stimulus = visual.TextStim(window, text, height=text_height,
                                    color = text_color, pos=text_pos)
    return text_stimulus

def present_objective_response_screen(text_stimulus, window):
    text_stimulus.draw()
    window.flip()                                    

def get_objective_response(resp_keys, automatic_responding):
    no_response = True
    rt_objective_stopwatch = core.Clock()
    while no_response:
        key_list = event.getKeys(resp_keys)
        if key_list:
            rt_objective = rt_objective_stopwatch.getTime()
            objective_response = key_list
            no_response = False
        if automatic_responding:
            no_response = False
            objective_response = ['automatic']
            rt_objective = 0
    event.clearEvents()
    return objective_response[0], rt_objective

#==============================================================================
# SUBJECTIVE RESPONSE
#==============================================================================
def create_subjective_response_screen(resp_keys, resp_names, box_positions_x,
                                      box_position_y, box_height, box_width,
                                      box_color, number_color, number_height,
                                      description_color, description_height,
                                      description_position_y, window,
                                      modality):
    if modality == 'visual':                                          
        box = visual.Rect(window, box_width, box_height, lineColor=box_color)
        text = visual.TextStim(window, text=None)
        for box_position_x in box_positions_x:
            index = box_positions_x.index(box_position_x)
            pos = (box_position_x, box_position_y)
            box.setPos(pos)
            box.draw()
            
            text.setPos(pos)
            text.setText(index + 1)
            text.setColor(number_color)
            text.setHeight(number_height)
            text.draw()
            
            pos = (box_position_x, description_position_y)
            text.setPos(pos)
            text.setText(resp_names[index])
            text.setColor(description_color)
            text.setHeight(description_height)
            text.draw()
            
        response_prompt = visual.BufferImageStim(window)
        window.clearBuffer()
        
    elif modality == 'auditory':
        response_prompt = sound.Sound(value='C', secs=0.1, octave=4,
                                      sampleRate=44100, bits=16, name='',
                                      autoLog=True)
                                     
    else:
        raise KeyError('modality is either "visual" or "auditory"')
        
    return response_prompt

def present_subjective_response_screen(prompt, modality, window):
    if modality == 'visual':
        prompt.draw()
        window.flip()
    elif modality == 'auditory':
        window.flip()
        prompt.play()
    else:
        raise KeyError('modality is either "visual" or "auditory"')
    
def get_subjective_response(resp_keys, automatic_responding):
    no_response = True
    rt_subjective_stopwatch = core.Clock()
    while no_response:
        key_list = event.getKeys(resp_keys)
        if key_list:
            rt_subjective = rt_subjective_stopwatch.getTime()
            subjective_response = key_list
            no_response = False
        if automatic_responding:
            no_response = False
            subjective_response = ['automatic']
            rt_subjective = 0
    event.clearEvents()
    return subjective_response[0], rt_subjective
    
def show_subjective_response(prompt, nframes, subjective_response,
                             box_positions_x, box_position_y, box_height,
                             box_width, box_color, box_fill_color,
                             number_color, number_height, modality, window):
    if modality == 'visual':                                 
        prompt.draw()
        box_position_x = box_positions_x[int(subjective_response) - 1]                                 
        pos = (box_position_x, box_position_y)
        box = visual.Rect(window, box_width, box_height, lineColor=box_color,
                          fillColor=box_fill_color, pos=pos)
        number = visual.TextStim(window, subjective_response,
                                 color=number_color, height=number_height,
                                 pos=pos)                             
        
        for nframe in range(nframes):
            box.draw()
            number.draw()
            window.flip()
        event.clearEvents()  
    elif modality == 'auditory':
        pass
    else:
        raise KeyError('modailty is either "visual" or "auditory"')                       
    
#==============================================================================
# WRITE DATA TO CSV FILE                              
#==============================================================================
def write_data_to_csv(data, filename):
    data_file = open(filename, 'a')
    read_file = open(filename, 'r')
    if len(read_file.readlines()) == 0:
        for data_key in data.keys():
            index = data.keys().index(data_key)
            if index + 1 < len(data.keys()):
                data_file.write(data_key + ',')
            else:
                data_file.write(data_key)
        data_file.write('\n')
    for datum_value in data.values():
        index = data.values().index(datum_value)
        datum_value = str(datum_value)
        if index + 1 < len(data.values()):
            data_file.write(datum_value + ',')
        else:
            data_file.write(datum_value)
    data_file.write('\n')
    data_file.close()
    
#==============================================================================
# PRACTICE
#==============================================================================
def pratice_run(ntrials, ## 18
                ts_col, ts_pos, ts_height, ts_resp, ts_font,
                fix, fix_nframes, fix_color, fix_pos, fix_height,
                delay_nframes,
                target_jitter, target_color, target_pos, target_height,
                target_font,
                mask_nframes, mask_nlines, mask_line_color, mask_line_width,
                mask_mu, mask_sigma,
                o_resp_keys, text_height, text_color, text_pos,
                modality, s_resp_keys, s_resp_names, box_positions_x,
                box_positions_y, box_height, box_width, box_color,
                number_color, number_height, description_color,
                description_height, description_position,
                show_answer_nframes, show_box_color, box_fill_color,
                window,
                even_digits, odd_digits, font_files,
                combinations, automatic_responding,
                subject, date, save_library, pd_check, seed_n):
    pd_stim = create_photodiode_stimulus(window)
    trial_type = 'practice'
    frames = range(1, (ntrials + 2) / 2)
    frames.reverse()
    frames *= 2
    tasks = ['quadruplet']
    tasks *= ntrials / len(tasks)
    random.shuffle(tasks)
    combination_quadruplet = [0] * ntrials
    combinations_pairs = range(ntrials)
    random.shuffle(combinations_pairs)
    combinations_singles = random.sample(range(16) * 2, ntrials)
    target_types = ['even', 'odd']
    target_types *= ntrials / len(target_types)
    even_digits = random.sample([2, 4, 6, 8] * 5, ntrials)
    odd_digits = random.sample([3, 5, 7, 9] * 5, ntrials)
    
    
    fix_stim = create_fixation_stimulus(fix, fix_color, fix_pos, fix_height,
                                        window)
    
    even_stimuli = create_target_stimuli(even_digits, target_font,
                                         target_color, target_pos,
                                         target_height, font_files, window)

    odd_stimuli = create_target_stimuli(odd_digits, target_font, target_color,
                                        target_pos, target_height, font_files,
                                        window)                                        
    response_prompt = create_subjective_response_screen(
                        s_resp_keys, s_resp_names, box_positions_x,
                        box_positions_y, box_height, box_width, box_color,
                        number_color, number_height, description_color,
                        description_height, description_position, window,
                        modality)

    objective_response_screen = create_objective_response_screen(
                                text_height, text_color, text_pos, window)

                                        
    
    for ntrial in xrange(ntrials):
        target_type = target_types[ntrial]
        target_nframes = frames[ntrial]
        task = tasks[ntrial]
        even_digit = even_digits[ntrial]
        odd_digit = odd_digits[ntrial]
        if task == 'quadruplet':
            current_combination = combination_quadruplet[ntrial]
        elif task == 'pairs':
            current_combination = combinations_pairs[ntrial]
        elif task == 'singles':
            current_combination = combinations_singles[ntrial]
            
        task_setting_stim = create_task_setting_stimulus(task, combinations,
                                                         current_combination,
                                                         ts_col, ts_pos,
                                                         ts_height, ts_font,
                                                         window)
            
        target_stimulus, jitter_x, jitter_y = \
            choose_target_stimulus(target_type, even_digit, odd_digit,
                                   even_digits, odd_digits,
                                   even_stimuli, odd_stimuli, target_jitter)
                                   
        mask_stimulus = create_mask_stimulus(mask_nlines, mask_line_color,
                                             mask_mu, mask_sigma,
                                             mask_line_width, window)
                                             
        present_task_setting_stimulus(task_setting_stim, ts_resp, window,
                                      automatic_responding)
        present_fixation_stimulus(fix_stim, fix_nframes, window)
        present_delay(delay_nframes, window)
        present_target_stimulus(target_stimulus, target_nframes,
                                pd_check, pd_stim,
                                window)
        present_mask_stimulus(mask_stimulus, mask_nframes, window)
        present_objective_response_screen(objective_response_screen, window)
        objective_response, rt_objective = get_objective_response(
                                    o_resp_keys,
                                    automatic_responding)
        present_subjective_response_screen(response_prompt, modality, window)
        subjective_response, rt_subjective = get_subjective_response(
                                                s_resp_keys,
                                                automatic_responding)
                                                
        show_subjective_response(response_prompt, show_answer_nframes,
                                 subjective_response, box_positions_x,
                                 box_positions_y, box_height, box_width,
                                 show_box_color, box_fill_color,
                                 number_color, number_height, modality,
                                 window)
        time = data.getDateStr()
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
        write_data_to_csv(data_dict, filename)                                             
            
        