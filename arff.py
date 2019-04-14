import numpy as np
import copy

class Data:
    '''ARFF Data'''
    def __init__(self, instance_values, class_map, class_names, types):
        self.instance_values = instance_values
        self.class_map = class_map
        self.class_names = class_names
        self.attr_types = types
        self.attr_idx = dict()
        self.attr_names = list()
        
        self._init_attr_names()
        self._init_max_min()
                    
        self.nr_virtual_points = len(self.instance_values)
        self.nr_total_instances = 2*self.nr_virtual_points
                    
    def _init_max_min(self):
        if len(self.instance_values) > 1:
            self.instance_view = self.instance_values.view(dtype=float).reshape(len(self.instance_values),-1)            
            self.max_values = np.amax(self.instance_view, 0) 
            self.min_values = np.amin(self.instance_view, 0)             
        else:
            self.instance_view = self.instance_values.view(dtype=float)
            self.max_values = copy.copy(self.instance_view)
            self.min_values = copy.copy(self.instance_view)
            
    def _init_attr_names(self):
        for i, attr in enumerate(self.attr_types):
            #if i == 0: #Dimitri
            if i < 2:
                continue
            attr_name, attr_type = attr
            self.attr_idx[attr_name] = i
            self.attr_names.append(attr_name)
        
    def __str__(self):
        s = 'Data: ' + str(len(self.instance_values)) + "\n"
        s += str(self.attr_names) + "\n"  
        s += " Max :" + str(self.max_values)+ "\n"  
        s += " Min :" + str(self.min_values)+ "\n"
        s += str(self.instance_values)
        s += '\n--------\n'
        return s
    
    def calculate_limits(self):
        self._init_max_min()
        
    def sort(self, attribute):
        self.instance_values.sort(order=attribute)
        
    def length(self):
        return len(self.instance_values)

    def getClasses(self):
        idx = 1
        if self.length() > 1:
            return self.instance_view[:,idx]
        elif self.length() == 1:
            return [self.instance_view[idx]]
        else:
            return []
    
    def getInstances(self, attribute):
        idx = self.attr_idx[attribute]
        if self.length() > 1:
            return self.instance_view[:,idx]
        elif self.length() == 1:
            return [self.instance_view[idx]]
        else:
            return []
        
    def getInstanceIndex(self, id):
        if self.length() > 1:                
            idx = np.argwhere(self.instance_view[:,0] == id)
            print(idx)
            return idx[0]
        elif self.length() == 1 and id == self.instance_view[0]:            
            return [0]
        else:
            return None
    
    def getId(self, idx):
        if self.length() > 1:        
            return self.instance_view[idx][0]
        elif self.length() == 1:
            return self.instance_view[0]
        else:
            return -1
                    
    def get_max(self, attribute):
        idx = self.attr_idx[attribute]
        return self.max_values[idx]
    def get_min(self, attribute):
        idx = self.attr_idx[attribute]
        return self.min_values[idx]
    def set_max(self, attribute, value):
        if len(self.max_values) > 0:
            idx = self.attr_idx[attribute]
            self.max_values[idx] = value
    def set_min(self, attribute, value):
        if len(self.min_values) > 0:
            idx = self.attr_idx[attribute]
            self.min_values[idx] = value


    

class ArffReader:
    def __init__(self):
        pass
    
    def read(self, filename):
        f = open(filename, 'r')
        types, classes_names = self._read_header(f)
        
        class_map = dict()
        for i, name in enumerate(classes_names):
            class_map[name] = float(i)
        
        output = self._read_instances(f, class_map)
        output = np.array(output, dtype=types)
        data = Data(output, class_map, classes_names, types)
                
        print ("read " + str(data.length()) + ' instances from ' + filename)
        print ("attribute names:", data.attr_types)
        print ("class names:", data.class_names)
        return data
        
    def _read_header(self, contents):
        dtype = list() 
        classes = None
        dtype.append(("id", float))        
        dtype.append(("class", float))  
        for line in contents:
            line = line.strip().lower()
            if line.startswith("%") or line.startswith("@RELATION"):
                continue
            if line == "@data":
                break            
            if line.find("@attribute") != -1:
                attr_name, attr_type = self._getAttribute(line)
                if attr_type in ["real", "numeric"]:
                    dtype.append((attr_name, float))
                elif attr_name == "class":
                    classes = attr_type.split(",")
                else:
                    raise NotImplemented()
        return dtype, classes

    def _getAttribute(self, line):
        attr_, attr_name, attr_type = line.split()
        attr_name = attr_name.lower()
        attr_type = attr_type.strip("'").strip("{").strip("}").lower()
        return attr_name, attr_type
        
    def _read_instances(self, contents, class_map): 
        output = list()
        class_values = list()
        count = 0.0
        for line in contents:
            if line.startswith("%"):
                continue
            line = line.split(',')
            row = list()
            row.append(count)
            cls = class_map[line[-1].strip('\n')]
            row.extend([cls]) #class
            row.extend([float(s.strip()) for s in line[0:-1]])
            output.append(tuple(row))
            count += 1.0
        return output

