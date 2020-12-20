"""Logic for retreiving and processing osu! API and Google Sheets data."""

#i don't really want to deal with figuring out how to get data from google sheets in production yet
#for now, the gsheets functionality is just for building a full db easier

from main.models import Player, Team, Map, Mappool, Match, Score, Stage

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
    if map_data:
        return map_data[0] 
    else:  
        return None

def get_match_data(match_id):
    """Return JSON response of get_beatmaps from the osu! API with the given diff id."""
    resp = requests.get(f'https://osu.ppy.sh/api/get_match?k={api_key}&mp={match_id}')
    match_data = resp.json()
    return match_data

def process_match_data(match_id, map, *, data=None, player_ids={}, ignore_threshold=1000, ignore_player_ids=[]):
    #no head-to-head functionality yet
    """Returns a dict of match data tailored for stat calculation.
    
    `data` is expected to be the data of a `get_match_data()` call, and is used in lieu of calling
    the osu! API - helpful if successive calls of this function for the same match occur.
    Otherwise, `match_id` is used to get match data, then the nth `map` (zero-indexed) is 
    obtained and processed. If available, `player_ids` should be provided, a dict of `player_ids`
    (str) to [`player_names` (str), `team_name` (str)].

    Map indexes are redirected like other paginated functions; indexes less than 0 become 0, and 
    indexes greater than the max index become the max index.

    - `ignore_player_list` will ignore specific player ids from calculation. 
    - `ignore_threshold` will ignore scores below a specific value. 1000 by default.

    This function aims to expose useful data not normally available from the get_match
    endpoint of the API.

    Returns the following dict:
    ```
    {
        "match_name": str,
        "match_id": str,
        "match_url": f'https://osu.ppy.sh/community/matches/{match_id}',
        "diff_id": str,
        "diff_url": f'https://osu.ppy.sh/b/{diff_id}',
        "map_thumbnail": f'https://b.ppy.sh/thumb/{diff_id}l.jpg',
        "map_name": f'{artist} - {title}',
        "winner": str, #(1 or 2)
        "score_difference": int,
        "team_1_score": int,
        "team_2_score": int, 
        "team_1_score_avg": float,
        "team_2_score_avg": float,
        "individual_scores": [
            {
                "user_id": str,
                "user_name": str,
                "score": int,
                "combo": int,
                "accuracy": float,
                "mod_val": int,
                "mods": [str, str, ...],
                "pass": str, #"0" or "1", where "0" is fail
                "hits": {
                    "300_count": int,
                    "100_count": int,
                    "50_count": int,
                    "miss_count": int
                },
                "team_contrib": float,
                "team": str #1 or 2,
                "team_name": str #equivalent to the _id of a Team document
            }, ...
        ]
        "start_time": str,
        "scoring_type": str,
        "team_type": str,
        "play_mode": str,
        "player_ids": {str: str, ...} #key is player id as str, value is actual username as str
    }
    ```
    """
    match_data = data

    if not match_data:
        match_data = get_match_data(match_id)

    max_index = len(match_data["games"])-1
    if map < 0:
        map = 1
    if map > max_index:
        map = max_index

    game_data = match_data["games"][int(map)]

    #stop execution here if no scores are available, but there was a game for some reason
    if not game_data['scores']:
        return None
    map_data = get_map_data(game_data["beatmap_id"])
    #now we'll start number crunching and stuff
    
    #if head-to-head or tag co-op is selected
    if game_data['team_type'] in ('0', '1'):
        #currently unsupported!
        return None

    #if a team mode is selected
    if game_data['team_type'] in ('2', '3'):
        #determine who belongs in what team as well as the team scores
        #as of now this is only used to get the number of players on a team, since we use
        #a conditional to add teams to the correct field anyways
        team_1_players = []
        team_2_players = []
        team_1_score = 0
        team_2_score = 0
        for player_score in game_data['scores']:
            #ignore if below minimum score threshold or in ignore list
            if int(player_score["score"]) < ignore_threshold or player_score["user_id"] in ignore_player_ids:
                continue
            if player_score["team"] == "1":
                team_1_players.append(player_score["user_id"])
                team_1_score += int(player_score["score"])
            if player_score["team"] == "2":
                team_2_players.append(player_score["user_id"])
                team_2_score += int(player_score["score"])

        #who won
        if team_1_score != team_2_score:
            winner = "Blue" if team_1_score > team_2_score else "Red"
        else:
            winner = "Tie"

        #score diff
        score_diff = abs(team_1_score-team_2_score)

        #generate the data for individual player scores for this map
        individual_scores = []
        for player_score in game_data["scores"]:
            #ignore if below minimum score threshold or in ignore list
            if int(player_score["score"]) < ignore_threshold or player_score["user_id"] in ignore_player_ids:
                continue
            count_300 = int(player_score["count300"])
            count_100 = int(player_score["count100"])
            count_50 = int(player_score["count50"])
            count_miss = int(player_score["countmiss"])
            acc_count = count_300 + count_100 + count_50 + count_miss
            acc_value = (count_300+(count_100/3)+(count_50/6))/acc_count
            score = int(player_score["score"])
            contrib = score/team_1_score if player_score["team"] == "1" else score/team_2_score
            
            #if we don't currently know what the name of a certain player id is, look it up against the mongodb and osuapi, in that order
            #might fail if the player is restricted, not sure on that
            try:
                player_name = player_ids[player_score["user_id"]][0]
                team_name = player_ids[player_score["user_id"]][1]
            except:
                #print(f"Hit DB for player ID {player_score['user_id']}")
                try:
                    player = Player.objects.get(osu_id=player_score["user_id"])
                    player_name = player.osu_name
                    team_name = player.team.team_name
                except Player.DoesNotExist:
                    #this means that we don't have this player saved for some reason
                    #so we'll go the alternative route, getting the username manually
                    #this'll probably happen if somebody tries to get a non-tournament mp
                    print(f"Lookup for {player_score['user_id']} failed, resorting to osu! api")
                    player_data = get_player_data(player_score["user_id"])
                    player_name = player_data["username"]
                    team_name = ""
                #add to player_ids dict, which will help us build a cache over time for certain processes
                player_ids[player_score["user_id"]] = [player_name, team_name]
            individual_score = {
                "user_id": player_score["user_id"],
                "user_name": player_name,
                "score": score,
                "combo": int(player_score["maxcombo"]),
                "accuracy": acc_value,
                "mod_val": int(game_data["mods"]),
                "mods": Mods(int(game_data["mods"])).to_list(), #global mods assumed
                "pass": player_score["pass"],
                "hits": {
                    "300_count": count_300,
                    "100_count": count_100,
                    "50_count": count_50,
                    "miss_count": count_miss
                },
                "team_contrib": contrib,
                "team": player_score["team"],
                "team_name": team_name
            }
            individual_scores.append(individual_score)
        #import pprint
        #pprint.pprint(match_data)
        #pprint.pprint(game_data)
        if map_data:
            map_name = f'{map_data["artist"]} - {map_data["title"]} [{map_data["version"]}]'
        else:
            map_name = "deleted beatmap"
        team_vs_final = {
            "match_name": match_data["match"]["name"],
            "match_id": match_id,
            "match_url": f'https://osu.ppy.sh/community/matches/{match_id}',
            "diff_id": game_data["beatmap_id"],
            "diff_url": f'https://osu.ppy.sh/b/{game_data["beatmap_id"]}',
            "map_name": map_name,
            "winner": winner,
            "score_difference": score_diff,
            "team_1_score": team_1_score,
            "team_2_score": team_2_score, 
            "team_1_score_avg": round(team_1_score/len(team_1_players),2) if len(team_1_players) != 0 else 0,
            "team_2_score_avg": round(team_2_score/len(team_2_players),2) if len(team_2_players) != 0 else 0,
            "individual_scores": individual_scores,
            "start_time": game_data["start_time"],
            "scoring_type": game_data["scoring_type"],
            "team_type": game_data["team_type"],
            "play_mode": game_data["play_mode"],
            "player_ids": player_ids
        }
        return team_vs_final

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
        'matches': 'matches!A2:G',
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
        map_data = get_map_data(row[1]) #this could return None but there's no support for pooling deleted beatmaps lol
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

