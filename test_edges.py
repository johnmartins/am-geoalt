from vertices import Vertex
from edges import Edge, EdgeCollection

v1 = Vertex.from_array([0,0,0])
v2 = Vertex.from_array([0,0,1])
v3 = Vertex.from_array([0,1,0])

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