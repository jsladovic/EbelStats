import matplotlib.pyplot as plt

class Graph:
    def displayPositions(self, tupple):
        plt.figure(figsize=(12, 5), dpi=100).subplots_adjust(left=0.05, right=0.8, top = 0.95, bottom=0.1)
        plt.axis([1, 44, 12.5, 0.5])
        plt.xticks([1, 5, 10, 15, 20, 25, 30, 35, 40, 44])
        plt.yticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])


       
        for club, positions in tupple:
            points = []
            for i in range(0, 44):
                if i >= len(positions):
                    break
                points.append(i + 1)
            plt.plot(points, positions, self.selectColor(club), label=club)

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), labelspacing=1.55, frameon=False)
        plt.show()

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
        
