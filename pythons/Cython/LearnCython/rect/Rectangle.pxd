cdef extern from "Rectangle.cc":
    pass

# Decalre the class with cdef
cdef extern from "Rectangle.h" namespace "shapes":

    cdef cppclass Rectangle:
        Rectangle() except +
        Rectangle(int, int, int, int) except +
        int getArea()
        void getSize(int* width, int* height)
        void move(int, int)
        void setEV(int)
        int getEV()