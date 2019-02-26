import numpy as np

class VertexCollection(set):
    '''
    Collection of verticies. Can only contain one vertex per coordinate (no duplicates)
    '''
    def __init__(self):
        self.x_vals = []
        self.y_vals = []
        self.z_vals = []

    def add(self, vertex):
        '''
        Add vertex to collection. 
        O(1), constant time
        '''
        contains_res = self.contains(vertex)
        if contains_res is not None:
            return contains_res
        
        super().add(vertex)
        self.x_vals.append(vertex.x)
        self.y_vals.append(vertex.y)
        self.z_vals.append(vertex.z)
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
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.adjacencies = set()
        self.change_set = []
    
    @classmethod
    def from_array(cls, array):
        if len(array) != 3:
            raise IndexError("The amount of elements can only be exactly 3 when using from_array method to create a Vertex")
        (x, y, z) = array
        return cls(x,y,z)

    def __str__(self):
        return "VX({}, {}, {})".format(self.x, self.y, self.z)

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y and self.z == other.z:
            return True
        return False

    def __hash__(self):
        return int(round(self.x + self.y + self.z)) # Not a great hash function. Should use a prime number, and modulus

    def get_array(self):
        '''
        Returns the vertex as a coordinate vector in the form of a numpy array
        '''
        return np.array([self.x, self.y, self.z])

    def set_array(self, array):
        '''
        Set the coordinate value of the vertex using a R^3 array
        '''
        self.x, self.y, self.z = array

    def set_adjacency(self, vertex):
        self.adjacencies.add(vertex)
        vertex.adjacencies.add(self)

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