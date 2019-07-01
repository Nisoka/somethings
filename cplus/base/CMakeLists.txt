project(speech-tools)
include_directories(${CMAKE_SOURCE_DIR})

include_directories(
  ${CMAKE_SOURCE_DIR}
  )

aux_source_directory(. DIR_SRCS)

# ADD_DEFINITIONS(-fpermissive)
add_executable(lambda 
    lambda.cc
    )
add_executable(variadic_template 
    variadic_template.cc
    )


# add link lib
# target_link_libraries(lambda -lm kaldi-base kaldi-matrix kaldi-util kaldi-feat)
target_link_libraries(lambda)
target_link_libraries(variadic_template)
