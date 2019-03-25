import os
from handle_stl import search_and_solve

input_file = "models/architecture.stl"
output_file = "fixed_models/test_arch.stl"

if os.path.exists(output_file):
    print("Removing output..")
    os.remove(output_file)

# Default parameter values
max_iterations = 2000       # Should be high enough to handle most reasonably complex models
ignore_ground = False       # Treat lowest known occupied Z-coordinate as ground
phi_min = 3.1415/4          # The minimum allowed overhang angle
plot = False                # Plot the model using matplotlib when the process is done
ground_tolerance = 0.01     # How close a vertex needs to be to the ground in order to be considered as touching it           
angle_tolerance = 0.017     # How close an angle needs to be to phi_min in order to be considered non-problematic (0.017 rad ~ 1 deg)
convergence_break = True    # If true, then the algorithm will stop once convergence has been reached (when warning count does not seem to change)
convergence_depth = 5       # Stop meta-algorithm after the amount of problems hasn't changed for this many iterations

# Run the algorithm
search_and_solve(input_file, output_file, 
max_iterations=max_iterations, 
ignore_ground=ignore_ground, 
convergence_depth=convergence_depth, 
phi_min=phi_min, 
plot=plot,
ground_tolerance=ground_tolerance,
angle_tolerance=angle_tolerance,
convergence_break=convergence_break)