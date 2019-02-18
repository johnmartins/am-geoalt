from faces import *
import numpy as np

def single_face_algorithm(face, atype="additive"):
    if (isinstance(face, Face) is False):
            raise TypeError('face argument needs to be of type Face().')
    if (isinstance(atype, str) is False):
            raise TypeError('atype argument needs to be a string.')

    if atype=="additive":
        print("Solving a problem with additive strategy:")
        # For additive algorithm type, find lowest point(s) push them in the xy-direction (away from normal) until the angle is ok.
        # Starts from the highest face and works its way down.
        vertex_matrix = np.array([face.vertex1.get_array(), face.vertex2.get_array(), face.vertex3.get_array()])
        vertex_list = [face.vertex1, face.vertex2, face.vertex3]
        z_cords = vertex_matrix[:,2]

        # Check if plane is parallel to Z-plane.
        if z_cords[0] == z_cords[1] and z_cords[1] == z_cords[2]:
            # Come up with solution to this. Shrink towards middle, perhaps?
            return
        
        # Calculate ratios of movement based on height. 
        # Lowest point should not move at all. 
        # Higher points should move further the higher up they are
        # Movements should be towards the XY-gradient
        index_lowest_first = np.argsort(z_cords)

        eliminate_angle(vertex_list[index_lowest_first[2]], vertex_list[index_lowest_first[0]], face.n_hat)
        eliminate_angle(vertex_list[index_lowest_first[2]], vertex_list[index_lowest_first[1]], face.n_hat)


    else:
        raise TypeError("Non-supported algorithm type.")

def eliminate_angle(anchor_vertex, roaming_vertex, n_hat, phi_min=np.pi/4):
    print("balls")

    neg_z_hat = [0,0,-1]

    n_xy = np.array([n_hat[0], n_hat[1], 0])
    vector = roaming_vertex.get_array() - anchor_vertex.get_array()
    angle = np.arccos(np.clip(np.dot(neg_z_hat, vector), -1.0, 1.0))
    print(angle*180/3.14)

    k = 0
    while (angle >= 0 and angle < phi_min):
        roaming_vertex.set_array(roaming_vertex.get_array() + n_xy*0.02)
        vector = roaming_vertex.get_array() - anchor_vertex.get_array()
        angle = np.arccos(np.clip(np.dot(neg_z_hat, vector), -1.0, 1.0))
        #print("angle = %d. vertex: %s" % ((angle*180/3.14), roaming_vertex.get_array()))
        k += 1
        if k == 300:
            return
        print("DONE!")