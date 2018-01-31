from datetime import datetime

class Match():
    # Number of points awarded for result
    win = 3
    otWin = 2
    draw = 1
    otLoss = 1
    loss = 0
    
    def __init__(self):
        self.homeScore = None
        self.awayScore = None
        self.details = Details()

    @staticmethod
    def maxPointsWon():
        return Match.win

    def numberOfPointsWon(self, club):
        if self.won(club):
            if self.overtime == None:
                return self.win
            return self.otWin
        if self.wonPoint(club):
            return self.otLoss
        return self.loss

    def won(self, club):
        if self.homeName == club and self.homeScore > self.awayScore:
            return True
        if self.awayName == club and self.homeScore < self.awayScore:
            return True
        return False

    def lost(self, club):
        if self.homeName == club and self.homeScore < self.awayScore:
            return True
        if self.awayName == club and self.homeScore > self.awayScore:
            return True
        return False

    def drawn(self, club):
        if self.homeScore == self.awayScore:
            return True
        return False

    def wonPoint(self, club):
        if self.won(club) or self.overtime != None or self.drawn(club):
            return True
        return False

    def didNotWinPoint(self, club):
        return not self.wonPoint(club)
    
    def fromDictionary(self, dictionary):
        self.idLong = dictionary['idLong']
        self.id = dictionary['id']

        self.homeName = dictionary['homeName']
        self.homeShortName = dictionary['homeShortName']
        self.awayName = dictionary['awayName']
        self.awayShortName = dictionary['awayShortName']
        self.date = datetime.strptime(dictionary['date'], '%Y-%m-%dT%H:%M:%S')

        self.tvChannels = dictionary['tvChannels'] if 'tvChannels' in dictionary else None
        self.homeScore = dictionary['homeScore'] if 'homeScore' in dictionary else None
        self.awayScore = dictionary['awayScore'] if 'awayScore' in dictionary else None
        self.overtime = dictionary['overtime'] if 'overtime' in dictionary else None
        
    def setMisc(self, idLong, date, id, tvChannels):
        self.idLong = idLong
        self.date = date
        self.id = id
        if tvChannels != '' and tvChannels != None:
            self.tvChannels = tvChannels

    def setHomeTeam(self, name, shortName):
        self.homeName = name
        self.homeShortName = shortName

    def setAwayTeam(self, name, shortName):
        self.awayName = name
        self.awayShortName = shortName

    def setScore(self, home, away, ot):
        self.homeScore = home
        self.awayScore = away
        if ot == '' or ot == None:
            self.overtime = None
        else:
            self.overtime = ot

    def wentToOvertime(self):
        if self.overtime == '' or self.overtime == None:
            return False
        return True

    def isFinished(self):
        if self.homeScore == None or self.awayScore == None:
            return False
        return True

    def printMatch(self):
        print('match ' + str(self.id) + ', date: ' + self.date.ctime())
        print('home team ' + self.homeName + ' (' + self.homeShortName + ')')
        print('away team ' + self.awayName + ' (' + self.awayShortName + ')')
        print(self.scoreToString())
        print('url id: ' + self.idLong + ', tv channels: ' + self.tvChannelsToString())

    def overtimeToString(self):
        if self.wentToOvertime():
            return '(after ' + self.overtime + ')'
        return ''

    def tvChannelsToString(self):
        if self.tvChannels == None:
            return ''
        return self.tvChannels

    def scoreToString(self):
        if self.isFinished():
            return 'score ' + str(self.homeScore) + ':' + str(self.awayScore) + self.overtimeToString()
        return 'match hasn\'t been played yet'

    def setPeriodDetails(self, periods):
        if not self.wentToOvertime():
            periods = periods[:3]
        self.details.goalsByPeriod = [n[0] for n in periods]
        self.details.shotsByPeriod = [n[1] for n in periods]
        #if sum([n[0] for n in self.details.goalsByPeriod]) != self.homeScore or sum([n[1] for n in self.details.goalsByPeriod]) != self.awayScore:
        #    raise 'incorrect sum of goals by period'

    def shotsForClub(self, club):
        if club == self.homeName:
            return self.homeShots()
        return self.awayShots()

    def outshotOpponents(self, club):
        if club == self.homeName and self.homeShots() > self.awayShots():
            return True
        if club == self.awayName and self.awayShots() > self.homeShots():
            return True
        return False

    def wasOutshot(self, club):
        if club == self.homeName and self.homeShots() < self.awayShots():
            return True
        if club == self.awayName and self.awayShots() < self.homeShots():
            return True
        return False

    def homeShots(self):
        return sum([n[0] for n in self.details.shotsByPeriod])

    def awayShots(self):
        return sum([n[1] for n in self.details.shotsByPeriod])

class Details():
    def __init__(self):
        self.goalsByPeriod = None
        self.shotsByPeriod = None

    def fromDictionary(self, dictionary):
        self.goalsByPeriod = dictionary['goalsByPeriod']
        self.shotsByPeriod = dictionary['shotsByPeriod']
