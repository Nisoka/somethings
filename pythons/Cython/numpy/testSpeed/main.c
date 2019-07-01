#include "main.h"
 
/***********************************
* 矩阵的加法
* 利用数组是顺序存储的特性, *
* 通过降维来访问二维数组! *
* r
***********************************/
void plus(double *a, double *b, double *r, int n, int m)
{
    int i, j;
    for(i = 0; i < n; i++)
    {
        for(j = 0; j < m; j++)
            *(r + i*m + j) = *(a + i*m + j) + *(b + i*m + j);
    }
}
 
/***********************************
* 矩阵的按元素乘法
* 利用数组是顺序存储的特性, *
* 通过降维来访问二维数组! *
* r
***********************************/
void mul(double *a, double *b, double *r, int n, int m)
{
    int i, j;
    for(i = 0; i < n; i++)
    {
        for(j = 0; j < m; j++)
            *(r + i*m + j) = *(a + i*m + j) * *(b + i*m + j);
    }
}
 
/***********************************
* main函数
* 利用数组是顺序存储的特性, *
* 通过降维来访问二维数组! *
* r
***********************************/
void main(double *a, double *b, double *r, int n, int m, int times)
{
    int i;
    // 循环times次
#pragma omp parallel for
    for (i = 0; i < times; i++)
    {
        // 矩阵的加法
        plus(a, b, r, n, m);
        
        // 矩阵按元素相乘
        // mul(a, b, r, n, m);
    }
}
