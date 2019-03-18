from vertices import *

vc = VertexCollection()
vertex1 = Vertex.from_array([1,2,3])
print("Vertex1 hash = %d" % vertex1.__hash__())
vertex2 = Vertex.from_array([2,1,3])
print("Vertex2 hash = %d" % vertex2.__hash__())

print("Vertex1 equals vertex2: %s" % vertex1.__eq__(vertex2))

vc.add(vertex1)
vc.add(vertex2)

print("Items in collection: %d" % len(vc))

for vertex in vc:
    print(vertex)

# Ensure that the same object is indeed returned
res = vc.contains(Vertex.from_array([2,1,3]))
if res is not None:
    res.x = 53
    print("vertex2 vs res: %s, %s" % (vertex2, res))

print(res)