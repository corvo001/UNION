file(GLOB_RECURSE SOURCES "*.cpp" "*.h")

add_executable(FractalExplorer ${SOURCES})

target_link_libraries(FractalExplorer ${OPENGL_LIBRARIES})

target_include_directories(FractalExplorer PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Compilar solo con OpenGL por ahora
target_compile_definitions(FractalExplorer PRIVATE SIMPLE_VERSION)