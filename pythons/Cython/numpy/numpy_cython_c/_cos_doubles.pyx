""" Example of wrapping a C function that takes C double arrays as input using
    the Numpy declarations from Cython """
# import both numpy and the Cython declarations for numpy
import numpy as np
cimport numpy as np

# if you want to use the Numpy-C-API from Cython
# (not strictly necessary for this example)
np.import_array()

# cdefine the signature of our c function
cdef extern from "cos_doubles.h":
    void cos_doubles (double * in_array, double * out_array, int size)
    void cos_doubles_matrix(double * in_array, double * out_array, int dim1, int dim2)

# create the wrapper code, with numpy type annotations
def cos_doubles_func(np.ndarray[double, ndim=1, mode="c"] in_array not None,
                     np.ndarray[double, ndim=1, mode="c"] out_array not None):
    cos_doubles(<double*> np.PyArray_DATA(in_array),
                <double*> np.PyArray_DATA(out_array),
                in_array.shape[0])


def cos_doubles_matrix_func(np.ndarray[double, ndim=2, mode="c"] in_array not None,
                     np.ndarray[double, ndim=2, mode="c"] out_array not None):
    # print(np.PyArray_DATA(in_array))
    print(in_array.shape[0], in_array.shape[1])

    cos_doubles_matrix(<double*> np.PyArray_DATA(in_array),
                       <double*> np.PyArray_DATA(out_array),
                       in_array.shape[0], in_array.shape[1])