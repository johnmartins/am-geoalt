import sys
import argparse
from handle_stl import search_and_solve

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("input", help="Input file path. Needs to be a .stl-file.", type=str)
parser.add_argument("output", help="Output file path", type=str)
parser.add_argument("-i","--imax", type=int, help="Max amount of iterations.")
parser.add_argument("-ig","--ignore_ground", action="store_true", help="Treat faces touching the ground as unsupported.")
parser.add_argument("-cd","--convergence_depth", type=int, help="Tolerance of convergence. Higher is more accurate, but will also take more time.")
parser.add_argument("-a", "--angle", "--phi_min", type=float, help="Minimum overhang angle")
parser.add_argument("--plot", action="store_true", help="Plot the processed model")
args = parser.parse_args()

# Params
max_iterations = 2000
ignore_ground = False
convergence_depth = 5
phi_min = 3.1415/4
plot = False

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

search_and_solve(args.input, args.output, max_iterations=max_iterations, ignore_ground=ignore_ground, convergence_depth=convergence_depth, phi_min=phi_min, plot=plot)

def print_usage():
    print("Usage: ")
    print("geoalt.py -i <inputfile> -o <outputfile>")
