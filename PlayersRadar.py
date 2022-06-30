
# Creating random player's radar from FBRef stats everyday
#
# Goals and steps required:
# - Retrieving the Premier League players database from the FBRef webpage:
# + Open the FBRef players webpage (https://fbref.com/en/comps/9/stats/Premier-League-Stats)
# + Use RegEx to process the HTML and change the player's name from ..."Tammy-Abraham"... to "Tammy Abraham"
# - Collect the stats from the webpage from the HTML
# - Determine the radar template for each player (inspiration: http://cboutaud.github.io/radar/radar.html)
# - Draw the radar with the gathered stats correlate with the player's position (GK, CB, FB, CM/DM, W, FW)
# - Export the radar out as a savable .png template
# - ... (steps relate to Raspberry Pi)

# Import necessary stuff

# + Package for RegEx
from re import findall, finditer, MULTILINE, DOTALL

# + Package for generating random player
from random import randint

# + Package for using CSV files
import csv

# + Package for radar charts
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mplsoccer import Radar, FontManager

# Download and save webpage

def download(url = 'http://fbref.com/',
             target_filename = 'download',
             filename_extension = 'html',
             save_file = False,
             char_set = 'UTF-8',
             lying = False,
             got_the_message = False):

    # Import the function for opening online documents and
    # the class for creating requests
    from urllib.request import urlopen, Request

    # Import an exception raised when a web server denies access
    # to a document
    from urllib.error import HTTPError

    # Open the web document for reading
    try:
        web_page = urlopen(url)
    except ValueError:
        print("Access error - Cannot find document at URL '" + url + "'\n")
        return None
    except HTTPError:
        print("Access error - Access denied to document at URL '" + url + "'\n")
        return None
    except Exception as message:
        print("Access error - Something went wrong when trying to download " + \
              "the document at URL '" + url + "'")
        print("Error message was:", message, "\n")
        return None

    # Read the contents as a character string
    try:
        web_page_contents = web_page.read().decode(char_set)
    except UnicodeDecodeError:
        print("Read error - Unable to decode document from URL '" + \
              url + "' as '" + char_set + "' characters\n")
        return None
    except Exception as message:
        print("Read error - Something went wrong when trying to decode " + \
              "the document from URL '" + url + "'")
        print("Error message was:", message, "\n")
        return None

    # Optionally write the contents to a local text file
    # (overwriting the file if it already exists!)
    if save_file:
        try:
            text_file = open(target_filename + '.' + filename_extension,
                             'w', encoding = char_set)
            text_file.write(web_page_contents)
            text_file.close()
        except Exception as message:
            print("Write error - Unable to write to file '" + \
                  target_filename + "'")
            print("Error message was:", message, "\n")

    # Return the downloaded document to the caller
    return web_page_contents

# Extract database from FBRef website
premier_league = download(url = 'https://fbref.com/en/comps/9/stats/Premier-League-Stats#stats_standard')

# Find all 520 players' name (including double entries)
# premier_league_players = findall("<tr ><th scope=\"row\" class=\"right \" data-stat=\"ranker\" >[0-9]+<\/th><td class=\"left \" data-append-csv=\"[A-Za-z-]+\" data-stat=\"player\" csk=\"[A-Za-z, áüïéúóíðãŁńćščÉöçë'äšÜěşØøİğßÇ-]+\" ><a href=\"\/en\/players\/[a-z0-9]+\/[A-Za-z-]+\">([A-Za-z áüïéúóíðãŁńćščÉöçë'äšÜěşØøİğßÇ-]+)<\/a><\/td><td class=\"left poptip\" data-stat=\"nationality\" data-tip=\"[A-Za-z]+\" ><a href=\"\/en\/country\/[A-Z]+\/[A-Za-z-]+\"><span style=\"white-space: nowrap\"><span class=\"f-i f-[a-z-]+\">[a-z]+<\/span> [A-Z]+<\/span><\/a><\/td><td class=\"center \" data-stat=\"position\" csk=\"[0-9]+\.[0-9]+\" >[A-Z,]+<\/td><td class=\"left \" data-stat=\"squad\" ><a href=\"\/en\/squads\/[a-z0-9]+\/[A-Za-z-]+-Stats\">[A-Za-z ]+<\/a><\/td>", premier_league)
# Find all 520 players' position(s)
# premier_league_players_position = findall("<tr ><th scope=\"row\" class=\"right \" data-stat=\"ranker\" >[0-9]+<\/th><td class=\"left \" data-append-csv=\"[A-Za-z-]+\" data-stat=\"player\" csk=\"[A-Za-z, áüïéúóíðãŁńćščÉöçë'äšÜěşØøİğßÇ-]+\" ><a href=\"\/en\/players\/[a-z0-9]+\/[A-Za-z-]+\">[A-Za-z áüïéúóíðãŁńćščÉöçë'äšÜěşØøİğßÇ-]+<\/a><\/td><td class=\"left poptip\" data-stat=\"nationality\" data-tip=\"[A-Za-z]+\" ><a href=\"\/en\/country\/[A-Z]+\/[A-Za-z-]+\"><span style=\"white-space: nowrap\"><span class=\"f-i f-[a-z-]+\">[a-z]+<\/span> [A-Z]+<\/span><\/a><\/td><td class=\"center \" data-stat=\"position\" csk=\"[0-9]+\.[0-9]+\" >([A-Z,]+)<\/td><td class=\"left \" data-stat=\"squad\" ><a href=\"\/en\/squads\/[a-z0-9]+\/[A-Za-z-]+-Stats\">[A-Za-z ]+<\/a><\/td>", premier_league)
# Find all 520 players' club(s)
# premier_league_players_club = findall("<tr ><th scope=\"row\" class=\"right \" data-stat=\"ranker\" >[0-9]+<\/th><td class=\"left \" data-append-csv=\"[A-Za-z-]+\" data-stat=\"player\" csk=\"[A-Za-z, áüïéúóíðãŁńćščÉöçë'äšÜěşØøİğßÇ-]+\" ><a href=\"\/en\/players\/[a-z0-9]+\/[A-Za-z-]+\">[A-Za-z áüïéúóíðãŁńćščÉöçë'äšÜěşØøİğßÇ-]+<\/a><\/td><td class=\"left poptip\" data-stat=\"nationality\" data-tip=\"[A-Za-z]+\" ><a href=\"\/en\/country\/[A-Z]+\/[A-Za-z-]+\"><span style=\"white-space: nowrap\"><span class=\"f-i f-[a-z-]+\">[a-z]+<\/span> [A-Z]+<\/span><\/a><\/td><td class=\"center \" data-stat=\"position\" csk=\"[0-9]+\.[0-9]+\" >[A-Z,]+<\/td><td class=\"left \" data-stat=\"squad\" ><a href=\"\/en\/squads\/[a-z0-9]+\/[A-Za-z-]+-Stats\">([A-Za-z ]+)<\/a><\/td>", premier_league)
# Find the players' playing time
# players_playing_time = findall("<tr ><th scope=\"row\" class=\"right \" data-stat=\"ranker\" >[0-9]+<\/th><td class=\"left \" data-append-csv=\"[A-Za-z-]+\" data-stat=\"player\" csk=\"[A-Za-z, áüïéúóíðãŁńćščÉöçë'äšÜěşØøİğßÇ-]+\" ><a href=\"\/en\/players\/[a-z0-9]+\/[A-Za-z-]+\">[A-Za-z áüïéúóíðãŁńćščÉöçë'äšÜěşØøİğßÇ-]+<\/a><\/td><td class=\"left poptip\" data-stat=\"nationality\" data-tip=\"[A-Za-z]+\" ><a href=\"\/en\/country\/[A-Z]+\/[A-Za-z-]+\"><span style=\"white-space: nowrap\"><span class=\"f-i f-[a-z-]+\">[a-z]+<\/span> [A-Z]+<\/span><\/a><\/td><td class=\"center \" data-stat=\"position\" csk=\"[0-9]+\.[0-9]+\" >[A-Z,]+<\/td><td class=\"left \" data-stat=\"squad\" ><a href=\"\/en\/squads\/[a-z0-9]+\/[A-Za-z-]+-Stats\">[A-Za-z ]+<\/a><\/td><td class=\"center \" data-stat=\"age\" >[0-9-]+<\/td><td class=\"center \" data-stat=\"birth_year\" >[0-9]+<\/td><td class=\"right \" data-stat=\"games\" >[0-9]+<\/td><td class=\"[a-z ]+\" data-stat=\"games_starts\" >[0-9]+<\/td><td class=\"right \" data-stat=\"minutes\" csk=\"([0-9]+)\" >[0-9,]+", premier_league)

