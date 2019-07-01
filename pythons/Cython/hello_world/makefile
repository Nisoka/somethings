
#filename: Makefile
all: hello_world cython_hello_world

CXXFLAGS += -I/usr/include/python3.6 `python3.6-config --cflags --ldflags` -fPIC
GADD = gcc
hello_world:
	$(GADD) $(CXXFLAGS) hello_world.c -c hello_world.c
	$(GADD) hello_world.o -o hello_world 

cython:
	cython -3 cython_hello_world.pyx

cython_hello_world: cython
	$(GADD)  $(CXXFLAGS) cython_hello_world.c -c
	$(GADD)  $(CXXFLAGS) -shared -o cython_hello_world.so hello_world.o cython_hello_world.o

clean:
	rm -rf hello_world hello_world.o cython_hello_world.so cython_hello_world.c cython_hello_world.o
