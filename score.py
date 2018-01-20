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
        # Number of points awarded for result
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
