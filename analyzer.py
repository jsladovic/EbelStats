from datetime import datetime
from crawler import EbelScheduleCrawler
from score import HeadToHead
from score import TeamScore
from score import Streak
from match import Match
from graph import Graph
from tabulate import tabulate
import json


class Analyzer():
    def getData(self, function, numberOfMatches, findHeadToHead):
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

        table = self.createTable(finishedMatches, function, 1)
        clubs = {club.name for club in table}
        positions = {}
        for club in clubs:
            positions[club] = []

        for i in range(2, 44):
            table = self.createTable(finishedMatches, function, i)
            for club in clubs:
                position = self.findPositionInTable(table, club)
                if i > table[position - 1].gamesPlayed:
                    continue
                positions[club].append(position)
        self.printTable(table)

        self.printGraphs(table, positions, numberOfMatches)        
        self.printLongestStreaks(finishedMatches, clubs, function)
        if findHeadToHead:
            self.printHeadToHeadScores(list(clubs), finishedMatches)

    def printHeadToHeadScores(self, clubs, matches):
        headToHeads = []
        for i in range(0, len(clubs) - 1):
            for j in range(i + 1, len(clubs)):
                matchesForClubs = self.matchesForClub(self.matchesForClub(matches, clubs[i]), clubs[j])
                headToHead = HeadToHead(clubs[i], clubs[j], matchesForClubs)
                headToHeads.append(headToHead)

        self.printBestHeadToHeads(headToHeads)
        self.printSplitSeries(clubs, headToHeads)

    def printBestHeadToHeads(self, headToHeads):
        headToHeads = sorted(headToHeads, key = lambda h2h: h2h.percentage(), reverse = True)
        print('\nBest head to head scores:')
        for headToHead in [h2h for h2h in headToHeads if h2h.percentage() >= 0.8]:
            print(headToHead.toString())

    def printSplitSeries(self, clubs, headToHeads):
        print('\nTeams that have split their series:')
        for club in clubs:
            splitSeries = [h2h for h2h in headToHeads if h2h.hasClub(club) and h2h.percentage() == 0.5]
            print(self.splitSeriesToString(club, splitSeries))

    def splitSeriesToString(self, club, splitSeries):
        if splitSeries == None or len(splitSeries) == 0:
            return club + ' didn\'t split any series'
        return club + ' split ' + str(len(splitSeries)) + ' series, against ' + self.otherClubsToString(club, splitSeries)

    def otherClubsToString(self, club, splitSeries):
        string = splitSeries[0].otherClub(club)
        for i in range(1, len(splitSeries)):
            string += ', ' + splitSeries[i].otherClub(club)
        return string

    def printLongestStreaks(self, finishedMatches, clubs, function):
        print('\nLongest winning streaks')
        self.findLongestStreak(finishedMatches, clubs, Match.won, function)

        print('\nLongest losing streaks')
        self.findLongestStreak(finishedMatches, clubs, Match.lost, function)

        print('\nLongest point streaks')
        self.findLongestStreak(finishedMatches, clubs, Match.wonPoint, function)

        print('\nLongest pointless streaks')
        self.findLongestStreak(finishedMatches, clubs, Match.didNotWinPoint, function)

    def printGraphs(self, table, positions, numberOfMatches):
        positions = sorted(positions.iteritems(), key = lambda (k,v): self.findPositionInTable(table, k))
        Graph().displayPositions(positions, numberOfMatches)
        return

    def findPositionInTable(self, table, clubName):
        position = 1
        for club in table:
            if club.name == clubName:
                return position
            position += 1

    def createTable(self, matches, function, matchLimit = None):
        clubs = {match.homeName for match in matches}
        table = []
        for club in clubs:
            clubMatches = function(self, matches, club)
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

    def findLongestStreak(self, matches, clubs, function, matchesFunction):
        longestStreaks = []
        print('\nBy club:')
        for club in clubs:
            streak = None
            longestStreak = None
            clubMatches = matchesFunction(self, matches, club)
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

    def homeMatchesForClub(self, matches, club):
        return [match for match in matches if match.homeName == club]

    def awayMatchesForClub(self, matches, club):
        return [match for match in matches if match.awayName == club]

print('\nOverall table')
Analyzer().getData(Analyzer.matchesForClub, 44, True)

print('\nHome table')
Analyzer().getData(Analyzer.homeMatchesForClub, 22, False)

print('\nAway table')
Analyzer().getData(Analyzer.awayMatchesForClub, 22, False)
