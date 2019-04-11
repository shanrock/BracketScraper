from bs4 import BeautifulSoup as soup
import pyodbc
import requests
import itertools as it
import re
from dateutil.parser import parse

def scrape_data(url):
    url = '{}{}'.format(base_url,day)
    response = requests.get(url)
    soupy = soup(response.content, 'lxml')     
    # connecting to database server
    server = 'rateurrefserver.database.windows.net' 
    database = '#' 
    dbUsername = '#' 
    password = '#' 
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+dbUsername+';PWD='+ password )
    cursor = cnxn.cursor()
    
    containers = soupy.findAll("div",{"class" : "team-container"})
    for container in containers:
        spans = container.findAll("span")
        divs = container.find("div",{"class": "record"})
        ranks = spans[0].text
        team_name = spans[1].text
        team_mascot = spans[2].text
        team_abbr = spans[3].text
        team_record = divs.text
        timing = soupy.select_one('[data-date]')['data-date']
        game_time = parse(timing).time()
        game_date = parse(timing).date()

        try:
            refs_container = soupy.find("div", {"class" : "game-info-note__container"})
            refs = refs_container.text
            ignore = re.compile(r"(Referees: )")
            refs_str = re.sub(ignore,'', refs)
            ref_names = refs_str.split(", ")
            ref1 = ref_names[0]
            ref2 = ref_names[1]
            ref3 = ref_names[2]
            
        except AttributeError:
            ref1 = "John Gattney"
            ref2 = "Earl Walton" 
            ref3 = "Paul Faia"
        
        # sql query to insert date into the database
        games_query = "INSERT INTO [dbo].[bracket] (name, abbr, mascot, team_record, ranks, game_time, game_date, ref1,ref2, ref3) VALUES (?,?,?,?,?,?,?,?,?,?)"
        cursor.execute(games_query, (team_name, team_abbr, team_mascot, team_record, ranks, game_time, game_date, ref1,ref2, ref3))

    # closing the connection
    cnxn.commit()
    cursor.close()
    del cursor
    cnxn.close()
    
    
if __name__ == '__main__':

   base_url ="http://www.espn.com/mens-college-basketball/game/_/id/401123"
    
   #Every page needed for 
   for day in it.chain(range(374,377), range(381,441)):
       scrape_data(base_url)



