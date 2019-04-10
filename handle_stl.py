from timeit import default_timer as timer
import time

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D
import ntpath
import os

from faces import Face, FaceCollection
from problemsolver import single_face_algorithm
from stl_creator import STLCreator
import geoalt_exceptions as geoexc
from zero_phi_strategy import ZeroPhiStrategy
from stl_parser import STLfile

def print_stl_information(stl):
    print("Model information:")
    print("\tName: %s" % stl.header.replace('\n',''))
    print("\tNormal count: %d" % len(stl.normals))
    print("\tPoint count: %d" % len(stl.vertices))
    print("\tGround level: %d" % stl.ground_level)

def plot_model(face_collection):
    # Create new empty plot
    fig = plt.figure()
    axes = mplot3d.Axes3D(fig)
    axes.set_xlabel("X axis")
    axes.set_ylabel("Y axis")
    axes.set_zlabel("Z axis")

    # Add vectors from models to plot
    good_collection = mplot3d.art3d.Poly3DCollection(face_collection.get_vertices(vtype="good"))
    good_collection.set_edgecolor('black') # Wireframe
    good_collection.set_facecolor('green')

    bad_collection = mplot3d.art3d.Poly3DCollection(face_collection.get_vertices(vtype="bad"))
    bad_collection.set_edgecolor('black') # Wireframe
    bad_collection.set_facecolor('red')
    axes.add_collection3d(good_collection)
    axes.add_collection3d(bad_collection)

    # Plot points
    #axes.scatter3D(model.x,model.y,model.z,color='yellow', s=1) # plot vertices

    # Display plot
    plt.show()

def check_paths(model_path, target_path, overwrite):
    model_exists = os.path.exists(model_path)
    target_exists = os.path.exists(target_path)

    if (model_exists is False):
        raise geoexc.InputFileNotFound("Selected model does not exist")

    if (target_exists is True):
        if overwrite is False:
            raise geoexc.OutputFileExists("Target path for altered model already exists. Please change it.")
        elif overwrite is True:
            print("Overwriting output file..")
            os.remove(target_path)
        else:
            raise geoexc.InvalidInputArgument("Invalid overwrite argument")

def orientation_optimization(stl, facecol, ignore_grounded, ground_level, ground_tolerance, phi_min, angle_tolerance):
    # Find optimal orientation
    iterations_per_axis = 37
    optimization_results = np.zeros([iterations_per_axis,3])

    for i in range(0, iterations_per_axis):
        degy = np.pi/180*5*i
        degx = 0
        stl.rotate(degy, axis='y')
        ground_level = stl.ground_level
        facecol.check_for_problems(ignore_grounded=ignore_grounded, ground_level=ground_level, ground_tolerance=ground_tolerance, phi_min=phi_min, angle_tolerance=angle_tolerance)
        print("%.2f Angle: %.2f\t Total weight: %.2f\t GL: %.2f" % (degy,i*5,facecol.total_weight, ground_level))
        optimization_results[i] = [degy, degx, facecol.total_weight]
        stl.rotate(-degy, axis='y')
    
    print(optimization_results)


def search_and_solve(model_path, altered_model_path, 
    phi_min = np.pi/4,          # Smallest allowed angle of overhang
    ignore_ground = False,      # Setting this to False results in rendering issues when using matplotlib 3d plotting.
    convergence_break = True,    # Stops the problem solving algorithm loop after the amount of warnings hasn't changed for n iterations.
    convergence_depth = 5,      # How many iterations that needs to be the same before it counts as convergence.
    ground_tolerance = 0.01,    # How close a vertex needs to be to the ground in order to be considered to be touching it.
    angle_tolerance = 0.017,    # How close an angle needs to be to phi_min in order to be considered to be acceptable.
    max_iterations = 2000,
    plot = True,
    overwrite_output = False,
    zero_phi_strategy = ZeroPhiStrategy.NONE):       # The maximum amount of iterations before the problem correction algorithm stops.

    # Check if model exists
    check_paths(model_path, altered_model_path, overwrite_output)

    # Start stopwatch
    time_start = timer()

    # Load model
    print("Loading the model..")
    stl = STLfile(model_path)

    # Print info
    #print_stl_information(model)
    time_model_info = timer()

    faces = stl.load()

    # Extract lowest Z to use as ground level (if ignore_ground is set to False).
    ground_level=stl.ground_level
    print_stl_information(stl)

    # Check for leaks
    for e in faces.edge_collection:
        if len(e.faces) != 2:
            print("POTENTIAL LEAK DETECTED! Bad Edge hash function, or leaking model")

    time_face_collection = timer()

    orientation_optimization(stl, faces, ignore_grounded=ignore_ground, ground_level=ground_level, ground_tolerance=ground_tolerance, phi_min=phi_min, angle_tolerance=angle_tolerance)

    # Do initial problem check
    faces.check_for_problems(ignore_grounded=ignore_ground, ground_level=ground_level, ground_tolerance=ground_tolerance, phi_min=phi_min, angle_tolerance=angle_tolerance)
    print("%d overhang surfaces detected" % faces.get_warning_count())
    time_problem_detection = timer()

    print("\nProblem correction process initiated. phi_min = %f \t Max iterations: %d. Convergence detection activated: %s. Convergence depth: %d" % (phi_min, max_iterations, convergence_break, convergence_depth))
    iterations = 0
    previous_warning_count = []
    for i in range(0, max_iterations):
        iterations = i + 1

        # Display progression
        print("Iteration (%d/%d):\t Approximate warnings detected: %d" % (i+1, max_iterations, faces.get_warning_count()))
        
        # Break if there are no more warnings
        if faces.get_warning_count() == 0:
            print("No more problems encountered")
            break

        # Go through each problematic face and run the SFA
        for face in faces.problem_faces:
            if face.has_bad_angle is True:
                single_face_algorithm(face, atype="additive", phi_min=phi_min, zero_phi_strategy=zero_phi_strategy)

        # For each vertex, apply the changes proposed by the SFA
        for vertex in faces.get_vertex_collection():
            net_vector = vertex.perform_change()

        # Re-run the problem detection algorithm
        faces.check_for_problems(ignore_grounded=ignore_ground, ground_level=ground_level, ground_tolerance=ground_tolerance, phi_min=phi_min, angle_tolerance=angle_tolerance)

        # Check if the amount of warnings has converged towards a value. If so, then break.
        if convergence_break is True:
            previous_warning_count.append(faces.get_warning_count())
            final_elements = previous_warning_count[len(previous_warning_count)-convergence_depth:] 
            if max(final_elements) == min(final_elements) and len(previous_warning_count) > convergence_depth:
                print("Warning count convergence detected. Breaking.")
                break

    # Stop first stopwatch
    time_problem_correction = timer()

    # Save changes to a new STL file
    print("Saving changes to a new STL-file..")
    stl_creator = STLCreator(altered_model_path, faces)
    stl_creator.build_file()
    time_stl_creation = timer()

    print("\nPerformance:")
    print("Loaded model information in %.2f seconds" % (time_model_info-time_start))
    print("Gathered necessary vertex and face data in %.2f seconds" % (time_face_collection-time_model_info))
    print("Processed problem detection in %.2f seconds" % (time_problem_detection-time_face_collection))
    print("Processed %d iterations of problem correction in %.2f seconds" % (iterations, time_problem_correction-time_problem_detection))
    print("Created a new STL file in %.2f seconds" % (time_stl_creation-time_problem_correction))

    print("\nDone!")
        
    if plot is True:
        plot_model(faces)