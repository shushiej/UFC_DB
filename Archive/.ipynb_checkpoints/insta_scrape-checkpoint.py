import requests
from bs4 import BeautifulSoup
import mechanize

HOST = "https://www.instagram.com/accounts/login/?next=/explore/"

r = requests.post("https://www.instagram.com/accounts/login/ajax/facebook/", json={"accessToken" : "EAABwzLixnjYBAPErusVT9RhpsMs4SZB82hEuceDHQdn07UoihOl7GPq8FdqRor12qlYFAHIfCPYdBYSFzUBTpUOasJcPD2UDZBlvgYtTMizi7WBO4RypZAgCVmuHk9uZAEzDvutcSgWIQYaCIVEUbLIyRxhzHdM0hfrHdkl3GtEw4naiW7uZBBJjZCsRFPwVEAjWvJVtK1DAZDZD",
                                                                                    "fbUserId": 667266977,
                                                                                    "queryParams": {"next":"/explore/"}})

#r = requests.get("https://www.instagram.com/explore/")

#soup = BeautifulSoup(r.text, 'html.parser')

print(r.text)

#images = soup.findAll("div", {"class" : "Nnq7C"})

