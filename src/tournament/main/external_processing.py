"""Logic for retreiving and processing osu! API and Google Sheets data."""

#i don't really want to deal with figuring out how to get data from google sheets in production yet
#for now, the gsheets functionality is just for building a full db easier

from main.models import Player, Team, Map, Mappool

import os
import requests
from enum import IntFlag

#since heroku has its own environment variables
#if debug then load from main.env
if os.getenv("on_heroku") != "TRUE":
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=".env")

#region osu! api

api_key = os.getenv("osu_key")

#this probably won't be used at all here but just in case
class Mods(IntFlag):
    """Enum of the osu! mods exposed by the API.
    
    Underscores used for n-key mods because variable naming restrictions."""
    NM = 0,
    NF = 1,
    EZ = 2,
    TD = 4,
    HD = 8,
    HR = 16,
    SD = 32,
    DT = 64,
    RX = 128,
    HT = 256,
    NC = 512,
    FL = 1024,
    AT = 2048,
    SO = 4096,
    AP = 8192,
    PF = 16384,
    _4K = 32768,
    _5K = 65536,
    _6K = 131072,
    _7K = 262144,
    _8K = 524288,
    FI = 1048576,
    RD = 2097152,
    CN = 4194304,
    TP = 8388608,
    _9K = 16777216,
    CO = 33554432,
    _1K = 67108864,
    _3K = 134217728,
    _2K = 268435456,
    V2 = 536870912,
    MR = 1073741824

    def to_list(self):
        """Returns a list of strings represented by this enumeration."""
        mod_list = str(self).split("|")
        mod_list[0] = mod_list[0].split("Mods.")[1]
        return mod_list

#warning: osu! api v1 assumed for all below
def get_player_data(username):
    """Return JSON response of get_user from the osu! API with the given username."""
    #inherently works with either ID or username, ID preferred
    resp = requests.get(f'https://osu.ppy.sh/api/get_user?k={api_key}&u={username}')
    player_data = resp.json()
    return player_data[0]

def get_map_data(diff_id):
    """Return JSON response of get_beatmaps from the osu! API with the given diff id."""
    resp = requests.get(f'https://osu.ppy.sh/api/get_beatmaps?k={api_key}&b={diff_id}')
    map_data = resp.json()
    return map_data[0]

def get_match_data(match_id):
    """Return JSON response of get_beatmaps from the osu! API with the given diff id."""
    resp = requests.get(f'https://osu.ppy.sh/api/get_match?k={api_key}&mp={match_id}')
    match_data = resp.json()
    return match_data

#endregion

#region gsheets

#see https://www.geeksforgeeks.org/python-django-google-authentication-and-fetching-mails-from-scratch/
#will probably need this later
def get_all_gsheet_data(sheet_id):
    """Get data from Google Sheets."""
    #theoretically we'll need this practically never so imports occur here
    #if we find a need to regularly rebuild databases from gsheets, then we can move this out
    import pickle
    import os.path
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            #https://stackoverflow.com/questions/42519991/django-not-recognizing-or-seeing-json-file
            DIRNAME = os.path.dirname(__file__)
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(DIRNAME, 'google-credentials.json'), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    output = {}

    ranges = {
        'meta': 'meta!A2:B',
        'matches': 'matches!A2:F',
        'pools': 'pools!A2:D',
        'teams': 'teams!A2:E'
    }

    for range_id in ranges:
        range_name = ranges[range_id]
        result = sheet.values().get(spreadsheetId=sheet_id,
                                    range=range_name).execute()
        output[range_id] = result.get('values', [])

    return output

def create_players_and_teams(player_data):
    """Create new player and team instances based on gsheet data."""
    #teams need to be made first
    #done by converting the first element of each gsheet row to a string and using that as the team name
    #unfortunately this returns nothing and is too much of a pain to work with without the FKs
    #Team.objects.bulk_create([Team(team_name=row[0]) for row in player_data])

    #note: bulk-adding players might be an option but i won't implement rn
    for row in player_data:
        team_name = row[0]
        player_names = row[1:]
        team = Team.objects.create(team_name=team_name)
        for player_name in player_names:
            player_data = get_player_data(player_name)
            fields = {
                'osu_id': player_data["user_id"],
                'osu_name': player_data["username"],
                'country': "Nowhere", #it's probably time to make a field lmao - https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
                'country_code': player_data["country"],
                'osu_rank': player_data["pp_rank"],
                'osu_pp': player_data["pp_raw"],
                'country_rank': player_data["pp_country_rank"]
            }
            player = Player.objects.create(team=team, **fields)
            #print(player)
            #players.append(player)
    #Player.objects.bulk_create(players)

def create_pools_and_maps(pool_data):
    current_pool_object = None
    for row in pool_data:
        if row[0] != '':
            #this signifies that we are on a new mappool
            #so we now we make another pool

            #to maintain comaptibility with the bot's import function,
            #the use of "END" is supported here
            #the last "map" in a bulk add should always be ["END", ...]
            if row[0] != "END":
                metadata = row[0].split(", ")
                fields = {
                    'mappool_name':metadata[0],
                    'short_name': metadata[1]
                }
                current_pool_object = Mappool.objects.create(**fields)
            else:
                #don't process this row, which is the last
                break
        #get and process map data
        map_data = get_map_data(row[1])
        #be aware that there are no extra calculations for mod values here
        #(consider adding post-mod columns to gsheets?)
        fields = {
            'diff_id': map_data["beatmap_id"],
            'set_id': map_data["beatmapset_id"],
            'pool_id': row[3],
            'map_type': row[2],
            'artist': map_data["artist"],
            'title': map_data["title"],
            'diff_name': map_data['version'],
            'creator': map_data["creator"],
            'max_combo': map_data["max_combo"],
            'star_rating': map_data["difficultyrating"],
            'cs': map_data["diff_size"],
            'ar': map_data["diff_approach"],
            'od': map_data["diff_overall"],
            'hp': map_data["diff_drain"],
            'duration': map_data["total_length"]
        }
        Map.objects.create(mappool=current_pool_object, **fields)

def add_all_from_gsheets(sheet_id):
    data = get_all_gsheet_data(sheet_id)
    create_players_and_teams(data['teams'])
    create_pools_and_maps(data['pools'])

#endregion