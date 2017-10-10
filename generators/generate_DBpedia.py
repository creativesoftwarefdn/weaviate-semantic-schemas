import json
import urllib.request
from bs4 import BeautifulSoup
import datetime

##
# Buildlog function
#
# i = output line
##
counter = 1
def buildLog( i ):
    global counter
    counter += 1
    print(str(counter).zfill(7)  + " | " + str(datetime.datetime.now().time()) + " | " + i)

##
#
##
def loadClasses( soup ):
    for div in soup.find_all('li'):
        for childdiv in div.find_all('a'):
            print(childdiv['name'])
            if len(div.find_all('li') ) > 0:
                for childOfChild in div.find_all('li'):
                    loadClasses( childOfChild )
            break
        break

##
# Start building
##
with urllib.request.urlopen("http://mappings.dbpedia.org/server/ontology/classes/") as url:
    loadClasses(BeautifulSoup(url.read(), "lxml"))


buildLog("DONE")