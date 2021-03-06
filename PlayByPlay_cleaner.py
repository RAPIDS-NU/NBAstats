import pandas as pd
import datetime as dt
from math import *
import numpy as np
import requests, json, os

pd.options.mode.chained_assignment = None

pd.set_option('display.max_rows', 10000)
pd.set_option('display.max_colwidth', 10000)
pd.set_option('display.width', None)

def clocktosec(clock):
    """
    Turns clock (HH:MM or MM:SS format) into time in units.
    """
    m, s = clock.split(':')
    return 60 * int(m) + int(s)

"""
this class will be used to collect the play by play data using the NBAData api to access the data from data.nba.com.
the data will be put into a dataframe that can be used with the dataframe of positional data. 
TODO:
- create constructor (params: date of the game, gameid)
- create fields for different parts of the data
- collect into dataframe to be used with position data. 
"""
class playbyplay_data(object):



    '''
    steps for cleaning data:
    - get data into dataframe
    - filter for 3pt shots
    - match up on time
    '''


    def __init__(self, gameID):
        """
        Stores ID, and notes that data has not been called yet.
        """
        self.ID = gameID
        self.g = 1
        self.three_pt_shots = ''


    def getData(self):
        """
        Queries STATS server for game data.
        """
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:53.0) Gecko/20100101 Firefox/53.0'}
        params = {'EndPeriod': 10, 'GameID': self.ID, 'StartPeriod': 1}
        r = requests.get("http://stats.nba.com/stats/playbyplayv2", params=params, headers=headers)
        self.data = r.json()
        self.g = 0 #Signifier. Separated out for debugging purposes.
        return self.data

    def unpack(self):
        """
        Unpacks json data received from STATS to extract the full play by play
        and put it in a convertible format.
        """
        if self.g:
            self.getData()
            self.g = 0

        """
        Creates data frame to match Json
        """
        plays = self.data['resultSets']
        plays = plays[0]
        cols = plays['headers']
        self.playbyplay_init = pd.DataFrame(plays['rowSet'], columns=cols)

        """
        Reformats columns
        """
        keepers = ['EVENTMSGTYPE', 'PERIOD', 'PCTIMESTRING', 'HOMEDESCRIPTION', 'VISITORDESCRIPTION',\
                   'PLAYER1_ID', 'PLAYER1_NAME', 'PLAYER1_TEAM_ID', 'PLAYER1_TEAM_ABBREVIATION', \
                   'PLAYER2_ID', 'PLAYER2_NAME', 'PLAYER2_TEAM_ID', 'PLAYER2_TEAM_ABBREVIATION', \
                   'PLAYER3_ID', 'PLAYER3_NAME', 'PLAYER3_TEAM_ID', 'PLAYER3_TEAM_ABBREVIATION']
        strCols = ['PCTIMESTRING', 'HOMEDESCRIPTION', 'VISITORDESCRIPTION', 'PLAYER1_ID', 'PLAYER1_NAME', \
                   'PLAYER1_TEAM_ID', 'PLAYER1_TEAM_ABBREVIATION', 'PLAYER2_ID', 'PLAYER2_NAME', \
                   'PLAYER2_TEAM_ID', 'PLAYER2_TEAM_ABBREVIATION', 'PLAYER3_ID', 'PLAYER3_NAME', \
                   'PLAYER3_TEAM_ID', 'PLAYER3_TEAM_ABBREVIATION']
        intCols = ['EVENTMSGTYPE', 'PERIOD']

        """
        sets DF with desired columns, and changeds the datatypes to either string of integer
        """


        self.playbyplay = self.playbyplay_init[keepers]

        for index, row in self.playbyplay.iterrows():
            if (row['HOMEDESCRIPTION'] is None):
                self.playbyplay.at[index,'HOMEDESCRIPTION'] = row['VISITORDESCRIPTION']



        for col in strCols:
            self.playbyplay[col] = self.playbyplay[col].astype(str)
        for col in intCols:
            self.playbyplay[col] = self.playbyplay[col].astype(int)

        self.playbyplay = self.playbyplay.drop(['VISITORDESCRIPTION'],axis=1)

        self.playbyplay.columns = ['EVENTMSGTYPE', 'Quarter', 'PCTIMESTRING', 'DESCRIPTION',\
                   'PLAYER1_ID', 'PLAYER1_NAME', 'PLAYER1_TEAM_ID', 'PLAYER1_TEAM_ABBREVIATION', \
                   'PLAYER2_ID', 'PLAYER2_NAME', 'PLAYER2_TEAM_ID', 'PLAYER2_TEAM_ABBREVIATION', \
                   'PLAYER3_ID', 'PLAYER3_NAME', 'PLAYER3_TEAM_ID', 'PLAYER3_TEAM_ABBREVIATION']


        """
        Seperates out 3 point attempts, addes clock.
        """
        """
        #2.1 Identifies rows where shots occur, and the appropriate rebound for
             each shot.
        """
        self.three_pt_shots = self.playbyplay.index[self.playbyplay['DESCRIPTION'].str.contains('3PT')]

        """
        #2.2 Adds clock column and orders.
        """
        self.playbyplay['Clock'] = self.playbyplay['PCTIMESTRING'].apply(clocktosec)
        self.playbyplay.sort_values(by=['Quarter', 'Clock'], ascending=[True, False], inplace=True)

        """
        #2.3 Separates the correct rows into new frames.
        """
        self.three_pt_shots = self.playbyplay.iloc[self.three_pt_shots, :]
        self.three_pt_shots.reset_index(inplace=True, drop=True)
        return

    def run(self):
        self.unpack()

    def return_df(self):
        self.run()
        return self.three_pt_shots

if __name__ == '__main__':
    import time
    t = time.time()
    pbp = playbyplay_data('0021500293')
    print(pbp.return_df())
    print('Runtime: ' + str(time.time() - t) + ' seconds')

