import matplotlib.pyplot as plt

class PlotIt(object):
    def __init__(self):
        self.x1 = None
        self.x2 = None        
        self.lines = list()
        
    def setData(self, dataset, attribute_1, attribute_2):        
        self.x1 = dataset.getInstances(attribute_1)
        self.x2 = dataset.getInstances(attribute_2)
        self.attribute_1 = attribute_1
        self.attribute_2 = attribute_2
        self.lines = list()
        
    def line(self, attribute, value, minVal, maxVal):
        self.lines.append((attribute, value, minVal, maxVal))   
    
    def draw(self):
        plt.plot(self.x2, self.x1, 'ro')
        for l in self.lines:
            attribute, value, minVal, maxVal = l
            if attribute == self.attribute_1:
                plt.hlines(y=value, xmin=minVal, xmax=maxVal)
            elif attribute == self.attribute_2:
                plt.vlines(x=value, ymin=minVal, ymax=maxVal)
        plt.show()

myplt = PlotIt()