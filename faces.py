import numpy as np
import numpy.linalg as linalg

from verticies import *

class FaceCollection:
    '''
    Collection of Face objects
    '''
    def __init__(self):
        self.faces = []
        self.problem_faces = []
        self.good_faces = []

        self.problem_verticies = []
        self.good_verticies = []
        self.verticies = []
        self.vertex_collection = VertexCollection()

        self.iterator_pointer = 0
    
    def append(self, face):
        if (isinstance(face, Face) is False):
            raise TypeError('face argument needs to be of type Face()')
        if face.has_bad_angle is True:
            self.problem_faces.append(face)
            self.problem_verticies.append(face.get_verticies())
        else:
            self.good_faces.append(face)
            self.good_verticies.append(face.get_verticies())

        self.vertex_collection.add(Vertex.from_array(face.get_verticies()[0]))
        self.vertex_collection.add(Vertex.from_array(face.get_verticies()[1]))
        self.vertex_collection.add(Vertex.from_array(face.get_verticies()[2]))

        self.verticies.append(face.get_verticies())
        self.faces.append(face)
    
    def __iter__(self):
        return self

    def __next__(self):
        if self.iterator_pointer > (len(self.faces) - 1):
            self.iterator_pointer = 0
            raise StopIteration
        else: 
            self.iterator_pointer += 1
            return self.faces[self.iterator_pointer - 1]
    
    def get_warning_count(self):
        return len(self.problem_faces)

    def get_verticies(self, vtype="all"):
        if vtype=="all":
            return self.verticies
        elif vtype=="bad":
            return self.problem_verticies
        elif vtype=="good":
            return self.good_verticies

    def get_vertex_collection(self):
        return self.vertex_collection


class Face:
    '''
    STL polygon face
    '''
    def __init__(self, vert1, vert2, vert3, n):
        '''
        vert1, vert2, vert3: verticies of a polygon\n
        n: normal vector\n
        phi_min: minimum angular difference between normal vector and -z_hat before marked as a problematic surface
        '''
        self.vert1 = Vertex.from_array(vert1)
        self.vert2 = Vertex.from_array(vert2)
        self.vert3 = Vertex.from_array(vert3)

        self.v1 = None
        self.v2 = None
        self.__set_vectors__()

        self.n = n
        self.n_hat = n / linalg.norm(n)
        self.has_bad_angle = self.check_for_problems()

    def __set_vectors__(self):
        self.v1 = self.vert1.get_array() - self.vert2.get_array()
        self.v2 = self.vert3.get_array() - self.vert2.get_array()
    
    def check_for_problems(self, phi_min=np.pi/4, ignore_grounded=True):
        '''
        phi_min: Min angle before problem, in rads.
        ignore_grounded: Ignore surfaces close to the floor (prone to visual buggs in python)
        '''
        # Check the angle of the normal factor, and compare it to that of the inverted z-unit vector
        neg_z_hat = [0,0,-1]
        angle = np.arccos(np.clip(np.dot(self.n_hat, neg_z_hat), -1.0, 1.0))
        if angle >= 0 and angle < phi_min:
            if self.vert1.get_array()[2] < 0.01 and self.vert2.get_array()[2] < 0.01 and self.vert3.get_array()[2] < 0.01 and ignore_grounded is False:
                return False
            return True

        return False

    def get_verticies(self):
        return np.array([self.vert1.get_array(), self.vert2.get_array(), self.vert3.get_array()])