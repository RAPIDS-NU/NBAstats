import json, os
import pandas as pd
import numpy as np

"""
this class will be used to collect the position data of a SportVU Json file and the additional 3 point information 
(is the ball being shot from the 3 point line, time of the shot, etc) 
the data will be stored a Pandas dataframe which will then be used to against the play by play dataframe
TODO:
-create constructor (params: json file name and path)
-create fields for different parts of data
-create methods for finding 3 point information
-collect into the single dataframe to be returned
"""
class postition_data(object):
