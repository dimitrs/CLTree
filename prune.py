

class PruneTree2(object):
    def prune(self, node, min_y, min_rd):
        if node.isLeaf():
            node.setPruneState(True)
            return

        childNodes = node.getChildNodes()
        for n in childNodes:
            if n.getNrInstancesInNode() < min_y:
                n.setPruneState(True)
            else:
                self.prune(n, min_y, min_rd)
                
        if len(childNodes) < 2:
            node.setPruneState(True)
            return
        
        if childNodes[0].isPrune() and childNodes[1].isPrune():
            if childNodes[0].getRelativeDensity() > min_rd and childNodes[1].getRelativeDensity() > min_rd:
                node.setPruneState(True)
            elif childNodes[0].getNrInstancesInNode() == 0:
                node.setPruneState(True)
            elif childNodes[1].getNrInstancesInNode() == 0:
                node.setPruneState(True)
            #else:
            #    node.setPruneState(False)
        
        
class PruneTree(object):
    def prune(self, node, min_y, min_rd):
        if node.isLeaf():
            node.setPruneState(True)
            return

        childNodes = node.getChildNodes()
        for n in childNodes:
            if n.getNrInstancesInNode() < min_y:
                node.setPruneState(True)
            else:
                self.prune(n, min_y, min_rd)
                
        if len(childNodes) < 2:
            node.setPruneState(True)
            return
        
        node.setPruneState(False)
        if childNodes[0].isPrune() and childNodes[1].isPrune():
            if childNodes[0].getRelativeDensity() > min_rd and childNodes[1].getRelativeDensity() > min_rd:
                node.setPruneState(True)
            elif childNodes[0].getNrInstancesInNode() == 0:
                node.setPruneState(True)
            elif childNodes[1].getNrInstancesInNode() == 0:
                node.setPruneState(True)
        