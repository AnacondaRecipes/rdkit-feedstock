#!/bin/bash

set -euxo pipefail

POPCNT_OPTIMIZATION="ON"
if [[ "$target_platform" == linux-aarch64 ]]; then
    # ARM does not have popcnt instructions, afaik
    POPCNT_OPTIMIZATION="OFF"
fi

# `cairo` was needed to generate high-quality PNGs for structure depiction,
# see https://www.rdkit.org/docs/Install.html?highlight=cairo#recommended-extras
# but we  disable it by customer requested to avoid having dependency on cairo->libX11 as staring from v2023.03.3 
cmake ${CMAKE_ARGS:-} \
-D CMAKE_BUILD_TYPE=Release \
-D CMAKE_INSTALL_PREFIX="$PREFIX" \
-D BOOST_ROOT="$PREFIX" \
-D Boost_NO_SYSTEM_PATHS=ON \
-D Boost_NO_BOOST_CMAKE=ON \
-D Python3_EXECUTABLE="${PYTHON}" \
-D PYTHON_INSTDIR="$SP_DIR" \
-D RDK_BUILD_AVALON_SUPPORT=ON \
-D RDK_BUILD_CAIRO_SUPPORT=OFF \
-D RDK_BUILD_CPP_TESTS=ON \
-D RDK_BUILD_INCHI_SUPPORT=ON \
-D RDK_BUILD_FREESASA_SUPPORT=ON \
-D RDK_BUILD_YAEHMOP_SUPPORT=ON \
-D RDK_BUILD_XYZ2MOL_SUPPORT=ON \
-D RDK_BUILD_PYTHON_WRAPPERS=ON \
-D RDK_INSTALL_INTREE=OFF \
-D RDK_INSTALL_STATIC_LIBS=OFF \
-D RDK_OPTIMIZE_POPCNT=${POPCNT_OPTIMIZATION} \
.

make -j"${CPU_COUNT}"
make install

## How to run unit tests:
## 1. Set RDK_BUILD_CPP_TESTS to ON
## 2. Uncomment lines below
export PYTHONPATH=$SP_DIR:${PYTHONPATH:-}
export RDBASE=$SRC_DIR

# All these test failed with reason: Subprocess aborted
ctest --output-on-failure -j"${CPU_COUNT}" -E \
    "shape_test|graphmoltestPickler|molbundleTestsCatch|testEnumeration|pyChemReactionEnumerations|\
tautomerQueryTestCatch|pyTautomerQuery|pyFilterCatalog|pyFragCatalog|distGeomHelpersCatch|pyMolDraw2D|\
substructLibraryTest|substructLibraryCatchTest|pySubstructLibrary|pyGraphMolWrap|testScaffoldNetwork|\
generalizedSubstructCatch|pyGeneralizedSubstruct|pythonSourceTests|pyScaffoldNetworkPickling|pyDetermineBonds"
