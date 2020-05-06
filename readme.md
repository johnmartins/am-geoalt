# Installation
To install all necessary modules, run `pip install -r requirements.txt`.

To use the GUI you need wxPython. The installation of wxPython on windows is no different than the usual (`pip install -U wxPython`), but for linux you might have to do some research. 

# Using the GUI
To start the GUI run `python3 gui.py`. The wxPython module is required for the GUI to run properly.

The GUI is by default setup for orientation optimization. 

To run the geometry alteration algorithm, set max iterations > 0 (eg. 1000). Then choose if you want to use orientation optimization or not (note that orientation optimization is very time consuming). To disable orientation optimization uncheck the checkbox "analyze optimal orientation".

You may provide an initial orientation of your model by selecting the angles (in degrees) manually using the X rotation and Y rotation controls.

If the algorithm doesn't do anything then you may want to consider fiddling with the tolerances, though this is otherwise generally a bad idea.

# Using the command interface
To use the command line interface use `python3 geoalt.py`. This is the help documentation:

```
usage: geoalt.py [-h] [-i IMAX] [-ig] [-cd CONVERGENCE_DEPTH] [-a ANGLE] [--plot] [--angle_tolerance ANGLE_TOLERANCE] [--ground_tolerance GROUND_TOLERANCE] [--no_convergence] [-ow]
                 [-zps ZERO_PHI_STRATEGY] [-or ORIENTATION [ORIENTATION ...]]
                 input output

positional arguments:
  input                 Input file path. Needs to be a .stl-file.
  output                Output file path.

optional arguments:
  -h, --help            show this help message and exit
  -i IMAX, --imax IMAX  Max amount of iterations.
  -ig, --ignore_ground  Treat faces touching the ground as unsupported.
  -cd CONVERGENCE_DEPTH, --convergence_depth CONVERGENCE_DEPTH
                        Tolerance of convergence. Higher is more accurate, but will also take more time.
  -a ANGLE, --angle ANGLE, --phi_min ANGLE
                        Minimum overhang angle.
  --plot                Plot the processed model.
  --angle_tolerance ANGLE_TOLERANCE
                        Required proximity to phi_min.
  --ground_tolerance GROUND_TOLERANCE
                        Required proximity to ground to be considered as touching it.
  --no_convergence      If used then the algorithm will not stop if nothing changes. Not recommended.
  -ow, --overwrite      If used then the output file will be overwritten if it already exists.
  -zps ZERO_PHI_STRATEGY, --zero_phi_strategy ZERO_PHI_STRATEGY
                        Zero Phi Strategy: How to deal with zero phi overhangs. Default is to ignore (None).
  -or ORIENTATION [ORIENTATION ...], --orientation ORIENTATION [ORIENTATION ...]
                        Provide a fixed orientation in which to print the model. Defaults to zero rotation.
   ```
