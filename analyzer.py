from datetime import datetime
from crawler import EbelScheduleCrawler
from score import TeamScore
from score import Streak
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

        print('\nLongest winning streaks')
        self.findLongestStreak(finishedMatches, clubs, Match.won)

        print('\nLongest losing streaks')
        self.findLongestStreak(finishedMatches, clubs, Match.lost)

        print('\nLongest point streaks')
        self.findLongestStreak(finishedMatches, clubs, Match.wonPoint)

        print('\nLongest pointless streaks')
        self.findLongestStreak(finishedMatches, clubs, Match.didNotWinPoint)
        
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
            clubMatches = self.matchesForClub(matches, club)
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

    def findLongestStreak(self, matches, clubs, function):
        longestStreaks = []
        print('\nBy club:')
        for club in clubs:
            streak = None
            longestStreak = None
            clubMatches = self.matchesForClub(matches, club)
            for match in range (0, len(clubMatches) - 1):
                if function(clubMatches[match], club):
                    if streak == None:
                        streak = Streak(club, match + 1)
                    else:
                        streak.extend()
                        
                    if longestStreak == None or streak.length() > longestStreak.length():
                        longestStreak = streak
                else:
                    longestStreaks = self.addStreakToLongestStreaks(longestStreaks, streak)
                    streak = None
            longestStreaks = self.addStreakToLongestStreaks(longestStreaks, streak)
            print(longestStreak.toString())

        print('\nOverall:')
        for i in range(0, len(longestStreaks)):
            print(str(i + 1) + '. ' + longestStreaks[i].toString())

    def addStreakToLongestStreaks(self, streaks, streak):
        numberOfStreaks = 10
        if streak == None:
            return streaks
        if len(streaks) < numberOfStreaks or streak.length() > streaks[numberOfStreaks - 1].length():
            streaks.append(streak)
            streaks = sorted(streaks, key = lambda s: s.length(), reverse = True)
            return streaks[:numberOfStreaks]
        return streaks

    def matchesForClub(self, matches, club):
        return [match for match in matches if match.homeName == club or match.awayName == club]

Analyzer().getData()
