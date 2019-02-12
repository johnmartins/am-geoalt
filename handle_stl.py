from stl import mesh
import stl
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt
import time

class Face:
    def __init__(self, v1, v2, n):
        self.v1 = v1
        self.v2 = v2
        self.n = n

# Load model
model = mesh.Mesh.from_file('models/u_shape_45.stl')

# Create new empty plot
fig = plt.figure()
axes = mplot3d.Axes3D(fig)

# Add vectors from models to plot
axes.add_collection3d(mplot3d.art3d.Poly3DCollection(model.vectors))

# Scale automatically
scale = model.points.flatten(-1)
axes.auto_scale_xyz(scale, scale, scale)

# Print info
print(" ")
print("Model information:")
print("\tClosed: %s" % model.is_closed())
print("\tPolygon count: %d" % (len(model.vectors)))
print("\tNormal count: %d" % len(model.normals))
print("\tPoint count: %d" % len(model.points))

# Plot points
axes.scatter3D(model.x,model.y,model.z,color='red')

# Plot wireframe (does not show all edges)
for i in range(0,len(model.vectors)):
    axes.plot_wireframe(np.array(model.x[i]), np.array(model.y[i]), np.array([model.z[i], model.z[i]]), color="black")

# Get faces
faces = []
for r in range(0,12):
    v1 = np.array(model.vectors[r][0]) - np.array(model.vectors[r][1])
    v2 = np.array(model.vectors[r][2]) - np.array(model.vectors[r][1])
    n = model.normals[r]
    res1 = np.dot(v1, n)
    res2 = np.dot(v2, n)

    # Ensure that the vectors are perpendicular to the normal
    if (res1 != 0 or res2 != 0):
        exit(1)
    
    f = Face(v1, v2, n)
    faces.append(f)

# Display plot
plt.show()

model.get
