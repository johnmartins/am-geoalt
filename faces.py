import numpy as np

from verticies import *

class FaceCollection:
    '''
    Collection of Face objects
    '''
    def __init__(self):
        self.faces = []
        self.problem_faces = []
        self.good_faces = []

        self.vertex_collection = VertexCollection()

        self.iterator_pointer = 0
    
    def append(self, face):
        '''
        Add face to face collection
        '''

        if (isinstance(face, Face) is False):
            raise TypeError('face argument needs to be of type Face()')
        if face.has_bad_angle is True:
            self.problem_faces.append(face)
        else:
            self.good_faces.append(face)

        face.vertex1 = self.vertex_collection.add(face.vertex1)
        face.vertex2 = self.vertex_collection.add(face.vertex2)
        face.vertex3 = self.vertex_collection.add(face.vertex3)

        self.faces.append(face)
    
    def __iter__(self):
        '''
        Contributes to making this class iterable by providing an interface
        '''
        return self

    def __next__(self):
        '''
        Contributes to making this class iterable by providing a pointer.
        '''
        if self.iterator_pointer > (len(self.faces) - 1):
            self.iterator_pointer = 0
            raise StopIteration
        else: 
            self.iterator_pointer += 1
            return self.faces[self.iterator_pointer - 1]
    
    def get_warning_count(self):
        '''
        Returns the amount of potentially problematic faces
        '''
        return len(self.problem_faces)

    def get_verticies(self, vtype="all"):
        return_array = []
        if vtype=="all":
            for f in self.faces:
                return_array.append(f.get_verticies())
        elif vtype=="bad":
            for f in self.problem_faces:
                return_array.append(f.get_verticies())
        elif vtype=="good":
            for f in self.good_faces:
                return_array.append(f.get_verticies())
        return return_array

    def get_vertex_collection(self):
        return self.vertex_collection


class Face:
    '''
    STL polygon face
    '''
    def __init__(self, vertex1, vertex2, vertex3, n):
        '''
        vert1, vert2, vert3: verticies of a polygon\n
        n: normal vector\n
        phi_min: minimum angular difference between normal vector and -z_hat before marked as a problematic surface
        '''
        self.vertex1 = Vertex.from_array(vertex1)
        self.vertex2 = Vertex.from_array(vertex2)
        self.vertex3 = Vertex.from_array(vertex3)

        self.v1 = None
        self.v2 = None
        self.__set_vectors__()

        self.n = n
        self.n_hat = n / np.linalg.norm(n)
        self.has_bad_angle, self.angle = self.check_for_problems()

    def __set_vectors__(self):
        self.v1 = self.vertex1.get_array() - self.vertex2.get_array()
        self.v2 = self.vertex3.get_array() - self.vertex2.get_array()
    
    def check_for_problems(self, phi_min=np.pi/4, ignore_grounded=True):
        '''
        phi_min: Min angle before problem, in rads.
        ignore_grounded: Ignore surfaces close to the floor (prone to visual buggs in python)
        '''
        # Check the angle of the normal factor, and compare it to that of the inverted z-unit vector
        neg_z_hat = [0,0,-1]
        angle = np.arccos(np.clip(np.dot(self.n_hat, neg_z_hat), -1.0, 1.0))
        if angle >= 0 and angle < phi_min:
            if self.vertex1.get_array()[2] < 0.01 and self.vertex2.get_array()[2] < 0.01 and self.vertex3.get_array()[2] < 0.01 and ignore_grounded is False:
                return False, angle
            return True, angle

        return False, angle

    def get_verticies(self):
        return np.array([self.vertex1.get_array(), self.vertex2.get_array(), self.vertex3.get_array()])