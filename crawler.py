from selenium import webdriver
from datetime import datetime
from match import Match
from match import Details
import json

def serializeJson(obj):
    if isinstance(obj, (datetime)):
        return obj.isoformat()
    if isinstance(obj, (Details)):
        return None
    raise TypeError ("Type %s not serializable" % type(obj))

class EbelScheduleCrawler():
    url = 'http://www.erstebankliga.at/spielplan'
    tableXpath = '//*[@id="los_schedule"]/div/div/div[2]/table/tbody/tr'

    # to be used when selecting different schedules
    dropdownXpath = '//*[@id="los_option_division_id"]'
    
    def __init__(self, cacheFileName):
        self.cacheFileName = cacheFileName
    
    def cacheMatches(self, matches):
        matchesJson = json.dumps([ob.__dict__ for ob in matches], default=serializeJson)

        with open(self.cacheFileName, 'w') as f:
            f.write(matchesJson)
            f.close

    def parse(self, browser):
        browser.getPage(self.url)
        nodes = browser.findByXpath(self.tableXpath)
        matches = []
        for node in nodes:
            print(node.text)
            matches.append(self.parseMatchNode(node))
        self.cacheMatches(matches)
        return matches

    def parseMatchNode(self, node):        
        childNodes = node.find_elements_by_tag_name('td')
        if len(childNodes) < 14:
            raise Exception('error while parsing web, too few elements to parse the match')
        
        match = Match()
        match.setHomeTeam(self.correctClubNames(childNodes[4].text), childNodes[3].get_attribute('value'))
        match.setAwayTeam(self.correctClubNames(childNodes[12].text), childNodes[11].get_attribute('value'))

        if '-hd-label-FINISHED' in node.get_attribute('class'):
            if childNodes[6].text.isdigit() and childNodes[8].text.isdigit():
                match.setScore(int(childNodes[6].text), int(childNodes[8].text), childNodes[9].text.strip())
            
        dateString = childNodes[0].text        
        matchDate = datetime.strptime(dateString.split(', ')[1], '%d.%m.%Y')
        matchTime = datetime.strptime(childNodes[1].text, '%H:%M')
        matchDate = matchDate.replace(hour = matchTime.hour, minute = matchTime.minute)
        match.setMisc(node.get_attribute('id'), matchDate, int(childNodes[2].text), childNodes[13].text.strip())
        
        return match

    def correctClubNames(self, club):
        if 'Alperia' in club:
            return 'HCB Foxes'
        if club == 'EC-KAC':
            return 'EC KAC'
        if club == 'EC VSV':
            return 'EC Villach SV'
        if club == 'HC TWK Innsbruck \'Die Haie\'':
            return 'HC TWK Innsbruck'
        if club == 'EHC Liwest Black Wings Linz':
            return 'EHC Black Wings Linz'
        return club
