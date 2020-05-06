import re
from timeit import default_timer as timer
import numpy as np
from struct import unpack

from geoalt_geometry.faces import Face, FaceCollection
from geoalt_geometry.vertices import Vertex
from geoalt_stl.stl_creator import STLCreator

class STLfile:
    def __init__(self, filename):
        self.filename = filename
        self.header = ""
        self.vertices = []
        self.normals = []
        self.ground_level = 0
        self.grounded = False       # This variable is set by the external "Face" class.

    def rotate(self, theta, axis):
        '''
        Rotate the model around the X, Y or Z axis. The results are immediately stored.
        '''
        self.grounded = False # Rotating the model could cause the model to no longer be grounded.

        b = np.array(self.vertices).T

        if axis.lower() == "x":
            T = np.array([
                [1,0,0],
                [0,np.cos(theta),-np.sin(theta)],
                [0,np.sin(theta),np.cos(theta)]
            ])
        elif axis.lower() == "y":
            T = np.array([
                [np.cos(theta),0,np.sin(theta)],
                [0,1,0],
                [-np.sin(theta),0,np.cos(theta)]
            ])
        elif axis.lower() == "z":
            raise NotImplementedError("Rotation around the Z-axis is not yet implemented.")
        else:
            raise TypeError('Value of axis needs to be the string value of x, y, or z.')

        res = np.dot(T, b)
        self.vertices = res.T.tolist()
        self.calculate_ground_level()

    def calculate_ground_level(self):
        '''
        Fetches the lowest Z-element that can be found in the current orientation of the model.
        Notice that the ground level changes if the model is rotated, but is automatically recalculated and can be fetched through the stl.ground_level variable.
        '''
        verts = np.array(self.vertices)
        self.ground_level = verts.min(axis=0)[2]

    def __new_face__(self, facecol, n):
        '''
        Create and store a new face.
        '''
        normal_index = len(self.normals)
        vertex_index = len(self.vertices)
        self.normals.append(n)

        face = Face(facecol, normal_index, vertex_index)
        return face

    def __new_vertex__(self, face, array):
        '''
        Create and store a new vertex
        '''
        vertex_index = len(self.vertices)
        self.vertices.append(array)
        face.vertices.append(Vertex(face.face_collection, vertex_index))

    def load(self):
        '''
        This generic load method is used to load any type of .stl-file. It will compensate automatically for ASCII, binary or colored binary STLs.
        '''
        f = open(self.filename, 'rb')
        type_str = f.read(5).decode('utf-8')
        f.close()

        if "SOLID" in type_str.upper():
            try:
                return self.load_ascii()
            except UnicodeDecodeError:
                # If it fails to load as ascii, then it is probaby a binary file.
                return self.load_binary()
        elif "COLOR" in type_str.upper():
            print("COLOR LOAD")
            return self.load_binary(color=True)

        return self.load_binary()

    def load_binary(self, color=False):
        '''
        Load function specifically made for binary files. 
        '''
        facecol = FaceCollection(self)
        f = open(self.filename, 'rb')

        if color is True:
            f.read(80)
            self.header = "Colored solid."
        else:
            try:
                self.header = f.read(80).decode('utf-8')
            except UnicodeDecodeError:
                f.close()
                return self.load_binary(color=True)
        
        face_count = int.from_bytes(f.read(4), byteorder='little', signed=False)

        for i in range(0,face_count):
            n = unpack('<fff', f.read(12))
            face = self.__new_face__(facecol, [n[0], n[1], n[2]])

            v1 = unpack('<fff', f.read(12))
            self.__new_vertex__(face, [v1[0], v1[1], v1[2]])
            v2 = unpack('<fff', f.read(12))
            self.__new_vertex__(face, [v2[0], v2[1], v2[2]])
            v3 = unpack('<fff', f.read(12))
            self.__new_vertex__(face, [v3[0], v3[1], v3[2]])

            face.n_hat_original = face.refresh_normal_vector()
            facecol.append(face)

            spacer = int.from_bytes(f.read(2), byteorder='little', signed=False)

        f.close()

        self.calculate_ground_level()
        return facecol

    def load_ascii(self):
        '''
        Load function specifically made for ASCII files.
        '''
        facecol = FaceCollection(self)

        f = open(self.filename, 'r')
        ln = 1 # File line nr
        fl = 1 # Face line nr

        current_face = None

        for line in f:
            if ln == 1:
                self.header = line
            else:
                if fl == 1:
                    # Face normal
                    # Create new face
                    if "endsolid" in line:
                        # End of the file.
                        print("Reached end of solid.")
                        break
                    else:
                        search = re.search(r"facet\snormal\s+(\S+)\s+(\S+)\s+(\S+)", line)
                        current_face = self.__new_face__(facecol, np.array([float(search.group(1)),float(search.group(2)),float(search.group(3))]))
                elif fl == 2 or fl == 6 :
                    # Outer loop or End loop
                    pass
                elif fl in range(3,6):
                    # Vertex
                    vertexStr = line
                    search = re.search(r"vertex\s+(\S+)\s+(\S+)\s+(\S+)", vertexStr)
                    self.__new_vertex__(current_face, np.array([float(search.group(1)),float(search.group(2)),float(search.group(3))]))
                elif fl == 7:
                    # End facet
                    current_face.n_hat_original = current_face.refresh_normal_vector() 
                    facecol.append(current_face)
                    current_face = None
                    fl = 0
                else:
                    raise TypeError("Error encountered when parsing through face. Unhandled face line number.")
                fl += 1 # Face line += 1
            ln += 1 # File line += 1
        f.close()
        self.calculate_ground_level()
        return facecol
