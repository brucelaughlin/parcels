import numpy as np
import datetime

def get_days_per_output_timestep(times, ages):
    for i_float in range(times.shape[0]):
        if not np.isnat(times[i_float,1]):
            num_timestepCalc_per_timestepOut = int(ages[i_float,1] - ages[i_float,0])
            test_timestep_0 = np.array(times[i_float,0],dtype='datetime64[s]').astype(datetime.datetime).tolist()
            test_timestep_1 = np.array(times[i_float,1],dtype='datetime64[s]').astype(datetime.datetime).tolist()
            break

    if np.isnat(times[i_float,1]):
        raise RuntimeError("All trajectories have length 1")


    seconds_per_timestepOut = (test_timestep_1 - test_timestep_0).seconds

    days_per_output_timestep = seconds_per_timestepOut/86400

    if seconds_per_timestepOut > 86400:
        raise RuntimeError("Currently can't handle output timesteps greater than 1 day")

    # It may not be generally safe to assume that I'm getting integers from these divisions, but I've never configured runs where this won't be true
    #timestepCalc_per_day_preRounding = 86400/timestepCalc_seconds
    #timestepCalc_per_day = int(timestepCalc_per_day_preRounding)


    #return timestepCalc_per_day, seconds_per_timestepOut
    return days_per_output_timestep



