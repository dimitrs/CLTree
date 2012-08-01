from arff import Data
from plot import PlotIt

from math import sqrt as sqrt

myplt = PlotIt()

def _relative_density(dataset):
    return float(dataset.length())/dataset.nr_virtual_points


class BuildTree(object):
    def __init__(self, min_split):       
        self.cutCreator = InfoGainCutFactory(min_split)
        self.datasetSplitter = DatasetSplitter()                        
        self.root = None
            
    def build(self, dataset):
        self._build_tree(dataset, None, 0)        
        return self.root

    def _build_tree(self, dataset, parent, depth):
        bestCut = self._findBestCut(dataset)  
        attribute = "" if bestCut is None else bestCut.attribute
    
        dt_node = CLNode(dataset, parent, attribute, depth)           
        if parent: parent.addChildNode(dt_node)
        if self._isRootNode(depth): self.root = dt_node
        
        if bestCut is None:
            return
        
        lhs_dataset, rhs_dataset = self._splitDatasetUsingBestCut(dataset, bestCut)
        
        #self._plotCut(bestCut, dataset, lhs_dataset, rhs_dataset)

        if lhs_dataset.length() > 0:
            self._build_tree(lhs_dataset, dt_node, (depth+1))
        if rhs_dataset.length() > 0:
            self._build_tree(rhs_dataset, dt_node, (depth+1))
            
            
    def _isRootNode(self, depth):
        if depth==0 and self.root is None: return True
        
    def _splitDatasetUsingBestCut(self, dataset, bestCut):                           
        dataset.sort(bestCut.attribute)        
        idx = dataset.getInstanceIndex(bestCut.inst_id)        
        lhs_set, rhs_set = self.datasetSplitter.split(dataset, bestCut.attribute, bestCut.value, idx+1)                        
        
        for attribute in dataset.attr_names:        
            if attribute == bestCut.attribute:
                continue
            minVal = dataset.get_min(attribute)
            maxVal = dataset.get_max(attribute)
            lhs_set.set_min(attribute, minVal)
            lhs_set.set_max(attribute, maxVal)
            rhs_set.set_min(attribute, minVal)
            rhs_set.set_max(attribute, maxVal)
        
        return lhs_set, rhs_set            
            
    def _findBestCut(self, dataset):               
        bestCut = None
        for attribute in dataset.attr_names:
            dataset.sort(attribute)
            di_cut1 = self._calcCut1(dataset, attribute)
            if di_cut1 is None: # Ignore dimension
                continue
            
            di_cut2 = self._calcCut2(di_cut1)
            if di_cut2 is None:
                bestCut = self._selectLowerDensityCut(di_cut1, bestCut)
                continue
            
            di_cut3 = self._calcCut3(di_cut1, di_cut2)
            if di_cut3 is None:
                bestCut = self._selectLowerDensityCut(di_cut2, bestCut)
            else:
                bestCut = self._selectLowerDensityCut(di_cut3, bestCut)         
        return bestCut
            
    def _calcCut1(self, dataset, attribute):   
        return self.cutCreator.cut(dataset, attribute) 

    def _calcCut2(self, di_cut1):   
        lower_density_set = di_cut1.getLowerDensityRegion() 
        return self.cutCreator.cut(lower_density_set, di_cut1.attribute)                                        
            
    def _calcCut3(self, di_cut1, di_cut2):   
        adjacentRegion = di_cut2.getAdjacentRegion(di_cut1.value, di_cut1.attribute)
        otherRegion = di_cut2.getNonAdjacentRegion(di_cut1.value, di_cut1.attribute)
                
        di_cut3 = None
        if _relative_density(adjacentRegion) <= _relative_density(otherRegion):
            lower_density_set = di_cut2.getLowerDensityRegion()                                    
            di_cut3 = self.cutCreator.cut(lower_density_set, di_cut2.attribute)                                        
        return di_cut3
    
    def _selectLowerDensityCut(self, cut1, cut2):
        if cut1 is None: return cut2
        if cut2 is None: return cut1
        rd1 = cut1.getRelativeDensityOfLowerDensityRegion() 
        rd2 = cut2.getRelativeDensityOfLowerDensityRegion()
        if rd1 < rd2: return cut1
        else: return cut2
        
    def _plotCut(self, bestCut, dataset, lhs_dataset, rhs_dataset):
        if lhs_dataset.length() > 0 or rhs_dataset.length() > 0:
            if myplt.attribute_1 == bestCut.attribute:
                minVal = dataset.get_min(myplt.attribute_2)
                maxVal = dataset.get_max(myplt.attribute_2)
            else:
                minVal = dataset.get_min(myplt.attribute_1)
                maxVal = dataset.get_max(myplt.attribute_1)
            myplt.line(bestCut.attribute, bestCut.value, minVal, maxVal)
            #myplt.draw()


