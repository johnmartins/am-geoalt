import sys
import argparse
from handle_stl import search_and_solve
import geoalt_exceptions as geoexc
from zero_phi_strategy import ZeroPhiStrategy

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("input", help="Input file path. Needs to be a .stl-file.", type=str)
parser.add_argument("output", help="Output file path.", type=str)
parser.add_argument("-i","--imax", type=int, help="Max amount of iterations.")
parser.add_argument("-ig","--ignore_ground", action="store_true", help="Treat faces touching the ground as unsupported.")
parser.add_argument("-cd","--convergence_depth", type=int, help="Tolerance of convergence. Higher is more accurate, but will also take more time.")
parser.add_argument("-a", "--angle", "--phi_min", type=float, help="Minimum overhang angle.")
parser.add_argument("--plot", action="store_true", help="Plot the processed model.")
parser.add_argument("--angle_tolerance", type=float, help="Required proximity to phi_min.")
parser.add_argument("--ground_tolerance", type=float, help="Required proximity to ground to be considered as touching it.")
parser.add_argument("--no_convergence", action="store_true", help="If used then the algorithm will not stop if nothing changes. Not recommended.")
parser.add_argument("-ow","--overwrite", action="store_true", help="If used then the output file will be overwritten if it already exists.")
parser.add_argument("-zps","--zero_phi_strategy", help="Zero Phi Strategy: How to deal with zero phi overhangs. Default is to ignore (None).")
parser.add_argument("-or", "--orientation", type=float, nargs="+", help="Provide a fixed orientation in which to print the model. Defaults to zero rotation.")
args = parser.parse_args()

# Default parameter values
max_iterations = 0       # Should be high enough to handle most reasonably complex models
ignore_ground = False       # Treat lowest known occupied Z-coordinate as ground
phi_min = 3.1415/4          # The minimum allowed overhang angle
plot = False                # Plot the model using matplotlib when the process is done
ground_tolerance = 0.01     # How close a vertex needs to be to the ground in order to be considered as touching it           
angle_tolerance = 0.017     # How close an angle needs to be to phi_min in order to be considered non-problematic (0.017 rad ~ 1 deg)
convergence_break = True    # If true, then the algorithm will stop once convergence has been reached (when warning count does not seem to change)
convergence_depth = 5       # Stop meta-algorithm after the amount of problems hasn't changed for this many iterations
overwrite = False
zero_phi_strategy = ZeroPhiStrategy.NONE
fixed_orientation = None

# Check which arguments were specified, and overwrite respective default paramter values
if args.imax:
    max_iterations = args.imax
if args.ignore_ground:
    ignore_ground = True
if args.convergence_depth:
    convergence_depth = args.convergence_depth
if args.angle:
    phi_min = args.angle
if args.plot:
    plot=True
if args.ground_tolerance:
    ground_tolerance = args.ground_tolerance
if args.angle_tolerance:
    angle_tolerance = args.angle_tolerance
if args.no_convergence:
    convergence_break = False
if args.overwrite:
    overwrite = True
if args.zero_phi_strategy:
    print("ZERO PHI STRAT: %s" % args.zero_phi_strategy.upper())
    if args.zero_phi_strategy.upper() == "NONE":
        zero_phi_strategy = ZeroPhiStrategy.NONE
    elif args.zero_phi_strategy.upper() == "INJECT":
        zero_phi_strategy = ZeroPhiStrategy.INJECT
    else:
        raise geoexc.InvalidInputArgument("No such zero phi strategy. Can only be none or inject.")
if args.orientation:
    if len(args.orientation) != 2:
        raise geoexc.InvalidInputArgument("--orientation requires two arguments. For example: --orientation 3.14 1.57.")
    else:
        fixed_orientation = args.orientation


# Run the algorithm
try:
    search_and_solve(args.input, args.output, 
    max_iterations=max_iterations, 
    ignore_ground=ignore_ground, 
    convergence_depth=convergence_depth, 
    phi_min=phi_min, 
    plot=plot,
    ground_tolerance=ground_tolerance,
    angle_tolerance=angle_tolerance,
    convergence_break=convergence_break,
    overwrite_output=overwrite,
    zero_phi_strategy=zero_phi_strategy,
    fixed_orientation=fixed_orientation)
except geoexc.InputFileNotFound:
    print("Input file could not be found (%s). Please control the path provided" % args.input)
except geoexc.OutputFileExists:
    print("Output path (%s) is already occupied by another file. Please change the provided path." % args.output)
