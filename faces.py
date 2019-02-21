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

    def check_for_problems(self, phi_min=np.pi/4, ignore_grounded=False, ground_level=0, ground_tolerance=0.01):
        self.good_faces = []
        self.problem_faces = []
        for f in self.faces:
            f.refresh_normal_vector()
            has_bad_angle, angle = f.check_for_problems(phi_min=phi_min, ignore_grounded=ignore_grounded, ground_level=ground_level, ground_tolerance=ground_tolerance)
            if has_bad_angle is True:
                self.problem_faces.append(f)
            else: 
                self.good_faces.append(f)


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
        self.top_z = self.__calc_top_z__()

        self.v1 = None
        self.v2 = None
        self.__set_vectors__()

        self.n = n
        self.n_hat = n / np.linalg.norm(n)
        self.has_bad_angle = None
        self.angle = None

    def __connect_verticies__(self):
        '''
        Connect all verticies to each other
        '''
        self.vertex1.set_adjacency(self.vertex2)
        self.vertex1.set_adjacency(self.vertex3)
        self.vertex2.set_adjacency(self.vertex3)

    def __calc_top_z__(self):
        M = np.array([self.vertex1.get_array(), self.vertex2.get_array(), self.vertex3.get_array()])
        z_array = M[:,2]
        index_lowest_first = np.argsort(z_array)
        topz = M[index_lowest_first[2],2]
        return topz

    def __set_vectors__(self):
        self.v1 = self.vertex1.get_array() - self.vertex2.get_array()
        self.v2 = self.vertex3.get_array() - self.vertex2.get_array()

    def refresh_normal_vector(self):
        vector1 = self.vertex2.get_array() - self.vertex1.get_array()
        vector2 = self.vertex3.get_array() - self.vertex1.get_array()
        self.n = np.cross(vector1, vector2)
        self.n_hat = self.n/np.linalg.norm(self.n)
    
    def check_for_problems(self, phi_min=np.pi/4, ignore_grounded=False, ground_level=0, ground_tolerance = 0.01):
        '''
        phi_min: Min angle before problem, in rads.
        ignore_grounded: Ignore surfaces close to the floor (prone to visual buggs in python)
        '''
        # Check the angle of the normal factor, and compare it to that of the inverted z-unit vector
        neg_z_hat = [0,0,-1]
        angle = np.arccos(np.clip(np.dot(self.n_hat, neg_z_hat), -1.0, 1.0))
        self.angle = angle

        # Check if angle is within problem threshold
        if angle >= 0 and angle < phi_min:

            # Check if grounded
            if self.check_grounded(ground_level, ground_tolerance) is True and ignore_grounded is False:
                self.has_bad_angle = False
                return False, angle
            
            self.has_bad_angle = True
            return True, angle
        
        self.has_bad_angle = False
        return False, angle

    def get_verticies(self):
        return np.array([self.vertex1.get_array(), self.vertex2.get_array(), self.vertex3.get_array()])

    def __lt__(self, other):
        if self.top_z > other.top_z:
            return True
        else: 
            return False

    def check_grounded(self, ground_level, ground_tolerance):
        '''
        Check if this surface is parallel to the ground.
        '''
        # Calculate differences between individual vertex Z-elements, and the ground level.
        diff_1 = np.abs(self.vertex1.get_array()[2] - ground_level)
        diff_2 = np.abs(self.vertex2.get_array()[2] - ground_level)
        diff_3 = np.abs(self.vertex3.get_array()[2] - ground_level)

        # If any of the ground levels is above the threshold, then return false, else return true.
        if diff_1 > ground_tolerance or diff_2 > ground_tolerance or diff_3 > ground_tolerance:
            return False
        
        return True
        