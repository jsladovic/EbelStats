from datetime import datetime
from crawler import EbelScheduleCrawler
from matchCrawler import EbelMatchCrawler
from browser import Browser
from score import HeadToHead
from score import TeamScore
from score import Streak
from match import Match
from match import Details
from graph import Graph
from tabulate import tabulate
import json


class Analyzer():
    def __init__(self):
        self.browser = None
        
    def getData(self, function, numberOfMatches, findHeadToHead):
        cacheCompleteScheduleName = 'cache/ebel_schedule_complete.json'
        cacheFileName = 'cache/ebel_schedule_' + datetime.today().strftime('%d_%m_%Y') + '.json'
        matches = []
        try:
            f = open(cacheCompleteScheduleName, 'r')
            text = f.read()
            matches = self.deserializeMatches(text)
        except:
            try:
                f = open(cacheFileName, 'r')
                text = f.read()
                matches = self.deserializeMatches(text)
            except:
                matches = EbelScheduleCrawler(cacheFileName).parse(self.getBrowser())

        finishedMatches = [match for match in matches if match.isFinished()]
        finishedMatches = sorted(finishedMatches, key = lambda match: match.date)

        for match in finishedMatches:
            cacheFileName = 'cache/match/' + match.idLong + '.json'
            try:
                f = open(cacheFileName, 'r')
                text = f.read()
                match.details = self.deserializeMatchDetails(text)
            except:
                EbelMatchCrawler().parse(self.getBrowser(), match)
                self.cacheMatchDetails(match, cacheFileName)
                            
        self.closeBrowser()

        table, positions, clubs = self.createTable(finishedMatches, function)
        #self.printGraphs(table, positions, numberOfMatches)        
        #self.printLongestStreaks(finishedMatches, clubs, function)
        
        if findHeadToHead:
            #self.printHeadToHeadScores(list(clubs), finishedMatches)
            #self.printShotDetails(list(clubs), finishedMatches)
            for i in range(0, 3):
                print('\nTable for period ' + str(i + 1) + '/3:')
                self.createTable(finishedMatches, function, i)

    def printShotDetails(self, clubs, matches):
        shotSum = dict()
        wereOutshot = dict()
        outshotOpposition = dict()
        wonWhileOutshot = dict()
        lostDespiteOutshooting = dict()
        
        for club in clubs:
            shotSum[club] = 0
            wereOutshot[club] = []
            outshotOpposition[club] = []
            wonWhileOutshot[club] = []
            lostDespiteOutshooting[club] = []
            
            matchesForClub = self.matchesForClub(matches, club)
            for match in matchesForClub:
                shotSum[club] += match.shotsForClub(club)
                if match.wasOutshot(club):
                    wereOutshot[club].append(match)
                    if match.won(club):
                        wonWhileOutshot[club].append(match)
                if match.outshotOpponents(club):
                    outshotOpposition[club].append(match)
                    if match.lost(club):
                        lostDespiteOutshooting[club].append(match)
                   
        print('\nMost shots per club:')
        shotSum = sorted(shotSum.iteritems(), key = lambda(k,v) : v, reverse = True)
        for i in range(0, len(shotSum)):
            print(str(i + 1) + '. ' + shotSum[i][0] + ' - ' + str(shotSum[i][1]))

        print('\nTeams that outshot the opposition in most matches:')
        outshotOpposition = sorted(outshotOpposition.iteritems(), key = lambda(k,v) : len(v), reverse = True)
        for i in range(0, len(outshotOpposition)):
            print(str(i + 1) + '. ' + outshotOpposition[i][0] + ' outshot the opposition in ' + str(len(outshotOpposition[i][1])) + ' matches')

        print('\nTeams that were outshot in most matches:')
        wereOutshot = sorted(wereOutshot.iteritems(), key = lambda(k,v) : len(v), reverse = True)
        for i in range(0, len(wereOutshot)):
            print(str(i + 1) + '. ' + wereOutshot[i][0] + ' were outshot in ' + str(len(wereOutshot[i][1])) + ' matches')

        print('\nTeams that won the most games despite being outshot:')
        wonWhileOutshot = sorted(wonWhileOutshot.iteritems(), key = lambda(k,v) : len(v), reverse = True)
        for i in range(0, len(wonWhileOutshot)):
            print(str(i + 1) + '. ' + wonWhileOutshot[i][0] + ' won ' + str(len(wonWhileOutshot[i][1])) + ' matches')

        print('\nTeams that lost the most games when they outshot the opposition:')
        lostDespiteOutshooting = sorted(lostDespiteOutshooting.iteritems(), key = lambda(k,v) : len(v), reverse = True)
        for i in range(0, len(wonWhileOutshot)):
            print(str(i + 1) + '. ' + lostDespiteOutshooting[i][0] + ' lost ' + str(len(lostDespiteOutshooting[i][1])) + ' matches')
            
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

    def createTable(self, matches, function, period = None):
        table = self.createTableForMatches(matches, function, 1, period)
        clubs = {club.name for club in table}
        positions = {}
        for club in clubs:
            positions[club] = []

        for i in range(2, 45):
            table = self.createTableForMatches(matches, function, i, period)
            for club in clubs:
                position = self.findPositionInTable(table, club)
                if i > table[position - 1].gamesPlayed:
                    continue
                positions[club].append(position)
        if period == None:
            self.printTable(table)
        else:
            self.printTableShort(table)
        return table, positions, clubs

    def createTableForMatches(self, matches, function, matchLimit, period = None):
        clubs = {match.homeName for match in matches}
        table = []
        for club in clubs:
            clubMatches = function(self, matches, club)
            score = TeamScore(club)
            for match in clubMatches:
                if matchLimit != None and score.gamesPlayed >= matchLimit:
                    break
                if match.homeName == club:
                    if period == None:
                        score.addHomeGame(match)
                    else:
                        score.addHomePeriod(match, period)
                else:
                    if period == None:
                        score.addAwayGame(match)
                    else:
                        score.addAwayPeriod(match, period)
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

    def printTableShort(self, table):
        clubTable = []
        header = ['position', 'name', 'games played', 'wins', 'draws', 'losses',
                  'goals for', 'goals against', 'goal difference', 'points']
        position = 1
        for club in table:
            clubTable.append(club.formatWithDraws(position))
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

    def deserializeMatchDetails(self, text):
        dictionary = json.loads(text)
        details = Details()
        details.fromDictionary(dictionary)
        return details

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

    def getBrowser(self):
        if self.browser == None:
            self.browser = Browser()
        return self.browser

    def closeBrowser(self):
        if self.browser != None:
            self.browser.closeBrowser()
        self.browser = None

    def cacheMatchDetails(self, match, cacheFileName):
        matchJson = json.dumps(match.details.__dict__)

        with open(cacheFileName, 'w') as f:
            f.write(matchJson)
            f.close

print('\nOverall stats')
Analyzer().getData(Analyzer.matchesForClub, 44, True)

#print('\nHome stats')
#Analyzer().getData(Analyzer.homeMatchesForClub, 22, False)

#print('\nAway stats')
#Analyzer().getData(Analyzer.awayMatchesForClub, 22, False)