class DatasetSplitter:
    def __init__(self):
        pass
    
    def split(self, dataset, attribute, value, idx):
        l = dataset.instance_values[0:idx]
        r = dataset.instance_values[idx:]
                
        lhs_set = Data(l, dataset.class_map, dataset.class_names, dataset.attr_types)
        rhs_set = Data(r, dataset.class_map, dataset.class_names, dataset.attr_types)        
                
        rhs_set.set_min(attribute, value)
        
        self._splitNrVirtualPoints(dataset, attribute, value, lhs_set, rhs_set)
        self._updateVirtualPoints(lhs_set)
        self._updateVirtualPoints(rhs_set)
        
        return lhs_set, rhs_set
        
    def _splitNrVirtualPoints(self, dataset, attribute, value, in_set, out_set):
        minV = dataset.get_min(attribute)
        maxV = dataset.get_max(attribute)
        in_set.nr_virtual_points = int(abs(dataset.nr_virtual_points*((value-minV)/(maxV-minV))))
        out_set.nr_virtual_points = dataset.nr_virtual_points - in_set.nr_virtual_points
        if out_set.nr_virtual_points < 0:
            self.raiseUndefinedNumberOfPoints()
    
    def _updateVirtualPoints(self, data_set):            
        nr_points_in_set = data_set.length()
        data_set.nr_virtual_points = self._calcNumberOfPointsToAdd(nr_points_in_set, data_set.nr_virtual_points)
        data_set.nr_total_instances = nr_points_in_set + data_set.nr_virtual_points
            
    def _calcNumberOfPointsToAdd(self, nr_points_in_node, nr_points_inherited):    
        if nr_points_inherited < nr_points_in_node:
            nr_points = nr_points_in_node
        else:
            nr_points = nr_points_inherited
        return nr_points
    
    def raiseUndefinedNumberOfPoints(self):
        raise DatasetSplitter.UndefinedNumberOfPoints()
    class UndefinedNumberOfPoints(Exception):
        pass    
    
       
class InfoGainCutFactory:
    def __init__(self, min_split):
        self.min_split = min_split
        self.datasetSplitter = DatasetSplitter()

    def cut(self, dataset, attribute):
        di_cut = None
        max_info_gain = -1          
        instances = dataset.getInstances(attribute)
        for i, value in enumerate(instances):
            if self._hasRectangle(dataset, attribute, value):
                lhs_set, rhs_set = self.datasetSplitter.split(dataset, attribute, value, i+1)                
                ig, lset, rset = self._info_gain(dataset, lhs_set, rhs_set)
                if ig > max_info_gain:
                    max_info_gain = ig
                    di_cut = Cut(attribute, value, dataset.getId(i), lset, rset)        
        return di_cut
    
    def _hasRectangle(self, dataset, attribute, value):
        if dataset.get_max(attribute) == dataset.get_min(attribute): 
            return False
        else:
            if dataset.get_max(attribute) == value:
                return False
            else:
                return True

    def _info_gain(self, dataset, lhs_set, rhs_set):                   
        if (lhs_set.nr_total_instances < self.min_split) or (rhs_set.nr_total_instances < self.min_split):
            return -1, lhs_set, rhs_set
    
        ratio_instances_lhs = (float(lhs_set.nr_total_instances)/dataset.nr_total_instances)
        ratio_instances_rhs = (float(rhs_set.nr_total_instances)/dataset.nr_total_instances)
        entropy2 = ratio_instances_lhs*self._calc_entropy(lhs_set) + ratio_instances_rhs*self._calc_entropy(rhs_set)
    
        entropy1 = self._calc_entropy(dataset)
        
        return (entropy1 - entropy2), lhs_set, rhs_set

    def _calc_entropy(self, dataset):
        nr_existing_instances = dataset.length()
        total = nr_existing_instances + dataset.nr_virtual_points
        terms = list()
        terms.append((float(nr_existing_instances)/float(total))*sqrt(float(nr_existing_instances)/float(total)))    
        terms.append((float(dataset.nr_virtual_points)/float(total))*sqrt(float(dataset.nr_virtual_points)/float(total)))                
        return sum(terms)*-1
        
