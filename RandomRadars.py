
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

# + Package for radar charts
import pandas as pd
import matplotlib
import matplotlib.backends
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
# premier_league = download(url = 'https://fbref.com/en/comps/9/stats/Premier-League-Stats#stats_standard')

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
    if (playing_time >= 900):

        player0.append(premier_league_players[i][0]) # Add player's name
        player0.append(positions_list[i][0]) # Add player's position from the positions_list list
        player0.append(premier_league_players_club[i][0]) # Add player's club

        premier_league_database.append(player0) # Add the player's informations into the database

# Choose a random player every time the code runs
random_player = premier_league_database[randint(0, len(premier_league_database))]
print(random_player)

# for i in range(0, len(premier_league_database)):
    # if (premier_league_database[i][0] == "Lionel Messi"):
            # random_player = premier_league_database[i]

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

    # Determine team's colours to use for the radar

    if (player[2] == 'Arsenal') or (player[2] == 'Southampton') or (player[2] == 'Sheffield Utd') or (player[2] == 'Atlético Madrid') or (player[2] == 'Athletic Club') or (player[2] == 'Brest') or (player[2] == 'Dijon') or (player[2] == 'Granada') or (player[2] == 'Köln') or (player[2] == 'Lille') or (player[2] == 'Mainz 05') or (player[2] == 'Monaco') or (player[2] == 'Nîmes') or (player[2] == 'RB Leipzig') or (player[2] == 'Reims') or (player[2] == 'Rennes') or (player[2] == 'Sevilla') or (player[2] == 'Stuttgart') or (player[2] == 'Union Berlin'):
            
        kwargs_rings = {'facecolor': '#f72516'}
        kwargs_radar = {'facecolor': '#d1d1d1'}
        title_color = '#f72516'
        
    elif (player[2] == 'Aston Villa'):

        kwargs_radar = {'facecolor': '#480025'}
        kwargs_rings = {'facecolor': '#95bfe5'}
        title_color = '#480025'

    elif (player[2] == 'Brighton') or (player[2] == 'Strasbourg') or (player[2] == 'Schalke 04'):

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

    elif (player[2] == 'Fulham') or (player[2] == 'Eint Frankfurt') or (player[2] == 'Eintracht Frankfurt') or (player[2] == 'Leverkusen') or (player[2] == "M'Gladbach") or (player[2] == "Mönchengladbach") or (player[2] == 'Angers') or (player[2] == 'Juventus') or (player[2] == 'Parma') or (player[2] == 'Spezia'):

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

    elif (player[2] == 'Wolves'):

        kwargs_radar = {'facecolor': '#f9a01b'}
        kwargs_rings = {'facecolor': '#231f20'}
        title_color = '#f9a01b'

    elif (player[2] == 'Arminia'):

        kwargs_radar = {'facecolor': '#004e95'}
        kwargs_rings = {'facecolor': '#000000'}
        title_color = '#004e95'

    elif (player[2] == 'Augsburg'):

        kwargs_radar = {'facecolor': '#d1d1d1'}
        kwargs_rings = {'facecolor': '#008000'}
        title_color = '#008000'

    elif (player[2] == 'Bayern Munich'):

        kwargs_radar = {'facecolor': '#f30107'}
        kwargs_rings = {'facecolor': '#cef6e3'}
        title_color = '#f30107'

    elif (player[2] == 'Dortmund'):

        kwargs_radar = {'facecolor': '#fde100'}
        kwargs_rings = {'facecolor': '#231f20'}
        title_color = '#fde100'

    elif (player[2] == 'Freiburg') or (player[2] == 'Nice'):

        kwargs_radar = {'facecolor': '#fd1220'}
        kwargs_rings = {'facecolor': '#000000'}
        title_color = '#fd1220'

    elif (player[2] == 'Hertha BSC'):

        kwargs_radar = {'facecolor': '#201ef7'}
        kwargs_rings = {'facecolor': '#04003e'}
        title_color = '#201ef7'

    elif (player[2] == 'Hoffenheim'):

        kwargs_radar = {'facecolor': '#0b53c3'}
        kwargs_rings = {'facecolor': '#d1d1d1'}
        title_color = '#0b53c3'

    elif (player[2] == 'Union Berlin'):

        kwargs_radar = {'facecolor': '#008064'}
        kwargs_rings = {'facecolor': '#d1d1d1'}
        title_color = '#008064'

    elif (player[2] == 'Werder Bremen'):

        kwargs_radar = {'facecolor': '#008064'}
        kwargs_rings = {'facecolor': '#d1d1d1'}
        title_color = '#008064'

    elif (player[2] == 'Wolfsburg'):

        kwargs_radar = {'facecolor': '#0c4011'}
        kwargs_rings = {'facecolor': '#d1d1d1'}
        title_color = '#0c4011'

    elif (player[2] == 'Alavés'):

        kwargs_radar = {'facecolor': '#0a3ff5'}
        kwargs_rings = {'facecolor': '#d1d1d1'}
        title_color = '#0a3ff5'

    elif (player[2] == 'Barcelona'):

        kwargs_radar = {'facecolor': '#0000bf'}
        kwargs_rings = {'facecolor': '#9a0000'}
        title_color = '#9a0000'

    elif (player[2] == 'Betis'):

        kwargs_radar = {'facecolor': '#0b3b24'}
        kwargs_rings = {'facecolor': '#137f22'}
        title_color = '#0b3b24'

    elif (player[2] == 'Cádiz'):

        kwargs_radar = {'facecolor': '#ffe500'}
        kwargs_rings = {'facecolor': '#0000ff'}
        title_color = '#ffe500'

    elif (player[2] == 'Celta Vigo'):

        kwargs_radar = {'facecolor': '#aaddff'}
        kwargs_rings = {'facecolor': '#550099'}
        title_color = '#aaddff'

    elif (player[2] == 'Eibar'):

        kwargs_radar = {'facecolor': '#1a4991'}
        kwargs_rings = {'facecolor': '#d1d1d1'}
        title_color = '#1a4991'

    elif (player[2] == 'Elche'):

        kwargs_radar = {'facecolor': '#ffffff'}
        kwargs_rings = {'facecolor': '#99dd11'}
        title_color = '#99dd11'

    elif (player[2] == 'Getafe'):

        kwargs_radar = {'facecolor': '#005999'}
        kwargs_rings = {'facecolor': '#d1d1d1'}
        title_color = '#005999'

    elif (player[2] == 'Huesca'):

        kwargs_radar = {'facecolor': '#283380'}
        kwargs_rings = {'facecolor': '#cf122d'}
        title_color = '#283380'

    elif (player[2] == 'Levante'):

        kwargs_radar = {'facecolor': '#0000ff'}
        kwargs_rings = {'facecolor': '#b4053f'}
        title_color = '#0000ff'

    elif (player[2] == 'Osasuna'):

        kwargs_radar = {'facecolor': '#0a346f'}
        kwargs_rings = {'facecolor': '#d91a21'}
        title_color = '#d91a21'

    elif (player[2] == 'Real Madrid'):

        kwargs_radar = {'facecolor': '#d1d1d1'}
        kwargs_rings = {'facecolor': '#febe10'}
        title_color = '#00529f'

    elif (player[2] == 'Real Sociedad'):

        kwargs_radar = {'facecolor': '#143c8b'}
        kwargs_rings = {'facecolor': '#d1d1d1'}
        title_color = '#143c8b'

    elif (player[2] == 'Valencia'):

        kwargs_radar = {'facecolor': '#000000'}
        kwargs_rings = {'facecolor': '#ffdf1c'}
        title_color = '#000000'

    elif (player[2] == 'Villarreal'):

        kwargs_radar = {'facecolor': '#ffff00'}
        kwargs_rings = {'facecolor': '#005187'}
        title_color = '#ffff00'

    elif (player[2] == 'Valladolid'):

        kwargs_radar = {'facecolor': '#921b88'}
        kwargs_rings = {'facecolor': '#d1d1d1'}
        title_color = '#921b88'

    elif (player[2] == 'Bordeaux'):

        kwargs_radar = {'facecolor': '#00002f'}
        kwargs_rings = {'facecolor': '#d1d1d1'}
        title_color = '#00002f'

    elif (player[2] == 'Lens'):

        kwargs_radar = {'facecolor': '#ed1c24'}
        kwargs_rings = {'facecolor': '#fff200'}
        title_color = '#231f20'

    elif (player[2] == 'Lorient'):

        kwargs_radar = {'facecolor': '#ff4a00'}
        kwargs_rings = {'facecolor': '#000000'}
        title_color = '#ff4a00'

    elif (player[2] == 'Lyon'):

        kwargs_radar = {'facecolor': '#161659'}
        kwargs_rings = {'facecolor': '#da001a'}
        title_color = '#161659'

    elif (player[2] == 'Marseille'):

        kwargs_radar = {'facecolor': '#2faee0'}
        kwargs_rings = {'facecolor': '#bea064'}
        title_color = '#2faee0'

    elif (player[2] == 'Metz'):

        kwargs_radar = {'facecolor': '#6e0f12'}
        kwargs_rings = {'facecolor': '#d1d1d1'}
        title_color = '#6e0f12'

    elif (player[2] == 'Montpellier'):

        kwargs_radar = {'facecolor': '#000066'}
        kwargs_rings = {'facecolor': '#ff6600'}
        title_color = '#000066'

    elif (player[2] == 'Nantes'):

        kwargs_radar = {'facecolor': '#004433'}
        kwargs_rings = {'facecolor': '#ffff00'}
        title_color = '#004433'

    elif (player[2] == 'Paris S-G') or (player[2] == 'Paris Saint-Germain'):

        kwargs_radar = {'facecolor': '#000040'}
        kwargs_rings = {'facecolor': '#e30613'}
        title_color = '#000040'

    elif (player[2] == 'Saint-Étienne'):

        kwargs_radar = {'facecolor': '#d1d1d1'}
        kwargs_rings = {'facecolor': '#0c5025'}
        title_color = '#0c5025'

    elif (player[2] == 'Atalanta'):

        kwargs_radar = {'facecolor': '#0d0d41'}
        kwargs_rings = {'facecolor': '#141414'}
        title_color = '#0d0d41'

    elif (player[2] == 'Benevento'):

        kwargs_radar = {'facecolor': '#ffd400'}
        kwargs_rings = {'facecolor': '#e21a2b'}
        title_color = '#ffd400'

    elif (player[2] == 'Bologna') or (player[2] == 'Cagliari') or (player[2] == 'Genoa'):

        kwargs_radar = {'facecolor': '#1b2838'}
        kwargs_rings = {'facecolor': '#9f1f33'}
        title_color = '#1b2838'

    elif (player[2] == 'Crotone'):

        kwargs_radar = {'facecolor': '#373753'}
        kwargs_rings = {'facecolor': '#f43333'}
        title_color = '#373753'

    elif (player[2] == 'Fiorentina'):

        kwargs_radar = {'facecolor': '#5526b9'}
        kwargs_rings = {'facecolor': '#d1d1d1'}
        title_color = '#5526b9'

    elif (player[2] == 'Hellas Verona'):

        kwargs_radar = {'facecolor': '#ffed00'}
        kwargs_rings = {'facecolor': '#071397'}
        title_color = '#ffed00'

    elif (player[2] == 'Inter'):

        kwargs_radar = {'facecolor': '#0267ab'}
        kwargs_rings = {'facecolor': '#000000'}
        title_color = '#0267ab'

    elif (player[2] == 'Lazio'):

        kwargs_radar = {'facecolor': '#030347'}
        kwargs_rings = {'facecolor': '#b0d0ff'}
        title_color = '#b0d0ff'

    elif (player[2] == 'Milan'):

        kwargs_radar = {'facecolor': '#f72516'}
        kwargs_rings = {'facecolor': '#000000'}
        title_color = '#f72516'

    elif (player[2] == 'Roma'):

        kwargs_radar = {'facecolor': '#feb42f'}
        kwargs_rings = {'facecolor': '#731e25'}
        title_color = '#731e25'

    elif (player[2] == 'Sampdoria'):

        kwargs_radar = {'facecolor': '#0000ff'}
        kwargs_rings = {'facecolor': '#2737a3'}
        title_color = '#0000ff'

    elif (player[2] == 'Sassuolo'):

        kwargs_radar = {'facecolor': '#33b65b'}
        kwargs_rings = {'facecolor': '#231f20'}
        title_color = '#33b65b'

    elif (player[2] == 'Torino'):

        kwargs_radar = {'facecolor': '#55151a'}
        kwargs_rings = {'facecolor': '#ecb215'}
        title_color = '#55151a'

    else:

        kwargs_radar = {'facecolor': '#8b7d37'}
        kwargs_rings = {'facecolor': '#7f7f7f'}
        title_color = '#8b7d37'

    if (player[1] == 'GK'): # If the random player is a goalkeeper...

        goalkeeper = goalkeeper.drop(['Squad'], axis = 1) # Remove non-stats columns

        goalkeeper_backup = goalkeeper

        goalkeeper = goalkeeper[(goalkeeper['Player'] == player[0])].reset_index() # Find the stats that belong to the random player

        goalkeeper_backup = goalkeeper_backup[(goalkeeper_backup['Min'] >= 900)].reset_index()

        # Create a list of parameters
        params = list(goalkeeper.columns)
        params = params[4:] # Slice list to remove the Player column

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

        values = values[4:] # Remove the name from the original values set
            
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
        title1_text = axs['title'].text(0.05, 0.65, player[0], fontsize = 27, fontproperties = robotto_bold.prop, 
                                        ha = 'left', va = 'center')
        title2_text = axs['title'].text(0.05, 0.3, player[2], fontsize = 20, fontproperties = robotto_regular.prop,
                                        ha = 'left', va = 'center', color = title_color)
        title3_text = axs['title'].text(0.95, 0.65, 'Radar Chart', fontsize = 24, fontproperties = robotto_regular.prop,
                                        ha='right', va='center')
        title4_text = axs['title'].text(0.95, 0.25, 'Template: vs Goalkeepers in the Top 5 European Leagues\nAll stats are per 90 minutes', 
                                        fontsize = 15, fontproperties = robotto_regular.prop, 
                                        ha='right', va='center', color = '#cc2a3f')

        fig.set_facecolor("#ffffff")
        fig.set_figwidth(14)
        fig.set_figheight(14)
        
        plt.savefig("randomradar.png", facecolor = 'auto', edgecolor = 'auto', orientation = 'portrait', papertype = 'a2')

    elif (player[1] == 'CB'):

        centre_back['Player'] = centre_back['Player'].str.split('\\', expand = True)[0]

        centre_back = centre_back.drop(['Squad'], axis = 1) # Remove non-stats columns

        centre_back_backup = centre_back

        centre_back = centre_back[(centre_back['Player'] == player[0])].reset_index() # Find the stats that belong to the random player

        centre_back_backup = centre_back_backup[(centre_back_backup['Pos'] == 'CB') & (centre_back_backup['Min'] >= 900)].reset_index()

        # Create a list of parameters
        params = list(centre_back.columns)
        params = params[4:] # Slice list to remove the Player column

        low = [] # Create a list of lower boundaries
        high = [] # Create a list of higher boundaries
        values = [] # Create a list of values for the radar

        # For loops to add values to the lists above

        for x in params:

            if (x == 'Dispossessed') | (x == 'Fouls Made') | (x == 'Dribbled Past By Opposition'):
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
        endnote_text = axs['endnote'].text(0.985, 0.5, 'Created by @PlayersRadar/@dgouilard\nData via FBRef / Statsbomb', fontsize = 15,
                                           fontproperties = robotto_regular.prop, ha = 'right', va = 'center')
        title1_text = axs['title'].text(0.03, 0.65, player[0], fontsize = 27, fontproperties = robotto_bold.prop, 
                                        ha = 'left', va = 'center')
        title2_text = axs['title'].text(0.03, 0.3, player[2], fontsize = 20, fontproperties = robotto_regular.prop,
                                        ha = 'left', va = 'center', color = title_color)
        title3_text = axs['title'].text(0.985, 0.65, 'Radar Chart', fontsize = 24, fontproperties = robotto_regular.prop,
                                        ha='right', va='center')
        title4_text = axs['title'].text(0.985, 0.2, 'Template: vs Centre-backs in the Top 5 European Leagues\nAll stats are per 90 minutes', 
                                        fontsize = 15, fontproperties = robotto_regular.prop, 
                                        ha='right', va='center', color = '#cc2a3f')

        fig.set_facecolor("#ffffff")
        fig.set_figwidth(14)
        fig.set_figheight(14)
        
        plt.savefig("randomradar.png", facecolor = 'auto', edgecolor = 'auto', orientation = 'portrait', papertype = 'a2')

    elif (player[1] == 'FB'):

        full_back['Player'] = full_back['Player'].str.split('\\', expand = True)[0]

        full_back = full_back.drop(['Squad'], axis = 1) # Remove non-stats columns

        full_back_backup = full_back

        full_back = full_back[(full_back['Player'] == player[0])].reset_index() # Find the stats that belong to the random player

        full_back_backup = full_back_backup[(full_back_backup['Pos'] == 'FB') & (full_back_backup['Min'] >= 900)].reset_index()

        # Create a list of parameters
        params = list(full_back.columns)
        params = params[4:] # Slice list to remove the Player column

        low = [] # Create a list of lower boundaries
        high = [] # Create a list of higher boundaries
        values = [] # Create a list of values for the radar

        # For loops to add values to the lists above

        for x in params:

            if (x == 'Dispossessed') | (x == 'Fouls Made') | (x == 'Dribbled Past By Opposition'):
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
        endnote_text = axs['endnote'].text(0.985, 0.5, 'Created by @PlayersRadar/@dgouilard\nData via FBRef / Statsbomb', fontsize = 15,
                                           fontproperties = robotto_regular.prop, ha = 'right', va = 'center')
        title1_text = axs['title'].text(0.03, 0.65, player[0], fontsize = 27, fontproperties = robotto_bold.prop, 
                                        ha = 'left', va = 'center')
        title2_text = axs['title'].text(0.03, 0.3, player[2], fontsize = 20, fontproperties = robotto_regular.prop,
                                        ha = 'left', va = 'center', color = title_color)
        title3_text = axs['title'].text(0.985, 0.65, 'Radar Chart', fontsize = 24, fontproperties = robotto_regular.prop,
                                        ha='right', va='center')
        title4_text = axs['title'].text(0.985, 0.2, 'Template: vs Full-backs in the Top 5 European Leagues\nAll stats are per 90 minutes', 
                                        fontsize = 15, fontproperties = robotto_regular.prop, 
                                        ha='right', va='center', color = '#cc2a3f')
        
        fig.set_facecolor("#ffffff")
        fig.set_figwidth(14)
        fig.set_figheight(14)
        
        plt.savefig("randomradar.png", facecolor = 'auto', edgecolor = 'auto', orientation = 'portrait', papertype = 'a2')

    elif (player[1] == 'CM'):

        central_mid['Player'] = central_mid['Player'].str.split('\\', expand = True)[0]

        central_mid = central_mid.drop(['Squad'], axis = 1) # Remove non-stats columns

        central_mid_backup = central_mid

        central_mid = central_mid[(central_mid['Player'] == player[0])].reset_index() # Find the stats that belong to the random player

        central_mid_backup = central_mid_backup[(central_mid_backup['Pos'] == 'CM') & (central_mid_backup['Min'] >= 900)].reset_index()

        # Create a list of parameters
        params = list(central_mid.columns)
        params = params[4:] # Slice list to remove the Player column

        low = [] # Create a list of lower boundaries
        high = [] # Create a list of higher boundaries
        values = [] # Create a list of values for the radar

        # For loops to add values to the lists above

        for x in params:

            if (x == 'Dispossessed') | (x == 'Fouls Made') | (x == 'Dribbled Past By Opposition'):
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
        endnote_text = axs['endnote'].text(0.985, 0.5, 'Created by @PlayersRadar/@dgouilard\nData via FBRef / Statsbomb', fontsize = 15,
                                           fontproperties = robotto_regular.prop, ha = 'right', va = 'center')
        title1_text = axs['title'].text(0.03, 0.65, player[0], fontsize = 27, fontproperties = robotto_bold.prop, 
                                        ha = 'left', va = 'center')
        title2_text = axs['title'].text(0.03, 0.3, player[2], fontsize = 20, fontproperties = robotto_regular.prop,
                                        ha = 'left', va = 'center', color = title_color)
        title3_text = axs['title'].text(0.985, 0.65, 'Radar Chart', fontsize = 24, fontproperties = robotto_regular.prop,
                                        ha='right', va='center')
        title4_text = axs['title'].text(0.985, 0.2, 'Template: vs Central/Defensive Midfielders in the Top 5 European Leagues\nAll stats are per 90 minutes', 
                                        fontsize = 15, 
                                        fontproperties = robotto_regular.prop, 
                                        ha='right', va='center', color = '#cc2a3f')

        fig.set_facecolor("#ffffff")
        fig.set_figwidth(14)
        fig.set_figheight(14)
        
        plt.savefig("randomradar.png", facecolor = 'auto', edgecolor = 'auto', orientation = 'portrait', papertype = 'a2')

    elif (player[1] == 'AM'):

        attacking_mid = attacking_mid.drop(['Squad'], axis = 1) # Remove non-stats columns

        attacking_mid_backup = attacking_mid

        attacking_mid = attacking_mid[(attacking_mid['Player'] == player[0])].reset_index() # Find the stats that belong to the random player

        attacking_mid_backup = attacking_mid_backup[(attacking_mid_backup['Pos'] == 'AM') & (attacking_mid_backup['Min'] >= 900)].reset_index()

        # Create a list of parameters
        params = list(attacking_mid.columns)
        params = params[4:] # Slice list to remove the Player column

        low = [] # Create a list of lower boundaries
        high = [] # Create a list of higher boundaries
        values = [] # Create a list of values for the radar

        # For loops to add values to the lists above

        for x in params:

            if (x == 'Dispossessed') | (x == 'Fouls Made') | (x == 'Dribbled Past By Opposition'):
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
        endnote_text = axs['endnote'].text(0.985, 0.5, 'Created by @PlayersRadar/@dgouilard\nData via FBRef / Statsbomb', fontsize = 15,
                                           fontproperties = robotto_regular.prop, ha = 'right', va = 'center')
        title1_text = axs['title'].text(0.03, 0.65, player[0], fontsize = 27, fontproperties = robotto_bold.prop, 
                                        ha = 'left', va = 'center')
        title2_text = axs['title'].text(0.03, 0.3, player[2], fontsize = 20, fontproperties = robotto_regular.prop,
                                        ha = 'left', va = 'center', color = title_color)
        title3_text = axs['title'].text(0.985, 0.65, 'Radar Chart', fontsize = 24, fontproperties = robotto_regular.prop,
                                        ha='right', va='center')
        title4_text = axs['title'].text(0.985, 0.2, 'Template: vs Attacking Midfielders in the Top 5 European Leagues\nAll stats are per 90 minutes', 
                                        fontsize = 15, 
                                        fontproperties = robotto_regular.prop, 
                                        ha='right', va='center', color = '#cc2a3f')

        fig.set_facecolor("#ffffff")
        fig.set_figwidth(14)
        fig.set_figheight(14)
        
        plt.savefig("randomradar.png", facecolor = 'auto', edgecolor = 'auto', orientation = 'portrait', papertype = 'a2')

    elif (player[1] == 'W'):

        attacking_mid = attacking_mid.drop(['Squad'], axis = 1) # Remove non-stats columns

        attacking_mid_backup = attacking_mid

        attacking_mid = attacking_mid[(attacking_mid['Player'] == player[0])].reset_index() # Find the stats that belong to the random player

        attacking_mid_backup = attacking_mid_backup[(attacking_mid_backup['Pos'] == 'W') & (attacking_mid_backup['Min'] >= 900)].reset_index()

        # Create a list of parameters
        params = list(attacking_mid.columns)
        params = params[4:] # Slice list to remove the Player column

        low = [] # Create a list of lower boundaries
        high = [] # Create a list of higher boundaries
        values = [] # Create a list of values for the radar

        # For loops to add values to the lists above

        for x in params:

            if (x == 'Dispossessed') | (x == 'Fouls Made') | (x == 'Dribbled Past By Opposition'):
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
        endnote_text = axs['endnote'].text(0.985, 0.5, 'Created by @PlayersRadar/@dgouilard\nData via FBRef / Statsbomb', fontsize = 15,
                                           fontproperties = robotto_regular.prop, ha = 'right', va = 'center')
        title1_text = axs['title'].text(0.03, 0.65, player[0], fontsize = 27, fontproperties = robotto_bold.prop, 
                                        ha = 'left', va = 'center')
        title2_text = axs['title'].text(0.03, 0.3, player[2], fontsize = 20, fontproperties = robotto_regular.prop,
                                        ha = 'left', va = 'center', color = title_color)
        title3_text = axs['title'].text(0.985, 0.65, 'Radar Chart', fontsize = 24, fontproperties = robotto_regular.prop,
                                        ha='right', va='center')
        title4_text = axs['title'].text(0.985, 0.2, 'Template: vs Wingers in the Top 5 European Leagues\nAll stats are per 90 minutes', 
                                        fontsize = 15, 
                                        fontproperties = robotto_regular.prop, 
                                        ha='right', va='center', color = '#cc2a3f')

        fig.set_facecolor("#ffffff")
        fig.set_figwidth(14)
        fig.set_figheight(14)
        
        plt.savefig("randomradar.png", facecolor = 'auto', edgecolor = 'auto', orientation = 'portrait', papertype = 'a2')

    else:

        forward['Player'] = forward['Player'].str.split('\\', expand = True)[0]

        forward = forward.drop(['Squad'], axis = 1) # Remove non-stats columns

        forward_backup = forward

        forward = forward[(forward['Player'] == player[0])].reset_index() # Find the stats that belong to the random player

        forward_backup = forward_backup[(forward_backup['Pos'] == 'FW') & (forward_backup['Min'] >= 900)].reset_index()

        # Create a list of parameters
        params = list(forward.columns)
        params = params[4:] # Slice list to remove the Player column

        low = [] # Create a list of lower boundaries
        high = [] # Create a list of higher boundaries
        values = [] # Create a list of values for the radar

        # For loops to add values to the lists above

        for x in params:

            if (x == 'Dispossessed') | (x == 'Fouls Made') | (x == 'Dribbled Past By Opposition'):
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
        endnote_text = axs['endnote'].text(0.985, 0.5, 'Created by @PlayersRadar/@dgouilard\nData via FBRef / Statsbomb', fontsize = 15,
                                           fontproperties = robotto_regular.prop, ha = 'right', va = 'center')
        title1_text = axs['title'].text(0.03, 0.65, player[0], fontsize = 27, fontproperties = robotto_bold.prop, 
                                        ha = 'left', va = 'center')
        title2_text = axs['title'].text(0.03, 0.3, player[2], fontsize = 20, fontproperties = robotto_regular.prop,
                                        ha = 'left', va = 'center', color = title_color)
        title3_text = axs['title'].text(0.985, 0.65, 'Radar Chart', fontsize = 24, fontproperties = robotto_regular.prop,
                                        ha='right', va='center')
        title4_text = axs['title'].text(0.985, 0.2, 'Template: vs Forwards in the Top 5 European Leagues \nAll stats are per 90 minutes', 
                                        fontsize = 15, fontproperties = robotto_regular.prop, 
                                        ha='right', va='center', color = '#cc2a3f')

        fig.set_facecolor("#ffffff")
        fig.set_figwidth(14)
        fig.set_figheight(14)

        plt.savefig("randomradar.png", facecolor = 'auto', edgecolor = 'auto', orientation = 'portrait', papertype = 'a2')

radar_creating(random_player)