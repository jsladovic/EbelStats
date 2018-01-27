from selenium import webdriver
from datetime import datetime
from match import Match
import json


class EbelMatchCrawler():
    scoreXpath = '//*[@id="los_game_fullreport"]/div/div[1]/div[5]/div'
    statsXpath = '//*[@id="los_game_fullreport"]/div/div[3]/div[2]/div[2]'
    goalsXpath = '//*[@id="los_game_fullreport"]/div/div[4]/div[2]/div[2]'
    penaltiesXpath = '//*[@id="los_game_fullreport"]/div/div[5]'
    
    def parse(self, browser, match, cacheFileName):
        print('match ' + match.idLong)
        browser.getPage(self.getUrl(match.idLong))
        match.setPeriodDetails(self.parseScore(browser.findByXpath(self.scoreXpath)))
        return

    def parseScore(self, nodes):
        periodNodes = nodes[0].find_elements_by_tag_name('div')[1:]
        scoreNodes = nodes[1].find_elements_by_tag_name('div')[1:]
        shotNodes = nodes[2].find_elements_by_tag_name('div')[1:]

        if len(periodNodes) != len(scoreNodes) or len(periodNodes) != len(shotNodes):
            raise 'incorrect number of period, score or shot nodes for match'

        periods = []
        for i in range(0, len(periodNodes)):
            periods.append([[int(n) for n in scoreNodes[i].text.split(':')], [int(n) for n in shotNodes[i].text.split(':')]])
        return periods

    def getUrl(self, id):
        return 'http://www.erstebankliga.at/stats-ebel/spiel?gameId={id}&divisionId=1903'.format(id = id)
