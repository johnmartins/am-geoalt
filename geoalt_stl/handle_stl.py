from timeit import default_timer as timer
import time

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D
import ntpath
import os

from geoalt_geometry.faces import FaceCollection

from problemsolver import single_face_algorithm
import geoalt_exceptions as geoexc
from zero_phi_strategy import ZeroPhiStrategy

from geoalt_stl.stl_creator import STLCreator
from geoalt_stl.stl_parser import STLfile


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

def display_best_orientations(res, wei):
    print("Optimal orientation:\t Xrot = %.2f,\t Yrot = %.2f,\t Weight = %.2f. Grounded: %s" % (res[wei[0],0]*180/np.pi, res[wei[0],1]*180/np.pi, res[wei[0],2], 'yes' if res[wei[0],3] == 1 else 'no'))
    for i in range(1,10):
        if len(res) > i:
            print("Alternative %d:\t Xrot = %.2f,\t Yrot = %.2f,\t Weight = %.2f, Grounded: %s" % (i+1,res[wei[i],0]*180/np.pi, res[wei[i],1]*180/np.pi, res[wei[i],2], 'yes' if res[wei[i],3] == 1 else 'no'))
        else:
            break

def orientation_optimization(stl, facecol, ignore_grounded, ground_level, ground_tolerance, phi_min, angle_tolerance, grounded_only):
    '''
    This method is used to rotate the model into different orientations .
    This is done to aid in finding the orientation most suitable for printing
    '''
    print("Performing orientation optimization..")
    # Find optimal orientation
    iterations_per_axis = 37
    optimization_results = np.zeros([iterations_per_axis**2,4])

    for i in range(0, iterations_per_axis):
        degx = np.pi/180*5*i
        
        # Rotate around X Axis
        stl.rotate(degx, axis='x')
        angular_step_size = np.pi/180*5
        degy = 0

        for j in range(0, iterations_per_axis):

            # Rotate around y axis
            stl.rotate(degy, axis='y')
            ground_level = stl.ground_level
            facecol.check_for_problems(ignore_grounded=ignore_grounded, ground_level=ground_level, ground_tolerance=ground_tolerance, phi_min=phi_min, angle_tolerance=angle_tolerance)
            optimization_results[(i*iterations_per_axis)+j] = [degx, angular_step_size*j, facecol.total_weight, int(stl.grounded)]
            degy = angular_step_size
        
        # Reset y
        stl.rotate(-1*angular_step_size*(iterations_per_axis-1), axis='y')

        # Reset rotation
        stl.rotate(-degx, axis='x')

        percentage_done = ((i+1)/iterations_per_axis) * 100
        print("%.2f%%" % percentage_done, end='\r', flush=True)

    print("Done!", flush=True, end="\r")

    if grounded_only is True:
        count = np.count_nonzero(optimization_results[:,3])
        grounded_results = np.zeros([count,4])
        j = 0
        for i in range(0, len(optimization_results)):
            if optimization_results[i,3] == 1:
                grounded_results[j,:] = optimization_results[i,:]
                j += 1
        optimization_results = grounded_results
                
    weights = optimization_results[:,2]
    weights_ordered_indices = np.argsort(weights)
    display_best_orientations(optimization_results, weights_ordered_indices)

    stl.rotate(optimization_results[weights_ordered_indices[0],0], axis='x')
    stl.rotate(optimization_results[weights_ordered_indices[0],1], axis='y')

def search_and_solve(model_path, altered_model_path, 
    phi_min = np.pi/4,          # Smallest allowed angle of overhang
    ignore_ground = False,      # Setting this to False results in rendering issues when using matplotlib 3d plotting.
    convergence_break = True,   # Stops the problem solving algorithm loop after the amount of warnings hasn't changed for n iterations.
    convergence_depth = 5,      # How many iterations that needs to be the same before it counts as convergence.
    ground_tolerance = 0.01,    # How close a vertex needs to be to the ground in order to be considered to be touching it.
    angle_tolerance = 0.017,    # How close an angle needs to be to phi_min in order to be considered to be acceptable.
    max_iterations = 2000,      # The maximum amount of iterations before the problem correction algorithm stops.
    plot = True,                # Plot using matplotlib after the process is finished
    overwrite_output = False,   # Overwrite target output file if it already exists
    zero_phi_strategy = ZeroPhiStrategy.NONE,   # Strategy for dealing with flat overhangs
    fixed_orientation = None,   # Pre-specified orientation
    ignore_rot_opt = False,
    grounded_only = False):    # Skip orientation optimization (rotation optimization) step

    # Check if model exists
    check_paths(model_path, altered_model_path, overwrite_output)

    time_start = timer()
    # Load the model into memory
    print("Loading the model..")
    stl = STLfile(model_path)
    faces = stl.load()

    # Extract lowest Z to use as ground level (if ignore_ground is set to False).
    ground_level=stl.ground_level
    print_stl_information(stl)

    # Check for leaks
    for e in faces.edge_collection:
        if len(e.faces) != 2:
            print("POTENTIAL LEAK DETECTED! Bad Edge hash function, or leaking model")

    time_model_loaded = timer()

    # Optimize the model for the best possible orientation
    if fixed_orientation is not None:
        ignore_rot_opt = True

    if ignore_rot_opt is False:
        orientation_optimization(stl, faces, 
            ignore_grounded=ignore_ground, 
            ground_level=ground_level, 
            ground_tolerance=ground_tolerance, 
            phi_min=phi_min, 
            angle_tolerance=angle_tolerance,
            grounded_only=grounded_only)
        ground_level = stl.ground_level
    elif fixed_orientation is not None:
        stl.rotate(fixed_orientation[0], axis='x')
        stl.rotate(fixed_orientation[1], axis='y')
        ground_level = stl.ground_level

    time_orientation = timer()

    # Do initial problem check
    faces.check_for_problems(ignore_grounded=ignore_ground, ground_level=ground_level, ground_tolerance=ground_tolerance, phi_min=phi_min, angle_tolerance=angle_tolerance)
    print("%d overhang surfaces detected" % faces.get_warning_count())

    time_problem_detection = timer()

    print("\nProblem correction process initiated. phi_min = %f \nMax iterations: %d. \nConvergence detection activated: %s. Convergence depth: %d" % (phi_min, max_iterations, convergence_break, convergence_depth))
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
    print("Parsed through the STL file in %.2f seconds" % (time_model_loaded-time_start))
    print("Model orientation (optimizatin) completed in %.2f seconds" % (time_orientation-time_model_loaded))
    print("Processed problem detection in %.2f seconds" % (time_problem_detection-time_orientation))
    print("Processed %d iterations of problem correction in %.2f seconds" % (iterations, time_problem_correction-time_problem_detection))
    print("Created a new STL file in %.2f seconds" % (time_stl_creation-time_problem_correction))

    print("\nDone!")
        
    if plot is True:
        plot_model(faces)