cmake_minimum_required(VERSION 3.16)
project(UNION)

# Configuración del estándar C++
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Configuración para Windows
if(WIN32)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -static-libgcc -static-libstdc++")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static")
endif()

# Buscar SFML
find_package(SFML 2.5 COMPONENTS system window graphics audio REQUIRED)

# Crear el ejecutable
add_executable(UNION 
    main.cpp
)

# Enlazar librerías
target_link_libraries(UNION 
    sfml-graphics 
    sfml-window 
    sfml-system
)

# Para Windows, enlazar librerías adicionales
if(WIN32)
    target_link_libraries(UNION 
        shell32
        user32
        gdi32
        winmm
        ole32
        oleaut32
        imm32
        version
    )
endif()

# Configurar icono y propiedades del ejecutable (opcional)
if(WIN32)
    set_target_properties(UNION PROPERTIES
        WIN32_EXECUTABLE TRUE
        LINK_FLAGS "/SUBSYSTEM:WINDOWS"
    )
endif()

# Copiar recursos necesarios
configure_file(${CMAKE_SOURCE_DIR}/README.md ${CMAKE_BINARY_DIR}/README.md COPYONLY)