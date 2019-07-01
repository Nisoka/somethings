# cython是 Python 与 C/C++ 的中间沟通语言
# cython 是Python C/C++ 的合集的修改
# cython 通过引用C++的头文件,获得函数的声明
# 后期再链接 C++ 的obj文件, 找到对应的函数实现.

# eg:
#   cython -3 cy_file.pyx
#   out:
#      cy_file.c(现在还不会处理为.cc)

# 1 cython 可以利用python的易用性, 来写代码, 然后cython直接将其转化为C代码
# 2 cython 可以封装C/C++ 的源码, 编译成so 可以作为python模块调用.

# 1 封装C/C++ 动态链接库so, 形成一个模块, 扩展python
# 	这是通过修改 cy_file.pyx文件, 
#   cython 向其中 添加 #include "Python.h", 
#   使用Python API 修改cy_file.pyx 为调用了 Python API 的 C 源文件
#   这样的 cy_file.c 就编译 链接 后的 .so 
#   这样得到的 动态链接库.so 就是正常的so库, 同时也可以用作python的扩展模块

# 2 将Python 处理为C/C++语言
#   cython 是 python的超集, 所以cython 中可以写任何python, 调用python库


# 3 使用
#   1 file.h file.cc, cy_file.pyx
#     file.cc 中包含正常的C/C++ 代码
#     file.h 包含函数声明
#     cy_file.pyx 包含C 函数引用, python代码, 直接转化为标准C 代码.
#     
#   2 
#   使用 cy_file.pyx 引用 file.cc 中的实现函数
#   cdef extern from "file.h":
#       void plus(double *a, double *b, double *r, int n, int m)
#   使用 python 封装函数
#   def cython_plus(np.ndarray[double, ndim=2, mode="c"] a not None,
#                  np.ndarray[double, ndim=2, mode="c"] b not None, 
#                  np.ndarray[double, ndim=2, mode="c"] r not None,
#                  times not None):
# 			plus(<double*> np.PyArray_DATA(a),
#             	 <double*> np.PyArray_DATA(b),
#             	 <double*> np.PyArray_DATA(r),
#                a.shape[0],
#                a.shape[1],
#                <int> times)
#  3 编译
#    PYTHON3FLAGS = `python3.6-config --cflags --libs --ldflags`
#    1 g++ file.cc -c -o file.o 
#      仅编译(-c) file.cc (目的是编译导出函数 plus 的实现)
#      这里仅仅进行编译, 不做链接,不生成程序或者库

#    2 cython -3 cy_file.pyx  (cy_file.c)
#      转化 cython 代码为 C 代码(会包含很多python API 扩展时用的函数 --- PyInit, PyModul ..... )

#    3 g++ $(PYTHON3FLAGS) cy_file.c -fPIC -c -o cy_file.o
#      必须 带上 Python.h 进行编译, 不然无头文件
#      !!! 这个cy_file.c 就是正常的 C源码, 可以直接使用了. 但是使用时 需要链接必备的库 --- PYTHON3FLAGS

#    4 g++ --shared -o cy_file.so $(PYTHON3FLAGS) cy_file.o file.o
#      链接 cy_file.o file.o 为 cy_file.so
#      注意,这里 $(PYTHON3FLAGS) 一定要放在 --shared -o cy_file.so 之后.

# 这里介绍的都是简单一个文件的
#    当使用多个文件时, 
#    1 g++ file.cc -c -o file.o
#      g++ file1.cc -c -o file1.o
#      g++ file2.cc -c -o file2.o
#      g++ file3.cc -c -o file3.o
#    2 cython -3 cy_file.pyx
#    3 g++ $(PYTHON3FLAGS) cy_file.c -fPIC -c -o cy_file.o
#      ar -cr cy_file.a cy_file.o file.o file1.o file2.o file3.o
#      ranlib cy_file.a
#      打包所有需要的C源码到 静态链接库 .a 文件中
#      ar 
#        -c 创建库
#        -r 插入文件
#      ranlib 更新库
#    4 g++ --shared -o cy_file.so -Wl,-soname=cy_file.so,--whole-archive cy_file.a $(PYTHON3FLAGS)
#    或者
#    4 g++ --shared -fPIC -o cy_file.so cy_file.o file.o file1.o file2.o file3.o $(PYTHON3FLAGS)

