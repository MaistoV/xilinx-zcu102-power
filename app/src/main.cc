/*
 * Copyright 2019 Xilinx Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <assert.h>
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>

#include <cassert>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <queue>
#include <string>
#include <vector>
// #include <chrono>

#include "common.h"
#include "utils.h"

#include <glog/logging.h> /* for InitGoogleLogging() */

/* header file OpenCV for image processing */
#include <opencv2/opencv.hpp>
#include "xir/xrt_device_handle.hpp"

using namespace std;

// /* Stop this function from being inlined */
// __attribute__ ((__noinline__))
// void flag_function_1(){
//   asm("");
// }
// /* Stop this function from being inlined */
// __attribute__ ((__noinline__))
// void flag_function_2(){
//   asm("nop");
// }

/* Array with static initialization, array size must be compile-time constant */
/* I know this is ugly, forgive me */
#define WAIT_FOR_THREADS(list) \
for (thread& t: list) { \
  /* only threads that are not destructed can be joined;  */ \
  if (t.joinable()) { \
    t.join(); \
  }   \
} \


int main(int argc, char *argv[]) {
  GraphInfo shapes;
  vector<string> labels, images_names;
  string baseImagePath = "./datasets/cifar100/";
  string labelsPath = "../datasets/images_imagenet/labels.txt";
  char out_dir[128] = ".";
  bool run_softmax = false;
  int max_images = 100;
  int num_threads = 1;
  if (argc < 2) {
    cout << "Set SHOW_IMAGES environment variable to show images_names on screen during classification\n";
    cout << "Set DEBUG_RUN environment variable to show debug info\n";
    cout << "Usage: " << argv[0] << " <model_file> " <<
            "\n[<image_path>=" << baseImagePath << "] " <<
            "\n[<label_list>="  << labelsPath   << "] " <<
            "\n[<run_softmax>=" << run_softmax  << "] " <<
            "\n[<max_images>="  << max_images   << "] " <<
            "\n[<num_threads>=" << num_threads  << "] " <<
            "\n[<out_dir>="     << out_dir      << "] " <<
            endl ;
    return -1;
  }
  if (argc >= 3) {
    baseImagePath = argv[2];
  }
  if (argc >= 4) {
    labelsPath = argv[3];
  }
  if (argc >= 5) {
    run_softmax = ( atoi(argv[4]) == 0 ) ? false : true;
  }
  if (argc >= 6) {
    max_images = atoi(argv[5]);
  }
  if (argc >= 7) {
    num_threads = atoi(argv[6]);
  }
  if (argc >= 8) {
    strcpy(out_dir,argv[7]);
  }

  /* debug_run */
  bool debug_run = (getenv("DEBUG_RUN") != nullptr);
  if ( debug_run ) {
    cout << "Running with arguments: "
        << argv[0] << "\n "
        "model_path\t= " << argv[1] << "\n "
        "baseImagePath\t= " << baseImagePath << "\n "
        "labelsPath\t= "    << labelsPath    << "\n "
        "run_softmax\t= "   << run_softmax   << "\n "
        "max_image\t= "     << max_images    << "\n "
        "num_threads\t= "   << num_threads   << "\n "
        "out_dir \t = "     << out_dir       << "\n "
        ;
  }

  /* Init google logging to remove stderr output */
  google::InitGoogleLogging(argv[0]);

  /* Read device info */
  int dpu_num = 0;
  int sfm_num = 0;
  read_dpu_info(&dpu_num, &sfm_num);

  /* Load all image names */
  ListImages(baseImagePath, images_names, max_images);
  size_t num_images = images_names.size();
  size_t num_images_per_thread = size_t(num_images / num_threads);
  if ( debug_run & ( num_images % num_threads != 0 ) ) {
    cerr << "\nERROR: num_threads is not an integer divider of num_images, reminder will be dropped. This requires a large number of images\n";
  }
  if ( num_images == 0 ) {
    cerr << "\nERROR: No images_names existing under " << baseImagePath << endl;
    return -1;
  }

  /* Load all labels labels */
  // LoadLabels(labelsPath, labels);
  // if ( labels.size() == 0 ) {
  //   cerr << "\nError: No labels exist in file labels.txt." << endl;
  //   return -1;
  // }

  /***************************************************************************/
  /* NOTE: can't wrap this code in a function due to dynamic types handling */
  /* Read xmodel */
  auto graph = xir::Graph::deserialize(argv[1]);
  auto dpu_subgraph = get_dpu_subgraph(graph.get());
  /* Create an array of runners from same subgraph */
  vector<std::unique_ptr<vart::Runner>> runner_list;
  for (int i = 0; i < num_threads; ++i) {
    runner_list.push_back(vart::Runner::create_runner(dpu_subgraph[0], "run"));
  }

  /* Prepare the memory layout of the intput and output tensors of the runner */
  auto inputTensors = runner_list[0]->get_input_tensors();
  auto outputTensors = runner_list[0]->get_output_tensors();
  /* Get in/out tensor shape */
  int inputCnt = inputTensors.size();
  int outputCnt = outputTensors.size();
  TensorShape inshapes[inputCnt];
  TensorShape outshapes[outputCnt];
  shapes.inTensorList = inshapes;
  shapes.outTensorList = outshapes;
  getTensorShape(runner_list[0].get(), &shapes, inputCnt, outputCnt);
  /***************************************************************************/
  /* Check size of label list agaist output tensor size */
  if ( labels.size() != shapes.outTensorList[0].size ) {
    cout << "WARNING: number of labels is different from the number of classes\n";
  }

  /* Define macro for thread arguments */
  #define runCNN_ARGS(index) num_threads, num_images_per_thread, \
                              runner_list[index].get(), shapes, \
                              baseImagePath, images_names, labels, sfm_num, run_softmax

  /* Flag for uprobes */
  // flag_function_1();
	struct timespec end_measure;
	struct timespec start_measure;
  FILE* fd;

  char filename [128] = "";
  strcpy(filename, out_dir);
  strcat(filename, "/");
  strcat(filename, getenv("XMODEL_BASENAME"));
  strcat(filename, ".csv.time");

  fd = fopen(filename, "w");
  if ( fd == NULL ) {
    fprintf(stderr, "Can't open %s\n", (char*)filename);
    return -1;
  }

  // Start timestamp
  clock_gettime(CLOCK_REALTIME, &start_measure);

// #define ARRAY_VECTORN
#ifdef ARRAY_VECTORN
  /* I know this is even uglier, but C/C++ preprocessor does not explicitly support loops (for good reasons) */
  switch ( num_threads ) {
  case 1: {
    array<thread, 1> threads_list = { thread(runCNN, 0, runCNN_ARGS(0)) };
    WAIT_FOR_THREADS(threads_list)
    break;
  }
  case 2: {
    array<thread, 2> threads_list = {
      thread(runCNN, 0, runCNN_ARGS(0)),
      thread(runCNN, 1, runCNN_ARGS(1))
    };
    WAIT_FOR_THREADS(threads_list)
    break;
  }
  case 3: {
    array<thread, 3> threads_list = {
      thread(runCNN, 0, runCNN_ARGS(0)),
      thread(runCNN, 1, runCNN_ARGS(1)),
      thread(runCNN, 2, runCNN_ARGS(2))
    };
    WAIT_FOR_THREADS(threads_list)
    break;
  }
  case 4: {
    array<thread, 4> threads_list = {
      thread(runCNN, 0, runCNN_ARGS(0)),
      thread(runCNN, 1, runCNN_ARGS(1)),
      thread(runCNN, 2, runCNN_ARGS(2)),
      thread(runCNN, 3, runCNN_ARGS(3))
    };
    WAIT_FOR_THREADS(threads_list)
    break;
  }
  case 5: {
    array<thread, 5> threads_list = {
      thread(runCNN, 0, runCNN_ARGS(0)),
      thread(runCNN, 1, runCNN_ARGS(1)),
      thread(runCNN, 2, runCNN_ARGS(2)),
      thread(runCNN, 3, runCNN_ARGS(3)),
      thread(runCNN, 4, runCNN_ARGS(4))
    };
    WAIT_FOR_THREADS(threads_list)
    break;
  }
  case 6: {
    array<thread, 6> threads_list = {
      thread(runCNN, 0, runCNN_ARGS(0)),
      thread(runCNN, 1, runCNN_ARGS(1)),
      thread(runCNN, 2, runCNN_ARGS(2)),
      thread(runCNN, 3, runCNN_ARGS(3)),
      thread(runCNN, 4, runCNN_ARGS(4)),
      thread(runCNN, 5, runCNN_ARGS(5))
    };
    };

    WAIT_FOR_THREADS(threads_list)
    break;
  }
  // case 7: {
  //   array<thread, 7> threads_list = {
  //     thread(runCNN, 0, runCNN_ARGS(0)),
  //     thread(runCNN, 1, runCNN_ARGS(1)),
  //     thread(runCNN, 2, runCNN_ARGS(2)),
  //     thread(runCNN, 3, runCNN_ARGS(3)),
  //     thread(runCNN, 4, runCNN_ARGS(4)),
  //     thread(runCNN, 5, runCNN_ARGS(5)),
  //     thread(runCNN, 6, runCNN_ARGS(6))
  //   };
  //   WAIT_FOR_THREADS(threads_list)
  //   break;
  // }
  // case 8: {
  //   array<thread, 8> threads_list = {
  //     thread(runCNN, 0, runCNN_ARGS(0)),
  //     thread(runCNN, 1, runCNN_ARGS(1)),
  //     thread(runCNN, 2, runCNN_ARGS(2)),
  //     thread(runCNN, 3, runCNN_ARGS(3)),
  //     thread(runCNN, 4, runCNN_ARGS(4)),
  //     thread(runCNN, 5, runCNN_ARGS(5)),
  //     thread(runCNN, 6, runCNN_ARGS(6)),
  //     thread(runCNN, 7, runCNN_ARGS(7))
  //   };
  //   WAIT_FOR_THREADS(threads_list)
  //   break;
  // }
  // case 9: {
  //   array<thread, 9> threads_list = {
  //     thread(runCNN, 0, runCNN_ARGS(0)),
  //     thread(runCNN, 1, runCNN_ARGS(1)),
  //     thread(runCNN, 2, runCNN_ARGS(2)),
  //     thread(runCNN, 3, runCNN_ARGS(3)),
  //     thread(runCNN, 4, runCNN_ARGS(4)),
  //     thread(runCNN, 5, runCNN_ARGS(5)),
  //     thread(runCNN, 6, runCNN_ARGS(6)),
  //     thread(runCNN, 7, runCNN_ARGS(7)),
  //     thread(runCNN, 8, runCNN_ARGS(8))
  //   };
  //   WAIT_FOR_THREADS(threads_list)
  //   break;
  // }
  default:{
    cerr << "Number of threads not supported\n";
    break;
  }
  }

