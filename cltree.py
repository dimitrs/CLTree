from arff import Data, ArffReader
from build import BuildTree, _relative_density, myplt
from prune import PruneTree
from plot import PlotIt
              
class CLTree:
    def __init__(self, dataset, min_split=1):
        if dataset is None:
            self.raiseUndefinedDataset()
            
        self.dataset = dataset        
        self.min_split = min_split
        self.clusters = list()
        self.root = None

    def buildTree(self):
        b = BuildTree(self.min_split)
        self.root = b.build(self.dataset)        

    def pruneTree(self, min_y, min_rd):
        if self.root is None:
            self.raiseUndefinedTree()        
        min_y = self._transformPercentageToAbsoluteNumber(min_y)        
        p = PruneTree()        
        p.prune(self.root, min_y, min_rd)
                            
    def getClustersList(self, min_nr_instances=1):
        if self.root is None:
            self.raiseUndefinedTree()
        self.clusters = list()
        self._getClustersList(self.root, min_nr_instances) 
        return self.clusters

    def _getClustersList(self, node, min_nr_instances):
        if node.isPrune() and node.getNrInstancesInNode() >= min_nr_instances:            
            self.clusters.append(node)        
            return
        #if node.isLeaf():
        #    self.clusters.append(node)                
        nodes = node.getChildNodes()
        for n in nodes:
            if n: self._getClustersList(n, min_nr_instances)

    def _transformPercentageToAbsoluteNumber(self, min_y):
        return int((float(min_y)/100.0)*self.dataset.length())
        
    def raiseUndefinedDataset(self):
        raise CLTree.UndefinedDataset()
    class UndefinedDataset(Exception):
        pass    
    def raiseUndefinedTree(self):
        raise CLTree.UndefinedTree()
    class UndefinedTree(Exception):
        pass    
        




    
if __name__ == '__main__':
    print '----------------'
    print 'Clustering      '
    print '----------------'
    r = ArffReader()
    #data = r.read('test/gen.arff')
    data = r.read('test/D05.arff')

    """
    clusterplt = PlotIt()        
    dim0 = "x0"
    dim1 = "x1"    
    myplt.setData(data, dim0, dim1)
    clusterplt.setData(data, dim0, dim1)
    """
    
    cltree = CLTree(data)     
    cltree.buildTree()
                    
    # The minimum number of instances a cluster must contain. It is 
    # expressed as a percentage of the total number of instances in 
    # the data set. Recommended value: 1-5%
    min_y = 1

    # Specifies whether two adjacent regions should joined to form 
    # a bigger region. Recommended value: 10-30%
    min_rd = 10
    
    cltree.pruneTree(min_y, min_rd)        
    clusters = cltree.getClustersList(min_nr_instances=2)
    
    c = 0
    for i, node in enumerate(clusters):
        """
        x0_max = node.dataset.get_max(dim0)
        x0_min = node.dataset.get_min(dim0)
        x1_max = node.dataset.get_max(dim1)
        x1_min = node.dataset.get_min(dim1)        
        clusterplt.line(dim0, x0_max, x1_min, x1_max)
        clusterplt.line(dim0, x0_min, x1_min, x1_max)
        clusterplt.line(dim1, x1_max, x0_min, x0_max)
        clusterplt.line(dim1, x1_min, x0_min, x0_max)
        """
        c += node.getNrInstancesInNode()
        print "Cluster", i
        print node
    print "Total instances clustered: ", c
    #clusterplt.draw()
    #myplt.draw()
    