def create_match_from_import(api_match_data, match_id, stage):
    """Create match with the given api_match_data. 
    
    Goes over every game and player until it sees at least
    two players from two distinct teams (to prevent referees from
    being counted).
    
    Returns Match object, None if teams couldn't be determined."""
    #see if it's possible to create the required fields

    for index, game_data in enumerate(api_match_data["games"]):
        team_1 = None
        team_1_check = False
        team_2 = None
        team_2_check = False
        processed = process_match_data(api_match_data["match"]["match_id"], index, data=api_match_data)
        if processed == None:
            continue
        for score in processed["individual_scores"]:
            try:
                player = Player.objects.get(osu_id=score["user_id"])
            except Player.DoesNotExist:
                continue
            if not team_1:
                team_1 = player.team
                continue
            if not team_2:
                if player.team == team_1:
                    team_1_check = True
                    continue
                else:
                    team_2 = player.team
                    continue
            if not team_2_check:
                if player.team == team_2:
                    team_2_check = True
                    continue
        if team_1_check and team_2_check:
            #print(f"mp/{api_match_data['match']['match_id']}: {team_1.team_name}vs.{team_2.team_name}")
            return Match.objects.create(match_id=match_id, team_1=team_1, team_2=team_2, stage=stage)
    return None

def create_stages(match_data):
    stages = []
    stage_objs = []
    for row in match_data:
        if row[3] not in stages:
            stages.append(row[3])
    for stage in stages:
        stage_objs.append(Stage(stage_name=stage))
    Stage.objects.bulk_create(stage_objs)
    
