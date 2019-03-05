from stl_creator import *
from faces import *
facecol = FaceCollection()
stlmaker = STLCreator("./here.txt",facecol)
stlmaker.build_file()