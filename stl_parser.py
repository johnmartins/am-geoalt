import re
from faces import Face, FaceCollection
from vertices import Vertex
from timeit import default_timer as timer
import numpy as np
from stl_creator import STLCreator

class STLfile:
    def __init__(self, filename):
        self.filename = filename
        self.header = ""
        self.vertices = []
        self.normals = []

    def new_face(self, facecol, n):
        normal_index = len(self.normals)
        vertex_index = len(self.vertices)
        self.normals.append(n)

        face = Face(facecol, normal_index, vertex_index)
        return face

    def new_vertex(self, face, array):
        #print("Vertex: %s" % array)
        vertex_index = len(self.vertices)
        self.vertices.append(array)
        face.vertices.append(Vertex(face.face_collection, vertex_index))

    def load_binary(self):
        f = open(self.filename, 'rb')
        f.close()
        pass

    def load_ascii(self):
        facecol = FaceCollection(self)

        f = open(self.filename, 'r')
        ln = 1 # File line nr
        fl = 1 # Face line nr

        t1_tot = 0
        t2_tot = 0
        t3_tot = 0
        t4_tot = 0
        t5_tot = 0

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
                    t7_1 = timer()
                    # End facet
                    current_face.n_hat_original = current_face.refresh_normal_vector() 
                    t2, t3, t4, t5 = facecol.append(current_face)
                    t2_tot += t2
                    t3_tot += t3
                    t4_tot += t4
                    t5_tot += t5
                    current_face = None
                    fl = 0
                else:
                    raise TypeError("Error encountered when parsing through face. Unhandled face line number.")
                fl += 1 # Face line += 1
            ln += 1 # File line += 1
        f.close()

        print("Performance:")
        print("t2 tot: %.2f" % t2_tot)
        print("t3 tot: %.2f" % t3_tot)
        print("t4 tot: %.2f" % t4_tot)
        print("t5 tot: %.2f" % t5_tot)
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