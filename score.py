from match import Match

class TeamScore():
    def __init__(self, name):
        self.name = name
        self.gamesPlayed = 0
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.otWins = 0
        self.otLosses = 0
        self.goalsFor = 0
        self.goalsAgainst = 0

    def addHomeGame(self, match):
        self.gamesPlayed += 1
        self.goalsFor += match.homeScore
        self.goalsAgainst += match.awayScore
        
        if match.homeScore == match.awayScore:
            self.draws += 1
        elif match.homeScore > match.awayScore:
            if match.wentToOvertime():
                self.otWins += 1
            else:
                self.wins += 1
        else:
            if match.wentToOvertime():
                self.otLosses += 1
            else:
                self.losses += 1

    def addHomePeriod(self, match, period):
        self.gamesPlayed += 1
        homeGoals = match.details.goalsByPeriod[period][0]
        awayGoals = match.details.goalsByPeriod[period][1]
        self.goalsFor += homeGoals
        self.goalsAgainst += awayGoals

        if homeGoals == awayGoals:
            self.draws += 1
        elif homeGoals > awayGoals:
            self.wins += 1
        else:
            self.losses += 1

    def addAwayGame(self, match):
        self.gamesPlayed += 1
        self.goalsFor += match.awayScore
        self.goalsAgainst += match.homeScore
        
        if match.homeScore == match.awayScore:
            self.draws += 1
        elif match.awayScore > match.homeScore:
            if match.wentToOvertime():
                self.otWins += 1
            else:
                self.wins += 1
        else:
            if match.wentToOvertime():
                self.otLosses += 1
            else:
                self.losses += 1

    def addAwayPeriod(self, match, period):
        self.gamesPlayed += 1
        homeGoals = match.details.goalsByPeriod[period][0]
        awayGoals = match.details.goalsByPeriod[period][1]
        self.goalsFor += awayGoals
        self.goalsAgainst += homeGoals

        if homeGoals == awayGoals:
            self.draws += 1
        elif homeGoals < awayGoals:
            self.wins += 1
        else:
            self.losses += 1

    def calculatePoints(self):
        return self.wins * Match.win + self.otWins * Match.otWin + self.otLosses * Match.otLoss + self.losses * Match.loss + self.draws * Match.draw

    def goalDifference(self):
        return self.goalsFor - self.goalsAgainst

    def format(self, position):
        return [position, self.name, self.gamesPlayed, self.wins, self.losses, self.otWins, self.otLosses,
                self.goalsFor, self.goalsAgainst, self.goalDifference(), self.calculatePoints()]

    def formatWithDraws(self, position):
        return [position, self.name, self.gamesPlayed, self.wins, self.draws, self.losses, 
                self.goalsFor, self.goalsAgainst, self.goalDifference(), self.calculatePoints()]

class Streak:
    def __init__(self, club, startingMatch):
        self.startingMatch = startingMatch
        self.endingMatch = startingMatch
        self.club = club

    def extend(self):
        self.endingMatch += 1

    def length(self):
        return self.endingMatch - self.startingMatch + 1

    def toString(self):
        return self.club + ' -> games ' + str(self.startingMatch) + ' to ' + str(self.endingMatch) + '(' + str(self.length()) + ')'

class HeadToHead:
    def __init__(self, club1, club2, matches):
        self.clubs = [club1, club2]
        self.matches = matches

    def maxNumberOfPoints(self):
        return len(self.matches) * Match.maxPointsWon()

    def winnerPointsWon(self):
        club1PointsWon = 0
        for match in self.matches:
            club1PointsWon += match.numberOfPointsWon(self.clubs[0])

        if club1PointsWon >= self.maxNumberOfPoints() - club1PointsWon:
            return club1PointsWon
        return self.maxNumberOfPoints() - club1PointsWon

    def winnerLoser(self):
        club1PointsWon = 0
        for match in self.matches:
            club1PointsWon += match.numberOfPointsWon(self.clubs[0])

        if club1PointsWon >= self.maxNumberOfPoints() - club1PointsWon:
            return self.clubs[0], self.clubs[1]
        return self.clubs[1], self.clubs[0]

    def hasNoMatches(self):
        return self.matches == None or len(self.matches) == 0

    def percentage(self):
        if self.hasNoMatches():
            return 0.0
        return self.winnerPointsWon() / float(self.maxNumberOfPoints())

    def toString(self):
        if self.hasNoMatches():
            return self.clubs[0] + ' and ' + self.clubs[1] + ' haven\' played yet'
        if self.percentage() == 0.5:
            return self.clubs[0] + ' and ' + self.clubs[1] + ' split the series, both winning ' + str(self.winnerPointsWon()) + ' points'
        winner, loser = self.winnerLoser()
        return winner + ' won ' + str(self.winnerPointsWon()) + ' out of ' + str(self.maxNumberOfPoints()) + ' against ' + loser + ' (' + str(round(self.percentage() * 100, 1)) + '%)'

    def hasClub(self, club):
        if club in self.clubs:
            return True
        return False

    def otherClub(self, club):
        if club not in self.clubs:
            raise Exception('club not in head to head clubs')
        if club == self.clubs[0]:
            return self.clubs[1]
        return self.clubs[0]
