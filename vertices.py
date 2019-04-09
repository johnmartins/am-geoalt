import numpy as np

class VertexCollection(set):

    def add(self, vertex):
        '''
        Add vertex to collection. 
        O(1), constant time
        '''
        contains_res = self.contains(vertex)
        if contains_res is not None:
            return contains_res
        
        super().add(vertex)

        return vertex
    
    def contains(self, vertex):
        '''
        Check if vertex exists in set
        O(n), linear time
        '''
        if vertex in self:
            for v in self:
                if v.__eq__(vertex):
                    return v
        else:
            return None
        raise IndexError("Something went terribly wrong when using contains method in VertexCollection.")


class Vertex:
    '''
    Class variables:\n
        eq_method: "exact" or "proximity". Exact is quick, but imprecise. Proximity is slow, but better.\n
    '''
    eq_method = "proximity"

    def __init__(self, facecol, index):
        self.facecol = facecol
        self.index = index
        self.change_set = []        # An array of changes proposed by the problem solver
        
        # These variables are responsible for a vertex "knowledge" of its surrounding vertices
        self.adjacencies = set()    # A set of all adjacent vertices
        self.is_pole = True         # True if all adjacent vertices are above this vertex.

    def x(self):
        return self.facecol.stlfile.vertices[self.index][0]

    def y(self):
        return self.facecol.stlfile.vertices[self.index][1]

    def z(self):
        return self.facecol.stlfile.vertices[self.index][2]

    def __str__(self):
        return "VX({}, {}, {})".format(self.x(), self.y(), self.z())

    def __eq__(self, other):
        if Vertex.eq_method == "proximity":
            # Slow, but more certain
            if abs(self.x() - other.x()) > 0.001:
                return False
            if abs(self.y() - other.y()) > 0.001:
                return False
            if abs(self.z() - other.z()) > 0.001:
                return False
            return True
        elif Vertex.eq_method == "exact":
            # Fast, but might cause leaks
            if self.x() == other.x() and self.y() == other.y() and self.z() == other.z():
                return True
            return False
        else:
            raise TypeError("Unknown eq method for Vertex class")

    def __hash__(self):
        h = hash(self.x()+self.y()+self.z())
        return h

    def get_array(self):
        '''
        Returns the vertex as a coordinate vector in the form of a numpy array
        '''
        return np.array(self.facecol.stlfile.vertices[self.index])

    def set_array(self, array):
        '''
        Set the coordinate value of the vertex using a R^3 array
        '''
        self.facecol.vertices[self.index] = array

    def set_adjacency(self, vertex):
        self.adjacencies.add(vertex)
        vertex.adjacencies.add(self)
        if vertex.z() < self.z():
            self.is_pole = False
        else:
            vertex.is_pole = False
        
        if np.abs(vertex.z() - self.z()) < 0.01:
            self.is_pole = False
            vertex.is_pole = False

    def add_change_partial(self, vector):
        self.change_set.append(vector)
    
    def reset_change_set(self):
        self.change_set = []

    def perform_change(self):
        if len(self.change_set) == 0:
            return
        net_vector = np.array([0,0,0])
        for v in self.change_set:
            net_vector = net_vector + v

        net_vector_mean = net_vector/len(self.change_set)
        
        self.set_array(self.get_array() + net_vector_mean)
        self.reset_change_set()
        return net_vector_mean