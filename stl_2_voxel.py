from mesh_vox import read_and_reshape_stl, voxelize
from stl import mesh
import stl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

# Convert to binary (TODO: if ascii)
model = mesh.Mesh.from_file('models/u_shape_arc.stl')
model.get_mass_properties
model.save('parse_this.stl', mode=stl.Mode.BINARY)

input_path = 'parse_this.stl'

resolution = 20
model_mesh, bounding_box = read_and_reshape_stl(input_path, resolution)
vxls, bounding_box = voxelize(model_mesh, bounding_box)

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_aspect('equal')

ax.voxels(vxls, edgecolor="k")
plt.show()

