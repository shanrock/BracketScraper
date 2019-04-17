from bs4 import BeautifulSoup as soup
#from selenium import webdriver
import pyodbc
import requests
import itertools as it
import re
from dateutil.parser import parse
import datetime as dt
	
	
def away_team(url,game_id):
    url = '{}{}'.format(base_url,day)
    r = requests.get(url)
    soupy = soup(r.content, 'lxml')    

    connecting to database server
    server = '#.database.windows.net' 
    database = '#' 
    dbUsername = '#' 
    password = '#'
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+dbUsername+';PWD='+ password )
    cursor = cnxn.cursor()

    containers = soupy.findAll("div",{"class" : "competitors"})
    for container in containers:
        spans = container.findAll("span")
        divs = container.findAll("div",{"class": "record"})
        rank = spans[0].text
        team = spans[1].text
        mascot = spans[2].text
        abbr = spans[3].text
        record = divs[0].text
        logo_cont = container.findAll("img", {"class" : "team-logo"})
        logo = logo_cont[0]['src']
        game_detail = soupy.find("div", {"class" : "game-details"}).text
        region = game_detail.split(" - ")[1]

        # sql query to insert date into the database
        games_query = "INSERT INTO [dbo].[team] (id,team, abbr, mascot,\
        record, region, rank,logo) VALUES (?,?,?,?,?,?,?,?)"
        cursor.execute(games_query, (game_id, team, abbr, mascot, record, region, rank, logo))

    # closing the connection
        cnxn.commit()
        cursor.close()
        del cursor
        cnxn.close()

def home_team(url,game_id):
    url = '{}{}'.format(base_url,day)
    r = requests.get(url)
    soupy = soup(r.content, 'lxml')    

    server = '#.database.windows.net' 
    database = '#' 
    dbUsername = '#' 
    password = '#'
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+dbUsername+';PWD='+ password )
    cursor = cnxn.cursor()
    
    containers = soupy.findAll("div",{"class" : "competitors"})
    for container in containers:
        spans = container.findAll("span")
        divs = container.findAll("div",{"class": "record"})
        rank = spans[5].text
        team = spans[6].text
        mascot = spans[7].text
        abbr = spans[8].text
        record = divs[1].text
        logo_cont = container.findAll("img", {"class" : "team-logo"})
        logo = logo_cont[1]['src']
        game_detail = soupy.find("div", {"class" : "game-details"}).text
        region = game_detail.split(" - ")[1]
        print(team)
        print(game_id)
        
        games_query = "INSERT INTO [dbo].[team] (id,team, abbr, mascot,\
        record, region, rank,logo) VALUES (?,?,?,?,?,?,?,?)"
        cursor.execute(games_query, (game_id, team, abbr, mascot, record, region, rank, logo))
    
        # closing the connection
    cnxn.commit()
    cursor.close()
    del cursor
    cnxn.close()
  
if __name__ == '__main__':

   base_url ="http://www.espn.com/mens-college-basketball/game/_/id/401123"
   game_id = 0
   for day in it.chain(range(393,421), range(435,439)):
       game_id += 1
       away_team(base_url,game_id)
       game_id += 1
       home_team(base_url,game_id)