#else
  /********************** Run multiple threads ********************/
  /* For loop and push_back into vector */
  vector<thread> threads_list;
  for ( int i = 0; i < num_threads; ++i ) {
    threads_list.push_back( thread( runCNN, i, runCNN_ARGS(i) ) );
  }

  for ( thread& t: threads_list ) {
    /* only threads that are not destructed can be joined;  */
    if ( t.joinable() ) {
      t.join();
    }
  }
  // threads_list.clear();
  // threads_list.shrink_to_fit();
  // vector<thread>().swap( threads_list );

  /*****************************************************************/
#endif

  /* Flag for uprobes */
  // flag_function_2();

  // End timestamp
  clock_gettime(CLOCK_REALTIME, &end_measure);

  // Print to file
  printf("[INFO] Printing runtime to file %s\n", filename);
  // Header
  fprintf(fd, "Start(sec);End(sec)\n");
  // Data
  fprintf(fd, "%llu.%.9lu;%llu.%.9lu\n", (unsigned long long)start_measure.tv_sec, start_measure.tv_nsec,
                                         (unsigned long long)end_measure.tv_sec, end_measure.tv_nsec);

  // Close file
  fclose(fd);

  // Clear objects
  labels.clear();
  images_names.clear();
  // labels.shrink_to_fit();
  // images_names.shrink_to_fit();
  vector<string>().swap( labels );
  vector<string>().swap( images_names );

  return 0;
}