class Cut:
    def __init__(self, attribute, value, inst_id, lhsset, rhsset):
        self.attribute = attribute
        self.value = value
        self.inst_id = inst_id
        self.lhs_set = lhsset
        self.rhs_set = rhsset

    def __str__(self):
        s = 'Cut: ' + self.attribute + "\n"
        s += str(self.lhs_set.attr_names) + "\n"  
        s += " Max lhs:" + str(self.lhs_set.max_values)+ "\n"  
        s += " Min lhs:" + str(self.lhs_set.min_values)+ "\n"
        s += " Max rhs:" + str(self.rhs_set.max_values)+ "\n" 
        s += " Min rhs:" + str(self.rhs_set.min_values)        
        s += '\n--------\n'
        return s
                
    def getNonAdjacentRegion(self, value, attribute):    
        dataset = self.getAdjacentRegion(value, attribute)
        if dataset is self.lhs_set:
            return self.rhs_set
        if dataset is self.rhs_set:
            return self.lhs_set
        return None
        
    def getAdjacentRegion(self, value, attribute):
        def getMinimumDistanceFromValue(dataset, attribute, value):
            distance1 = abs(dataset.get_max(attribute) - value)
            distance2 = abs(dataset.get_min(attribute) - value)
            return min(distance1, distance2)
        rhs_distance = getMinimumDistanceFromValue(self.rhs_set, attribute, value)
        lhs_distance = getMinimumDistanceFromValue(self.lhs_set, attribute, value)

        if lhs_distance < rhs_distance: return self.rhs_set
        else: return self.lhs_set
    
    def getRelativeDensityOfLowerDensityRegion(self):    
        lower_density_set = self.getLowerDensityRegion()                                                    
        r_density = _relative_density(lower_density_set)                
        return r_density

    def getLowerDensityRegion(self):
        if self.lhs_set is None or self.rhs_set is None:
            self.raiseNoRegionsDefined()
            
        if _relative_density(self.lhs_set) > _relative_density(self.rhs_set):
            return self.rhs_set
        else:
            return self.lhs_set  
    
    def raiseNoRegionsDefined(self):
        raise Cut.NoRegionsDefined("hi")
    class NoRegionsDefined(Exception):
        pass    
       
         
class CLNode(object):
    def __init__(self, dataset, parent, attribute, depth):
        self.dataset = dataset
        self.parent = parent
        self.attribute = attribute
        self.children = list()
        self.can_prune = False

    def setPruneState(self, prune):
        self.can_prune = prune

    def isPrune(self):
        return self.can_prune

    def getRelativeDensity(self):
        return _relative_density(self.dataset)*100.0

    def getNrInstancesInNode(self):
        return self.dataset.length()
    
    def addChildNode(self, node):
        self.children.append(node)

    def getChildNodes(self):
        return self.children
    
    def isLeaf(self):
        if len(self.children) == 0: 
            return True
        else: 
            return False

    def raiseAddNode(self):
        raise CLNode.AddNodeIlogical("hi")
    class AddNodeIlogical(Exception):
        pass   
    
    def _getMajorityClassName(self):
        counts = [0] * len(self.dataset.class_names)
        class_idx = dict()
        for i, cls in enumerate(self.dataset.class_names):
            class_idx[cls] = i
        new_dict = dict (zip(self.dataset.class_map.values(),self.dataset.class_map.keys()))            
        for cls in list(self.dataset.getClasses()):
            v = new_dict[cls]
            counts[class_idx[v]] += 1
            
        max_count = -2
        self.max_class = -1 
        for i, c in enumerate(counts):
            if c > max_count:
                max_count = c
                self.max_class = self.dataset.class_names[i]        

        self.percent = int((max_count / float(self.dataset.length()) )* 100)               
        self.misclassified = self.dataset.length() - max_count

    def __str__(self):
        attr = list()
        p = self
        while p:
            attr.append(p.attribute)
            p = p.parent
        
        self._getMajorityClassName()
        s = 'Node: ' + '\n'
        s += str(self.dataset.length()) + ' instances, ' + str(self.misclassified) + ' misclassified, ' + str(self.percent)+ '% '+ self.max_class
        s += ", " + str(int(self.getRelativeDensity())) + " relative density " + '\n'
        s += "Cuts " + str(set(attr))+ '\n'
        
        self.dataset.calculate_limits()
        for name in self.dataset.attr_names:
            s += name + ' max: ' + str(self.dataset.get_max(name))+\
                ' min: ' + str(self.dataset.get_min(name))+'\n'
        
        return s


         
         
