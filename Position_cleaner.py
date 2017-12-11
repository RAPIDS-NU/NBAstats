import json, os
import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_colwidth', 100000)
pd.set_option('display.width', None)

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

'''
steps for cleaning data:
- make a dataset for each moment (keep position data untouched)
- create dataframe for ball movements to attach to movements
- filter data for where ball is behind 3 point line and being shot
'''


class postition_data(object):

    def __init__(self, path, game_id):

        self.playerDict = {}
        self.ID = game_id
        '''
        columns for the final dataset:
        '''
        self.final_col = ['GameClock', 'Quarter', 'ShotClock', 'Position',
                          'Clock', 'BallX', 'BallY', 'BallZ', 'LowStart', 'HighStart']
        with open(path + self.ID) as json_data:
            self.data = json.load(json_data)
        self.events = self.data['events']

    def unpack(self):
        """
        Unpacks the json file and formats it to the initial DataFrame.
        """
        events = self.data['events']
        moments = []
        """
        creates dataframe based on each moment
        """
        cols1 = ['Quarter', 'EvID', 'GameClock', 'ShotClock', 'NoClue', 'Position']
        for i, event in enumerate(events):
            moments += event['moments']
            if i == 0:
                # Used later to totally order on court position
                # Done on a per-game basis due to roster volatility
                vis = event['visitor']
                home = event['home']
        Moments = pd.DataFrame(moments, columns=cols1)
        Moments['Clock'] = Moments['GameClock'].astype(int)
        Moments['Quarter'] = Moments['Quarter'].astype(int)

        """
        dataframe of ball position, to by synced to moments dataframe
        """
        ballMom = []
        for moment in Moments['Position']:
            ballMom.append(moment[0])

        cols2 = ['TeamID', 'PlayerID', 'BallX', 'BallY', 'BallZ']
        ballFrame = pd.DataFrame(ballMom, columns=cols2)
        ballFrame['TeamID'] = ballFrame['TeamID'].astype(str)
        ballFrame['PlayerID'] = ballFrame['PlayerID'].astype(str)

        """
        Creates dictionary for player positions to be used when coordinating.
        """
        posDict = {'G': 1.0, 'G-F': 5.0 / 3, 'F-G': 7.0 / 3, 'F': 3.0, 'F-C': 11.0 / 3, 'C-F': 13.0 / 3, 'C': 5.0}
        for player in (home['players'] + vis['players']):
            self.playerDict[str(player['playerid'])] = posDict[player['position']]

        """
        Creates final frame of Positions to be used in coordination script.
        """
        self.Positions = pd.concat([Moments, ballFrame], axis=1)
        self.Positions.drop_duplicates(subset=['Quarter', 'GameClock', 'ShotClock', 'BallX', 'BallY', 'BallZ'],
                                       inplace=True)
        self.Positions = self.Positions.sort_values(by=['Quarter', 'GameClock'], ascending=[True, False])
        self.Positions = self.Positions[self.Positions['TeamID'] == '-1']
        self.Positions.reset_index(inplace=True, drop=True)
        return self.Positions

    def feat_gen(self):
        """
        Generates some base features that are used when coordinating.
        """
        """
        Identifies when the ball is starting to rise or fall.
        """
        """
        Identify when ball is lower than in previous position.
        """
        self.Positions['Lower'] = (self.Positions['BallZ'].shift() > self.Positions['BallZ']).astype(int)
        """
        Changes the balls dimensions to half court. Not stored in final
             DataFrame because ball x,y,z is not used.
        """
        newpos = self.Positions[['BallX', 'BallY']].values - np.array([47, 0])
        newpos = np.absolute(newpos)
        """
        Creates a time signature for when ball starts going up, or starts going down.
        """
        self.Positions['LowStart'] = ((self.Positions['Lower'] == 1) & (self.Positions['Lower'].shift() != 1)).astype(
            int) * self.Positions['Clock']
        self.Positions['HighStart'] = ((self.Positions['Lower'] == 0) & (self.Positions['Lower'].shift() != 0)).astype(
            int) * self.Positions['Clock']

        self.Positions = self.Positions[self.final_col]
        self.Positions.reset_index(inplace=True, drop=True)
        return self.Positions

    def run(self):
        self.unpack()
        self.feat_gen()

    def return_df(self):
        self.run()
        return self.Positions



    def getPlayerID(self, id):
        visitor = self.events[0]["visitor"]
        home = self.events[0]["home"]
        # initialize new dictionary
        id_dict = {}

        players = home["players"]
        players.extend(visitor["players"])
        id_dict = {}
        for player in players:
            id_dict[player['playerid']] = [player["firstname"] + " " + player["lastname"],
                                           player["jersey"]]
        id_dict.update({-1: ['ball', np.nan]})

        return id_dict[id][0]


if __name__ == '__main__':
    import time

    t = time.time()
    path = './'
    gameID = '0021500293.json'
    sport = postition_data(path, gameID)
    print(sport.return_df())
    print('Runtime: ' + str(time.time() - t) + ' seconds')