# Read the players' position CSV file using Pandas
positions = pd.read_csv('Positions.csv', delimiter = ';') # Read the CSV file in the same folder
player_name = positions.drop(['Pos', 'Squad', 'Min'], axis = 1)
player_club = positions.drop(['Player', 'Pos', 'Min'], axis = 1)
playing_time = positions.drop(['Player', 'Pos', 'Squad'], axis = 1)
positions = positions.drop(['Player', 'Squad', 'Min'], axis = 1) # Drop the players' name column

positions_list = [] # Create a blank list to store the new positions
premier_league_players = []
premier_league_players_club = []
players_playing_time = []

# A for loop to add the new positions to the list

for x in range(len(positions)):
    positions_list.append(positions.iloc[x].values.tolist())
    premier_league_players.append(player_name.iloc[x].values.tolist())
    premier_league_players_club.append(player_club.iloc[x].values.tolist())
    players_playing_time.append(playing_time.iloc[x].values.tolist())

# Create a blank database to store the players' informations
premier_league_database = []

# A for loop to group the sets of information with each other (with >= 300 mins playing time)

for i in range(0, len(premier_league_players)):

    player0 = [] # Create a blank list to add each player to the database

    playing_time = int(players_playing_time[i][0]) # Change playing time value from str to int

    # An if statement to determine if a player has played 300 minutes or more this season or not
    if (playing_time >= 300):

        player0.append(premier_league_players[i][0]) # Add player's name
        player0.append(positions_list[i][0]) # Add player's position from the positions_list list
        player0.append(premier_league_players_club[i][0]) # Add player's club

        premier_league_database.append(player0) # Add the player's informations into the database

# Choose a random player every time the code runs
random_player = premier_league_database[randint(0, len(premier_league_database))]
print(random_player)

# Define a function to set up the radar with a title and an endnote

def radar_mosaic(radar_height=0.915, title_height=0.06, figheight=14):
   
    endnote_height = 1 - title_height - radar_height
    figwidth = figheight * radar_height
    figure, axes = plt.subplot_mosaic([['title'], ['radar'], ['endnote']],
                                      gridspec_kw={'height_ratios': [title_height, radar_height,
                                                                     endnote_height],
                                                   'bottom': 0, 'left': 0, 'top': 1,
                                                   'right': 1, 'hspace': 0},
                                      figsize=(figwidth, figheight))
    axes['title'].axis('off')
    axes['endnote'].axis('off')
    return figure, axes

matplotlib.use('Agg')

# Create a radar based on the random player's position

