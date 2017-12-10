import json
import requests
import pandas as pd
import numpy as np
import seaborn as sns
import pprint as pprint
import NBAData as nba
import time

pd.set_option('display.max_rows', 10000)
pd.set_option('display.max_colwidth', 10000)
pd.set_option('display.width', None)

sns.set_color_codes()
sns.set_style("white")

#opening the json file
with open('0021500293.json') as data_file:
    game_data = json.load(data_file)

#gets the movement data from a
def get_movement_data(data):
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
    # Column labels
    headers = ["team_id", "player_id", "x_loc", "y_loc",
               "radius", "moment", "game_clock", "period", "shot_clock"]
    player_moments = []
    #len(allMoments)
    #for moments in allMoments:
    moments = allMoments[1]
    for moment in moments:
        # For each player/ball in the list found within each moment

        for player in moment[5]:
            # Add additional information to each player/ball
            # This info includes the index of each moment, the game clock
            # and shot clock values for each moment
            player.extend((moments.index(moment), str(time.strftime("%M:%S", time.gmtime(moment[2]))), moment[0], moment[3]))
            #player["game_clock"] = time.strftime("%M:%S", time.gmtime(100))
            player_moments.append(player)

    movement_df = pd.DataFrame(player_moments, columns=headers)
    players = home["players"]
    players.extend(visitor["players"])
    id_dict = {}
    for player in players:
        id_dict[player['playerid']] = [player["firstname"] + " " + player["lastname"],
                                       player["jersey"]]
    id_dict.update({-1: ['ball', np.nan]})
    movement_df["player_name"] = movement_df.player_id.map(lambda x: id_dict[x][0])
    movement_df["player_jersey"] = movement_df.player_id.map(lambda x: id_dict[x][1])
    return movement_df


# gets the play by play data from the given json file and returns it in a dataframe
def get_play_by_play(json):
    data = json
    game_ID = data["gameid"]
    date = str(data["gamedate"])
    game_date = date.translate(str.maketrans('', '', '-'))
    q1 = nba.nba_data("play_by_play", game_date, str(game_ID), "1")
    q2 = nba.nba_data("play_by_play", game_date, str(game_ID), "2")
    q3 = nba.nba_data("play_by_play", game_date, str(game_ID), "3")
    q4 = nba.nba_data("play_by_play", game_date, str(game_ID), "4")
    game = [q1, q2, q3, q4]
    playheaders = ["clock", "description", "eventMsgType", "hTeamScore", "isScoreChange", "personId",
                   "teamId", "vTeamScore", "period"]
    playbyplay = []
    q = 0
    for quarter in game:
        q += 1
        plays = quarter["plays"]
        for play in plays:
            play["period"] = q
            play.pop("formatted", None)
            play.pop("isVideoAvailable", None)
            if play["eventMsgType"] == "1":
                play["eventMsgType"] = "Make"
            elif play["eventMsgType"] == "2":
                play["eventMsgType"] = "Miss"
            elif play["eventMsgType"] == "3":
                play["eventMsgType"] = "Free Throw"
            elif play["eventMsgType"] == "4":
                play["eventMsgType"] = "Rebound"
            elif play["eventMsgType"] == "5":
                play["eventMsgType"] = "Turnover"
            elif play["eventMsgType"] == "6":
                play["eventMsgType"] = "Personal Foul"
            elif play["eventMsgType"] == "7":
                play["eventMsgType"] = "Violation"
            elif play["eventMsgType"] == "8":
                play["eventMsgType"] = "Substitution"
            elif play["eventMsgType"] == "9":
                play["eventMsgType"] = "Timeout"
            elif play["eventMsgType"] == "10":
                play["eventMsgType"] = "Jumpball"
            playbyplay.append(play)
    return pd.DataFrame(playbyplay, columns=playheaders)

#syncs up the play by play dataframe for every shot attempt with the
#positional data from the movement dataframe to give movement data for every shot attempt in the game
def get_shot_data(data):
    move_data = get_movement_data(data)
    pbp_data = get_play_by_play(data)
    shot_data = pbp_data.loc[pbp_data["eventMsgType"].isin(["Make", "Miss"])]
    game_data = move_data.reindex(columns=["team_id", "player_id", "x_loc", "y_loc",
               "radius", "moment", "game_clock", "shot_clock",'description', 'eventMsgType', 'hTeamScore',
                                           'isScoreChange', 'personId', 'teamId', 'vTeamScore', "period"])

    moments = game_data.moment.unique()
    for moment in moments:
        moment_data = game_data.loc[game_data['moment'] == moment]
        moment_period_data = moment_data["period"]
        moment_clock_data = moment_data["game_clock"]
        play = shot_data.loc[shot_data["clock"].isin(moment_clock_data.tolist())
                             & shot_data["period"].isin(moment_period_data.tolist())].copy()
        #print(moment_clock_data)
        if len(play) > 0:
            game_data.loc[game_data['moment'] == moment, ["description"]] = play["description"].iloc[0]
            game_data.loc[game_data['moment'] == moment, ["eventMsgType"]] = play["eventMsgType"].iloc[0]
            game_data.loc[game_data['moment'] == moment, ["hTeamScore"]] = play["hTeamScore"].iloc[0]
            game_data.loc[game_data['moment'] == moment, ["isScoreChange"]] = play["isScoreChange"].iloc[0]
            game_data.loc[game_data['moment'] == moment, ["personId"]] = play["personId"].iloc[0]
            game_data.loc[game_data['moment'] == moment, ["teamId"]] = play["teamId"].iloc[0]
            game_data.loc[game_data['moment'] == moment, ["vTeamScore"]] = play["vTeamScore"].iloc[0]
    return game_data[game_data.description.notnull()]

shots = (get_shot_data(game_data))

print(shots)

#game_pbp = get_play_by_play(game_data)








#parsed = nba.nba_data("play_by_play", "20151205", "0021500293", "1")
#print(json.dumps(parsed, indent=4, sort_keys=True))
# print(nba.nba_data("play_by_play", "20151205", "0021500293", "1"))
