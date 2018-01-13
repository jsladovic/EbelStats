from datetime import datetime
from crawler import EbelScheduleCrawler
from match import Match
from graph import Graph
from tabulate import tabulate
import json

class Analyzer():
    def getData(self):
        cacheFileName = 'cache/ebel_schedule_' + datetime.today().strftime('%d_%m_%Y') + '.json'
        matches = []
        try:
            f = open(cacheFileName, 'r')
            text = f.read()
            matches = self.deserializeMatches(text)
        except:
            matches = EbelScheduleCrawler(cacheFileName).parse()

        finishedMatches = [match for match in matches if match.isFinished()]
        finishedMatches = sorted(finishedMatches, key = lambda match: match.date)

        table = self.createTable(finishedMatches, 1)
        clubs = {club.name for club in table}
        positions = {}
        for club in clubs:
            positions[club] = []

        for i in range(2, 44):
            table = self.createTable(finishedMatches, i)
            for club in clubs:
                position = self.findPositionInTable(table, club)
                if i > table[position - 1].gamesPlayed:
                    continue
                positions[club].append(position)
        self.printTable(table)

        positions = sorted(positions.iteritems(), key = lambda (k,v): self.findPositionInTable(table, k))
        Graph().displayPositions(positions)

    def findPositionInTable(self, table, clubName):
        position = 1
        for club in table:
            if club.name == clubName:
                return position
            position += 1

    def createTable(self, matches, matchLimit = None):
        clubs = {match.homeName for match in matches}
        table = []
        for club in clubs:
            clubMatches = [match for match in matches if match.homeName == club or match.awayName == club]
            score = TeamScore(club)
            for match in clubMatches:
                if matchLimit != None and score.gamesPlayed >= matchLimit:
                    break
                if match.homeName == club:
                    score.addHomeGame(match)
                else:
                    score.addAwayGame(match)
            table.append(score)

        return self.sortTable(table)

    def sortTable(self, table):
        table = sorted(table, key = lambda score: score.goalDifference(), reverse = True)
        table = sorted(table, key = lambda score: score.calculatePoints(), reverse = True)
        return table

    def printTable(self, table):
        clubTable = []
        header = ['position', 'name', 'games played', 'wins', 'losses', 'ot wins', 'ot losses',
                  'goals for', 'goals against', 'goal difference', 'points']
        position = 1
        for club in table:
            clubTable.append(club.format(position))
            position += 1
        print tabulate(clubTable, headers = header)

    def deserializeMatches(self, text):
        dictionary = json.loads(text)
        matches = []
        for element in dictionary:
            match = Match()
            match.fromDictionary(element)
            matches.append(match)
        return matches

class TeamScore():
    def __init__(self, name):
        self.name = name
        self.gamesPlayed = 0
        self.wins = 0
        self.losses = 0
        self.otWins = 0
        self.otLosses = 0
        self.goalsFor = 0
        self.goalsAgainst = 0

    def addHomeGame(self, match):
        if match.homeScore == match.awayScore:
            raise Exception('match must have a winner')

        self.gamesPlayed += 1
        self.goalsFor += match.homeScore
        self.goalsAgainst += match.awayScore
        if match.homeScore > match.awayScore:
            if match.wentToOvertime():
                self.otWins += 1
            else:
                self.wins += 1
        else:
            if match.wentToOvertime():
                self.otLosses += 1
            else:
                self.losses += 1

    def addAwayGame(self, match):
        if match.homeScore == match.awayScore:
            raise Exception('match must have a winner')

        self.gamesPlayed += 1
        self.goalsFor += match.awayScore
        self.goalsAgainst += match.homeScore
        if match.awayScore > match.homeScore:
            if match.wentToOvertime():
                self.otWins += 1
            else:
                self.wins += 1
        else:
            if match.wentToOvertime():
                self.otLosses += 1
            else:
                self.losses += 1

    def calculatePoints(self):
        win = 3
        otWin = 2
        otLoss = 1
        loss = 0

        return self.wins * win + self.otWins * otWin + self.otLosses * otLoss + self.losses * loss

    def goalDifference(self):
        return self.goalsFor - self.goalsAgainst

    def format(self, position):
        return [position, self.name, self.gamesPlayed, self.wins, self.losses, self.otWins, self.otLosses,
                self.goalsFor, self.goalsAgainst, self.goalDifference(), self.calculatePoints()]

Analyzer().getData()