#   注意!!!
#   0 编译不需要查找引用函数的定义, 只编译自己就好了.
#   1 cython -3 cy_file.pyx 生成的 C程序 
#     1 带有Python.h 
#     2 使用Python API C++ 扩展python模块的必要方法
#   2 编译 file.o 等文件 不能链接 必须使用-c 
#   3 编译 cy_file.c 必须使用 g++ $(PYTHON3FLAGS) cy_file.c -fPIC -c -o cy_file.o
#     1 $(PYTHON3FLAGS)
#     2 -fPIC ???
#   4 链接 $(PYTHON3FLAGS) 必须放到 --shared -o cy_file.so 之后.


# 应该模拟 kaldi-master/src/feat 的编译步骤.
# 1 既然向利用kaldi扩展python, 那么必须了解kaldi本身的编译方法,
#   要扩展的file.c文件的编译方法
# 2 你的cy_file.c 只需要使用相同的编译参数+ $(PYTHON3FLAGS) 就可以实现.

# 1 compile
# g++ -std=c++11 -I.. -isystem 
# 	/home/nan/git-nan/code/kaldi-master/tools/openfst/include 
# 	-O1 -Wno-sign-compare -Wall -Wno-sign-compare -Wno-unused-local-typedefs 
# 	-Wno-deprecated-declarations -Winit-self -DKALDI_DOUBLEPRECISION=0 
# 	-DHAVE_EXECINFO_H=1 -DHAVE_CXXABI_H -DHAVE_ATLAS 
# 	-I/home/nan/git-nan/code/kaldi-master/tools/ATLAS_headers/include 
# 	-msse -msse2 -pthread -g  -fPIC 
# 	-DHAVE_CUDA -I/usr/local/cuda/include   -c -o feat-to-dim.o feat-to-dim.cc

# 2 generate the a
# ar -cr kaldi-feat.a feature-functions.o feature-mfcc.o feature-plp.o feature-fbank.o feature-spectrogram.o mel-computations.o wave-reader.o pitch-functions.o resample.o online-feature.o signal.o feature-window.o
# ranlib kaldi-feat.a

# 3 generate the so
# g++ -shared -o libkaldi-feat.so 
# -Wl,--no-undefined  
# -Wl,--as-needed  
# -Wl,-soname=libkaldi-feat.so,--whole-archive kaldi-feat.a 
# -Wl,--no-whole-archive  
# -Wl,-rpath=/home/nan/git-nan/code/kaldi-master/tools/openfst/lib 
# -Wl,-rpath,/usr/lib/x86_64-linux-gnu -rdynamic 
# -Wl,-rpath=/home/nan/git-nan/code/kaldi-master/src/lib  
# ../transform/libkaldi-transform.so  ../gmm/libkaldi-gmm.so  ../tree/libkaldi-tree.so  ../util/libkaldi-util.so  ../matrix/libkaldi-matrix.so  ../base/libkaldi-base.so 
# /home/nan/git-nan/code/kaldi-master/tools/openfst/lib/libfst.so 
# /usr/lib/x86_64-linux-gnu/liblapack.so 
# /usr/lib/x86_64-linux-gnu/libcblas.so 
# /usr/lib/x86_64-linux-gnu/libatlas.so 
# /usr/lib/x86_64-linux-gnu/libf77blas.so 
# -lm -lpthread -ldl

# 4 generate the .run  noneed!!
# g++  -Wl,-rpath=/home/nan/git-nan/code/kaldi-master/tools/openfst/lib 
#      -Wl,-rpath,/usr/lib/x86_64-linux-gnu -rdynamic 
#      -Wl,-rpath=/home/nan/git-nan/code/kaldi-master/src/lib  
#      feat-to-dim.o   
#      ../hmm/libkaldi-hmm.so  ../feat/libkaldi-feat.so  ../transform/libkaldi-transform.so  ../gmm/libkaldi-gmm.so  ../tree/libkaldi-tree.so  ../util/libkaldi-util.so  ../matrix/libkaldi-matrix.so  ../base/libkaldi-base.so 
#      /home/nan/git-nan/code/kaldi-master/tools/openfst/lib/libfst.so 
#      /usr/lib/x86_64-linux-gnu/liblapack.so /usr/lib/x86_64-linux-gnu/libcblas.so 
#      /usr/lib/x86_64-linux-gnu/libatlas.so /usr/lib/x86_64-linux-gnu/libf77blas.so 
#      -lm -lpthread -ldl -o feat-to-dim



