import json, os
import pandas as pd
import numpy as np

print('hello')

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



    def __init__(self, path, game_id):
        self.ID = game_id
        '''
        columns foe the final dataset:
        '''
        self.keep_col = ['GameClock', 'Quarter', 'ShotClock', 'Position',
                         'Clock', 'BallX', 'BallY', 'BallZ', '3point', 'ShotStart', 'ShotEnd', 'Make?']
        with open(path + self.ID) as json_data:
            self.data = json.load(json_data)


'''
steps for cleaning data:
- make a dataset for each moment (keep position data untouched)
- create dataframe for ball movements to attach to movements
- filter data for where ball is behind 3 point line and being shot
'''
