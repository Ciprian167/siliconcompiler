#!/bin/sh

set -ex

# Get directory of script
src_path=$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P)/..

USE_SUDO_INSTALL="${USE_SUDO_INSTALL:-yes}"
if [ "${USE_SUDO_INSTALL:-yes}" = "yes" ]; then
    SUDO_INSTALL=sudo
else
    SUDO_INSTALL=""
fi

mkdir -p deps
cd deps

if [ -z ${PREFIX} ]; then
    PREFIX=~/.local
fi

sudo dnf config-manager --set-enabled devel || true
# Install core dependencies.
sudo yum install -y gcc gcc-c++ gcc-gfortran blas blas-devel \
    cmake lapack lapack-devel bison flex fftw-devel fftw \
    suitesparse suitesparse-devel autoconf automake libtool \
    git openmpi-devel openmpi
sudo dnf config-manager --set-disabled devel || true

sudo yum install -y wget

# Download Trilinos.
## Version specified in: https://github.com/Xyce/Xyce/blob/master/INSTALL.md#building-trilinos
trilinos_version=14-4-0
wget https://github.com/trilinos/Trilinos/archive/refs/tags/trilinos-release-${trilinos_version}.tar.gz --no-verbose -O trilinos.tar.gz
mkdir -p trilinos
tar --strip-components=1 -xf trilinos.tar.gz -C trilinos

# Download Xyce.
git clone $(python3 ${src_path}/_tools.py --tool xyce --field git-url) xyce
cd xyce
git checkout $(python3 ${src_path}/_tools.py --tool xyce --field git-commit)

# Build Trilinos
mkdir trilinos-build
cd trilinos-build
cmake \
    -D CMAKE_INSTALL_PREFIX="$PREFIX/trilinos" \
    -D AMD_LIBRARY_DIRS="/usr/lib" \
    -D TPL_AMD_INCLUDE_DIRS="/usr/include/suitesparse" \
    -D CMAKE_C_COMPILER=/usr/lib64/openmpi/bin/mpicc \
    -D CMAKE_CXX_COMPILER=/usr/lib64/openmpi/bin/mpicxx \
    -D CMAKE_Fortran_COMPILER=/usr/lib64/openmpi/bin/mpifort \
    -C ../cmake/trilinos/trilinos-MPI-base.cmake \
    ../../trilinos
cmake --build . -j$(nproc)
$SUDO_INSTALL make install
cd ..

# Build Xyce
mkdir xyce-build
cd xyce-build

cmake \
    -D CMAKE_INSTALL_PREFIX="$PREFIX" \
    -D Trilinos_ROOT=$PREFIX/trilinos \
    -D BUILD_SHARED_LIBS=ON \
    -D CMAKE_C_COMPILER=/usr/lib64/openmpi/bin/mpicc \
    -D CMAKE_CXX_COMPILER=/usr/lib64/openmpi/bin/mpicxx \
    -D CMAKE_Fortran_COMPILER=/usr/lib64/openmpi/bin/mpifort \
    ..
cmake --build . -j$(nproc)
cmake --build . -j$(nproc) --target xycecinterface
$SUDO_INSTALL make install
cd -
