from datetime import datetime

class Match():
    def __init__(self):
        self.homeScore = None
        self.awayScore = None
    
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
