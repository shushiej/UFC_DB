import requests
from bs4 import BeautifulSoup

HOST = "https://www.ufc.com/rankings"


def update_ranks():
    try:
        r = requests.get(HOST)
        soup = BeautifulSoup(r.text, 'html.parser')
    except:
        print("An Error Occurred")
        return
    

    classes = soup.findAll("div",{"class" : "view-grouping-content"})

    ranks = {}

    for c in classes:
        w_class = c.find("h4").text

        all_players = c.findAll("div", {"class" : "views-row"})
        players = []
        for p in all_players:
            players.append(p.text)

        ranks[w_class] = players

    return ranks


ranks = update_ranks()
