import pandas as pd
import numpy as np
from PlayByPlay_cleaner import playbyplay_data
from collections import Counter
from Position_cleaner import postition_data
import time


class Coordination(object):

    def __init__(self, gameID, path):
        self.jsonID = gameID
        self.pbpID = gameID[:-5] #strips '.json'
        self.path = path

    def playbyplay(self):
        self.pbpEX = playbyplay_data(self.pbpID)
        return self.pbpEX.return_df()

    def position(self):
        self.position_data = postition_data(self.path, self.jsonID)
        return self.position_data.return_df()

    def sync_datasets(self):
        pbp_df = self.playbyplay()
        pos_df = self.position()
        self.final_df = pd.merge(pbp_df, pos_df, on=['Clock', 'Quarter'])
        self.final_df['EventID'] = 0
        eventid = 1
        last_i = len(self.final_df)
        for index, row in self.final_df.iterrows():
            self.final_df['EventID'][index] = eventid
            if index != last_i - 1:
                if self.final_df['DESCRIPTION'][index] != self.final_df['DESCRIPTION'][index + 1]:
                    eventid += 1





    def run(self):
        self.sync_datasets()
        return self.final_df


if __name__ == '__main__':
    import time, os
    import random
    t = time.time()
    path = './'
    game = '0021500293.json'
    coo = Coordination(game, path)
    print(coo.run().head(1000))
    print('Runtime: ' + str(time.time() - t) + ' seconds')