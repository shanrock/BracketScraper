from bs4 import BeautifulSoup as soup
import pyodbc
import requests
import itertools as it
import re
from dateutil.parser import parse
import datetime as dt

def scrape_data(url,game_id):
    url = '{}{}'.format(base_url,day)
    r = requests.get(url)
    soupy = soup(r.content, 'lxml')    
  
    # connecting to database server
    server = '#.database.windows.net' 
    database = '#' 
    dbUsername = '#' 
    password = '#'  
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+dbUsername+';PWD='+ password )
    cursor = cnxn.cursor()
    
#    containers = soupy.findAll("div",{"class" : "team-container"})
    containers = soupy.findAll("div",{"class" : "competitors"})
    for container in containers:
        info_wrapper = soupy.findAll("div", {"class": "team-info-wrapper"})
        team_away = info_wrapper[0].find("span", {"class":"long-name"}).text
        team_away_mascot = info_wrapper[0].find("span", {"class":"short-name"}).text
        team_away_abbr = info_wrapper[0].find("span", {"class":"abbrev"}).text
        team_home = info_wrapper[1].find("span", {"class":"long-name"}).text
        team_home_mascot = info_wrapper[1].find("span", {"class":"short-name"}).text
        team_home_abbr = info_wrapper[1].find("span", {"class":"abbrev"}).text
        game_detail = soupy.find("div", {"class" : "game-details"}).text
        
        # grabbing the round information
        if(game_id == 1 or game_id == 2 or game_id == 3):
            game_round = game_detail.split(" - ")[1]
        else:
            game_round = game_detail.split(" - ")[2]
        
        # converting the data-date to correct datetime for db
        # grabbing the attribute value is faster than using selenium
        # storing in utc time to easily connect game to tweet data
        
        timing = soupy.select_one('[data-date]')['data-date']
        game_time = parse(timing).time()
        game_date = parse(timing).date()
        date_time = dt.datetime.combine(game_date, game_time)
        
        # refs were left off from page 403
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
            
        print(game_id)
        # sql query to insert date into the database
        games_query = "INSERT INTO [dbo].[test_bracket] (id,game_round,home_team,home_mascot,\
        home_abbr,away_team,away_mascot,away_abbr,date_time,ref1,ref2,ref3) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
        cursor.execute(games_query, (game_id, game_round, team_home, team_home_mascot, team_home_abbr,
                                     team_away, team_away_mascot, team_away_abbr, date_time, ref1,ref2, ref3))
     
    # closing the connection
    cnxn.commit()
    cursor.close()
    del cursor
    cnxn.close()
    
  
if __name__ == '__main__':

   base_url ="http://www.espn.com/mens-college-basketball/game/_/id/401123"
   game_id = 0
    # loop through every page ( except first four ) on bracket page
   for day in it.chain(range(374,377), range(381,441)):
       game_id += 1
       scrape_data(base_url,game_id)



