import re
from faces import Face, FaceCollection
from vertices import Vertex
from timeit import default_timer as timer
import numpy as np
from stl_creator import STLCreator
from struct import unpack

class STLfile:
    def __init__(self, filename):
        self.filename = filename
        self.header = ""
        self.vertices = []
        self.normals = []
        self.ground_level = 0

    def rotate(self, theta, axis):
        b = np.array(self.vertices).T

        if axis == "x":
            T = np.array([
                [1,0,0],
                [0,np.cos(theta),-np.sin(theta)],
                [0,np.sin(theta),np.cos(theta)]
            ])
        elif axis == "y":
            T = np.array([
                [np.cos(theta),0,np.sin(theta)],
                [0,1,0],
                [-np.sin(theta),0,np.cos(theta)]
            ])
        elif axis == "z":
            pass
        else:
            raise TypeError('Value of axis needs to be the string value of x, y, or z.')

        res = np.dot(T, b)
        self.vertices = res.T.tolist()
        self.calculate_ground_level()

    def calculate_ground_level(self):
        verts = np.array(self.vertices)
        self.ground_level = verts.min(axis=0)[2]

    def new_face(self, facecol, n):
        normal_index = len(self.normals)
        vertex_index = len(self.vertices)
        self.normals.append(n)

        face = Face(facecol, normal_index, vertex_index)
        return face

    def new_vertex(self, face, array):
        vertex_index = len(self.vertices)
        self.vertices.append(array)
        face.vertices.append(Vertex(face.face_collection, vertex_index))

    def load(self):
        f = open(self.filename, 'rb')
        type_str = f.read(5).decode('utf-8')
        f.close()

        if "SOLID" in type_str.upper():
            return self.load_ascii()
        if "COLOR" in type_str.upper():
            raise TypeError("COLOR STL UNSUPPORTED ATM")
        else:
            return self.load_binary()


    def load_binary(self):
        facecol = FaceCollection(self)
        f = open(self.filename, 'rb')

        self.header = f.read(80).decode('utf-8')
        face_count = int.from_bytes(f.read(4), byteorder='little', signed=False)

        for i in range(0,face_count):
            n = unpack('<fff', f.read(12))
            face = self.new_face(facecol, [n[0], n[1], n[2]])

            v1 = unpack('<fff', f.read(12))
            self.new_vertex(face, [v1[0], v1[1], v1[2]])
            v2 = unpack('<fff', f.read(12))
            self.new_vertex(face, [v2[0], v2[1], v2[2]])
            v3 = unpack('<fff', f.read(12))
            self.new_vertex(face, [v3[0], v3[1], v3[2]])

            face.n_hat_original = face.refresh_normal_vector()
            facecol.append(face)

            spacer = int.from_bytes(f.read(2), byteorder='little', signed=False)

        f.close()

        self.calculate_ground_level()
        return facecol

    def load_ascii(self):
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
                        print("END SOLID.")
                        break
                    else:
                        search = re.search(r"facet\snormal\s+(\S+)\s+(\S+)\s+(\S+)", line)
                        current_face = self.new_face(facecol, np.array([float(search.group(1)),float(search.group(2)),float(search.group(3))]))
                elif fl == 2 or fl == 6 :
                    # Outer loop or End loop
                    pass
                elif fl in range(3,6):
                    # Vertex
                    vertexStr = line
                    search = re.search(r"vertex\s+(\S+)\s+(\S+)\s+(\S+)", vertexStr)
                    self.new_vertex(current_face, np.array([float(search.group(1)),float(search.group(2)),float(search.group(3))]))
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

def testParser():
    t1 = timer()

    stl = STLfile("models/architecture.stl")
    facecol = stl.load_ascii()
    t2 = timer()

    print(len(stl.normals))
    print(len(stl.vertices))
    print(len(facecol.get_vertex_collection()))

    dt = t2 - t1
    print("Time: %.2f seconds" % dt)

    for e in facecol.edge_collection:
        if len(e.faces) != 2:
            print("POTENTIAL LEAK DETECTED!")

    stl_creator = STLCreator("fixed_models/test.stl", facecol)
    stl_creator.build_file()
    print("Done")

def testRotate():
    print("Rotate")
    b = np.array([[0,0,1],[0,1,0]]).T
    theta = np.pi/2
    a = np.array([
        [np.cos(theta),0,np.sin(theta)],
        [0,1,0],
        [-np.sin(theta),0,np.cos(theta)]
    ])
    res = np.dot(a, b)
    print(res)

def testBinary():
    t1 = timer()

    stl = STLfile("models/wiffle.stl")
    facecol = stl.load()

    t2 = timer()