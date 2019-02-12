from stl import mesh
import stl
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import numpy.linalg as linalg
import matplotlib.pyplot as plt
import time

class Face:
    def __init__(self, v1, v2, n):
        self.v1 = v1
        self.v2 = v2
        self.n = n
        self.n_hat = n / linalg.norm(n)
        self.has_bad_angle = self.__check_for_problems__()
    
    def __check_for_problems__(self):
        v1 = self.n_hat
        v2 = [0,0,-1]
        angle =  np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0))
        if angle >= 0 and angle < np.pi/4:
            return True
        return False


def collect_faces(verticies, normals):
    '''
    Take all verticies and normals from the STL file and lump them into directional faces.
    '''
    # Get faces
    faces = []
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
        
        f = Face(v1, v2, n)
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
model = mesh.Mesh.from_file('models/u_shape_45.stl')
# Print info
print_stl_information(model)
# Set faces
faces = collect_faces(model.vectors, model.normals)
warning_count = 0
for face in faces:
    if face.has_bad_angle is True:
        warning_count += 1
print("%d warnings detected" % warning_count)

# Create new empty plot
fig = plt.figure()
axes = mplot3d.Axes3D(fig)

# Add vectors from models to plot
axes.add_collection3d(mplot3d.art3d.Poly3DCollection(model.vectors))

# Scale automatically
scale = model.points.flatten(-1)
axes.auto_scale_xyz(scale, scale, scale)

# Plot points
axes.scatter3D(model.x,model.y,model.z,color='red')

# Plot wireframe (does not show all edges)
for i in range(0,len(model.vectors)):
    axes.plot_wireframe(np.array(model.x[i]), np.array(model.y[i]), np.array([model.z[i], model.z[i]]), color="black")

# Display plot
plt.show()

model.get
