from stl import mesh
import stl
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import numpy.linalg as linalg
import matplotlib.pyplot as plt
import time

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
        return self.x + self.y + self.z # Not a great hash function


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
        self.vert1 = vert1
        self.vert2 = vert2
        self.vert3 = vert3

        self.v1 = None
        self.v2 = None
        self.__set_vectors__()

        self.n = n
        self.n_hat = n / linalg.norm(n)
        self.has_bad_angle = self.check_for_problems()

    def __set_vectors__(self):
        self.v1 = np.array(self.vert1) - np.array(self.vert2)
        self.v2 = np.array(self.vert3) - np.array(self.vert2)
    
    def check_for_problems(self, phi_min=np.pi/4, ignore_grounded=True):
        '''
        phi_min: Min angle before problem, in rads.
        ignore_grounded: Ignore surfaces close to the floor (prone to visual buggs in python)
        '''
        # Check the angle of the normal factor, and compare it to that of the inverted z-unit vector
        neg_z_hat = [0,0,-1]
        angle = np.arccos(np.clip(np.dot(self.n_hat, neg_z_hat), -1.0, 1.0))
        if angle >= 0 and angle < phi_min:
            if self.vert1[2] < 0.01 and self.vert2[2] < 0.01 and self.vert3[2] < 0.01 and ignore_grounded is False:
                return False
            return True

        return False

    def get_verticies(self):
        return np.array([self.vert1, self.vert2, self.vert3])


def collect_faces(verticies, normals):
    '''
    Take all verticies and normals from the STL file and lump them into directional faces.
    '''
    # Get faces
    faces = FaceCollection()
    perp_tolerance = 0.001
    for r in range(0,len(verticies)):
        v1 = np.array(verticies[r][0]) - np.array(verticies[r][1])
        v2 = np.array(verticies[r][2]) - np.array(verticies[r][1])
        n = np.array(normals[r])
        res1 = np.dot(v1, n)
        res2 = np.dot(v2, n)

        # Ensure that the vectors are perpendicular to the normal
        if (res1 > perp_tolerance or res2 > perp_tolerance):
            print("WARNING! NON PERPENDICULAR NORMAL VECTOR:")
            print(res1)
            print(res2)
            exit(1)
        
        f = Face(np.array(verticies[r][0]), np.array(verticies[r][1]), np.array(verticies[r][2]), n)
        faces.append(f)
    return faces

def print_stl_information(model):
    print("Model information:")
    print("\tName: %s" % model.name)
    print("\tClosed: %s" % model.is_closed())
    print("\tPolygon count: %d" % (len(model.vectors)))
    print("\tNormal count: %d" % len(model.normals))
    print("\tPoint count: %d" % len(model.points))


# Load model
model = mesh.Mesh.from_file('models/cube.stl')
# Print info
print_stl_information(model)

# Create vertex
vert = Vertex.from_array([99, 23, 18])
vert2 = Vertex.from_array([99, 23, 18])
vert3 = Vertex.from_array([98, 23, 19])
vert4 = Vertex.from_array([3, 11, 70])
vert5 = Vertex.from_array([20, 50, 80])
vert6 = Vertex.from_array([33, 44, 55])

vertex_col = VertexCollection()
vertex_col.add(vert)
vertex_col.add(vert)
vertex_col.add(vert2)
vertex_col.add(vert3)
vertex_col.add(vert4)
vertex_col.add(vert5)
vertex_col.add(vert6)
print(vertex_col.x_vals)
print(vertex_col.y_vals)
print(vertex_col.z_vals)

print(len(vertex_col))
for cord in vertex_col:
    print(cord)


# Set faces
faces = collect_faces(model.vectors, model.normals)
print("%d warnings detected" % faces.get_warning_count())

# Create new empty plot
fig = plt.figure()
axes = mplot3d.Axes3D(fig)

# Add vectors from models to plot
good_collection = mplot3d.art3d.Poly3DCollection(faces.get_verticies(vtype="good"))
good_collection.set_edgecolor('black') # Wireframe
good_collection.set_facecolor('green')
good_collection.set_alpha(0.2)

bad_collection = mplot3d.art3d.Poly3DCollection(faces.get_verticies(vtype="bad"))
bad_collection.set_edgecolor('black') # Wireframe
bad_collection.set_facecolor('red')
axes.add_collection3d(good_collection)
axes.add_collection3d(bad_collection)


# Scale automatically
scale = model.points.flatten('C')
axes.auto_scale_xyz(scale, scale, scale)

# Plot points
#axes.scatter3D(model.x,model.y,model.z,color='yellow', s=1) # plot verticies

# Display plot
plt.show()

model.get
