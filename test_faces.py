from faces import Face
import numpy as np

v1 = np.array([0,0,0])
v2 = np.array([1,0,0])
v3 = np.array([0,1,0])
n = np.array([0,0,1])

f1 = Face(v1,v2,v3,n)
f2 = Face(v2,v3,v1,n)

if f1.__eq__(f2):
    print("f1 equals f2, though the vertices are scrambled")

ar = [f1]

if f2 in ar:
    print("f2 is in array")
    