#this creates matches, not updates them!!
#needs to be rewritten if needed to do update magic
def create_matches(match_data):
    scores = []
    player_id_cache = {}
    for row in match_data:
        api_match_data = get_match_data(row[0])
        if not api_match_data['games']:
            continue

        try:
            match = Match.objects.get(match_id=row[6])
        except Match.DoesNotExist:
            stage = Stage.objects.get(stage_name=row[3])
            match = create_match_from_import(api_match_data, row[6], stage)
        

        #we don't determine the pool name until we're inside the for loop
        #which is why processing this match's bans ended up inside
        #i can't think of any better alternatives that wouldn't do the same pool-finding process anyways
        bans_processed = False

        for index, game_data in enumerate(api_match_data["games"]):
            #ignoring maps if they are either not in pool or explicitly ignored
            if index in [int(map_index) for map_index in row[5].split(",")]:
                continue
            processed = process_match_data(row[0], index, data=api_match_data, player_ids=player_id_cache)
            if processed == None:
                continue
            player_id_cache = processed["player_ids"] #update the player id cache
            try:
                #a single "map" is part of a "game"
                game_map = Map.objects.get(diff_id=processed["diff_id"])
                game_map.pick_count += 1
            except Map.DoesNotExist:
                #this map isn't in the pool; don't go any further
                #get() with no results returns <Model>.DoesNotExist
                continue
            
            #process bans for this match if needed
            if not bans_processed:
                for ban_shorthand in [str(banned_id) for banned_id in row[4].split(",")]:
                    #print(f"Processing {ban_shorthand} for {game_map.mappool} (stage {row[3]}, id {row[0]})")
                    banned_map = Map.objects.get(mappool=game_map.mappool, pool_id=ban_shorthand)
                    banned_map.ban_count += 1
                    banned_map.save()
                    match.bans.add(banned_map)
                bans_processed = True

            #oh my god the function complexity lol
            for score in processed["individual_scores"]:
                player = Player.objects.get(osu_id=score["user_id"])
                #generate score fields
                fields = {
                    "player": player,
                    "team": player.team,
                    "match": match,
                    "match_index": index,
                    "map": game_map,
                    "score": score["score"],
                    "combo": score["combo"],
                    "accuracy":score["accuracy"],
                    "team_total": processed["team_1_score"] if score["team"]==1 else processed["team_2_score"],
                    "score_difference": processed["score_difference"] if processed["winner"] == score["team"] else -(processed["score_difference"]),
                    "contrib": score["score"]/processed["team_1_score"] if score["team"] == "1" else score["score"]/processed["team_2_score"],
                    "count_300": score["hits"]["300_count"],
                    "count_100": score["hits"]["100_count"],
                    "count_50": score["hits"]["50_count"],
                    "count_miss": score["hits"]["miss_count"],
                }
                scores.append(Score(**fields))
    Score.objects.bulk_create(scores)

def add_all_from_gsheets(sheet_id):
    data = get_all_gsheet_data(sheet_id)
    create_players_and_teams(data['teams'])
    create_pools_and_maps(data['pools'])
    create_stages(data['matches'])
    create_matches(data['matches'])

#endregion