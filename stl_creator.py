from faces import FaceCollection, Face

class STLCreator:
    '''
    Class for creating STL files out of a FaceCollection
    '''
    def __init__(self, file_destination, face_collection):
        # Ensure that all arguments are of the correct type
        if isinstance(file_destination, str) is False:
            raise TypeError("Filename needs to be a String.")
        
        if isinstance(face_collection, FaceCollection) is False:
            raise TypeError("Face collection needs to be a FaceCollection.")
        
        self.file_destination = file_destination
        self.face_collection = face_collection
        self.stream = None
    
    def build_file(self):
        '''
        Build the STL file
        '''
        if self.stream is not None:
            raise IOError("File stream was already opened")

        self.__create_file__()
        self.__parse_face_collection__()
        self.__close_file__()
    
    def __create_file__(self):
        try:
            self.stream = open(file=self.file_destination, mode="x", encoding="utf-8", newline=None)
            self.stream.write("solid GeoAlt\n")
        except FileExistsError:
            print("File aready exists.")

    def __close_file__(self):
        self.stream.write("endsolid GeoAlt\n")
        self.stream.close()
        self.stream = None
    
    def __parse_face_collection__(self):
        for face in self.face_collection:
            face.refresh_normal_vector()
            self.stream.write("\tfacet normal %f %f %f\n" % (face.n[0], face.n[1], face.n[2]))            
            self.stream.write("\t\touter loop\n")
            self.stream.write("\t\t\tvertex %f %f %f\n" % (face.vertex1.x, face.vertex1.y, face.vertex1.z))
            self.stream.write("\t\t\tvertex %f %f %f\n" % (face.vertex2.x, face.vertex2.y, face.vertex2.z))
            self.stream.write("\t\t\tvertex %f %f %f\n" % (face.vertex3.x, face.vertex3.y, face.vertex3.z))
            self.stream.write("\t\tendloop\n")
            self.stream.write("\tendfacet\n")
    