def radar_creating(player = random_player):

    # Read all of the CSV files

    goalkeeper = pd.read_csv('Goalkeeper radar.csv', delimiter = ';')
    centre_back = pd.read_csv('Centre-back radar.csv', delimiter = ';')
    full_back = pd.read_csv('Full-back radar.csv', delimiter = ';')
    central_mid = pd.read_csv('CM-DM radar.csv', delimiter = ';')
    attacking_mid = pd.read_csv('AM-W radar.csv', delimiter = ';')
    forward = pd.read_csv('Striker radar.csv', delimiter = ';')

    if (player[1] == 'GK'): # If the random player is a goalkeeper...

        goalkeeper = goalkeeper.drop(['Squad'], axis = 1) # Remove non-stats columns

        goalkeeper_backup = goalkeeper

        goalkeeper = goalkeeper[(goalkeeper['Player'] == player[0])].reset_index() # Find the stats that belong to the random player

        # Create a list of parameters
        params = list(goalkeeper.columns)
        params = params[3:] # Slice list to remove the Player column

        low = [] # Create a list of lower boundaries
        high = [] # Create a list of higher boundaries
        values = [] # Create a list of values for the radar

        # For loops to add values to the lists above

        for x in params:
            a = min(goalkeeper_backup[params][x])
            low.append(a)
    
            b = max(goalkeeper_backup[params][x])
            high.append(b)

        for x in range(len(goalkeeper['Player'])):
            values = goalkeeper.iloc[x].values.tolist()

        values = values[3:] # Remove the name from the original values set
            
        # Set up values for the radar

        radar = Radar(params, low, high,
                      # Round values to integer or keep them as float values
                      round_int = [False] * 5,
                      num_rings = 6,  # The number of concentric circles (excluding center circle)
                      ring_width = 0.75, center_circle_radius = 0.5)

        # Create figures and axes using the function defined above
        fig, axs = radar_mosaic(radar_height = 0.8, title_height = 0.07, figheight = 12)

        # Load some fonts using mplsoccer's FontManager package
        URL1 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Thin.ttf?raw=true'
        robotto_thin = FontManager(URL1)
        URL2 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Regular.ttf?raw=true'
        robotto_regular = FontManager(URL2)
        URL3 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Bold.ttf?raw=true'
        robotto_bold = FontManager(URL3)

        # Determine team's colours to use for the radar

        if (player[2] == 'Arsenal') or (player[2] == 'Southampton') or (player[2] == 'Sheffield Utd'):
            
            kwargs_rings = {'facecolor': '#ed1c24'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#ed1c24'
        
        elif (player[2] == 'Aston Villa'):

            kwargs_radar = {'facecolor': '#480025'}
            kwargs_rings = {'facecolor': '#95bfe5'}
            title_color = '#480025'

        elif (player[2] == 'Brighton'):

            kwargs_rings = {'facecolor': '#0054a6'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#0054a6'

        elif (player[2] == 'Burnley'):

            kwargs_radar = {'facecolor': '#6a003a'}
            kwargs_rings = {'facecolor': '#99d6ea'}
            title_color = '#6a003a'

        elif (player[2] == 'Chelsea'):

            kwargs_rings = {'facecolor': '#0a4595'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#0a4595'

        elif (player[2] == 'Crystal Palace'):

            kwargs_radar = {'facecolor': '#1b458f'}
            kwargs_rings = {'facecolor': '#eb302e'}
            title_color = '#1b458f'

        elif (player[2] == 'Everton'):

            kwargs_rings = {'facecolor': '#00369c'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#00369c'

        elif (player[2] == 'Fulham'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#000000'}
            title_color = '#000000'

        elif (player[2] == 'Leeds United'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#1d428a'}
            title_color = '#1d428a'

        elif (player[2] == 'Leicester City'):

            kwargs_radar = {'facecolor': '#273e8a'}
            kwargs_rings = {'facecolor': '#fdbe11'}
            title_color = '#273e8a'

        elif (player[2] == 'Liverpool') or (player[2] == 'Manchester Utd'):

            kwargs_radar = {'facecolor': '#e31b23'}
            kwargs_rings = {'facecolor': '#f6eb61'}
            title_color = '#e31b23'

        elif (player[2] == 'Manchester City'):

            kwargs_radar = {'facecolor': '#6caee0'}
            kwargs_rings = {'facecolor': '#1c2c5b'}
            title_color = '#6caee0'

        elif (player[2] == 'Newcastle Utd'):

            kwargs_rings = {'facecolor': '#383838'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#383838'

        elif (player[2] == 'Tottenham') or (player[2] == 'West Brom'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#132257'}
            title_color = '#132257'

        elif (player[2] == 'West Ham'):

            kwargs_radar = {'facecolor': '#7d2c3b'}
            kwargs_rings = {'facecolor': '#1bb1e7'}
            title_color = '#7d2c3b'

        else:

            kwargs_radar = {'facecolor': '#f9a01b'}
            kwargs_rings = {'facecolor': '#231f20'}
            title_color = '#f9a01b'

        # Plot the radar
        radar.setup_axis(ax = axs['radar']) # Setup an axis to draw the radar
        rings_inner = radar.draw_circles(ax = axs['radar'], facecolor = '#b7b7b7', edgecolor = '#b7b7b7') # Draw inner circles
        radar_output = radar.draw_radar(values, ax = axs['radar'],
                                        kwargs_radar = kwargs_radar,
                                        kwargs_rings = kwargs_rings)
        radar_poly, rings_outer, vertices = radar_output
        range_labels = radar.draw_range_labels(ax = axs['radar'], fontsize = 19, 
                                               fontproperties = robotto_thin.prop)
        param_labels = radar.draw_param_labels(ax = axs['radar'], fontsize = 17, 
                                               fontproperties = robotto_regular.prop)

        # Adding the endnote and title text (these axes range from 0-1, i.e. 0, 0 is the bottom left)
        # Note we are slightly offsetting the text from the edges by 0.01 (1%, e.g. 0.99)
        endnote_text = axs['endnote'].text(0.99, 0.5, 'Created by @PlayersRadar/@dgouilard\nData via FBRef / Statsbomb', fontsize = 15,
                                           fontproperties = robotto_regular.prop, ha = 'right', va = 'center')
        title1_text = axs['title'].text(0.01, 0.65, player[0], fontsize = 27, fontproperties = robotto_bold.prop, 
                                        ha = 'left', va = 'center')
        title2_text = axs['title'].text(0.01, 0.3, player[2], fontsize = 18, fontproperties = robotto_regular.prop,
                                        ha = 'left', va = 'center', color = title_color)
        title3_text = axs['title'].text(0.99, 0.65, 'Radar Chart', fontsize = 24, fontproperties = robotto_regular.prop,
                                        ha='right', va='center')
        title4_text = axs['title'].text(0.99, 0.25, 'Template: Goalkeeper\nAll stats are per 90 minutes', fontsize = 14, fontproperties = robotto_regular.prop, 
                                        ha='right', va='center', color = '#cc2a3f')

        fig.set_facecolor("#ffffff")
        fig.set_figwidth(13)
        fig.set_figheight(13)
        
        plt.savefig("randomradar.png", facecolor = 'auto', edgecolor = 'auto', orientation = 'portrait', papertype = 'a2')
        
        plt.show()

    elif (player[1] == 'CB'):

        centre_back['Player'] = centre_back['Player'].str.split('\\', expand = True)[0]

        centre_back = centre_back.drop(['Squad'], axis = 1) # Remove non-stats columns

        centre_back_backup = centre_back

        centre_back = centre_back[(centre_back['Player'] == player[0])].reset_index() # Find the stats that belong to the random player

        centre_back_backup = centre_back_backup[(centre_back_backup['Pos'] == 'CB') & (centre_back_backup['Min'] >= 300)].reset_index()

        # Create a list of parameters
        params = list(centre_back.columns)
        params = params[4:] # Slice list to remove the Player column

        low = [] # Create a list of lower boundaries
        high = [] # Create a list of higher boundaries
        values = [] # Create a list of values for the radar

        # For loops to add values to the lists above

        for x in params:

            if (x == 'Dispossessed') | (x == 'Fouls Made') | (x == 'Dribbled Past'):
                a = max(centre_back_backup[params][x])
                low.append(a)
    
                b = min(centre_back_backup[params][x])
                high.append(b)
            else:
                a = min(centre_back_backup[params][x])
                low.append(a)
    
                b = max(centre_back_backup[params][x])
                high.append(b)

        for x in range(len(centre_back['Player'])):
            values = centre_back.iloc[x].values.tolist()

        values = values[4:] # Remove the name from the original values set

       # Set up values for the radar

        radar = Radar(params, low, high,
                      # Round values to integer or keep them as float values
                      round_int = [False] * 11,
                      num_rings = 6,  # The number of concentric circles (excluding center circle)
                      ring_width = 0.75, center_circle_radius = 0.5)

        # Create figures and axes using the function defined above
        fig, axs = radar_mosaic(radar_height = 0.8, title_height = 0.07, figheight = 12)

        # Load some fonts using mplsoccer's FontManager package
        URL1 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Thin.ttf?raw=true'
        robotto_thin = FontManager(URL1)
        URL2 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Regular.ttf?raw=true'
        robotto_regular = FontManager(URL2)
        URL3 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Bold.ttf?raw=true'
        robotto_bold = FontManager(URL3)

        # Determine team's colours to use for the radar

        if (player[2] == 'Arsenal') or (player[2] == 'Southampton') or (player[2] == 'Sheffield Utd'):
            
            kwargs_rings = {'facecolor': '#ed1c24'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#ed1c24'
        
        elif (player[2] == 'Aston Villa'):

            kwargs_radar = {'facecolor': '#480025'}
            kwargs_rings = {'facecolor': '#95bfe5'}
            title_color = '#480025'

        elif (player[2] == 'Brighton'):

            kwargs_rings = {'facecolor': '#0054a6'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#0054a6'

        elif (player[2] == 'Burnley'):

            kwargs_radar = {'facecolor': '#6a003a'}
            kwargs_rings = {'facecolor': '#99d6ea'}
            title_color = '#6a003a'

        elif (player[2] == 'Chelsea'):

            kwargs_rings = {'facecolor': '#0a4595'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#0a4595'

        elif (player[2] == 'Crystal Palace'):

            kwargs_radar = {'facecolor': '#1b458f'}
            kwargs_rings = {'facecolor': '#eb302e'}
            title_color = '#1b458f'

        elif (player[2] == 'Everton'):

            kwargs_rings = {'facecolor': '#00369c'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#00369c'

        elif (player[2] == 'Fulham'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#000000'}
            title_color = '#000000'

        elif (player[2] == 'Leeds United'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#1d428a'}
            title_color = '#1d428a'

        elif (player[2] == 'Leicester City'):

            kwargs_radar = {'facecolor': '#273e8a'}
            kwargs_rings = {'facecolor': '#fdbe11'}
            title_color = '#273e8a'

        elif (player[2] == 'Liverpool') or (player[2] == 'Manchester Utd'):

            kwargs_radar = {'facecolor': '#e31b23'}
            kwargs_rings = {'facecolor': '#f6eb61'}
            title_color = '#e31b23'

        elif (player[2] == 'Manchester City'):

            kwargs_radar = {'facecolor': '#6caee0'}
            kwargs_rings = {'facecolor': '#1c2c5b'}
            title_color = '#6caee0'

        elif (player[2] == 'Newcastle Utd'):

            kwargs_rings = {'facecolor': '#383838'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#383838'

        elif (player[2] == 'Tottenham') or (player[2] == 'West Brom'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#132257'}
            title_color = '#132257'

        elif (player[2] == 'West Ham'):

            kwargs_radar = {'facecolor': '#7d2c3b'}
            kwargs_rings = {'facecolor': '#1bb1e7'}
            title_color = '#7d2c3b'

        else:

            kwargs_radar = {'facecolor': '#f9a01b'}
            kwargs_rings = {'facecolor': '#231f20'}
            title_color = '#f9a01b'

        # Plot the radar
        radar.setup_axis(ax = axs['radar']) # Setup an axis to draw the radar
        rings_inner = radar.draw_circles(ax = axs['radar'], facecolor = '#b7b7b7', edgecolor = '#b7b7b7') # Draw inner circles
        radar_output = radar.draw_radar(values, ax = axs['radar'],
                                        kwargs_radar = kwargs_radar,
                                        kwargs_rings = kwargs_rings)
        radar_poly, rings_outer, vertices = radar_output
        range_labels = radar.draw_range_labels(ax = axs['radar'], fontsize = 19, 
                                               fontproperties = robotto_thin.prop)
        param_labels = radar.draw_param_labels(ax = axs['radar'], fontsize = 17, 
                                               fontproperties = robotto_regular.prop)

        # Adding the endnote and title text (these axes range from 0-1, i.e. 0, 0 is the bottom left)
        # Note we are slightly offsetting the text from the edges by 0.01 (1%, e.g. 0.99)
        endnote_text = axs['endnote'].text(0.99, 0.5, 'Created by @PlayersRadar/@dgouilard\nData via FBRef / Statsbomb', fontsize = 15,
                                           fontproperties = robotto_regular.prop, ha = 'right', va = 'center')
        title1_text = axs['title'].text(0.01, 0.65, player[0], fontsize = 25, fontproperties = robotto_bold.prop, 
                                        ha = 'left', va = 'center')
        title2_text = axs['title'].text(0.01, 0.3, player[2], fontsize = 18, fontproperties = robotto_regular.prop,
                                        ha = 'left', va = 'center', color = title_color)
        title3_text = axs['title'].text(0.99, 0.65, 'Radar Chart', fontsize = 24, fontproperties = robotto_regular.prop,
                                        ha='right', va='center')
        title4_text = axs['title'].text(0.99, 0.25, 'Template: Centre-back\nAll stats are per 90 minutes', fontsize = 14, fontproperties = robotto_regular.prop, 
                                        ha='right', va='center', color = '#cc2a3f')

        fig.set_facecolor("#ffffff")
        fig.set_figwidth(13)
        fig.set_figheight(13)
        
        plt.savefig("randomradar.png", facecolor = 'auto', edgecolor = 'auto', orientation = 'portrait', papertype = 'a2')
        
        plt.show()

    elif (player[1] == 'FB'):

        full_back['Player'] = full_back['Player'].str.split('\\', expand = True)[0]

        full_back = full_back.drop(['Squad'], axis = 1) # Remove non-stats columns

        full_back_backup = full_back

        full_back = full_back[(full_back['Player'] == player[0])].reset_index() # Find the stats that belong to the random player

        full_back_backup = full_back_backup[(full_back_backup['Pos'] == 'FB') & (full_back_backup['Min'] >= 300)].reset_index()

        # Create a list of parameters
        params = list(full_back.columns)
        params = params[4:] # Slice list to remove the Player column

        low = [] # Create a list of lower boundaries
        high = [] # Create a list of higher boundaries
        values = [] # Create a list of values for the radar

        # For loops to add values to the lists above

        for x in params:

            if (x == 'Dispossessed') | (x == 'Fouls Made') | (x == 'Dribbled Past'):
                a = max(full_back_backup[params][x])
                low.append(a)
    
                b = min(full_back_backup[params][x])
                high.append(b)
            else:
                a = min(full_back_backup[params][x])
                low.append(a)
    
                b = max(full_back_backup[params][x])
                high.append(b)

        for x in range(len(full_back['Player'])):
            values = full_back.iloc[x].values.tolist()

        values = values[4:] # Remove the name from the original values set

        # Set up values for the radar

        radar = Radar(params, low, high,
                      # Round values to integer or keep them as float values
                      round_int = [False] * 12,
                      num_rings = 6,  # The number of concentric circles (excluding center circle)
                      ring_width = 0.75, center_circle_radius = 0.5)

        # Create figures and axes using the function defined above
        fig, axs = radar_mosaic(radar_height = 0.8, title_height = 0.07, figheight = 12)

        # Load some fonts using mplsoccer's FontManager package
        URL1 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Thin.ttf?raw=true'
        robotto_thin = FontManager(URL1)
        URL2 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Regular.ttf?raw=true'
        robotto_regular = FontManager(URL2)
        URL3 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Bold.ttf?raw=true'
        robotto_bold = FontManager(URL3)

        # Determine team's colours to use for the radar

        if (player[2] == 'Arsenal') or (player[2] == 'Southampton') or (player[2] == 'Sheffield Utd'):
            
            kwargs_rings = {'facecolor': '#ed1c24'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#ed1c24'
        
        elif (player[2] == 'Aston Villa'):

            kwargs_radar = {'facecolor': '#480025'}
            kwargs_rings = {'facecolor': '#95bfe5'}
            title_color = '#480025'

        elif (player[2] == 'Brighton'):

            kwargs_rings = {'facecolor': '#0054a6'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#0054a6'

        elif (player[2] == 'Burnley'):

            kwargs_radar = {'facecolor': '#6a003a'}
            kwargs_rings = {'facecolor': '#99d6ea'}
            title_color = '#6a003a'

        elif (player[2] == 'Chelsea'):

            kwargs_rings = {'facecolor': '#0a4595'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#0a4595'

        elif (player[2] == 'Crystal Palace'):

            kwargs_radar = {'facecolor': '#1b458f'}
            kwargs_rings = {'facecolor': '#eb302e'}
            title_color = '#1b458f'

        elif (player[2] == 'Everton'):

            kwargs_rings = {'facecolor': '#00369c'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#00369c'

        elif (player[2] == 'Fulham'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#000000'}
            title_color = '#000000'

        elif (player[2] == 'Leeds United'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#1d428a'}
            title_color = '#1d428a'

        elif (player[2] == 'Leicester City'):

            kwargs_radar = {'facecolor': '#273e8a'}
            kwargs_rings = {'facecolor': '#fdbe11'}
            title_color = '#273e8a'

        elif (player[2] == 'Liverpool') or (player[2] == 'Manchester Utd'):

            kwargs_radar = {'facecolor': '#e31b23'}
            kwargs_rings = {'facecolor': '#f6eb61'}
            title_color = '#e31b23'

        elif (player[2] == 'Manchester City'):

            kwargs_radar = {'facecolor': '#6caee0'}
            kwargs_rings = {'facecolor': '#1c2c5b'}
            title_color = '#6caee0'

        elif (player[2] == 'Newcastle Utd'):

            kwargs_rings = {'facecolor': '#383838'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#383838'

        elif (player[2] == 'Tottenham') or (player[2] == 'West Brom'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#132257'}
            title_color = '#132257'

        elif (player[2] == 'West Ham'):

            kwargs_radar = {'facecolor': '#7d2c3b'}
            kwargs_rings = {'facecolor': '#1bb1e7'}
            title_color = '#7d2c3b'

        else:

            kwargs_radar = {'facecolor': '#f9a01b'}
            kwargs_rings = {'facecolor': '#231f20'}
            title_color = '#f9a01b'

        # Plot the radar
        radar.setup_axis(ax = axs['radar']) # Setup an axis to draw the radar
        rings_inner = radar.draw_circles(ax = axs['radar'], facecolor = '#b7b7b7', edgecolor = '#b7b7b7') # Draw inner circles
        radar_output = radar.draw_radar(values, ax = axs['radar'],
                                        kwargs_radar = kwargs_radar,
                                        kwargs_rings = kwargs_rings)
        radar_poly, rings_outer, vertices = radar_output
        range_labels = radar.draw_range_labels(ax = axs['radar'], fontsize = 19, 
                                               fontproperties = robotto_thin.prop)
        param_labels = radar.draw_param_labels(ax = axs['radar'], fontsize = 17, 
                                               fontproperties = robotto_regular.prop)

        # Adding the endnote and title text (these axes range from 0-1, i.e. 0, 0 is the bottom left)
        # Note we are slightly offsetting the text from the edges by 0.01 (1%, e.g. 0.99)
        endnote_text = axs['endnote'].text(0.99, 0.5, 'Created by @PlayersRadar/@dgouilard\nData via FBRef / Statsbomb', fontsize = 15,
                                           fontproperties = robotto_regular.prop, ha = 'right', va = 'center')
        title1_text = axs['title'].text(0.01, 0.65, player[0], fontsize = 25, fontproperties = robotto_bold.prop, 
                                        ha = 'left', va = 'center')
        title2_text = axs['title'].text(0.01, 0.3, player[2], fontsize = 18, fontproperties = robotto_regular.prop,
                                        ha = 'left', va = 'center', color = title_color)
        title3_text = axs['title'].text(0.99, 0.65, 'Radar Chart', fontsize = 24, fontproperties = robotto_regular.prop,
                                        ha='right', va='center')
        title4_text = axs['title'].text(0.99, 0.25, 'Template: Full-back\nAll stats are per 90 minutes', fontsize = 14, fontproperties = robotto_regular.prop, 
                                        ha='right', va='center', color = '#cc2a3f')
        
        fig.set_facecolor("#ffffff")
        fig.set_figwidth(13)
        fig.set_figheight(13)
        
        plt.savefig("randomradar.png", facecolor = 'auto', edgecolor = 'auto', orientation = 'portrait', papertype = 'a2')
        
        plt.show()

    elif (player[1] == 'CM'):

        central_mid['Player'] = central_mid['Player'].str.split('\\', expand = True)[0]

        central_mid = central_mid.drop(['Squad'], axis = 1) # Remove non-stats columns

        central_mid_backup = central_mid

        central_mid = central_mid[(central_mid['Player'] == player[0])].reset_index() # Find the stats that belong to the random player

        central_mid_backup = central_mid_backup[(central_mid_backup['Pos'] == 'CM') & (central_mid_backup['Min'] >= 300)].reset_index()

        # Create a list of parameters
        params = list(central_mid.columns)
        params = params[4:] # Slice list to remove the Player column

        low = [] # Create a list of lower boundaries
        high = [] # Create a list of higher boundaries
        values = [] # Create a list of values for the radar

        # For loops to add values to the lists above

        for x in params:

            if (x == 'Dispossessed') | (x == 'Fouls Made') | (x == 'Dribbled Past'):
                a = max(central_mid_backup[params][x])
                low.append(a)
    
                b = min(central_mid_backup[params][x])
                high.append(b)
            else:
                a = min(central_mid_backup[params][x])
                low.append(a)
    
                b = max(central_mid_backup[params][x])
                high.append(b)

        for x in range(len(central_mid['Player'])):
            values = central_mid.iloc[x].values.tolist()

        values = values[4:] # Remove the name from the original values set

        # Set up values for the radar

        radar = Radar(params, low, high,
                      # Round values to integer or keep them as float values
                      round_int = [False] * 11,
                      num_rings = 6,  # The number of concentric circles (excluding center circle)
                      ring_width = 0.75, center_circle_radius = 0.5)

        # Create figures and axes using the function defined above
        fig, axs = radar_mosaic(radar_height = 0.8, title_height = 0.07, figheight = 12)

        # Load some fonts using mplsoccer's FontManager package
        URL1 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Thin.ttf?raw=true'
        robotto_thin = FontManager(URL1)
        URL2 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Regular.ttf?raw=true'
        robotto_regular = FontManager(URL2)
        URL3 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Bold.ttf?raw=true'
        robotto_bold = FontManager(URL3)

        # Determine team's colours to use for the radar

        if (player[2] == 'Arsenal') or (player[2] == 'Southampton') or (player[2] == 'Sheffield Utd'):
            
            kwargs_rings = {'facecolor': '#ed1c24'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#ed1c24'
        
        elif (player[2] == 'Aston Villa'):

            kwargs_radar = {'facecolor': '#480025'}
            kwargs_rings = {'facecolor': '#95bfe5'}
            title_color = '#480025'

        elif (player[2] == 'Brighton'):

            kwargs_rings = {'facecolor': '#0054a6'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#0054a6'

        elif (player[2] == 'Burnley'):

            kwargs_radar = {'facecolor': '#6a003a'}
            kwargs_rings = {'facecolor': '#99d6ea'}
            title_color = '#6a003a'

        elif (player[2] == 'Chelsea'):

            kwargs_rings = {'facecolor': '#0a4595'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#0a4595'

        elif (player[2] == 'Crystal Palace'):

            kwargs_radar = {'facecolor': '#1b458f'}
            kwargs_rings = {'facecolor': '#eb302e'}
            title_color = '#1b458f'

        elif (player[2] == 'Everton'):

            kwargs_rings = {'facecolor': '#00369c'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#00369c'

        elif (player[2] == 'Fulham'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#000000'}
            title_color = '#000000'

        elif (player[2] == 'Leeds United'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#1d428a'}
            title_color = '#1d428a'

        elif (player[2] == 'Leicester City'):

            kwargs_radar = {'facecolor': '#273e8a'}
            kwargs_rings = {'facecolor': '#fdbe11'}
            title_color = '#273e8a'

        elif (player[2] == 'Liverpool') or (player[2] == 'Manchester Utd'):

            kwargs_radar = {'facecolor': '#e31b23'}
            kwargs_rings = {'facecolor': '#f6eb61'}
            title_color = '#e31b23'

        elif (player[2] == 'Manchester City'):

            kwargs_radar = {'facecolor': '#6caee0'}
            kwargs_rings = {'facecolor': '#1c2c5b'}
            title_color = '#6caee0'

        elif (player[2] == 'Newcastle Utd'):

            kwargs_rings = {'facecolor': '#383838'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#383838'

        elif (player[2] == 'Tottenham') or (player[2] == 'West Brom'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#132257'}
            title_color = '#132257'

        elif (player[2] == 'West Ham'):

            kwargs_radar = {'facecolor': '#7d2c3b'}
            kwargs_rings = {'facecolor': '#1bb1e7'}
            title_color = '#7d2c3b'

        else:

            kwargs_radar = {'facecolor': '#f9a01b'}
            kwargs_rings = {'facecolor': '#231f20'}
            title_color = '#f9a01b'

        # Plot the radar
        radar.setup_axis(ax = axs['radar']) # Setup an axis to draw the radar
        rings_inner = radar.draw_circles(ax = axs['radar'], facecolor = '#b7b7b7', edgecolor = '#b7b7b7') # Draw inner circles
        radar_output = radar.draw_radar(values, ax = axs['radar'],
                                        kwargs_radar = kwargs_radar,
                                        kwargs_rings = kwargs_rings)
        radar_poly, rings_outer, vertices = radar_output
        range_labels = radar.draw_range_labels(ax = axs['radar'], fontsize = 19, 
                                               fontproperties = robotto_thin.prop)
        param_labels = radar.draw_param_labels(ax = axs['radar'], fontsize = 17, 
                                               fontproperties = robotto_regular.prop)

        # Adding the endnote and title text (these axes range from 0-1, i.e. 0, 0 is the bottom left)
        # Note we are slightly offsetting the text from the edges by 0.01 (1%, e.g. 0.99)
        endnote_text = axs['endnote'].text(0.99, 0.5, 'Created by @PlayersRadar/@dgouilard\nData via FBRef / Statsbomb', fontsize = 15,
                                           fontproperties = robotto_regular.prop, ha = 'right', va = 'center')
        title1_text = axs['title'].text(0.01, 0.65, player[0], fontsize = 25, fontproperties = robotto_bold.prop, 
                                        ha = 'left', va = 'center')
        title2_text = axs['title'].text(0.01, 0.3, player[2], fontsize = 18, fontproperties = robotto_regular.prop,
                                        ha = 'left', va = 'center', color = title_color)
        title3_text = axs['title'].text(0.99, 0.65, 'Radar Chart', fontsize = 24, fontproperties = robotto_regular.prop,
                                        ha='right', va='center')
        title4_text = axs['title'].text(0.99, 0.25, 'Template: Central/Defensive Midfielder\nAll stats are per 90 minutes', fontsize = 14, 
                                        fontproperties = robotto_regular.prop, 
                                        ha='right', va='center', color = '#cc2a3f')

        fig.set_facecolor("#ffffff")
        fig.set_figwidth(13)
        fig.set_figheight(13)
        
        plt.savefig("randomradar.png", facecolor = 'auto', edgecolor = 'auto', orientation = 'portrait', papertype = 'a2')
        
        plt.show()

    elif (player[1] == 'AM') or (player[1] == 'W'):

        attacking_mid['Player'] = attacking_mid['Player'].str.split('\\', expand = True)[0]

        attacking_mid = attacking_mid.drop(['Squad'], axis = 1) # Remove non-stats columns

        attacking_mid_backup = attacking_mid

        attacking_mid = attacking_mid[(attacking_mid['Player'] == player[0])].reset_index() # Find the stats that belong to the random player

        attacking_mid_backup = attacking_mid_backup[(attacking_mid_backup['Pos'] == 'AM') | (attacking_mid_backup['Pos'] == 'W')
                                                    & (attacking_mid_backup['Min'] >= 300)].reset_index()

        # Create a list of parameters
        params = list(attacking_mid.columns)
        params = params[4:] # Slice list to remove the Player column

        low = [] # Create a list of lower boundaries
        high = [] # Create a list of higher boundaries
        values = [] # Create a list of values for the radar

        # For loops to add values to the lists above

        for x in params:

            if (x == 'Dispossessed') | (x == 'Fouls Made') | (x == 'Dribbled Past'):
                a = max(attacking_mid_backup[params][x])
                low.append(a)
    
                b = min(attacking_mid_backup[params][x])
                high.append(b)
            else:
                a = min(attacking_mid_backup[params][x])
                low.append(a)
    
                b = max(attacking_mid_backup[params][x])
                high.append(b)

        for x in range(len(attacking_mid['Player'])):
            values = attacking_mid.iloc[x].values.tolist()

        values = values[4:] # Remove the name from the original values set

        # Set up values for the radar

        radar = Radar(params, low, high,
                      # Round values to integer or keep them as float values
                      round_int = [False] * 11,
                      num_rings = 6,  # The number of concentric circles (excluding center circle)
                      ring_width = 0.75, center_circle_radius = 0.5)

        # Create figures and axes using the function defined above
        fig, axs = radar_mosaic(radar_height = 0.8, title_height = 0.07, figheight = 12)

        # Load some fonts using mplsoccer's FontManager package
        URL1 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Thin.ttf?raw=true'
        robotto_thin = FontManager(URL1)
        URL2 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Regular.ttf?raw=true'
        robotto_regular = FontManager(URL2)
        URL3 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Bold.ttf?raw=true'
        robotto_bold = FontManager(URL3)

        # Determine team's colours to use for the radar

        if (player[2] == 'Arsenal') or (player[2] == 'Southampton') or (player[2] == 'Sheffield Utd'):
            
            kwargs_rings = {'facecolor': '#ed1c24'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#ed1c24'
        
        elif (player[2] == 'Aston Villa'):

            kwargs_radar = {'facecolor': '#480025'}
            kwargs_rings = {'facecolor': '#95bfe5'}
            title_color = '#480025'

        elif (player[2] == 'Brighton'):

            kwargs_rings = {'facecolor': '#0054a6'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#0054a6'

        elif (player[2] == 'Burnley'):

            kwargs_radar = {'facecolor': '#6a003a'}
            kwargs_rings = {'facecolor': '#99d6ea'}
            title_color = '#6a003a'

        elif (player[2] == 'Chelsea'):

            kwargs_rings = {'facecolor': '#0a4595'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#0a4595'

        elif (player[2] == 'Crystal Palace'):

            kwargs_radar = {'facecolor': '#1b458f'}
            kwargs_rings = {'facecolor': '#eb302e'}
            title_color = '#1b458f'

        elif (player[2] == 'Everton'):

            kwargs_rings = {'facecolor': '#00369c'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#00369c'

        elif (player[2] == 'Fulham'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#000000'}
            title_color = '#000000'

        elif (player[2] == 'Leeds United'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#1d428a'}
            title_color = '#1d428a'

        elif (player[2] == 'Leicester City'):

            kwargs_radar = {'facecolor': '#273e8a'}
            kwargs_rings = {'facecolor': '#fdbe11'}
            title_color = '#273e8a'

        elif (player[2] == 'Liverpool') or (player[2] == 'Manchester Utd'):

            kwargs_radar = {'facecolor': '#e31b23'}
            kwargs_rings = {'facecolor': '#f6eb61'}
            title_color = '#e31b23'

        elif (player[2] == 'Manchester City'):

            kwargs_radar = {'facecolor': '#6caee0'}
            kwargs_rings = {'facecolor': '#1c2c5b'}
            title_color = '#6caee0'

        elif (player[2] == 'Newcastle Utd'):

            kwargs_rings = {'facecolor': '#383838'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#383838'

        elif (player[2] == 'Tottenham') or (player[2] == 'West Brom'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#132257'}
            title_color = '#132257'

        elif (player[2] == 'West Ham'):

            kwargs_radar = {'facecolor': '#7d2c3b'}
            kwargs_rings = {'facecolor': '#1bb1e7'}
            title_color = '#7d2c3b'

        else:

            kwargs_radar = {'facecolor': '#f9a01b'}
            kwargs_rings = {'facecolor': '#231f20'}
            title_color = '#f9a01b'

        # Plot the radar
        radar.setup_axis(ax = axs['radar']) # Setup an axis to draw the radar
        rings_inner = radar.draw_circles(ax = axs['radar'], facecolor = '#b7b7b7', edgecolor = '#b7b7b7') # Draw inner circles
        radar_output = radar.draw_radar(values, ax = axs['radar'],
                                        kwargs_radar = kwargs_radar,
                                        kwargs_rings = kwargs_rings)
        radar_poly, rings_outer, vertices = radar_output
        range_labels = radar.draw_range_labels(ax = axs['radar'], fontsize = 19, 
                                               fontproperties = robotto_thin.prop)
        param_labels = radar.draw_param_labels(ax = axs['radar'], fontsize = 17, 
                                               fontproperties = robotto_regular.prop)

        # Adding the endnote and title text (these axes range from 0-1, i.e. 0, 0 is the bottom left)
        # Note we are slightly offsetting the text from the edges by 0.01 (1%, e.g. 0.99)
        endnote_text = axs['endnote'].text(0.99, 0.5, 'Created by @PlayersRadar/@dgouilard\nData via FBRef / Statsbomb', fontsize = 15,
                                           fontproperties = robotto_regular.prop, ha = 'right', va = 'center')
        title1_text = axs['title'].text(0.01, 0.65, player[0], fontsize = 25, fontproperties = robotto_bold.prop, 
                                        ha = 'left', va = 'center')
        title2_text = axs['title'].text(0.01, 0.3, player[2], fontsize = 18, fontproperties = robotto_regular.prop,
                                        ha = 'left', va = 'center', color = title_color)
        title3_text = axs['title'].text(0.99, 0.65, 'Radar Chart', fontsize = 24, fontproperties = robotto_regular.prop,
                                        ha='right', va='center')
        title4_text = axs['title'].text(0.99, 0.25, 'Template: Attacking Midfielder/Winger\nAll stats are per 90 minutes', fontsize = 14, 
                                        fontproperties = robotto_regular.prop, 
                                        ha='right', va='center', color = '#cc2a3f')

        fig.set_facecolor("#ffffff")
        fig.set_figwidth(13)
        fig.set_figheight(13)
        
        plt.savefig("randomradar.png", facecolor = 'auto', edgecolor = 'auto', orientation = 'portrait', papertype = 'a2')
        
        plt.show()

    else:

        forward['Player'] = forward['Player'].str.split('\\', expand = True)[0]

        forward = forward.drop(['Squad'], axis = 1) # Remove non-stats columns

        forward_backup = forward

        forward = forward[(forward['Player'] == player[0])].reset_index() # Find the stats that belong to the random player

        forward_backup = forward_backup[(forward_backup['Pos'] == 'FW') & (forward_backup['Min'] >= 300)].reset_index()

        # Create a list of parameters
        params = list(forward.columns)
        params = params[4:] # Slice list to remove the Player column

        low = [] # Create a list of lower boundaries
        high = [] # Create a list of higher boundaries
        values = [] # Create a list of values for the radar

        # For loops to add values to the lists above

        for x in params:

            if (x == 'Dispossessed') | (x == 'Fouls Made') | (x == 'Dribbled Past'):
                a = max(forward_backup[params][x])
                low.append(a)
    
                b = min(forward_backup[params][x])
                high.append(b)
            else:
                a = min(forward_backup[params][x])
                low.append(a)
    
                b = max(forward_backup[params][x])
                high.append(b)

        for x in range(len(forward['Player'])):
            values = forward.iloc[x].values.tolist()

        values = values[4:] # Remove the name from the original values set

        # Set up values for the radar

        radar = Radar(params, low, high,
                      # Round values to integer or keep them as float values
                      round_int = [False] * 12,
                      num_rings = 6,  # The number of concentric circles (excluding center circle)
                      ring_width = 0.75, center_circle_radius = 0.5)

        # Create figures and axes using the function defined above
        fig, axs = radar_mosaic(radar_height = 0.8, title_height = 0.07, figheight = 12)

        # Load some fonts using mplsoccer's FontManager package
        URL1 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Thin.ttf?raw=true'
        robotto_thin = FontManager(URL1)
        URL2 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Regular.ttf?raw=true'
        robotto_regular = FontManager(URL2)
        URL3 = 'https://github.com/googlefonts/roboto/blob/main/src/hinted/Roboto-Bold.ttf?raw=true'
        robotto_bold = FontManager(URL3)

        # Determine team's colours to use for the radar

        if (player[2] == 'Arsenal') or (player[2] == 'Southampton') or (player[2] == 'Sheffield Utd'):
            
            kwargs_rings = {'facecolor': '#ed1c24'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#ed1c24'
        
        elif (player[2] == 'Aston Villa'):

            kwargs_radar = {'facecolor': '#480025'}
            kwargs_rings = {'facecolor': '#95bfe5'}
            title_color = '#480025'

        elif (player[2] == 'Brighton'):

            kwargs_rings = {'facecolor': '#0054a6'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#0054a6'

        elif (player[2] == 'Burnley'):

            kwargs_radar = {'facecolor': '#6a003a'}
            kwargs_rings = {'facecolor': '#99d6ea'}
            title_color = '#6a003a'

        elif (player[2] == 'Chelsea'):

            kwargs_rings = {'facecolor': '#0a4595'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#0a4595'

        elif (player[2] == 'Crystal Palace'):

            kwargs_radar = {'facecolor': '#1b458f'}
            kwargs_rings = {'facecolor': '#eb302e'}
            title_color = '#1b458f'

        elif (player[2] == 'Everton'):

            kwargs_rings = {'facecolor': '#00369c'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#00369c'

        elif (player[2] == 'Fulham'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#000000'}
            title_color = '#000000'

        elif (player[2] == 'Leeds United'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#1d428a'}
            title_color = '#1d428a'

        elif (player[2] == 'Leicester City'):

            kwargs_radar = {'facecolor': '#273e8a'}
            kwargs_rings = {'facecolor': '#fdbe11'}
            title_color = '#273e8a'

        elif (player[2] == 'Liverpool') or (player[2] == 'Manchester Utd'):

            kwargs_radar = {'facecolor': '#e31b23'}
            kwargs_rings = {'facecolor': '#f6eb61'}
            title_color = '#e31b23'

        elif (player[2] == 'Manchester City'):

            kwargs_radar = {'facecolor': '#6caee0'}
            kwargs_rings = {'facecolor': '#1c2c5b'}
            title_color = '#6caee0'

        elif (player[2] == 'Newcastle Utd'):

            kwargs_rings = {'facecolor': '#383838'}
            kwargs_radar = {'facecolor': '#d1d1d1'}
            title_color = '#383838'

        elif (player[2] == 'Tottenham') or (player[2] == 'West Brom'):

            kwargs_rings = {'facecolor': '#d1d1d1'}
            kwargs_radar = {'facecolor': '#132257'}
            title_color = '#132257'

        elif (player[2] == 'West Ham'):

            kwargs_radar = {'facecolor': '#7d2c3b'}
            kwargs_rings = {'facecolor': '#1bb1e7'}
            title_color = '#7d2c3b'

        else:

            kwargs_radar = {'facecolor': '#f9a01b'}
            kwargs_rings = {'facecolor': '#231f20'}
            title_color = '#f9a01b'

        # Plot the radar
        radar.setup_axis(ax = axs['radar']) # Setup an axis to draw the radar
        rings_inner = radar.draw_circles(ax = axs['radar'], facecolor = '#b7b7b7', edgecolor = '#b7b7b7') # Draw inner circles
        radar_output = radar.draw_radar(values, ax = axs['radar'],
                                        kwargs_radar = kwargs_radar,
                                        kwargs_rings = kwargs_rings)
        radar_poly, rings_outer, vertices = radar_output
        range_labels = radar.draw_range_labels(ax = axs['radar'], fontsize = 19, 
                                               fontproperties = robotto_thin.prop)
        param_labels = radar.draw_param_labels(ax = axs['radar'], fontsize = 17, 
                                               fontproperties = robotto_regular.prop)

        # Adding the endnote and title text (these axes range from 0-1, i.e. 0, 0 is the bottom left)
        # Note we are slightly offsetting the text from the edges by 0.01 (1%, e.g. 0.99)
        endnote_text = axs['endnote'].text(0.99, 0.5, 'Created by @PlayersRadar/@dgouilard\nData via FBRef / Statsbomb', fontsize = 15,
                                           fontproperties = robotto_regular.prop, ha = 'right', va = 'center')
        title1_text = axs['title'].text(0.01, 0.65, player[0], fontsize = 25, fontproperties = robotto_bold.prop, 
                                        ha = 'left', va = 'center')
        title2_text = axs['title'].text(0.01, 0.3, player[2], fontsize = 18, fontproperties = robotto_regular.prop,
                                        ha = 'left', va = 'center', color = title_color)
        title3_text = axs['title'].text(0.99, 0.65, 'Radar Chart', fontsize = 24, fontproperties = robotto_regular.prop,
                                        ha='right', va='center')
        title4_text = axs['title'].text(0.99, 0.25, 'Template: Forward\nAll stats are per 90 minutes', fontsize = 14, fontproperties = robotto_regular.prop, 
                                        ha='right', va='center', color = '#cc2a3f')

        fig.set_facecolor("#ffffff")
        fig.set_figwidth(13)
        fig.set_figheight(13)

        plt.savefig("randomradar.png", facecolor = 'auto', edgecolor = 'auto', orientation = 'portrait', papertype = 'a2')

        plt.show()

radar_creating(random_player)