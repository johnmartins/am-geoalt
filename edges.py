class EdgeCollection(set):

    def add(self, edge):
        '''
        Add an edge to the collection
        '''
        contains_res = self.contains(edge)
        if contains_res is not None:
            return contains_res
        
        super().add(edge)
        return edge

    def contains(self, edge):
        if edge in self:
            for e in self:
                if e.__eq__(edge):
                    return e
        else:
            return None
        raise IndexError("Something went south when searching the edge collection.")

class Edge:
    def __init__(self, vertex1, vertex2):
        self.vertex1 = vertex1
        self.vertex2 = vertex2

        self.faces = []

    def add_face(self, face):
        self.faces.append(face)

    def __hash__(self):
        # Är vertex1 och 2 satta?
        h = hash(self.vertex1.x + self.vertex2.x + self.vertex1.y + self.vertex2.y+ self.vertex1.z + self.vertex2.z)
        return h

    def __eq__(self, other):
        if self.vertex1 == other.vertex1 and self.vertex2 == other.vertex2:
            return True
        elif self.vertex2 == other.vertex1 and self.vertex1 == other.vertex2:
            return True
        return False