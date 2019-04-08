from vertices import Vertex
from edges import Edge, EdgeCollection
from faces import Face, FaceCollection
import numpy as np

v1 = Vertex.from_array([0,0,0])
v2 = Vertex.from_array([1,0,0])
v3 = Vertex.from_array([0,1,0])
v4 = Vertex.from_array([0,-1,0])
n = np.array([0,0,1])

e1 = Edge(v1, v2)
e2 = Edge(v2, v3)
e3 = Edge(v3, v1)
e2_rev = Edge(v3, v2)

ec = EdgeCollection()
ec.add(e1)
print("Edge collection after 1 unique add: %d" % len(ec))
ec.add(e2)
print("Edge collection after 2 unique adds: %d" % len(ec))
ec.add(e3)
print("Edge collection after 3 unique adds: %d" % len(ec))
ec.add(e3)
print("Edge collection after 3 unique adds and 1 non unique: %d" % len(ec))
ec.add(e2_rev)
print("Edge collection after 3 unique adds and 2 non unique: %d" % len(ec))

f1 = Face(v1.get_array(),v2.get_array(),v3.get_array(), n)
f2 = Face(v1.get_array(), v2.get_array(), v4.get_array(), n)

e1.associate_with_face(f1)
print(e1.faces)
e1.associate_with_face(f1)
print(e1.faces)
e1.associate_with_face(f2)
print(e1.faces)
e1.associate_with_face(f2)
print(e1.faces)