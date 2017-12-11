import requests
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
from data_synchronize import Coordination
from Position_cleaner import postition_data


'''
class to start visualizing the data from the final dataframe
'''

class visaulize(object):

    def __init__(self, gameID, path):
        self.df = Coordination(gameID, path).run()
        self.court = plt.imread("fullcourt.png")
        self.pos = postition_data(path, gameID)
        self.posDF = self.pos.return_df()

    #TODO change player id to player name for easier use
    def visualize_main_player(self, eventID):
        event_df = self.df[self.df['EventID'] == eventID]
        event_df = event_df.reset_index(drop=True)
        player_id = event_df['PLAYER1_ID'][0]
        position_data = event_df['Position']
        clock_data = event_df['GameClock']
        player_pos_data = []
        for index, row in position_data.iteritems():
            data = position_data[index]
            time = clock_data[index]
            for item in data:
                if int(item[1]) == int(player_id):
                    pos_time = list(item)
                    pos_time.append(time)
                    player_pos_data.append(pos_time)

        x_loc = []
        y_loc = []
        clock = []
        for item in player_pos_data:
            x_loc.append(item[2])
            y_loc.append(item[3])
            clock.append(item[5])


        plt.scatter(x_loc, y_loc, c=clock,
                   cmap=plt.cm.Blues, s=1000, zorder=1)

        cbar = plt.colorbar(orientation="horizontal")
        cbar.ax.invert_xaxis()

        plt.imshow(self.court, zorder=0, extent=[0, 94, 50, 0])

        # extend the x-values beyond the court b/c Harden
        # goes out of bounds
        plt.xlim(0, 101)

        plt.show()

    def visualize__full_play(self, player_id, quarter, startime, endtime):
        print(self.pos.getPlayerID(player_id))
        play_df = self.posDF[(self.posDF['GameClock'] <= startime) & (self.posDF['GameClock'] >= endtime)
                             & (self.posDF['Quarter'] == quarter)]
        play_df = play_df.reset_index(drop=True)
        position_data = play_df['Position']
        clock_data = play_df['GameClock']
        player_pos_data = []
        for index, row in position_data.iteritems():
            data = position_data[index]
            time = clock_data[index]
            for item in data:
                if int(item[1]) == int(player_id):
                    pos_time = list(item)
                    pos_time.append(time)
                    player_pos_data.append(pos_time)

        x_loc = []
        y_loc = []
        clock = []
        for item in player_pos_data:
            x_loc.append(item[2])
            y_loc.append(item[3])
            clock.append(item[5])

        plt.scatter(x_loc, y_loc, c=clock,
                   cmap=plt.cm.Blues, s=1000, zorder=1)

        cbar = plt.colorbar(orientation="horizontal")
        cbar.ax.invert_xaxis()

        plt.imshow(self.court, zorder=0, extent=[0, 94, 50, 0])

        # extend the x-values beyond the court b/c Harden
        # goes out of bounds
        plt.xlim(0, 101)

        plt.show()


if __name__ == '__main__':
    import time, os
    import random
    t = time.time()
    path = './'
    game = '0021500293.json'
    viz = visaulize(game, path)
    print(viz.visualize__full_play(203991, 1, 699, 650))
    print('Runtime: ' + str(time.time() - t) + ' seconds')