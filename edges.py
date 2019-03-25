class EdgeCollection(set):
    '''
    Collection of Edge objects
    '''
    def __init__(self):
        self.edges = []
        self.faces = []
    
    def add(self, edge):
        if (isinstance(edge, Edge) is False):
            raise TypeError('Edge argument needs to be of type Edge.')
        else:
            contains_res = self.contains(edge)
            if contains_res is not None:
                return contains_res

            super().add(edge)
            return edge
    
    def contains(self, edge):
        '''
        Check if edge exists in set.
        '''

        if edge in self:
            for e in self:
                if e.__eq__(edge):
                    return e
        else:
            return None
        raise IndexError("Something went terribly wrong when using contains method in edge collection.")
    
    
class Edge:
    def __init__(self, vertex1, vertex2):
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.faces = []
    
    def __eq__(self, other):
        if self.vertex1.__eq__(other.vertex1) and self.vertex2.__eq__(other.vertex2):
            return True
        if self.vertex2.__eq__(other.vertex1) and self.vertex1.__eq__(other.vertex2):
            return True
        return False

    def __hash__(self):
        h = hash(self.vertex1.z + self.vertex2.z)
        return h

    def associate_with_face(self, face):
        if face not in self.faces:
            self.faces.append(face)
        else:
            print("Dafuq")