"""
Yujia Liu    yujialiu@uchicago.edu
07/15/22

A general controller to assign tasks to the robot at certain timepoints
"""

import time
from src.get_time_str import get_time_str

# internal variables
_time_vec = []    # time points. Unit: minutes
_func_vec = []    # functions to execute at corresponding time points
_param_vec = []    # parameters to be passed to functions
_str_vec = []    # descriptions
_n_tip_vec = []    # number of tips required for each operation

def cat(time_vec, func_vec, param_vec, str_vec, n_tip_vec):
    "Add new list of instructions"
    
    # check lengths
    if ((len(time_vec) != len(func_vec)) or (len(time_vec) != len(str_vec)) 
        or (len(time_vec) != len(param_vec)) or (len(time_vec) != len(n_tip_vec))):
        raise Exception("Lengths do not agree. Abort")
    
    global _time_vec, _func_vec, _param_vec, _str_vec, _n_tip_vec
    _time_vec += list(time_vec)
    _func_vec += list(func_vec)
    _param_vec += list(param_vec)
    _str_vec += list(str_vec)
    _n_tip_vec += list(n_tip_vec)
    
def drop():
    "Clear all instructions"
    
    global _time_vec, _func_vec, _param_vec, _str_vec, _n_tip_vec
    
    _time_vec = []
    _func_vec = []
    _param_vec = []
    _str_vec = []
    _n_tip_vec = []

def report(unit="minutes"):
    "Print scheduled steps"
    
    global _time_vec, _func_vec, _param_vec, _str_vec, _n_tip_vec
    
    # report # tips required
    print("The protocol requires a total of", sum(_n_tip_vec), "tip(s)\n")
    
    for i in range(len(_time_vec)):
        # time conversion
        if unit == "hours":
            time_str = f"{_time_vec[i]/60:.2f} hours"
        else:
            time_str = str(_time_vec[i]) + " minutes"
        # compose a string
        s = f"At {time_str}, {_str_vec[i]}, with params {_param_vec[i]}"
        print(s)

def run(protocol, log_fn):
    """
    Parameters
    - time_vec: a list of integer time points in unit of minutes
    - func_vec: a list of functions to be run by the robot. A function only takes parameters from `param_vec`.
    The protocol context and instrument context is read as global variables. The order of the function is important.
    The order should corresponds to the order of `time_vec`. If more than one functions are assigned to the same
    time point, the one that occurs earlier in the list will have higher priority
    - param_vec: a list of parameters. Each element as a tuple
    - str_vec: a list of descriptions of the function for logging
    """
    
    global _time_vec, _func_vec, _param_vec, _str_vec, _n_tip_vec
    
    # check agreement for time_vec and func_vec
    if (len(_time_vec) != len(_func_vec)) or (len(_time_vec) != len(_str_vec)) or (len(_time_vec) != len(_param_vec)):
        raise Exception("Lengths do not agree. Abort")
        
    # regiester if is excuted
    is_excuted_vec = [0] * len(_time_vec)    # 0 not yet, 1 excuted
    
    # open log file for writing
    log_file = open(log_fn, 'a')    # appending, not erasing what's already there
    
    # turn on lights
    protocol.set_rail_lights(True)
    
    # record starting time
    start_time = time.time()
    
    # infinite loop as delay (this is not compatible with the opentrons client)
    while(True):
        # if all instructions are run, exit
        if sum(is_excuted_vec) == len(is_excuted_vec):
            break
            
        # what's time now?
        cur_time = time.time()
        elapsed = cur_time - start_time
        
        # time to run any function?
        for i in range(len(_time_vec)):
            if _time_vec[i] * 60 < elapsed and is_excuted_vec[i] == 0:
                _func_vec[i](*_param_vec[i])    # call the function
        
                # log
                time_str = get_time_str()
                s = f"{time_str}\t{_str_vec[i]}\t{_param_vec[i]}\n"
                log_file.write(s)
                log_file.flush()    # write immediately
                
                # flag excuted
                is_excuted_vec[i] = 1
    
    # turn off lights
    protocol.set_rail_lights(False)
    
    # close log file
    log_file.close()