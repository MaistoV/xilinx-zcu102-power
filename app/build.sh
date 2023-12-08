#
# Copyright 2019 Xilinx Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1
CXX=${CXX:-g++}
# $CXX --version 

result=0 && pkg-config --list-all | grep opencv4 > /dev/null && result=1 
if [ $result -eq 1 ]; then
	OPENCV_FLAGS=$(pkg-config --cflags --libs-only-L opencv4)
else
	OPENCV_FLAGS=$(pkg-config --cflags --libs-only-L opencv)
fi

DEFAULT_LIBS="-lvart-runner \
     ${OPENCV_FLAGS} \
     -lopencv_videoio  \
     -lopencv_imgcodecs \
     -lopencv_highgui \
     -lopencv_imgproc \
     -lopencv_core \
     -lglog \
     -lxir \
     -lunilog \
     -lpthread"
ADDITIONAL_LIBS="-lvart-dpu-controller"
     # -lvart-dpu-runner \
     # -lvart-softmax-runner \
     # -lvitis_ai_library-math \
LIBS="$DEFAULT_LIBS $ADDITIONAL_LIBS"

# common folder comes from https://github.com/Xilinx/Vitis-AI/tree/2.0/demo/VART/common
FLAGS="-pg -fno-inline -I. \
     -I=/usr/include/opencv4 \
     -I=/usr/include/glog \
     -I=/install/Debug/include \
     -I=/install/Release/include \
     -L=/install/Debug/lib \
     -L=/install/Release/lib \
     -I/usr/include/vitis \
     -I$PWD/utils \
     -I$PWD/common -std=c++17 \
     $PWD/src/main.cc \
     $PWD/common/common.cpp  \
     $PWD/utils/utils.cpp  \
     -Wl,-rpath=$PWD/lib \
     $LIBS"

name_O0=$(basename $PWD)_O0
name_O2=$(basename $PWD)_O2

# $CXX -O2 -o $name_O2 $FLAGS

mv $name_O0 "$name".old 2> /dev/null
# Remove D_FORTIFY_SOURCE because it requires optimizations
CXX=$(echo $CXX | sed 's/D_FORTIFY_SOURCE=2/D_FORTIFY_SOURCE=0/g')
$CXX -O0 -o $name_O0 $FLAGS 


if test -f "$name_O0"; then
     aarch64-xilinx-linux-objdump -d -m aarch64 $name_O0 > $name_O0.dis
     echo "Done:" $(ls $name_O0) "is available"
     # echo "Scping to board..."
     # bash scp_to_board.sh $name_O0
else 
     echo "No $name_O0 exists, something went wrong"
     exit 1
fi