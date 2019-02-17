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
        len_before = len(self)
        super().add(vertex)
        len_after = len(self)
        # Only append xyz-arrays if the object actualy was added to the set.
        if (len_after > len_before):
            self.x_vals.append(vertex.x)
            self.y_vals.append(vertex.y)
            self.z_vals.append(vertex.z)


class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
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
        return int(round(self.x + self.y + self.z)) # Not a great hash function

    def get_array(self):
        return np.array([self.x, self.y, self.z])