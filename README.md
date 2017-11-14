# NBAstats

group members: Matt Morgan, Jeff curran, Nik Pousette, Clarance Mow

##Project Goals:
- create a model to predict 3 point chances bases off positional and play by play data
- create visualizations of plays, heatmaps of shots, and other visualizations

##Plan:
###3 Point Predictor
   - clean data using the playbyplay_cleaner and position_clear classes
   - combine data types differently for each model
   - create machine learning model to try to predict if shot will do in
   - possible model ideas:
       - predict 3pt shot based on all player positions + weighted 3pt %, see if there is a notable improvement 
       - do the same for just shooter and defender data

###Visualizations
   - Use play by Play data to develop heat maps for a given player/team
   - possibly animate a given play (D3?)
   - get data into Tableau to start the visualization/exploration process 
    
