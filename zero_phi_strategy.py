from enum import Enum
import numpy as np
class ZeroPhiStrategy(Enum):
    NONE = None
    INJECT = "Inject"

def inject(face):
    '''
    This method is used to introduce an angle to an otherwise 0 angle plane
    '''    
    for edge in face.get_edges():
        for f in edge.faces:
            if (f is face):
                continue

            else:
                # Check if changes are already staged
                # This prevents a flat surface from being treated more than once.
                for vertex in face.get_vertices():
                    if len(vertex.change_set) != 0:
                        # Changes has already been staged for this face. Leave it alone this iteration.
                        return

                # Check if adjacent face has an angle, and that it is underneath this face.
                if f.angle > 0.017 and face.top_z >= f.top_z:
                    print("[DEBUG] Adding angle to flat overhang face..")

                    z_array = f.get_vertices_as_arrays()[:,2]
                    # Sort the indexes in order of highest to lowest z value
                    z_array_sorted_indexes = np.argsort(z_array)
                    # Set z diff to halfway to the bottom of the face
                    dz = (z_array[z_array_sorted_indexes[0]] - z_array[z_array_sorted_indexes[2]])/2

                    # Introduce angle.
                    edge.vertex1.add_change_partial(np.array([0,0,dz]))
                    edge.vertex2.add_change_partial(np.array([0,0,dz]))
                    return

