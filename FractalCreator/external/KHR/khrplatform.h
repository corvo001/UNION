#ifndef __khrplatform_h_
#define __khrplatform_h_

/* SPDX-License-Identifier: MIT
   Header mínimo compatible con GLAD (OpenGL 3.3) */

#if defined(_WIN32) && !defined(KHRONOS_STATIC)
#  define KHRONOS_APICALL __declspec(dllimport)
#else
#  define KHRONOS_APICALL
#endif

#define KHRONOS_APIENTRY
#define KHRONOS_APIATTRIBUTES

/* Tipos base */
#include <stddef.h>
#include <stdint.h>

typedef int8_t    khronos_int8_t;
typedef uint8_t   khronos_uint8_t;
typedef int16_t   khronos_int16_t;
typedef uint16_t  khronos_uint16_t;
typedef int32_t   khronos_int32_t;
typedef uint32_t  khronos_uint32_t;
typedef int64_t   khronos_int64_t;
typedef uint64_t  khronos_uint64_t;
typedef float     khronos_float_t;

/* Tipos necesarios para GLAD / OpenGL */
#include <stddef.h>   /* size_t, ptrdiff_t */
#include <stdint.h>   /* intptr_t, uintptr_t */

typedef intptr_t      khronos_intptr_t;
typedef uintptr_t     khronos_uintptr_t;
typedef ptrdiff_t     khronos_ssize_t;
typedef size_t        khronos_usize_t;

typedef khronos_uint32_t khronos_boolean_enum_t;
#ifndef KHRONOS_FALSE
# define KHRONOS_FALSE 0
#endif
#ifndef KHRONOS_TRUE
# define KHRONOS_TRUE 1
#endif

#endif /* __khrplatform_h_ */
