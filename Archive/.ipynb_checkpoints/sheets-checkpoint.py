import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

GOOGLE_SHEET_KEY = "1XMAxYAcMwKDgsfO2yicIgH8eNs97k93oBoXTHd5wGIk"

credentials = ServiceAccountCredentials.from_json_keyfile_name('My Project-c2276abeb298.json', scope)

gc = gspread.authorize(credentials)
sheet = gc.open_by_key(GOOGLE_SHEET_KEY)

player_stats = sheet.get_worksheet(0)
fight_info = sheet.get_worksheet(1)

print(fight_info.acell('A10'))