# ===============================manual simulate==========================================================
# Makefile 
#  1 前面指定目标, 最前面的目标就是终极目标 
#  2 只要实现终极目标即可
#  3 makefile 会先将所有 include 的 mk文件都 读取进来, 完成依赖关系
#  4 变量可以随意位置定义, 但是定义在后面的会覆盖前面的.
#    eg 
#      TESTVAR = TEST
#      prepare:
#      	 echo $(TESTVAR)
#      TESTVAR = TESTTEST
#    目标prepare 会打印出 TESTTEST。
#    因为 makefile 会先将所有内容读取进来，然后如果是重复定义变量，后面的会覆盖前面的
#  5 最后根据以来关系，才开始执行命令.
#  6 如果想要追加命令， 在后面 增加 all: target 的方式 可以执行 target的命令,
#    all: target1
#    all: target2
#    all: target3
#    这样会顺序的实现 target1 target2 target3 等
all: prepare_cython_cc

# 
prepare_cython_cc:
	cython -3 cy_feat_dim.pyx -o cy_feat_dim.cc

# must specify, otherwise cy_feat_dim.o can't use the parallel target prepare_cython_cc.
cy_feat_dim.o: cy_feat_dim.cc

EXTRA_LDFLAGS = `python3.6-config --cflags --libs --ldflags`
EXTRA_CXXFLAGS = `python3.6-config --cflags --libs --ldflags`

include ../kaldi.mk
OBJFILES = cy_feat_dim.o feat_dim.o

LIBNAME = cy_feat_dim

ADDLIBS = ../hmm/kaldi-hmm.a ../feat/kaldi-feat.a \
		../transform/kaldi-transform.a ../gmm/kaldi-gmm.a \
		../tree/kaldi-tree.a ../util/kaldi-util.a ../matrix/kaldi-matrix.a \
		../base/kaldi-base.a 

include ../makefiles/default_rules.mk

# must use all: over, because the all is the final target, 
all: over
over:
	rm ../lib/libcy_feat_dim.so
	mv libcy_feat_dim.so cy_feat_dim.so


# ===============================manual simulate==========================================================
all: feat_dim cy_feat_dim

include ../kaldi.mk

PYTHON3FLAGS = `python3.6-config --cflags --libs --ldflags`

LDFALGS = -Wl,-rpath=/home/nan/git-nan/code/kaldi-master/tools/openfst/lib \
			-Wl,-rpath,/usr/lib/x86_64-linux-gnu -rdynamic \
			-Wl,-rpath=/home/nan/git-nan/code/kaldi-master/src/lib  

ADDLIBSO = ../hmm/libkaldi-hmm.so ../feat/libkaldi-feat.so \
          ../transform/libkaldi-transform.so ../gmm/libkaldi-gmm.so \
          ../tree/libkaldi-tree.so ../util/libkaldi-util.so ../matrix/libkaldi-matrix.so \
          ../base/libkaldi-base.so

TOOLSSO = /home/nan/git-nan/code/kaldi-master/tools/openfst/lib/libfst.so \
			/usr/lib/x86_64-linux-gnu/liblapack.so \
			/usr/lib/x86_64-linux-gnu/libcblas.so \
			/usr/lib/x86_64-linux-gnu/libatlas.so \
			/usr/lib/x86_64-linux-gnu/libf77blas.so 

LDSOFLAGS = -Wl,--no-undefined -Wl,--as-needed -Wl,--no-whole-archive $(LDFALGS)
LDRUNFLAGS = $(LDFALGS)

LDFLAGS2 = -lm -lpthread -ldl

TARGETA = cy_feat_dim.a
TARGETSO= cy_feat_dim.so
COMPILEC = g++
feat_dim:
	$(COMPILEC) $(CXXFLAGS) feat_dim.cc -c -o feat_dim.o

cython:
	cython3 -3 cy_feat_dim.pyx

cy_feat_dim: cython
	$(COMPILEC) $(CXXFLAGS) $(PYTHON3FLAGS) cy_feat_dim.c -fPIC -c -o cy_feat_dim.o
	ar -cr $(TARGETA) cy_feat_dim.o feat_dim.o
	ranlib $(TARGETA)

	$(COMPILEC) -shared -o $(TARGETSO) -Wl,-soname=$(TARGETSO),--whole-archive $(TARGETA) $(LDSOFLAGS) $(TOOLSSO) $(ADDLIBSO) $(PYTHON3FLAGS) $(LDFLAGS2)

clean:
	rm -rf feat_dim feat_dim.o cy_feat_dim.so cy_feat_dim.cc cy_feat_dim.o
