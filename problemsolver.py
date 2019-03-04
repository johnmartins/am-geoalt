from faces import *
import numpy as np
import math

def single_face_algorithm(face, atype="additive", phi_min=np.pi/4):
    if (isinstance(face, Face) is False):
            raise TypeError('face argument needs to be of type Face().')
    if (isinstance(atype, str) is False):
            raise TypeError('atype argument needs to be a string.')

    if atype=="additive":
        # For additive algorithm type, find lowest point(s) push them in the xy-direction (away from normal) until the angle is ok.
        # Starts from the highest face and works its way down.
        # Gather all verticies, and fetch all z-coordinates
        vertex_matrix = np.array([face.vertex1.get_array(), face.vertex2.get_array(), face.vertex3.get_array()])
        vertex_list = [face.vertex1, face.vertex2, face.vertex3]
        z_cords = vertex_matrix[:,2]

        # Check if plane is parallel to Z-plane.
        if z_cords[0] == z_cords[1] and z_cords[1] == z_cords[2]:
            # Come up with solution to this. Shrink towards middle, perhaps?
            return
        
        # We only want to move the bottom two verticies, so we sort them. The vertex highest from the ground will be used as an "anchor", while the other two will be pushed
        index_lowest_first = np.argsort(z_cords)

        # Notice that the n_hat (normal vector) is NOT updated in between the edits, as doing so would cause the second edit to move in the wrong direction.
        eliminate_angle(vertex_list[index_lowest_first[2]], vertex_list[index_lowest_first[0]], face.n_hat_original, phi_min=phi_min)
        eliminate_angle(vertex_list[index_lowest_first[2]], vertex_list[index_lowest_first[1]], face.n_hat_original, phi_min=phi_min)

        # After editing the vertexes the face normal vector needs to be updated.
        face.refresh_normal_vector()

    else:
        raise TypeError("Non-supported algorithm type.")

def eliminate_angle(anchor_vertex, roaming_vertex, n_hat, phi_min=np.pi/4):
    delta_z = anchor_vertex.z - roaming_vertex.z
    # Make sure that the anchor is above the roaming vertex in the Z-axis
    if (delta_z <= 0 or delta_z < 0.01):
        return

    # tan(phi)
    tan_phi = math.tan(phi_min)
    # Calculate how far in the xy plane the roaming vertex SHOULD be from the anchor point in order to satisfy this face
    t_xy = delta_z/tan_phi
    # Extract the XY coordinates of the normal vector of this face
    n_xy = np.array([n_hat[0], n_hat[1], 0])
    # Get the unit vector of the XY compartment of the normal vector of this face
    n_xy_hat = n_xy / np.linalg.norm(n_xy)
    # Create a vector from the anchor point to the roaming point
    vector = roaming_vertex.get_array() - anchor_vertex.get_array()
    # Get the distance in the XY-plane between the anchor point and the roaming point
    vector_xy = np.dot(vector, n_xy_hat) 
    # Get the absolute value of that distance
    vector_xy_abs = np.linalg.norm(vector_xy)

    # Calculate the difference between how far the distance between the roaming vertex and the anchor vertex is and how long it should be.
    abs_diff = vector_xy_abs - t_xy
    # Add diff to close the gap.
    roaming_vertex.add_change_partial(n_xy_hat*abs_diff)