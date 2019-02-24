from timeit import default_timer as timer
import time

import matplotlib.pyplot as plt
import numpy as np
import stl
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D
from stl import mesh
import queue

from faces import Face, FaceCollection
from verticies import Vertex, VertexCollection
from problemsolver import *

def collect_faces(verticies, normals):
    '''
    Take all verticies and normals from the STL file and lump them into directional faces.
    '''
    # Get faces
    faces = FaceCollection()
    perp_tolerance = 0.001
    for r in range(0,len(verticies)):
        # Use verticies to calculate vectors. The vectors are then used to verify the normal vector.
        v1 = np.array(verticies[r][0]) - np.array(verticies[r][1])
        v2 = np.array(verticies[r][2]) - np.array(verticies[r][1])
        n = np.array(normals[r])
        res1 = np.dot(v1, n)
        res2 = np.dot(v2, n)

        # Ensure that the vectors are perpendicular to the normal
        if (res1 > perp_tolerance or res2 > perp_tolerance):
            raise ValueError("Non perpendicular normal vector encountered in STL file.")
        
        # Create new face, and append
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

def plot_model(face_collection):
    # Create new empty plot
    fig = plt.figure()
    axes = mplot3d.Axes3D(fig)
    axes.set_xlabel("X axis")
    axes.set_ylabel("Y axis")
    axes.set_zlabel("Z axis")

    # Add vectors from models to plot
    good_collection = mplot3d.art3d.Poly3DCollection(face_collection.get_verticies(vtype="good"))
    good_collection.set_edgecolor('black') # Wireframe
    good_collection.set_facecolor('green')

    bad_collection = mplot3d.art3d.Poly3DCollection(face_collection.get_verticies(vtype="bad"))
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

# Some settings
ignore_ground = True    # Setting this to False results in rendering issues when using matplotlib 3d plotting.
ground_tolerance = 0.01

# Parameters
ground_level=0

# Start stopwatch
time_start = timer()

# Load model
model = mesh.Mesh.from_file('models/cylinder.stl')

# Extract lowest Z to use as ground level (if ignore_ground is set to False).
if ignore_ground is False:
    Z=[]
    for polygon in model.vectors:
        for vector in polygon:
            Z.append(vector[2])
    ground_level = min(Z)
    print("Ground level identified as Z = %d" % ground_level)

# Print info
print_stl_information(model)

# Set faces
faces = collect_faces(model.vectors, model.normals)
faces.check_for_problems(ignore_grounded=ignore_ground, ground_level=ground_level, ground_tolerance=ground_tolerance)
print("%d warnings detected" % faces.get_warning_count())
print("%d unique verticies found" % len(faces.get_vertex_collection()))

# Stop first stopwatch
time_problem_detection = timer()

# Edit geometry
iterations=5

for i in range(0, iterations):
    pq = queue.PriorityQueue()
    for face in faces:
        if face.has_bad_angle is True:
            pq.put(face)

    if pq.empty():
        print("No more problems encountered")
        break

    while not pq.empty():
        face = pq.get()
        single_face_algorithm(face)

    faces.check_for_problems(ignore_grounded=ignore_ground, ground_level=ground_level, ground_tolerance=ground_tolerance)

# Stop first stopwatch
time_error_correction = timer()

print("\nPerformance:")
print("Processed problem detection in %d seconds" % (time_problem_detection-time_start) )
print("Processed %d iterations of error correction in %d seconds" % (iterations, time_error_correction-time_problem_detection))

plot_model(faces)
