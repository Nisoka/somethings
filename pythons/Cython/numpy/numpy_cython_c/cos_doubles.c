#include "cos_doubles.h"
#include <math.h>
#include <stdlib.h>

/*  Compute the cosine of each element in in_array, storing the result in
 *  out_array. */
void cos_doubles(double * in_array, double * out_array, int size){
    int i;
    for(i=0;i<size;i++){
        out_array[i] = cos(in_array[i]);
        if(i > size - 10)
            printf("%f %f\n", in_array[i], out_array[i]);
    }
}


void cos_doubles_matrix(double* in_array, double* out_array, int dim1, int dim2){
    
    printf("shape is %d, %d", dim1, dim2);

    for(int i = 0; i < dim1; i ++){
        for (int j = 0; j< dim2; j++){
            out_array[i*dim2+j] = cos(in_array[i*dim2 +j]);
            printf("%f %f\n", in_array[i*dim2+j], out_array[i*dim2+j]);
        }
    }
}