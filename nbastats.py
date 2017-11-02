import json
import pandas as pd
import numpy as np
import seaborn as sns



sns.set_color_codes()
sns.set_style("white")

with open('0021500293.json') as data_file:
    data = json.load(data_file)

gameID = data["gameid"]
gameDate = data["gamedate"]
events = data["events"]


eventIDs = []
for i in range(len(events)):
    eventIDs.append(events[i]["eventId"])

visitor = events[0]["visitor"]
home = events[0]["home"]

allMoments = []
for i in range(len(events)):
    allMoments.append(events[i]["moments"])

# pprint(allMoments[0][0])

# Column labels
headers = ["team_id", "player_id", "x_loc", "y_loc",
           "radius", "moment", "game_clock", "shot_clock"]

player_moments = []
moments = allMoments[0]

for moment in moments:
    # For each player/ball in the list found within each moment
    for player in moment[5]:
        # Add additional information to each player/ball
        # This info includes the index of each moment, the game clock
        # and shot clock values for each moment
        player.extend((moments.index(moment), moment[2], moment[3]))
        player_moments.append(player)

df = pd.DataFrame(player_moments, columns=headers)

players = home["players"]
players.extend(visitor["players"])

id_dict = {}
for player in players:
    id_dict[player['playerid']] = [player["firstname"]+" "+player["lastname"],
                                   player["jersey"]]

id_dict.update({-1: ['ball', np.nan]})

df["player_name"] = df.player_id.map(lambda x: id_dict[x][0])
df["player_jersey"] = df.player_id.map(lambda x: id_dict[x][1])

print df.head(11)
