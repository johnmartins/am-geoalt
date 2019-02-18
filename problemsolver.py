from faces import *

def single_face_algorithm(face, atype="additive"):
    if atype="additive":
        vertex1 = face.vert

    else:
        raise TypeError("Non-supported algorithm type.")