cmake_minimum_required(VERSION 3.20)
project(FractalCreator LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# === Elegir layout de Complex: xy | reim | realim | funcrealim | std ===
#    - xy       : struct { float x, y; }        (por defecto)
#    - reim     : struct { float re, im; }
#    - realim   : struct { float real, imag; }
#    - funcrealim: métodos real() / imag()
#    - std      : std::complex<float>
set(FRACTAL_COMPLEX_LAYOUT "xy" CACHE STRING "xy|reim|realim|funcrealim|std")

# Salidas
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin/$<CONFIG>)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib/$<CONFIG>)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib/$<CONFIG>)

# Rutas
set(ROOT_DIR      ${CMAKE_SOURCE_DIR})
set(SRC_DIR       ${ROOT_DIR}/src)
set(EXTERNAL_DIR  ${ROOT_DIR}/external)

# -----------------------------
# GLAD
# -----------------------------
add_library(glad STATIC ${EXTERNAL_DIR}/glad/glad.c)
target_include_directories(glad PUBLIC ${EXTERNAL_DIR})
set_target_properties(glad PROPERTIES LINKER_LANGUAGE C)

# -----------------------------
# GLFW (precompilado)
# -----------------------------
set(GLFW_INCLUDE_DIR ${EXTERNAL_DIR}/glfw/include)
# Ajusta a tu carpeta real de libs (lib-vc2022, lib-static-ucrt, etc.)
set(GLFW_LIB_DIR ${EXTERNAL_DIR}/glfw/lib-static-ucrt CACHE PATH "GLFW lib dir")
find_library(GLFW_LIB NAMES glfw3 glfw3dll PATHS ${GLFW_LIB_DIR} NO_DEFAULT_PATH REQUIRED)

add_library(glfw3 IMPORTED STATIC GLOBAL)
set_target_properties(glfw3 PROPERTIES
    IMPORTED_LOCATION "${GLFW_LIB}"
    INTERFACE_INCLUDE_DIRECTORIES "${GLFW_INCLUDE_DIR}"
)

# -----------------------------
# Dear ImGui (rama docking)
# -----------------------------
file(GLOB IMGUI_SRC
    ${EXTERNAL_DIR}/imgui/imgui.cpp
    ${EXTERNAL_DIR}/imgui/imgui_demo.cpp
    ${EXTERNAL_DIR}/imgui/imgui_draw.cpp
    ${EXTERNAL_DIR}/imgui/imgui_tables.cpp
    ${EXTERNAL_DIR}/imgui/imgui_widgets.cpp
    ${EXTERNAL_DIR}/imgui/backends/imgui_impl_glfw.cpp
    ${EXTERNAL_DIR}/imgui/backends/imgui_impl_opengl3.cpp
)
add_library(imgui STATIC ${IMGUI_SRC})
target_include_directories(imgui PUBLIC
    ${EXTERNAL_DIR}/imgui
    ${EXTERNAL_DIR}/imgui/backends
    ${GLFW_INCLUDE_DIR}
)
target_compile_definitions(imgui PUBLIC
    IMGUI_IMPL_OPENGL_LOADER_GLAD
    IMGUI_ENABLE_VIEWPORTS
)

# -----------------------------
# Código de la app
# -----------------------------
file(GLOB_RECURSE SRC_FILES "${SRC_DIR}/*.cpp")
list(FILTER SRC_FILES EXCLUDE REGEX ".*/external/.*")
list(FILTER SRC_FILES EXCLUDE REGEX ".*/build/.*")
list(FILTER SRC_FILES EXCLUDE REGEX ".*/CMakeFiles/.*")

if (WIN32)
    add_executable(FractalCreator WIN32 ${SRC_FILES})
else()
    add_executable(FractalCreator ${SRC_FILES})
endif()

# Includes del ejecutable (AQUÍ, tras crear el target)
target_include_directories(FractalCreator PRIVATE
    ${SRC_DIR}
    ${EXTERNAL_DIR}
    ${EXTERNAL_DIR}/stb   # para stb_image_write.h
    ${GLFW_INCLUDE_DIR}
)

find_package(OpenGL REQUIRED)

target_link_libraries(FractalCreator PRIVATE
    glad
    imgui
    glfw3
    OpenGL::GL
)

if (WIN32 AND NOT TARGET OpenGL::GL)
    target_link_libraries(FractalCreator PRIVATE opengl32)
endif()

if (MSVC)
    target_compile_definitions(FractalCreator PRIVATE _CRT_SECURE_NO_WARNINGS NOMINMAX)
    target_compile_options(FractalCreator PRIVATE /permissive- /W3 /FC)
endif()

# === Definir macro según FRACTAL_COMPLEX_LAYOUT ===
string(TOLOWER "${FRACTAL_COMPLEX_LAYOUT}" _FC_LAYOUT)
if     (_FC_LAYOUT STREQUAL "std")
    target_compile_definitions(FractalCreator PRIVATE FC_COMPLEX_STD)
elseif (_FC_LAYOUT STREQUAL "reim")
    target_compile_definitions(FractalCreator PRIVATE FC_COMPLEX_REIM)
elseif (_FC_LAYOUT STREQUAL "realim")
    target_compile_definitions(FractalCreator PRIVATE FC_COMPLEX_REALIM)
elseif (_FC_LAYOUT STREQUAL "funcrealim")
    target_compile_definitions(FractalCreator PRIVATE FC_COMPLEX_FUNCREALIM)
else()
    # xy: no se define nada (usa c.x / c.y por defecto)
endif()
