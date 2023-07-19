#!/bin/bash

set -euxo pipefail

echo "Building ${PKG_NAME}."


# Isolate the build.
mkdir -p Build-${PKG_NAME}
cd Build-${PKG_NAME} || exit 1

POPCNT_OPTIMIZATION="ON"
if [[ "$target_platform" == linux-ppc64le || "$target_platform" == linux-aarch64 ]]; then
    # PowerPC includes -mcpu=power8 optimizations already
    # ARM does not have popcnt instructions, afaik
    POPCNT_OPTIMIZATION="OFF"
fi

# Numpy cannot be found in ppc64le for some reason... some extra help will do ;)
EXTRA_CMAKE_FLAGS=""
if [[ "$target_platform" == linux-ppc64le ]]; then
    EXTRA_CMAKE_FLAGS+=" -D PYTHON_NUMPY_INCLUDE_PATH=${SP_DIR}/numpy/core/include"
fi

# Generate the build files.
echo "Generating the build files..."

cmake .. ${CMAKE_ARGS} \
-GNinja \
-D CMAKE_PREFIX_PATH=${PREFIX} \
-D CMAKE_INSTALL_PREFIX=${PREFIX} \
-D CMAKE_BUILD_TYPE=Release \
-D BOOST_ROOT="$PREFIX" \
-D Boost_NO_SYSTEM_PATHS=ON \
-D Boost_NO_BOOST_CMAKE=ON \
-D PYTHON_EXECUTABLE="$PYTHON" \
-D PYTHON_INSTDIR="$SP_DIR" \
-D RDK_BUILD_AVALON_SUPPORT=ON \
-D RDK_BUILD_CAIRO_SUPPORT=ON \
-D RDK_BUILD_CPP_TESTS=OFF \
-D RDK_BUILD_INCHI_SUPPORT=ON \
-D RDK_BUILD_FREESASA_SUPPORT=ON \
-D RDK_BUILD_YAEHMOP_SUPPORT=ON \
-D RDK_BUILD_XYZ2MOL_SUPPORT=ON \
-D RDK_BUILD_PYTHON_WRAPPERS=ON \
-D RDK_INSTALL_INTREE=OFF \
-D RDK_INSTALL_STATIC_LIBS=OFF \
-D RDK_OPTIMIZE_POPCNT=${POPCNT_OPTIMIZATION} \
${EXTRA_CMAKE_FLAGS}


# Build.
echo "Building..."
ninja -j${CPU_COUNT} || exit 1

## How to run unit tests:
## 1. Set RDK_BUILD_CPP_TESTS to ON
## 2. Uncomment lines below
# export RDBASE="$SRC_DIR"
# ctest --output-on-failure

# Installing
echo "Installing..."
ninja install || exit 1


# Error free exit!
echo "Error free exit!"
exit 0
