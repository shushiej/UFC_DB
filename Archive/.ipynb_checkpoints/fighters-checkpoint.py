import requests
from bs4 import BeautifulSoup
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
import json

UFC_FIGHTERS_HOST = "https://www.mixedmartialarts.com/fighter/"
UFC_RANKS_HOST = "https://www.ufc.com/rankings"

STATS = ["Age", "Gender", "Height", 
"Weight Class", "Out of", "Career Length", "Rounds Fought", 
"Avg. Fights/Year"]

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

GOOGLE_SHEET_KEY = "1XMAxYAcMwKDgsfO2yicIgH8eNs97k93oBoXTHd5wGIk"

CREDENTIALS_FILE = "My Project-c2276abeb298.json"

DUPLICATE_FIGHTERS = {}

CURRENT_ROW = 137

FIGHTER_RANK_DATA = {}

CURRENT_RANKS = {}

def read_file(filename):
    data = json.load(filename)
    return data

def write_to_file(filename, obj):
    with open(filename, 'w') as outfile:
        json.dump(obj, outfile)


def get_ufc_fighter_data(name, hardcoded = False): 
    FIGHTER_EXISTS = True
    DUPLICATE_FIGHTER = False
    try:
        if(hardcoded):
            r = requests.get(UFC_FIGHTERS_HOST + name)
        else:
            r = requests.get(UFC_FIGHTERS_HOST + "search?layout=&search="+name)

            if("error=nofighter" in r.url):
                FIGHTER_EXISTS = False
            elif("search?layout=&search=" in r.url):
                DUPLICATE_FIGHTER = True

        soup = BeautifulSoup(r.text, 'html.parser')
    except:
        print("Timeout")
        return
    stats_dict = {}

    if(FIGHTER_EXISTS):
        if(DUPLICATE_FIGHTER):
            stats_dict["duplicate"] = True
            return stats_dict

        name = soup.find('h1', {"class": "newsHeader"}).text.strip()

        for stat in STATS:
            stats_dict[stat] = get_table_data_from_heading(soup, stat)

        record = get_table_data_from_heading(soup, "Pro Record")
        record = record.split(" ")[0]
        wld = record.split("-")

        stats_dict["Wins"] = wld[0]
        stats_dict["Losses"]  = wld[1]
        stats_dict["Draws"]  = wld[2]

        stats_dict["KO Wins"] = get_table_data_from_heading(soup, "Wins", True)[0]
        stats_dict["Sub Wins"] = get_table_data_from_heading(soup, "Wins", True)[1]
        stats_dict["Dec Wins"] = get_table_data_from_heading(soup, "Wins", True)[2]

        stats_dict["KO Loss"] = get_table_data_from_heading(soup, "Losses", True)[0]
        stats_dict["Sub Loss"] = get_table_data_from_heading(soup, "Losses", True)[1]
        stats_dict["Dec Loss"] = get_table_data_from_heading(soup, "Losses", True)[2]

        stats_dict["Name"] = name

        streak = soup.findAll("h5", {"class": "fighter-info-title"})[2].text.strip() if len(soup.findAll("h5", {"class": "fighter-info-title"})) > 2 else 0
        stats_dict["Streak"] = streak

        stats_dict["duplicate"] = False
        
        return stats_dict

    return

def get_table_data_from_heading(soup, heading_name, multiple_siblings = False):
    el = soup.find("th", text=heading_name)
    if(el != None):
        if(multiple_siblings == True):
            all_sibs = []
            siblings = el.find_next_siblings("td")
            for s in siblings:
                all_sibs.append(s.text.strip())
            return all_sibs

        return el.find_next_sibling("td").text.strip()
    return

def get_ranks():
    try:
        r = requests.get(UFC_RANKS_HOST)
        soup = BeautifulSoup(r.text, 'html.parser')
    except:
        print("An Error Occurred")
        return
    
    get_last_updated_date(soup)
    classes = soup.findAll("div",{"class" : "view-grouping-content"})

    ranks = {}

    for c in classes:
        w_class = c.find("h4").text

        all_players = c.findAll("div", {"class" : "views-row"})
        players = []
        for p in all_players:
            players.append(p.text.lower())

        ranks[w_class] = players

    return ranks

def get_last_updated_date(soup):
    last_updated = soup.find("div", {"class" : "list-denotions"}).find("p", recursive=False).text
    return last_updated.split(":")[1].strip

def get_fighter_ranks():
    sheet = set_up_google_sheet()
    player_stats = sheet.get_worksheet(0)
    fighters = [x.lower() for x in player_stats.col_values(1)[1:]]
    fighter_rank = player_stats.col_values(14)[1:]
    fighter_class = player_stats.col_values(2)[1:]
    fighter_gender = player_stats.col_values(3)[1:]
    data = dict(zip(fighters, list(map(list,zip(fighter_rank, fighter_class, fighter_gender)))))

    return data

def get_current_rank_data():
    if(not CURRENT_RANKS):
        return get_ranks()

    return CURRENT_RANKS

def get_fighter_rank_data():
    if(not FIGHTER_RANK_DATA):
        return get_fighter_ranks()

    return FIGHTER_RANK_DATA


def set_up_google_sheet():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    gc = gspread.authorize(credentials)
    sheet = gc.open_by_key(GOOGLE_SHEET_KEY)

    return sheet

def update_sheet():
    sheet = set_up_google_sheet()
    player_stats = sheet.get_worksheet(0)
    data_file = read_file('./metadata.json')

    while(player_stats.acell("A"+str(data_file['current_row'])).value != ""):
        fighter_name = player_stats.acell("A"+str(data_file['current_row'])).value
        # Check if duplicate fighter
        data = get_ufc_fighter_data(fighter_name)

        if(data):
            if(data["duplicate"] == True):
                DUPLICATE_FIGHTERS[data_file['current_row']] = fighter_name
            else:
                player_stats.update_acell("B"+str(data_file['current_row']), data["Weight Class"])
                player_stats.update_acell("R"+str(data_file['current_row']), data["KO Loss"])
                player_stats.update_acell("S"+str(data_file['current_row']), data["Sub Loss"])
                player_stats.update_acell("T"+str(data_file['current_row']), data["Dec Loss"])
                player_stats.update_acell("U"+str(data_file['current_row']), data["Career Length"])

        data_file['current_row'] = data_file['current_row'] + 1
    



# Keep a Dict of row numbers and duplicate names. 



def update_existing_fighter(row):
    return

def add_new_fighter(name):
    return

def update_ranks():
    FIGHTER_RANK_DATA = get_fighter_rank_data()
    CURRENT_RANKS = get_current_rank_data()
    new_ranks = {}
    for k,v in FIGHTER_RANK_DATA.items():
        w_class = v[1]
        gender = v[2]

        if(gender == 'F'):
            v[1] = "Women's " + w_class

        if(w_class == 'Light-heavyweight'):
            v[1] = "Light Heavyweight"


        if(v[1] in CURRENT_RANKS.keys()):
            if(k in CURRENT_RANKS[v[1]]):
                new_ranks[k] = CURRENT_RANKS[v[1]].index(k)

    row = 2
    sheet = set_up_google_sheet()
    player_stats = sheet.get_worksheet(0)

    while(player_stats.acell("A"+str(row)).value != ""):
        fighter_name = player_stats.acell("A"+str(row)).value.lower()
        if(fighter_name in new_ranks.keys()):
             player_stats.update_acell("N"+str(row), new_ranks[fighter_name])
        else:
            player_stats.update_acell("N"+str(row), "-1")
        row = row + 1

update_ranks() 