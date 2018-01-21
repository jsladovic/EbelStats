import matplotlib.pyplot as plt
import matplotlib.lines as matLines
import matplotlib.text as matText

class Graph:
    def displayPositions(self, tupple, numberOfMatches):
        plt.rcParams['toolbar'] = 'None'
        self.fig = plt.figure(figsize=(12, 5), dpi=100)
        plt.subplots_adjust(left=0.05, right=0.8, top = 0.95, bottom=0.1)
        plt.axis([1, numberOfMatches, 12.5, 0.5])
        plt.yticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

        xTicks = [1, numberOfMatches]
        for i in range(0, numberOfMatches/5):
            xTicks.append((i + 1) * 5)
        plt.xticks(xTicks)

        self.lines = {}
        self.legendLines = {}
        self.legendTexts = {}
        for club, positions in tupple:
            points = []
            for i in range(0, numberOfMatches):
                if i >= len(positions):
                    break
                points.append(i + 1)
            self.lines[club] = plt.plot(points, positions, self.selectColor(club), label=club)

        self.legend = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), labelspacing=1.55, frameon=False)
        for legLine, _ in zip(self.legend.get_lines(), self.lines):
            legLine.set_picker(10)
            self.legendLines[legLine.get_label()] = legLine
            
        for legendText in self.legend.texts:
            legendText.set_picker(10)
            self.legendTexts[legendText.get_text()] = legendText

        self.fig.canvas.mpl_connect('pick_event', self.onPick)
        plt.show()

    def onPick(self, event):
        club = None
        if type(event.artist) is matLines.Line2D:
            club = event.artist.get_label()
        elif type(event.artist) is matText.Text:
            club = event.artist.get_text()

        if club != None:
            self.setVisibility(club)

    def setVisibility(self, club):
        line = self.lines[club][0]
        visibility = line.get_visible()
        
        if visibility == True and self.allLinesVisible():
            self.hideAllLinesExcept(club)
        elif visibility == True and self.onlyThisLineVisible(club):
            self.showAllLines()
        else:
            self.setLineVisibility(club, not visibility)
        
        self.fig.canvas.draw()

    def hideAllLinesExcept(self, club):
        for key in self.lines:
            if key == club:
                self.setLineVisibility(key, True)
            else:
                self.setLineVisibility(key, False)

    def showAllLines(self):
        for key in self.lines:
            self.setLineVisibility(key, True)

    def setLineVisibility(self, club, vis):
        self.lines[club][0].set_visible(vis)
        if vis == True:
            self.legendTexts[club].set_alpha(1.0)
            self.legendLines[club].set_alpha(1.0)
        else:
            self.legendTexts[club].set_alpha(0.3)
            self.legendLines[club].set_alpha(0.2)

    def allLinesVisible(self):
        for _, line in self.lines.iteritems():
            if line[0].get_visible() == False:
                return False

        return True

    def onlyThisLineVisible(self, club):
        for key, value in self.lines.iteritems():
            if value[0].get_visible() == True and key != club:
                return False

        return True

    def selectColor(self, club):
        if club == 'Vienna Capitals':
            return 'gold'
        if club == 'EC KAC':
            return 'red'
        if club == 'Dornbirn Bulldogs':
            return 'brown'
        if club == 'HCB Foxes':
            return 'green'
        if club == 'EC Villach SV':
            return 'black'
        if club == 'Moser Medical Graz99ers':
            return 'orange'
        if club == 'HC TWK Innsbruck':
            return 'cyan'
        if club == 'HC Orli Znojmo':
            return 'pink'
        if club == 'EHC Black Wings Linz':
            return 'gray'
        if club == 'KHL Medvescak Zagreb':
            return 'blue'
        if club == 'Fehervar AV 19':
            return 'aqua'
        if club == 'EC Red Bull Salzburg':
            return 'salmon'
        
        return 'blue'
        
